# No Nonsense News
*Scraping and Presenting World News Headlines*

## See the final product: [No Nonsense News Headlines](https://www.notion.so/felixleeb/a3f6eb244397478a9c9ac1d8c7b1babb?v=8948c08d08d44b39be52ec513618016a)

## For more information about the project visit the [project page](https://www.notion.so/felixleeb/No-Nonsense-News-0ecebf66967147dda6a96b549c7a73d1)

Here are a few scripts to scrape news headlines from all over the world using News API, format and translate them using Google Translate, and display the articles on a Notion page - all from the comfort of python.

# Usage

Aside from the requirements in the [`requirements.txt`](https://github.com/felixludos/nnn/blob/master/requirements.txt) file, you must also have a News API key (which you can get by signing up for free at [News API](https://newsapi.org/)). Additionally, if you wish to present the scraped articles with Notion, then you must have a Notion account and have your corresponding token (which can be found like [this](https://www.redgregory.com/notion/2020/6/15/9zuzav95gwzwewdu1dspweqbv481s5)).

This project heavily relies on [omni-fig](https://github.com/felixludos/omni-fig) for organizing the scripts and config files.

Assuming you have all the dependencies installed. You can run a full update (to scrape, translate, and present) all articles with the command (which uses the `usual` config found in `config/usual.yaml` - where the link must be replaced with your own Notion page):

```bash
python main.py usual
```

Or equivalently,

```bash
fig nnn usual
```

Each of the three steps can be done separately using:

```bash
fig scrape-news usual
fig sanitize-news usual
fig present-notion usual
```

# Performance

Scraping all top headline articles for all countries and all categories, requires about 350 requests to the News API, and takes less than ten minutes and collects around 1700-2000 articles. Thanks to parallelism, formatting and translating the articles is significantly faster and takes around two minutes. Finally, presenting the articles on Notion is somewhat problematic because with parallelism it can be done in less than five minutes, however all the necessary requests sent to the Notion server overload it. As a result, the number of workers must be decreased. In practice, a full update takes around 15-20 minutes, however the last step may require a few tries to coax the Notion servers into accepting all requests and to display all the articles.

Nevertheless, I reckon this performance is sufficient for a common use case to be: you run the script while making breakfast, and then by the time you are back at your computer, over a thousand headlines from all over the world are there to greet you. (Perhaps more important use case focuses more on the scraping and formatting steps to provide a dataset of headlines from all over the world for various NLP settings and analysis).

