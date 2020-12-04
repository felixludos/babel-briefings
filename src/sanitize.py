

import sys, os, time
try:
	from tqdm import tqdm
except ImportError:
	tqdm = None
import json
import pytz
from datetime import datetime
from itertools import product

import omnifig as fig
from humpack.farming import Farmer

from notion.client import NotionClient
from googletrans import Translator

from .common import THIS_DIR, NATION_CODES, CATEGORIES, \
	MissingTokenError, BadStatusError, MissingLinkError, load_response, save_response

LANGUAGE_KEYS = ['title', 'description', 'content']


def resolve_source(source, author):
	ID, name = source['id'], source['name']
	
	if name is not None:
		source = name
	elif ID is not None:
		source = ID
	else:
		source = None
	
	if author is None:
		author = source
	
	return source, author

def article_iterator(responses):
	
	for cat in CATEGORIES:
		if cat in responses:
			for response in responses[cat]:
				for article in response['articles']:
					article['nation'] = response['nation']
					article['category'] = response['category']
					article['timestamp'] = response['timestamp']
					yield article
		# yield cat # signal for next cat -> save results


def _init(**kwargs):
	trans = Translator()
	return {'trans': trans}
	

def _run(raw, raw_titles, trans, language, **kwargs):
	cat = raw['category']
	
	article = raw.copy()
	
	fixed = 0
	if article['title'] in raw_titles:
		article['category'] = raw_titles[article['title']]
		fixed = 1
	
	# if cat == 'general':
	# 	possible += 1
	
	article['source'], article['author'] = resolve_source(raw['source'], raw['author'])
	
	article['language'] = trans.detect(article['title']).lang
	article['original_title'] = article['title']
	if language is not None and article['language'] != language:
		for key in LANGUAGE_KEYS:
			if article[key] is not None:
				out = trans.translate(article[key], dest=language)
				article[key] = out.text
	
	# articles.append(article)
	#
	# if cat not in full:
	# 	full[cat] = []
	# full[cat].append(article)
	# existing_titles.add(article['original_title'])
	
	return fixed, article


