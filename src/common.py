

import sys, os, time
try:
	from tqdm import tqdm
except ImportError:
	tqdm = None
import json
import pytz


NATION_CODES = {
 'ar': 'Argentina',
 'au': 'Australia',
 'at': 'Austria',
 'be': 'Belgium',
 'br': 'Brazil',
 'bg': 'Bulgaria',
 'ca': 'Canada',
 'cn': 'China',
 'co': 'Colombia',
 'cu': 'Cuba',
 'cz': 'Czech Republic',
 'eg': 'Egypt',
 'fr': 'France',
 'de': 'Germany',
 'gr': 'Greece',
 'hk': 'Hong Kong',
 'hu': 'Hungary',
 'in': 'India',
 'id': 'Indonesia',
 'ie': 'Ireland',
 'il': 'Israel',
 'it': 'Italy',
 'jp': 'Japan',
 'lv': 'Latvia',
 'lt': 'Lithuania',
 'my': 'Malaysia',
 'mx': 'Mexico',
 'ma': 'Morocco',
 'nl': 'Netherlands',
 'nz': 'New Zealand',
 'ng': 'Nigeria',
 'no': 'Norway',
 'ph': 'Philippines',
 'pl': 'Poland',
 'pt': 'Portugal',
 'ro': 'Romania',
 'ru': 'Russia',
 'sa': 'Saudi Arabia',
 'rs': 'Serbia',
 'sg': 'Singapore',
 'sk': 'Slovakia',
 'si': 'Slovenia',
 'za': 'South Africa',
 'kr': 'South Korea',
 'se': 'Sweden',
 'ch': 'Switzerland',
 'tw': 'Taiwan',
 'th': 'Thailand',
 'tr': 'Turkey',
 'ae': 'UAE',
 'ua': 'Ukraine',
 'gb': 'United Kingdom',
 'us': 'United States',
 've': 'Venezuela',
}

CATEGORIES = ['general', 'science', 'technology', 'business',
              'health', 'entertainment', 'sports']

LANGUAGE_CODES = [('ab', 'Abkhaz'),
('aa', 'Afar'),
('af', 'Afrikaans'),
('ak', 'Akan'),
('sq', 'Albanian'),
('am', 'Amharic'),
('ar', 'Arabic'),
('an', 'Aragonese'),
('hy', 'Armenian'),
('as', 'Assamese'),
('av', 'Avaric'),
('ae', 'Avestan'),
('ay', 'Aymara'),
('az', 'Azerbaijani'),
('bm', 'Bambara'),
('ba', 'Bashkir'),
('eu', 'Basque'),
('be', 'Belarusian'),
('bn', 'Bengali'),
('bh', 'Bihari'),
('bi', 'Bislama'),
('bs', 'Bosnian'),
('br', 'Breton'),
('bg', 'Bulgarian'),
('my', 'Burmese'),
('ca', 'Catalan'),
('ch', 'Chamorro'),
('ce', 'Chechen'),
('ny', 'Chichewa'),
('zh', 'Chinese'),
('cv', 'Chuvash'),
('kw', 'Cornish'),
('co', 'Corsican'),
('cr', 'Cree'),
('hr', 'Croatian'),
('cs', 'Czech'),
('da', 'Danish'),
('dv', 'Divehi'),
('nl', 'Dutch'),
('dz', 'Dzongkha'),
('en', 'English'),
('eo', 'Esperanto'),
('et', 'Estonian'),
('ee', 'Ewe'),
('fo', 'Faroese'),
('fj', 'Fijian'),
('fi', 'Finnish'),
('fr', 'French'),
('ff', 'Fula'),
('gl', 'Galician'),
('ka', 'Georgian'),
('de', 'German'),
('el', 'Greek'),
('gn', 'Guaraní'),
('gu', 'Gujarati'),
('ht', 'Haitian'),
('ha', 'Hausa'),
('he', 'Hebrew'),
('hz', 'Herero'),
('hi', 'Hindi'),
('ho', 'Hiri Motu'),
('hu', 'Hungarian'),
('ia', 'Interlingua'),
('id', 'Indonesian'),
('ie', 'Interlingue'),
('ga', 'Irish'),
('ig', 'Igbo'),
('ik', 'Inupiaq'),
('io', 'Ido'),
('is', 'Icelandic'),
('it', 'Italian'),
('iu', 'Inuktitut'),
('ja', 'Japanese'),
('jv', 'Javanese'),
('kl', 'Kalaallisut'),
('kn', 'Kannada'),
('kr', 'Kanuri'),
('ks', 'Kashmiri'),
('kk', 'Kazakh'),
('km', 'Khmer'),
('ki', 'Gikuyu'),
('rw', 'Kinyarwanda'),
('ky', 'Kyrgyz'),
('kv', 'Komi'),
('kg', 'Kongo'),
('ko', 'Korean'),
('ku', 'Kurdish'),
('kj', 'Kwanyama'),
('la', 'Latin'),
('lb', 'Luxembourgish'),
('lg', 'Luganda'),
('li', 'Limburgish'),
('ln', 'Lingala'),
('lo', 'Lao'),
('lt', 'Lithuanian'),
('lu', 'Luba-Katanga'),
('lv', 'Latvian'),
('gv', 'Manx'),
('mk', 'Macedonian'),
('mg', 'Malagasy'),
('ms', 'Malay'),
('ml', 'Malayalam'),
('mt', 'Maltese'),
('mi', 'Māori'),
('mr', 'Marathi'),
('mh', 'Marshallese'),
('mn', 'Mongolian'),
('na', 'Nauru'),
('nv', 'Navajo'),
('nb', 'Norwegian Bokmål'),
('nd', 'North Ndebele'),
('ne', 'Nepali'),
('ng', 'Ndonga'),
('nn', 'Norwegian Nynorsk'),
('no', 'Norwegian'),
('ii', 'Nuosu'),
('nr', 'South Ndebele'),
('oc', 'Occitan'),
('oj', 'Ojibwe'),
('cu', 'Slavonic'),
('om', 'Oromo'),
('or', 'Oriya'),
('os', 'Ossetian'),
('pa', 'Punjabi'),
('pi', 'Pāli'),
('fa', 'Persian'),
('pl', 'Polish'),
('ps', 'Pashto'),
('pt', 'Portuguese'),
('qu', 'Quechua'),
('rm', 'Romansh'),
('rn', 'Kirundi'),
('ro', 'Romanian'),
('ru', 'Russian'),
('sa', 'Sanskrit'),
('sc', 'Sardinian'),
('sd', 'Sindhi'),
('se', 'Sami'),
('sm', 'Samoan'),
('sg', 'Sango'),
('sr', 'Serbian'),
('gd', 'Gaelic'),
('sn', 'Shona'),
('si', 'Sinhala, Sinhalese'),
('sk', 'Slovak'),
('sl', 'Slovene'),
('so', 'Somali'),
('st', 'Southern Sotho'),
('es', 'Spanish'),
('su', 'Sundanese'),
('sw', 'Swahili'),
('ss', 'Swati'),
('sv', 'Swedish'),
('ta', 'Tamil'),
('te', 'Telugu'),
('tg', 'Tajik'),
('th', 'Thai'),
('ti', 'Tigrinya'),
('bo', 'Tibetan'),
('tk', 'Turkmen'),
('tl', 'Tagalog'),
('tn', 'Tswana'),
('to', 'Tonga'),
('tr', 'Turkish'),
('ts', 'Tsonga'),
('tt', 'Tatar'),
('tw', 'Twi'),
('ty', 'Tahitian'),
('ug', 'Uyghur'),
('uk', 'Ukrainian'),
('ur', 'Urdu'),
('uz', 'Uzbek'),
('ve', 'Venda'),
('vi', 'Vietnamese'),
('vo', 'Volapük'),
('wa', 'Walloon'),
('cy', 'Welsh'),
('wo', 'Wolof'),
('fy', 'Western Frisian'),
('xh', 'Xhosa'),
('yi', 'Yiddish'),
('yo', 'Yoruba'),
('za', 'Zhuang, Chuang'),
('zu', 'Zulu'),
('zh-CN', 'Chinese'),  ('bshr', 'Croatian'), ('iw', 'Hebrew')]
LANGUAGE_CODES = dict(LANGUAGE_CODES)

