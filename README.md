
# Babel Briefings

*Breaking free of the Language Barrier*

This repo contains the code associated with the Babel Briefings dataset. To download the dataset, check out the [Huggingface](https://huggingface.co/datasets/felixludos/babel-briefings) or [Kaggle](https://www.kaggle.com/datasets/felixludos/babel-briefings) pages, and the (short) paper published in the NAACL 2024 proceedings is available on [arXiv](https://arxiv.org/abs/2403.19352).

To browse some of the samples of the dataset, visit the [website](https://felixludos.github.io/babel-briefings/). Alternatively, you can see a [demo](http://nnn.felixludos.com) on Notion with a single day's worth of samples.

The Babel Briefings dataset (v1) contains 4,719,199 news headlines across 30 different languages collected between 8 August 2020 and 29 November 2021. The headlines were collected using the [New API](https://newsapi.org/) by collecting the top headlines (usually about 30-70 articles) separately for each combination of the 54 locations x 7 categories almost every day. Note, that the same article may occur more than once across different locations, categories, or dates (which is recorded in the `instances` property), so in total 7,419,089 instances were collected.



## Data Collection

Here are a few scripts to scrape news headlines from all over the world using [News API](https://newsapi.org/), translate them with the [Helsinki-NLP](https://blogs.helsinki.fi/language-technology/) [Marian](https://marian-nmt.github.io/) machine translation models (using [HuggingFace](https://huggingface.co/)), and display the articles on a Notion page - all from the comfort of Python. There are also some scripts to enable translating the headlines using Google Translate for higher quality translations.

### Usage

Aside from the requirements in the [`requirements.txt`](https://github.com/felixludos/nnn/blob/master/requirements.txt) file, you must also have a News API key (which you can get by signing up for free at [News API](https://newsapi.org/)). Additionally, if you wish to present the scraped articles with Notion, then you must have a Notion account and have your corresponding token (which can be found like [this](https://www.redgregory.com/notion/2020/6/15/9zuzav95gwzwewdu1dspweqbv481s5)).

This project heavily relies on [omni-fig](https://github.com/felixludos/omni-fig) for organizing the scripts and config files.

The recommended way to update (scrape, translate, and present) all articles, is to first replace the link in the config file `config/usual.yaml` with a link to one of your notion pages where the table of articles should be created (it is recommended for the page to be empty).

After you only need to run:

```bash
python main.py usual
```

Or equivalently,

```bash
fig nnn usual
```

Due to the high volume of requests sent to the Notion server, you may receive an error 504 while uploading the articles to the Notion page. If this occurs wait for 30 seconds to a minute, and then resume the upload with the following command:

```bash
python main.py usual --resume
```

Each of the three steps can be done separately using:

```bash
fig scrape-news usual
fig sanitize-news usual
fig present-notion usual
```

(see [omni-fig](https://github.com/felixludos/omni-fig) and/or code for more information about the available arguments)

### Performance

Scraping all top headline articles for all countries and all categories, requires about 350 requests to the News API, and takes less than ten minutes and collects around 1700-2000 articles. Thanks to parallelism, formatting and translating the articles is significantly faster and takes around two minutes. Finally, presenting the articles on Notion is somewhat problematic because with parallelism it can be done in less than five minutes, however all the necessary requests sent to the Notion server overload it. As a result, the number of workers must be decreased. In practice, a full update takes around 15-20 minutes, however the last step may require a few tries to coax the Notion servers into accepting all requests and to display.

Nevertheless, I reckon this performance is sufficient for a common use case to be: you run the script while making breakfast, and then by the time you are back at your computer, over a thousand headlines from all over the world are there to greet you. (Perhaps more important use case focuses more on the scraping and formatting steps to provide a dataset of headlines from all over the world for various NLP settings and analysis).

