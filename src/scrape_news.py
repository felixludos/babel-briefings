
import sys, os, time
try:
	from tqdm import tqdm
except ImportError:
	tqdm = None
import json
import pytz
from datetime import datetime
from itertools import product

from argparse import Namespace

import omnifig as fig

import requests
# from newsapi.newsapi_exception import NewsAPIException
# from newsapi import NewsApiClient

from .common import THIS_DIR, MissingTokenError, BadStatusError, save_response, NATION_CODES, CATEGORIES


class Multi_News_API_Client:
	
	def __init__(self, *keys, silent=True, auto_retry=True):
		assert len(keys)
		self.idx = -1
		self.keys = keys
		self.silent = silent
		self.auto_retry = auto_retry
		
		self.restart_client()
		
	def get_top_headlines(self, **params):
		response = None
		if self.client is not None:
			retry = True
			while retry:
				try:
					response = self.client.get_top_headlines(**params)
					retry = False
				except Exception as e:
					print(e)
					self.restart_client()
					if self.client is None:
						raise e
					retry = True
				else:
					retry = response['status'] != 'ok' and self.auto_retry
					if retry:
						print(response)
						self.restart_client()
					# if retry and 'code' in response:
					# 	if response['code'] == 'rateLimited':
					# 		self.restart_client()
					# 	else:
					# 		raise Exception(response)
				
		return response
		
	# def _get_client(self, key):
	# 	return NewsApiClient(api_key=key)
		
	def restart_client(self):
		self.idx += 1
		if self.idx == len(self.keys):
			raise Exception('Out of API keys, unable to continue making requests')
			# self.client = None
			# return
		elif not self.silent:
			print(f'Using key {self.idx+1}/{len(self.keys)}')
		self.client = self._get_client(self.keys[self.idx])

class Requests_Client(Multi_News_API_Client):
	def __init__(self, *args, **kwargs):
		self._client = Namespace(get_top_headlines=self._request_headlines)
		super().__init__(*args, **kwargs)
		self.url_base = 'http://newsapi.org/v2/top-headlines?country={country}&category={category}&apiKey={apikey}' \
		                '&pageSize=100'

		
	def _request_headlines(self, **params):
		
		params['apikey'] = self.client.key
		
		url = self.url_base.format(**params)
		
		out = requests.get(url)
		
		return out.json()

	
	def _get_client(self, key):
		self._client.key = key
		return self._client
	
