
import sys, os, time
try:
	from tqdm import tqdm
except ImportError:
	tqdm = None
import json
import pytz
from datetime import datetime
from itertools import product
import uuid
import random

from requests import HTTPError

# from humpack.farming import Farmer

import omnifig as fig

# import emoji
# from notion.client import NotionClient
# from notion import block as nt

# from iso639 import languages

from .common import NATION_CODES, CATEGORIES, LANGUAGE_CODES, LANGUAGE_NATIONS


from .common import THIS_DIR, MissingTokenError, BadStatusError, MissingLinkError, load_response, save_response

CATEGORIES_COLORS = {
	'business': 'yellow',
	'entertainment': 'purple',
	'general': 'gray',
	'health': 'red',
	'science': 'green',
	'sports': 'pink',
	'technology': 'blue',
}

def load_client_page(A, silent=False):
	token = A.pulls('notion_token', 'token', default=os.environ.get('NOTION_TOKEN', None), silent=True)
	
	if token is None:
		raise MissingTokenError('You must specify a News API Token (either using "--token" arg or by setting '
		                        '"NOTION_TOKEN" environment variable)')
	
	client = NotionClient(token_v2=token)
	
	link = A.pulls('notion_link', 'link', default=None, silent=silent)
	
	if link is None:
		raise MissingLinkError('You must provide a link to the notion table that should be used as a news database')
	
	page = client.get_block(link)
	
	
	return client, page

NATION_EMOJI_FIXES = {
	'Czech_Republic': 'Czechia',
	'Hong_Kong': 'Hong_Kong_SAR_China',
	'UAE': 'United_Arab_Emirates',
	'US': 'United_States',
	'UK': 'United Kingdom',
	'Bosnia': 'Bosnia_&_Herzegovina',
}

LANGUAGE_FIXES = {
	'bshr': 'hr',
	'iw': 'he',
	'zh-CN': 'zh',
	'deen': 'de',
	'idms': 'id',
	'frco': 'fr',
	'hrbs': 'hr',
	'mkbg': 'mk',
	'esgl': 'es',
	'enms': 'en',
	'enfy': 'en',
	'gl': 'es',
	'eneu': 'en',
	'lbde': 'de',
}

def get_flag(nation):
	if nation in NATION_CODES:
		nation = NATION_CODES[nation]
	
	nation = nation.replace(' ', '_')
	if nation in NATION_EMOJI_FIXES:
		nation = NATION_EMOJI_FIXES[nation]
	return emoji.emojize(f':{nation}:')

def get_nation(code, with_emoji=True):
	assert code in NATION_CODES, f'Unknown nation code: {code}'
	
	name = NATION_CODES[code]
	
	if with_emoji:
		flag = get_flag(name)
		name = f'{flag} {name}'
	
	return name

def get_nation_names(with_emoji=True):
	
	nations = {}
	
	for code, name in NATION_CODES.items():
		
		if with_emoji:
			flag = get_flag(name)
			name = f'{flag} {name}'
		
		nations[code] = name
	
	return nations


def get_language_code(lang, as_emoji=True, procs=False):
	
	if lang is None:
		return 'Unknown'
	
	if not procs and len(lang) == 3:
		lang = languages.part2b[lang].part1 if lang in languages.part2b else lang
		return get_language_code(lang, as_emoji=as_emoji, procs=True)
	
	if lang in LANGUAGE_FIXES:
		lang = LANGUAGE_FIXES[lang]
	if len(lang) > 2:
		lang = lang[:2]
	
	if lang not in LANGUAGE_NATIONS:
		# print(f'WARNING: Encoutered an unknown language: {lang}')
		return 'Other'
	
	if not as_emoji:
		assert lang in LANGUAGE_CODES, f'Unknown language: {lang}'
		return LANGUAGE_CODES[lang]
	
	if lang not in LANGUAGE_NATIONS:
		raise Exception(f'Unknown language code: {lang}')
	
	return get_flag(LANGUAGE_NATIONS[lang])

def get_language_names(as_emoji=True):
	return set(get_language_code(code,  as_emoji=as_emoji) for code in LANGUAGE_NATIONS)


@fig.autocomponent('schema/full_table')
def full_table_schema(with_emoji=True):
	
	nation_options = [{'id' :str(uuid.uuid4()), 'color' :'default', 'value' :n}
	                  for n in get_nation_names(with_emoji=with_emoji).values()]
	
	category_options = [{'id' :str(uuid.uuid4()), 'color': CATEGORIES_COLORS[cat], 'value' :cat}
	                    for cat in CATEGORIES]
	
	sch = {
		"title": {"name": "Name", "type": "title"},
		"%9:q": {"name": "Compiled on", "type": "date"},
		# "1232": {
		#     "name": "Nations",
		#     "type": "multi_select",
		#     "options": nation_options,
		# },
		# "abcd": {
		#     "name": "Categories",
		#     "type": "multi_select",
		#     "options": category_options,
		# },
	}
	return sch


