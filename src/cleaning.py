from pathlib import Path
from tqdm import tqdm
import json
from .common import THIS_DIR

from omnibelt import load_json
import omnifig as fig



def load_jsonl(path):
	return [json.loads(line) for line in path.read_text().split('\n') if len(line)]
def save_jsonl(path, records):
	path.write_text('\n'.join(json.dumps(line) for line in records))
def save_jsonl_dict(path, data):
	save_jsonl(path, [{'title': title, 'description': desc, 'ids': ids} for (title, desc), ids in data.items()])
def to_ids(records):
	ids, errs = {}, set()
	for record in records:
		payload = record['title'], record.get('description')
		for ID in record.get('ids', [record.get('ID')]):
			if ID in ids:
				errs.add(ID)
			ids[ID] = payload
	return ids, errs
def group_ids(id_dict):
	table = {}
	for ID, value in id_dict.items():
		table.setdefault(value, []).append(ID)
	return table
def find_matches(ids1, ids2, strict=True):
	match, nomatch = set(), set()
	for ID in set(ids1) & set(ids2):
		(match if (ids1[ID] == ids2[ID]
				   if strict
				   else any(term1 is not None and len(term1) and term1 == term2 for term1, term2 in zip(ids1[ID], ids2[ID])))
		 else nomatch).add(ID)
	return match, nomatch
def remove_ids(id_dict, ids):
	for ID in ids:
		if ID in id_dict:
			id_dict.pop(ID)
	# return id_dict

def find_record_file(path, root=None, loc=None):
	if loc is not None:
		path = path.format(loc=loc)
	path = Path(path)
	if root is not None:
		path = root / path
	if root is None and not path.exists() and (THIS_DIR / path).exists():
		path = THIS_DIR / path
	return path


@fig.script('loc-prompts')
def loc_prompts(cfg: fig.Configuration):

	loc = cfg.pull('loc')
	if not isinstance(loc, str):
		raise ValueError(f'loc must be a string, not {type(loc)}')

	root = cfg.pull('root', None)

	promptpath = find_record_file(cfg.pull('promptpath'), root, loc)

	articleroot = Path(cfg.pull('articleroot'))
	articlepaths = list(articleroot.glob(cfg.pull('articlepattern', 'news-headlines-{loc}.json').format(loc=loc)))
	print(f'Found {len(articlepaths)} article files.')

	articles = [art for articlepath in tqdm(articlepaths) for art in load_json(articlepath)]
	print(f'Loaded {len(articles)} articles.')

	ids, errs = to_ids(articles)
	assert not errs

	prompts = group_ids(ids)

	print(f'Saving {len(prompts)} prompts ({len(ids)} unique IDs).')
	save_jsonl_dict(promptpath, prompts)

	print('Done.')



@fig.script('clean-prompts')
def clean_prompts(cfg: fig.Configuration):

	loc = cfg.pull('loc', None)
	if not isinstance(loc, str):
		raise ValueError(f'loc must be a string, not {type(loc)}')

	root = cfg.pull('root', None)

	blobroot = Path(cfg.pull('blobroot'))
	blobpaths = list(blobroot.glob(cfg.pull('blobpattern', 'saved_records_*.jsonl')))
	print(f'Found {len(blobpaths)} blob files.')

	accept_incomplete = cfg.pull('accept', False)

	# promptpath = localroot/'interface'/'prompts'/f'prompts-{loc}.jsonl'
	promptpath = find_record_file(cfg.pull('promptpath'), root, loc)
	assert promptpath.exists()

	# completedpath = localroot / 'interface' / 'completed' / f'completed_{loc}.jsonl'
	completedpath = find_record_file(cfg.pull('completedpath'), root, loc)
	if not completedpath.exists():
		print(f'No completed file found at {completedpath}. Creating an empty one.')
		completedpath.touch()

	new = [rec for blobpath in tqdm(blobpaths) for rec in load_jsonl(blobpath)]
	print(f'Loaded {len(new)} new candidates.')
	#%%
	completed = load_jsonl(completedpath)
	print(f'Loaded {len(completed)} completed records.')
	complids, errs = to_ids(completed)
	assert not errs
	#%%
	candids, errs = to_ids(new)
	assert not errs
	#%%
	dupes, inconsistent = find_matches(candids, complids)
	print(f'Found {len(dupes)} duplicates (ignoring).')
	if len(inconsistent):
		print(f'Found {len(inconsistent)} inconsistent records!')
	prev = len(complids)
	complids.update(candids)
	print(f'Added {len(complids) - prev} new completed records (now {len(complids)} completed).')
	#%%
	todo = load_jsonl(promptpath)
	print(f'Loaded {len(todo)} prompts.')
	todoids, errs = to_ids(todo)
	assert not errs
	#%%
	incomplete, unnecessary = find_matches(complids, todoids, strict=False)
	print()
	print(f'Found {len(incomplete)} untranslated prompts in completed.')
	print(f'Found {len(unnecessary)} newly completed prompts.')
	print()

	remove_ids(todoids, unnecessary)
	if accept_incomplete:
		remove_ids(todoids, incomplete)
	else:
		for redo in incomplete:
			todoids[redo] = complids[redo]
		remove_ids(complids, incomplete)

	remaining = group_ids(todoids)
	done = group_ids(complids)
	print(f'{len(remaining)} remaining prompts ({len(todoids)} unique IDs).')
	print(f'{len(done)} completed prompts ({len(complids)} unique IDs).')
	if loc is not None:
		print(f'Total for {loc}: {len(remaining) + len(done)} records ({len(todoids) + len(complids)} IDs)')

	save_jsonl_dict(promptpath, remaining)
	save_jsonl_dict(completedpath, done)

	for blobpath in blobpaths:
		blobpath.unlink()

	print('Done.')






























