# Babel Briefings News Headlines Dataset README

> Break Free from the Language Barrier

Version: 1 - Date: 30 Oct 2023

Collected and Prepared by Felix Leeb (Max Planck Institute for Intelligent Systems, Tübingen, Germany)

License: Babel Briefings Headlines Dataset © 2023 by Felix Leeb is licensed under [CC BY-NC-SA 4.0](http://creativecommons.org/licenses/by-nc-sa/4.0/) 

This dataset contains 4,719,199 news headlines across 30 different languages collected between 8 August 2020 and 29 November 2021. The headlines were collected using the [News API](https://newsapi.org/) by collecting the top headlines (usually about 30-70 articles) separately for each combination of the 54 locations x 7 categories almost every day. Note, that the same article may occur more than once across different locations, categories, or dates (which is recorded in the `instances` property), so in total 7,419,089 instances were collected.

For non-English articles, the article data is translated to English using Google Translate (see `en-title`, `en-description`, and `en-content` properties).

The dataset is provided in the form of 54 JSON files, one for each location containing the all the unique headlines that appeared for the first time in the corresponding location. Each headline is represented as a JSON object with the following properties:

- `ID`: (integer) a unique ID for each article 
- `title`: (string) the headline text in the original language
- `description`: (string) the article description in the original language
- `content`: (string) the first few words of the article in the original language
- `author`: (string) the author of the article
- `source-id`: (string) the news aggregator (e.g. Google-News)
- `source-name`: (string) usually the domain of the source where the article was published
- `url`: (string) the URL of the article
- `urlToImage`: (string) the URL to an image associated with the article
- `publishedAt`: (date) the article was published
- `instances`: (list) specific time and place where this article was posted. Each element contains:
  - `collectedAt`: (date) date and time when the article was collected
  - `category`: (string) of the article from 7 possible values (see below for full list)
  - `location`: (string) of the article from 54 possible values (see below for full list)
- `language`: (string) ISO-639 2-letter code for the language (inferred from location)
- `en-title`: (string) the headline text translated to English (if necessary)
- `en-description`: (string) the article description text translated to English (if necessary)
- `en-content`: (string) the first few words of the article translated to English (if necessary)


## Notes

- Unfortunately, due to an issue with News API, the `content` of articles originally in a non-latin based script (e.g. Chinese, Arabic, Japanese, Greek, Russian, etc.) are usually not available. However, for the most part all other articles should have a meaningful `content` property, and the `title` and `descriptions` appear unaffected.
- All properties except `language`, `en-title`, `en-description`, and `en-content` are taken directly from the News API responses. The language is inferred from the location, and the English translations are collected using Google Translate.


## Statistics

Here are a few basic summary statistics about the dataset.

### Articles by Language

| Code   | Language   |   Articles | Locations                                          |
|--------|------------|------------|----------------------------------------------------|
| en     | English    |    1128233 | au, ca, gb, ie, in, my, ng, nz, ph, sa, sg, us, za |
| es     | Spanish    |     455952 | ar, co, cu, mx, ve                                 |
| fr     | French     |     288328 | be, fr, ma                                         |
| zh     | Chinese    |     270887 | cn, hk, tw                                         |
| de     | German     |     259718 | at, ch, de                                         |
| pt     | Portuguese |     243829 | br, pt                                             |
| ar     | Arabic     |     178854 | ae, eg                                             |
| id     | Indonesian |     131252 | id                                                 |
| it     | Italian    |     129005 | it                                                 |
| tr     | Turkish    |     122724 | tr                                                 |
| el     | Greek      |     119940 | gr                                                 |
| ja     | Japanese   |     118475 | jp                                                 |
| pl     | Polish     |     116904 | pl                                                 |
| ru     | Russian    |     113395 | ru                                                 |
| nl     | Dutch      |     104031 | nl                                                 |
| th     | Thai       |      90708 | th                                                 |
| sv     | Swedish    |      86838 | se                                                 |
| ko     | Korean     |      83090 | kr                                                 |
| sr     | Serbian    |      80040 | rs                                                 |
| hu     | Hungarian  |      73509 | hu                                                 |
| cs     | Czech      |      70647 | cz                                                 |
| he     | Hebrew     |      67794 | il                                                 |
| bg     | Bulgarian  |      67223 | bg                                                 |
| uk     | Ukrainian  |      65610 | ua                                                 |
| ro     | Romanian   |      54601 | ro                                                 |
| no     | Norwegian  |      46804 | no                                                 |
| sk     | Slovak     |      43057 | sk                                                 |
| lv     | Latvian    |      40006 | lv                                                 |
| lt     | Lithuanian |      34719 | lt                                                 |
| sl     | Slovenian  |      33026 | si                                                 |

### Instances by category

| Category      |   Instances |
|---------------|-------------|
| sports        |     1132542 |
| entertainment |      982479 |
| business      |      840748 |
| technology    |      802933 |
| general       |      704692 |
| health        |      424188 |
| science       |      388281 |

### Instances by location

| Code   | Location             |   Instances |
|--------|----------------------|-------------|
| ae     | United Arab Emirates |      214256 |
| ar     | Argentina            |      159139 |
| ph     | Philippines          |      155365 |
| ng     | Nigeria              |      155112 |
| in     | India                |      145536 |
| us     | United States        |      144800 |
| ca     | Canada               |      143928 |
| sa     | Saudi Arabia         |      143382 |
| cu     | Cuba                 |      138675 |
| au     | Australia            |      138408 |
| br     | Brazil               |      136101 |
| ma     | Morocco              |      131974 |
| id     | Indonesia            |      131252 |
| eg     | Egypt                |      129382 |
| it     | Italy                |      129005 |
| gb     | United Kingdom       |      127391 |
| ie     | Ireland              |      126640 |
| mx     | Mexico               |      124499 |
| tr     | Turkey               |      122724 |
| gr     | Greece               |      119940 |
| de     | Germany              |      119917 |
| jp     | Japan                |      118475 |
| za     | South Africa         |      117351 |
| fr     | France               |      117210 |
| pl     | Poland               |      116904 |
| pt     | Portugal             |      115976 |
| co     | Colombia             |      115325 |
| my     | Malaysia             |      115223 |
| ru     | Russian Federation   |      113395 |
| at     | Austria              |      111867 |
| nz     | New Zealand          |      108809 |
| tw     | Taiwan               |      108652 |
| nl     | Netherlands          |      104031 |
| sg     | Singapore            |      101251 |
| be     | Belgium              |       99460 |
| cn     | China                |       91561 |
| ve     | Venezuela            |       91045 |
| th     | Thailand             |       90708 |
| se     | Sweden               |       86838 |
| kr     | Korea                |       83090 |
| hk     | Hong Kong            |       83051 |
| rs     | Serbia               |       80040 |
| hu     | Hungary              |       73509 |
| cz     | Czechia              |       70647 |
| ch     | Switzerland          |       68846 |
| il     | Israel               |       67794 |
| bg     | Bulgaria             |       67223 |
| ua     | Ukraine              |       65610 |
| ro     | Romania              |       54601 |
| no     | Norway               |       46804 |
| sk     | Slovakia             |       43057 |
| lv     | Latvia               |       40006 |
| lt     | Lithuania            |       34719 |
| si     | Slovenia             |       33026 |