@fig.script('scrape-news', description='Scrape news using News API')
def scrape_news(A):
	
	silent = A.pull('silent', False, silent=True)
	
	api_keys = A.pulls('news_api_keys', 'news_api_key', 'api_keys', 'api_key',
	                 default=os.environ.get('NEWS_API_KEY', None), silent=True)
	if api_keys is None or len(api_keys) == 0:
		raise MissingTokenError('You must specify a News API Token (either using "--api_key" arg or by setting '
		                        '"NEWS_API_KEY" environment variable)')
	
	if isinstance(api_keys, str):
		api_keys = api_keys.split(':')
	
	if not silent:
		print(f'Found {len(api_keys)} News API keys.')
	
	# newsapi = Multi_News_API_Client(*api_keys)
	newsapi = Requests_Client(*api_keys)
	
	root = A.pull('root', os.path.join(THIS_DIR, 'raw_news'))
	if not os.path.isdir(root):
		os.makedirs(root, exist_ok=True)
	
	current_datetime = A.pull('datetime', None)
	tz = A.pull('timezone', 'utc')
	
	if current_datetime is None:
		current_datetime = datetime.now(pytz.timezone(tz))
	else:
		fmt = A.pull('datetime_fmt', '%y%m%d-%H%M%S')
		current_datetime = datetime.strptime(current_datetime, fmt)
	
	today = current_datetime.strftime('%y-%m-%d')
	
	today_dir = os.path.join(root, today)
	if not os.path.isdir(today_dir):
		os.makedirs(today_dir, exist_ok=True)
	
	times = sorted(os.listdir(today_dir))
	now = current_datetime.strftime('%H-%M-%S')
	
	force_update = A.pull('force_update', False)
	
	if len(times):
		if not silent:
			print(f'Some news has already been scraped today {today}')
	
		# if force_update:
		# 	print(f' ... Rescraping for now: {now}')
		# else:
		# 	print(' ... No update necessary (set with "--force_update")')
		# 	return 0
	
	news_dir = os.path.join(today_dir, now)
	
	cats = A.pulls('scrape_categories', 'categories', default='general')
	
	if isinstance(cats, str):
		if cats == 'all':
			cats = CATEGORIES.copy()
		else:
			cats = [cats,]
	_valid = str(CATEGORIES + ['all'])
	_valid_cats = set(CATEGORIES)
	for cat in cats:
		assert cat in _valid_cats, f'Invalid category "{cat}", options: {_valid}'
	
	nations = A.pull('nations', 'all')
	
	if isinstance(nations, str):
		if nations == 'all':
			nations = list(NATION_CODES.keys())
		else:
			nations = [nations,]
	
	_valid = str(list(NATION_CODES.keys()) + ['all'])
	for nation in nations:
		assert nation in NATION_CODES, f'Invalid nation {nation} (2 letter code required), ' \
		                               f'options: {NATION_CODES.keys()}'
	
	skip_existing = A.pull('skip_existing', True)
	existing = set()
	
	if skip_existing:
		
		for time_dir in os.listdir(today_dir):
			time_dir = os.path.join(today_dir, time_dir)
			if os.path.isdir(time_dir):
				existing.update(tuple(fname.split('.')[0].split('_'))
				                for fname in os.listdir(time_dir))
	
	pbar = A.pull('pbar', True)
	if pbar and tqdm is None:
		print('WARNING: tqdm missing ... no progress bar possible')
		pbar = False
	

	skip_confirm = A.pull('skip_confirm', False)
	
	print()
	print('News Scraper using the News API')

	print('Categories: {}'.format(', '.join(cats)))
	print('Countries: {}'.format(', '.join(NATION_CODES[n] for n in nations)))
	print()
	
	num = len(nations) * len(cats)
	
	jobs = [item for item in product(cats, nations) if item not in existing]
	
	if len(jobs) < num:
		print(f'Filtered out {num-len(jobs)} existing responses (for today), {len(jobs)} remaining jobs')
	
	print(f'This will require {len(jobs)} new requests from News API')
	
	if not skip_confirm:
		out = input('Confirm to proceed (y/[n]): ')
		if out.lower() != 'y':
			print('\nQuitting without executing any requests.')
			return 0
	
	save_error_responses = A.pull('save_error_responses', True)
	
	os.makedirs(news_dir, exist_ok=True)
	
	if pbar:
		jobs = tqdm(jobs)
	
	for cat, nation in jobs:
		
		if pbar:
			jobs.set_description(f'{NATION_CODES[nation]:<12} {cat:>14}')
		
		name = f'{cat}_{nation}.json'
		path = os.path.join(news_dir, name)
		
		# response = json.load(open('test_bg_business.json', 'r'))
		# time.sleep(0.03)
		try:
			response = newsapi.get_top_headlines(category=cat, country=nation, page_size=100)

		except Exception as e:
			
			print(f'Using News API key number {newsapi.idx+1}, starts with: {newsapi.keys[newsapi.idx][:4]}...')
			
			raise e

		if response is None or ('status' in response and response['status'] != 'ok'):
			if save_error_responses:
				print(f'Saving response to: {path}')
				save_response(response, path)
			raise BadStatusError(response['status'])
		
		response['timestamp'] = f'{today}_{now} ({tz})'
		response['nation'] = nation
		response['category'] = cat
		
		save_response(response, path)
	
	print(f'All requests complete and saved to: {news_dir}')
	
	return 0






