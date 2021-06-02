import sys, os
from datetime import datetime
import omnifig as fig

from transformers import AutoTokenizer, AutoModelWithLMHead
from torch.distributions import Categorical

from transformers import MarianTokenizer, MarianMTModel
from typing import List

import pytz
import wget
import fasttext
from iso639 import languages
# from langdetect import detect

from collections import Counter
from pathlib import Path
from tqdm import tqdm
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader

from .common import THIS_DIR, CATEGORIES, NATION_CODES, save_response, load_response

FASTTEXT_URL = 'https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz'

TRANSLATION_MODELS = {
	'heb': None,
	'tur': 'Helsinki-NLP/opus-mt-tr-en',
	'por': None,
	'ukr': 'Helsinki-NLP/opus-mt-uk-en',
	'chi': 'Helsinki-NLP/opus-mt-zh-en',
	'rum': None,
	'lit': None,
	'ger': 'Helsinki-NLP/opus-mt-de-en',
	'lav': 'Helsinki-NLP/opus-mt-lv-en',
	'spa': 'Helsinki-NLP/opus-mt-es-en',
	'nor': 'Helsinki-NLP/opus-mt-ny-en',
	'hin': 'Helsinki-NLP/opus-mt-hi-en',
	'cze': 'Helsinki-NLP/opus-mt-cs-en',
	'bos': None,
	'jpn': 'Helsinki-NLP/opus-mt-ja-en',
	'swe': 'Helsinki-NLP/opus-mt-sv-en',
	'pol': 'Helsinki-NLP/opus-mt-pl-en',
	'tha': 'Helsinki-NLP/opus-mt-th-en',
	'slo': 'Helsinki-NLP/opus-mt-sk-en',
	'hun': 'Helsinki-NLP/opus-mt-hu-en',
	'mac': 'Helsinki-NLP/opus-mt-mk-en',
	'kor': 'Helsinki-NLP/opus-mt-ko-en',
	'rus': 'Helsinki-NLP/opus-mt-ru-en',
	'ita': 'Helsinki-NLP/opus-mt-it-en',
	'ind': 'Helsinki-NLP/opus-mt-id-en',
	'dut': 'Helsinki-NLP/opus-mt-nl-en',
	'ara': 'Helsinki-NLP/opus-mt-ar-en',
	'bul': 'Helsinki-NLP/opus-mt-bg-en',
	'srp': None,
	'fre': 'Helsinki-NLP/opus-mt-fr-en',
	'hau': 'Helsinki-NLP/opus-mt-ha-en',
	'guj': None,
	'glg': 'Helsinki-NLP/opus-mt-gl-en',
	'gre': None,
	'may': None,
	'slv': None
}



class ListDataset(Dataset):
	def __init__(self, data):
		self.data = data
	
	def __len__(self):
		return len(self.data)
	
	def __getitem__(self, idx):
		return self.data[idx]


class HOMT_Translator(nn.Module):
	def __init__(self, name, device='cpu', batch_size=None, pbar=False):
		super().__init__()
		
		model = MarianMTModel.from_pretrained(name)
		model.eval()
		model.to(device)
		
		tok = MarianTokenizer.from_pretrained(name)
		
		self.model = model
		self.tok = tok
		
		self.batch_size = batch_size
		self.pbar = pbar
		self.device = device
	
	def translate(self, *batch):
		return self.tok.batch_decode(self.model.generate(
			input_ids=self.tok.prepare_seq2seq_batch(src_texts=batch, return_tensors="pt").input_ids.to(self.device)).cpu(),
		                             skip_special_tokens=True)
	
	def forward(self, text):
		
		if self.batch_size is None:
			loader = [text]
		else:
			loader = DataLoader(ListDataset(text), batch_size=self.batch_size)
			if self.pbar:
				loader = tqdm(loader)
		
		completed = []
		for batch in loader:
			completed.extend(self.translate(*batch))
		
		return completed


class FastText_Language_Detector(nn.Module):
	
	def __init__(self, model_path=None, download=True):
		
		super().__init__()
		
		model_path = self._download(model_path, download=download)
		
		self.model = fasttext.load_model(str(model_path))
	
	def _download(self, path=None, download=True):
		
		if path is None:
			path = 'extra/lid.176.ftz'
		
		path = Path(path)
		
		if path.is_file():
			return path
		
		if not download:
			raise Exception('Missing Fasttext dection model parameters (set download=True to download them)')
		
		if path.is_dir():
			path = path / 'lid.176.ftz'
		
		wget.download(FASTTEXT_URL, out=str(path))
	
		return path
	
	def detect(self, text, k=None, probs=False):
		star = k is None
		if k is None:
			k = 1
		lbls, prob = self.model.predict(text, k=k)
		lbls = [l.split('__')[-1] for l in lbls]
		
		if star:
			lbls, prob = lbls[0], prob[0]
		
		return (lbls,prob) if probs else lbls
	
	def forward(self, text, k=None):
		
		ret_list = True
		if isinstance(text, str):
			ret_list = False
			text = [text]
	
		pred = [self.detect(t, k=k) for t in text]
		
		if ret_list:
			return pred
		return pred[0]