@fig.autocomponent('schema/news_table')
def full_table_schema(with_emoji=True, language_emojis=False):
	nation_options = [{'id': str(uuid.uuid4()), 'color': 'default', 'value': n}
	                  for n in get_nation_names(with_emoji=with_emoji).values()]
	
	category_options = [{'id': str(uuid.uuid4()), 'color': CATEGORIES_COLORS[cat], 'value': cat}
	                    for cat in CATEGORIES]
	
	language_options = get_language_names(as_emoji=language_emojis)
	language_options.add('Other')
	
	language_options = [{'id': str(uuid.uuid4()), 'color': 'default', 'value': lang}
	                    for lang in language_options]
	
	
	sch = {
		"title": {"name": "Title", "type": "title"},
		"r4sg": {"name": "Original Title", "type": "text"},
		"qwer": {"name": "Description", "type": "text"},
		"%9:q": {"name": "Published", "type": "date"},
		"%asq": {"name": "Collected", "type": "date"},
		"dV$q": {"name": "Author", "type": "text"},
		"axK$": {"name": "Source", "type": "text"},
		"OBcJ": {"name": "Link", "type": "url"},
		"1232": {
			"name": "Nation",
			"type": "select",
			"options": nation_options,
		},
		"abcd": {
			"name": "Category",
			"type": "select",
			"options": category_options,
		},
		"cbsd": {
			'name': 'Language',
			'type': 'select',
			'options': language_options,
		}
	}
	return sch

def get_view(cvb, view_type='table'):
	
	for view in cvb.views:
		if view.type == view_type:
			return view
	return cvb.views.add_new(view_type=view_type)

@fig.component('row_formatter')
class Notion_Formatter(fig.Configurable):
	def __init__(self, with_emoji=True, language_emojis=False, language='en', include_icons=True):
		
		self.with_emoji = with_emoji
		self.language_emoji = language_emojis
		self.language = language
		self.include_icons = include_icons
		
		self.clt = None
	
	def accept_schema(self, schema):
		raise NotImplementedError # TODO
	
	def parse_date(self, date):
		return datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
	
	def parse_timestamp(self, timestamp):
		if ' ' in timestamp:
			timestamp = timestamp.split(' ')[0]
		
		return datetime.strptime(timestamp, '%y-%m-%d_%H-%M-%S')
	
	def set_collection(self, clt):
		self.clt = clt
	
	def __call__(self, article):
		
		info = {}
		
		info['title'] = article['title']
		info['original_title'] = article['original_title']
		
		if article['author'] is not None:
			info['author'] = article['author']
		
		if article['source'] is not None and isinstance(article['source'], str):
			info['source'] = article['source']
		
		language = get_language_code(article['language'], as_emoji=self.language_emoji)
		info['language'] = language
		
		if language == 'Other':
			lang = article['language']
			otitle = article['original_title']
			print(f'\nUnknown language: {lang} from article: {otitle}')
		
		info['icon'] = get_flag(article['nation'])
		
		info['link'] = article['url']
		
		info['published'] = self.parse_date(article['publishedAt'])
		if 'timestamp' in article:
			info['collected'] = self.parse_timestamp(article['timestamp'])
		
		info['nation'] = get_nation(article['nation'], with_emoji=self.with_emoji)
		
		info['category'] = article['category']
		
		if article['urlToImage'] is not None:
			info['cover'] = article['urlToImage']
		
		if article['description'] is not None:
			info['description'] = article['description']
		
		row = self.clt.add_row(update_views=False, **info)
		
		# try:
		# 	row = self.clt.add_row(**info)
		# except HTTPError as e:
		#
		# 	if '413' in str(e): # payload too large - split into two transactions
		# 		later = {}
		# 		if 'description' in info:
		# 			later['description'] = info['description']
		# 			del info['description']
		# 		# later['title'] = info['title']
		# 		# del info['title']
		# 		later['original_title'] = info['original_title']
		# 		del info['original_title']
		# 		if 'cover' in info:
		# 			later['cover'] = info['cover']
		# 			del info['cover']
		# 		if 'link' in info:
		# 			later['link'] = info['link']
		# 			del info['link']
		#
		# 		row = self.clt.add_row(**info)
		#
		# 		# row.title = later['title']
		# 		if 'description' in later:
		# 			row.description = later['description']
		# 		row.original_title = later['original_title']
		# 		if 'cover' in later:
		# 			row.cover = later['cover']
		# 		if 'link' in later:
		# 			row.link = later['link']
		# 	else:
		# 		raise e
		
		
		# row.title = article['title']
		#
		# row.original_title = article['original_title']
		#
		# if article['author'] is not None:
		# 	row.author = article['author']
		#
		# if article['source'] is not None:
		# 	row.source = article['source']
		
		# language = get_language_code(article['language'], as_emoji=self.language_emoji)
		#
		# row.language = language
		
		
		# if self.include_icons:
		# 	row.icon = get_language_code(article['language'], as_emoji=True)
		
		# row.icon = get_flag(article['nation'])
		#
		# row.link = article['url']
		
		# row.published = self.parse_date(article['publishedAt'])
		# row.collected = self.parse_timestamp(article['timestamp'])
		
		# row.nation = get_nation(article['nation'], with_emoji=self.with_emoji)
		#
		# row.category = article['category']
		#
		# if article['urlToImage'] is not None:
		# 	row.cover = article['urlToImage']
		#
		# if article['description'] is not None:
		# 	row.description = article['description']
		
		# if article['content'] is not None:
		# 	row.children.add_new(nt.TextBlock, title=article['content'])
		
		
		return row.id, article