@fig.Script('sanitize-news', description='Format/Translate news headlines from json')
def format_news(A):
	
	# silent = A.pull('silent', False, silent=True) # TODO
	
	
	root = A.pull('root', os.path.join(THIS_DIR, 'raw_news'))
	
	# tz = A.pull('timezone', 'utc')
	today = A.pull('date', datetime.now(pytz.timezone('utc')).strftime('%y-%m-%d'))
	
	dest_dir = A.pull('dest_dir', 'clean_news')
	dest_name = A.pull('dest_name', f'{today}_clean') # without file extension
	out_path = os.path.join(dest_dir, f'{dest_name}.json')
	print(f'Will save sanitized articles to {out_path}')
	if not os.path.isdir(dest_dir):
		os.makedirs(dest_dir)
	
	assert out_path is not None, 'No outpath provided'
	
	news_root = os.path.join(root, today)
	
	assert os.path.isdir(news_root), f'No headlines for {today} were found in {root} (have you scraped any yet?)'
	
	timestamps = sorted(os.listdir(news_root))
	
	paths = {}
	for timestamp in timestamps:
		
		news_dir = os.path.join(news_root, timestamp)
		if os.path.isdir(news_dir):
			paths.update({record: os.path.join(news_dir, record) for record in os.listdir(news_dir)})
	
	pbar = A.pull('pbar', True)
	if pbar and tqdm is None:
		print('WARNING: tqdm missing ... no progress bar possible')
		pbar = False
	
	
	# trans = Translator()
	language = A.pull('language', 'en')
	if language is not None:
		print(f'Will translate all articles into {language}')
	
	cats = A.pull('categories', 'general')
	
	if isinstance(cats, str):
		if cats == 'all':
			cats = CATEGORIES.copy()
		else:
			cats = [cats, ]
	_valid = str(CATEGORIES + ['all'])
	_valid_cats = set(CATEGORIES)
	for cat in cats:
		assert cat in _valid_cats, f'Invalid category "{cat}", options: {_valid}'
	
	fix_general = A.pull('fix_general', True)
	raw_titles = {}
	
	skip_existing = A.pull('skip_existing', True)
	
	full = []
	existing_titles = set()
	if skip_existing and out_path is not None and os.path.isfile(out_path):
		full = load_response(out_path)
		existing_titles.update(a['original_title'] for a in full)

		print(f'Found previous collection of sanitized articles, using them to skip {len(existing_titles)} existing')
	
	limit = A.pull('limit', None)  # num articles per response
	if limit is not None:
		print(f'Only sanitizing the first {limit} articles for each response')
	
	responses = {}
	nums = {}
	
	for name, path in paths.items():
		response = load_response(path)
		cat = response['category']
		
		if response['status'] != 'ok':
			print(f'Skipping for bad status: {path}')
			continue
		
		if fix_general and cat != 'general':
			raw_titles.update({art['title']: cat for art in response['articles']})
		
		if cat not in cats:
			continue
		
		if skip_existing:
			response['articles'] = [a for a in response['articles'] if a['title'] not in existing_titles]
		
		if limit is not None:
			response['articles'] = response['articles'][:limit]
		
		if cat not in responses:
			nums[cat] = 0
			responses[cat] = []
		responses[cat].append(response)
		nums[cat] += len(response['articles'])
	
	total = sum(nums.values())
	
	num_workers = A.pull('sanitize_workers', '<>num_workers', 0)
	
	# save_interval = A.pull('interval', None) # TODO
	
	worker_info = f' ({num_workers} workers)' if num_workers > 0 else ''
	print(f'Will sanitize {total} articles in {len(responses)} categories '
	      f'from {sum(map(len,responses.values()))} responses.{worker_info}')
	
	print('Categories: {}'.format(', '.join(responses)))
	
	itr = article_iterator(responses)
	
	if pbar:
		itr = tqdm(itr, total=total)
	
	fixed = 0
	# possible = 0
	# cat_idx = 0
	art_num = 0
	# oldcat = None
	
	def _raw_args():
		for raw in itr:
			if pbar:
				fixed_info = f' (fixed {fixed})' if len(raw_titles) else ''
				# cat_info = f' ({cat_idx}/{nums[cat]})'
				itr.set_description('{:<12} {:>14}{}'.format(NATION_CODES[raw['nation']], raw['category'],
				                                               fixed_info))
			yield {'raw': raw}
	
	articles = []
	
	# raw, raw_titles, trans, language,

	arg_gen = _raw_args()
	farmer = Farmer(_run, volatile_gen=arg_gen, init_fn=_init,
	                private_args={'raw_titles': raw_titles, 'language': language},
	                timeout=A.pull('timeout', 20),
	                num_workers=num_workers)
	
	
	jobs = iter(farmer)
	
	for is_fixed, article in jobs:
		fixed += is_fixed
		art_num += 1
		
		if article['original_title'] not in existing_titles:
			full.append(article)
			articles.append(article)
		
		# if False:
		# 	save_response(articles, os.path.join(dest_dir, f'{dest_name}_{raw}.json'))
		
		existing_titles.add(article['original_title'])
	
	print(f'Formatted all {art_num} articles')
	
	save_response(full, out_path)
	
	return out_path
	
	# try:
	# 	for raw in itr:
	#
	# 		cat_idx += 1
	# 		art_num += 1
	#
	# 		cat = raw['category']
	# 		if oldcat is not None and cat != oldcat: # signal cat is complete -> save results
	#
	# 			save_response(articles, os.path.join(dest_dir, f'{dest_name}_{raw}.json'))
	#
	# 			cat_idx = 1
	# 			articles.clear()
	# 		oldcat = cat
	#
	# 		article = raw.copy()
	#
	# 		if article['title'] in raw_titles:
	# 			article['category'] = raw_titles[article['title']]
	# 			fixed += 1
	#
	# 		if cat == 'general':
	# 			possible += 1
	#
	# 		if pbar:
	# 			fixed_info = f' (fixed {fixed}/{possible})' if len(raw_titles) else ''
	# 			cat_info = f' ({cat_idx}/{nums[cat]})'
	# 			itr.set_description('{:<12} {:>14}{}{}'.format(NATION_CODES[raw['nation']], cat,
	# 			                                       cat_info, fixed_info))
	#
	# 		article['source'], article['author'] = resolve_source(raw['source'], raw['author'])
	#
	# 		article['language'] = trans.detect(article['title']).lang
	# 		article['original_title'] = article['title']
	# 		if language is not None and article['language'] != language:
	# 			for key in LANGUAGE_KEYS:
	# 				if article[key] is not None:
	# 					out = trans.translate(article[key], dest=language)
	# 					article[key] = out.text
	#
	# 		articles.append(article)
	#
	# 		if cat not in full:
	# 			full[cat] = []
	# 		full[cat].append(article)
	# 		existing_titles.add(article['original_title'])
	#
	# except KeyboardInterrupt as e:
	# 	print(f'Saving progress so far: {art_num}')
	# 	save_response(full, out_path)
	#
	# 	raise e
	