def load_article_files(root, cat='general'):
	full = []
	
	for path in root.glob(f'**/{cat}_*.json'):
		articles = load_response(path)['articles']
		nation = path.stem.split('.')[0].split('_')[-1]
		
		for article in articles:
			article['nation'] = nation
			article['category'] = cat
	
		full.extend(articles)
	
	return full
	
def recognize_language(code):
	if code in languages.part1:
		return languages.part1[code].part2b
	elif 'zh' in code:
		return languages.part1['zh'].part2b

@fig.Script('nlp-news', description='Format/Translate news headlines from json (using NLP models)')
def format_news(A):
	# silent = A.pull('silent', False, silent=True) # TODO
	
	root = A.pull('root', os.path.join(THIS_DIR, 'raw_news'))
	
	# tz = A.pull('timezone', 'utc')
	today = A.pull('date', datetime.now(pytz.timezone('utc')).strftime('%y-%m-%d'))
	
	dest_dir = A.pull('dest_dir', 'clean_news')
	dest_name = A.pull('dest_name', f'{today}_clean')  # without file extension
	out_path = os.path.join(dest_dir, f'{dest_name}.json')
	print(f'Will save sanitized articles to {out_path}')
	if not os.path.isdir(dest_dir):
		os.makedirs(dest_dir)
	

	device = A.pull('device', 'cuda' if torch.cuda.is_available() else 'cpu')
	if not torch.cuda.is_available():
		device = 'cpu'
	
	batch_size = A.pull('batch_size', 8)
	
	pbar = A.pull('pbar', True)
	if pbar and tqdm is None:
		print('WARNING: tqdm missing ... no progress bar possible')
		pbar = False
	
	language = A.pull('language', 'en')
	if language is not None:
		print(f'Will translate all articles into {language}')
	
	assert language == 'en'
	
	assert out_path is not None, 'No outpath provided'
	
	news_root = Path(os.path.join(root, today))
	
	assert news_root.is_dir(), f'No headlines for {today} were found in {root} (have you scraped any yet?)'
	
	raw = load_article_files(news_root, CATEGORIES[0])
	cats = {article['title']:article['category'] for article
	        in sum([load_article_files(news_root, cat) for cat in CATEGORIES[1:]],[])}
	
	##
	
	completed = set()
	if os.path.isfile(out_path):
		completed = {art['original_title'] for art in load_response(out_path)}
	
	detection = FastText_Language_Detector()
	fixed = 0
	
	langs = {}
	
	for article in raw:
		title = article['title']
		if title in completed:
			continue
		lang = recognize_language(detection(title))
		article['language'] = lang
		
		if lang not in langs:
			langs[lang] = []
		langs[lang].append(article)
		
		if title in cats:
			article['category'] = cats[title]
			fixed += 1
			
	total = sum(map(len,langs.values()))
	# print(langs.keys()) # testing
	
	print(f'Fixed {fixed}/{total} articles (skipping {len(raw) - total})')
	
	full = []
	if os.path.isfile(out_path):
		full = load_response(out_path)
		print(f'Loaded {len(full)} translated articles')

	progress = 0
	
	mnames = {}
	for lang, arts in langs.items():
		if lang == 'eng' or lang == 'en':
			progress += len(arts)
			for art in arts:
				art['original_title'] = art['title']
			full.extend(arts)
			continue
		
		mname = TRANSLATION_MODELS.get(lang, None)
		if mname is None:
			mname = 'Helsinki-NLP/opus-mt-mul-en'
			
		if mname not in mnames:
			if mname == 'Helsinki-NLP/opus-mt-mul-en':
				lang = None
			mnames[mname] = lang, []
		mnames[mname][1].extend(arts)
	
	save_response(full, out_path)
	print(f'Saved eng')
	
	for mname, (lang, arts) in mnames.items():
		
		model = HOMT_Translator(mname, device=device, batch_size=batch_size, pbar=pbar)
		
		lang = 'unknown' if lang is None else languages.part2b[lang].name
		
		print(f'Translating {len(arts)} {lang} articles (complete {progress}/{total})')
		
		tarts, titles = zip(*[(art,art['title']) for art in arts])
		out_titles = model(titles)
		for art, trans_title in zip(tarts, out_titles):
			art['original_title'] = art['title']
			art['title'] = trans_title
		
		darts, descs = zip(*[(art,art['description']) for art in arts
		                    if art['description'] is not None and len(art['description'])])
		with torch.no_grad():
			out_desc = model(descs)
		for art, trans_desc in zip(darts, out_desc):
			art['description'] = trans_desc
		
		del model
		
		full.extend(arts)
	
		save_response(full, out_path)
		
		print(f'Saved {lang}')
		progress += len(arts)

	
	print('All formatting complete')
	
	return full
	