@fig.script('new-notion-table', description='Create new notion table on the provided page')
def new_table(A):
	
	client, page = load_client_page(A)
	
	print(f'Creating new table on page: {page.title}')
	
	cvb = page.children.add_new(nt.CollectionViewBlock)
	
	schema = A.pull('schema')
	
	cvb.collection = client.get_collection(
		client.create_record("collection", parent=cvb, schema=schema)
	)
	
	title = A.pull('title', None)
	if title is not None:
		cvb.title = title
	
	description = A.pull('description', None)
	if description is not None:
		cvb.description = description
	
	
	view = get_view(cvb, view_type='table')
	
	page.refresh()
	
	ret_client = A.pull('return_client', False)
	
	if ret_client:
		return client, page
	
	return cvb.collection.id # returns ID of table

class NoTableFoundError(Exception):
	def __init__(self, link):
		super().__init__(f'No suitable table found on {link}')


def _run(article, formatter, **kwargs):
	return formatter(article)

def _init(A, table_id):
	client, page = load_client_page(A, silent=True)
	
	clt = client.get_collection(table_id)
	
	clt.refresh()
	cvb = clt.parent
	view = get_view(cvb)
	
	formatter = A.pull('formatter', silent=True)
	formatter.set_collection(clt)
	
	return {'formatter': formatter}