LANGUAGE_NATIONS = {
 'ha': 'Nigeria',
 'gl': 'Spain',
 'mk': 'Macedonia',
 'pt': 'Portugal',
 'es': 'Spain',
 'en': 'United Kingdom',
 'th': 'Thailand',
 'sk': 'Slovakia',
 'pl': 'Poland',
 'id': 'Indonesia',
 'ar': 'UAE',
 'zh': 'China',
 'zh-CN': 'China',
 'lt': 'Lithuania',
 'nl': 'Netherlands',
 'ru': 'Russia',
 'ms': 'Malaysia',
 'he': 'Israel',
 'hi': 'India',
 'co': 'France',
 'iw': 'Israel',
 'sv': 'Sweden',
 'lv': 'Latvia',
 'uk': 'Ukraine',
 'ko': 'South Korea',
 'bg': 'Bulgaria',
 'sr': 'Serbia',
 'tr': 'Turkey',
 'cs': 'Czech Republic',
 'el': 'Greece',
 'ro': 'Romania',
 'sl': 'Slovenia',
 'hr': 'Croatia',
 'fr': 'France',
 'it': 'Italy',
 'de': 'Germany',
 'ja': 'Japan',
 'bs': 'Bosnia',
 'no': 'Norway',
 'hu': 'Hungary',
 'gu': 'India',
}

# LANGUAGE_NATIONS = {
#  'Bosnian': 'Bosnia',
#  'Arabic': 'UAE',
#  'Swedish': 'Sweden',
#  'Chinese': 'China',
#  'Polish': 'Poland',
#  'Norwegian': 'Norway',
#  'Hungarian': 'Hungary',
#  'Bulgarian': 'Bulgaria',
#  'Italian': 'Italy',
#  'Japanese': 'Japan',
#  'Slovene': 'Slovenia',
#  'English': 'United Kingdom',
#  'Latvian': 'Latvia',
#  'Turkish': 'Turkey',
#  'Hebrew (modern)': 'Israel',
#  'Slovak': 'Slovakia',
#  'Portuguese': 'Portuguese',
#  'Indonesian': 'Indonesia',
#  'Korean': 'South Korea',
#  'Dutch': 'Netherlands',
#  'German': 'Germany',
#  'Romanian, Moldavan': 'Romania',
#  'Croatian': 'Croatia',
#  'French': 'France',
#  'Greek, Modern': 'Greece',
#  'Czech': 'Czech Republic',
#  'Russian': 'Russia',
#  'Thai': 'Thailand',
#  'Serbian': 'Serbia',
#  'Ukrainian': 'Ukraine',
#  'Lithuanian': 'Lithuania',
#  'Spanish; Castilian': 'Spain',
# }

def save_response(obj, path):
	with open(path, 'w') as f:
		json.dump(obj, f)


def load_response(path):
	with open(path, 'r') as f:
		return json.load(f)



THIS_DIR = os.path.dirname(os.path.dirname(__file__))

class MissingLinkError(Exception):
	pass

class MissingTokenError(Exception):
	pass

class BadStatusError(Exception):
	def __init__(self, status):
		super().__init__(f'received status: {status}')