@fig.script('present-notion', description='Present world news on Notion page')
def present_notion(A):
	
	silent = A.pull('silent', False, silent=True)
	
	now = datetime.now(pytz.timezone('utc'))
	
	today = A.pull('date', now.strftime('%y-%m-%d') )
	
	news_path = A.pull('news_path', None)
	
	if news_path is None:
		news_path = f'clean_news/{today}_clean.json'
	
	if not os.path.isfile(news_path):
		print(f'Error: no sanitized news found: {news_path}')
	
	articles = load_response(news_path)
	
	if len(articles) == 0:
		raise Exception(f'No articles found')# in specified categories: {cats}')
	
	client, page = load_client_page(A)
	
	link = A.pull('notion_link', '<>link', None, silent=True)
	
	table_id = A.pull('table_id', None)
	clt = None
	
	for child in page.children:
		if child.title == 'No Nonsense News Headlines':
			clt = child.collection
			table_id = clt.id
	if clt is None:
		if table_id is None:
			auto_create_new_table = A.pull('auto_create_new_table', True)
			
			print('Failed to find a table to present articles')
			
			if auto_create_new_table:
				print(' ... Creating a new table')
				A.begin()
				
				description = f'More info: [No-Nonsense-News](https://www.notion.so/felixleeb/' \
	                  f'No-Nonsense-News-0ecebf66967147dda6a96b549c7a73d1)'
				
				A.push('schema._type', 'schema/news_table', overwrite=False)
				A.push('title', 'No Nonsense News Headlines', overwrite=False)
				A.push('description', description, overwrite=False)
				
				table_id = fig.run('new-notion-table', A)
				
				print(f'Created table with ID: {table_id}')
				client.get_collection(table_id)
				
				A.abort()
			
			else:
				raise NoTableFoundError(link)
		
		clt = client.get_collection(table_id)
	
	clt.refresh()
	cvb = clt.parent
	view = get_view(cvb)
	
	present_dir = A.pull('present_dir', 'present_news')
	if present_dir is not None and not os.path.isdir(present_dir):
		os.makedirs(present_dir)
	
	row_tracker_path = None
	if present_dir is not None:
		row_tracker_path = os.path.join(present_dir, 'row_titles.json')
		print(f'Will keep track of current rows to improve updating in {row_tracker_path}')
	
	pbar = A.pull('pbar', True)
	if pbar and tqdm is None:
		print('WARNING: tqdm missing ... no progress bar possible')
		pbar = False
	
	resume = A.pull('resume', False)
	if resume:
		print('Resuming operation (so no existing records will be removed)')
	
	row_tracker = load_response(row_tracker_path) \
		if row_tracker_path is not None and os.path.isfile(row_tracker_path) else {}
	
	if len(row_tracker):
		print(f'Already aware of {len(row_tracker)} row titles.')
	
	if resume:
		remove_existing = False
	else:
		remove_existing = A.pull('remove_existing', True)
	skip_existing = A.pull('skip_existing', True)
	stepsize = A.pull('stepsize', 100)
	
	if remove_existing:
		skip_confirm = A.pull('skip_confirm', False)
		
		rows = clt.get_rows()
		
		if not skip_confirm:
			inp = input(f'Will remove existing {len(rows)} rows from table, confirm (y/[n])? ')
			if inp.lower() != 'y':
				print('Quitting without doing anything.')
				return 1
			
		if len(rows):
			
			batches = (len(rows) + stepsize - 1) // stepsize
			bidxs = range(batches)
			
			if pbar:
				bidxs = tqdm(bidxs, total=batches)
				bidxs.set_description(f'Removing existing {len(rows)} rows')
			
			for bidx in bidxs:
				with client.as_atomic_transaction():
					for row in rows[bidx*stepsize:(bidx+1)*stepsize]:
						row.remove()
			
			row_tracker.clear()
			
			print()
			
	clt.refresh()
	
	existing = set()
	if skip_existing:

		rows = clt.get_rows()
		
		row_iter = iter(rows)
		
		if pbar:
			row_iter = tqdm(row_iter, total=len(rows))
			row_iter.set_description(f'Collecting existing titles')
		
		for row in row_iter:
			ID = row.id
			if ID not in row_tracker:
				row_tracker[ID] = row.title
			existing.add(row_tracker[ID])
		
		if row_tracker_path is not None:
			save_response(row_tracker, row_tracker_path)
		
		print()
	
	# existing = set(row_tracker.values())
	
	clt.refresh()
	
	raw_num = len(articles)
	
	articles = [art for art in articles if art['title'] not in existing]
	
	num = len(articles)
	
	order = A.pull('order', True)
	if order is not None:
		if not isinstance(order, (list, tuple)):
			order = CATEGORIES.copy()
		
		for c in CATEGORIES:
			if c not in order:
				order.append(c)
		
		val = {cat:i for i, cat in enumerate(CATEGORIES)}
		val['general'] = 100 # last
		articles = sorted(articles, key=lambda a: val[a['category']])
		
	shuffle = A.pull('shuffle', False)
	if shuffle:
		random.shuffle(articles)
	
	
	num_workers = A.pull('num_workers', 0)
	
	skip_info = f' (skipping {raw_num - num})' if raw_num - num > 0 else ''
	worker_info = f' ({num_workers} workers)' if num_workers > 0 else ''
	
	print(f'Presenting {num} new articles {skip_info}{worker_info}')
	
	A.push('formatter._type', 'row_formatter', overwrite=False)
	
	
	itr = iter(articles)
	if pbar:
		itr = tqdm(itr, total=num)
	
	def _formatter_args():
		for article in itr:
			if pbar:
				nation, cat = article['nation'], article['category']
				itr.set_description(f'{NATION_CODES[nation]:<14} {cat:>12}')
			yield {'article': article}
	
	arg_gen = _formatter_args()
	farmer = Farmer(_run, volatile_gen=arg_gen, init_fn=_init,
	                private_args={'table_id': table_id, 'A': A},
	                num_workers=num_workers)
	
	jobs = iter(farmer)
	
	try:
		for ID, info in jobs:
			row_tracker[ID] = info['title']
	
	except Exception as e:
		
		if pbar:
			itr.close()
		
		if row_tracker_path is not None:
			save_response(row_tracker, row_tracker_path)
			print(f'Saved row IDs and titles for future updates: {row_tracker_path}')
			
		if isinstance(e, HTTPError):
			print('\nNOTE: This error is most likely due to the high volume of requests sent to \n'
			      'the Notion server to update the page. If so, you can wait \n'
			      'for a few minutes and retry (suggestion: use the "--resume" flag)\n')
			
		raise e
	
	if row_tracker_path is not None:
		save_response(row_tracker, row_tracker_path)
		print(f'Saved row IDs and titles for future updates: {row_tracker_path}')
	
	current = now.strftime("%d %b %Y")
	
	clt.description = f'More info: [No-Nonsense-News](https://www.notion.so/felixleeb/' \
	                  f'No-Nonsense-News-0ecebf66967147dda6a96b549c7a73d1) (Last updated {current})'
	
	clt.refresh()
