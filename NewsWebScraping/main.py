import argparse
import logging
import datetime
import csv
import re

from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt="%d/%m/%Y %I:%M:%S")

from common import config
import news_page_objects as news 

logger = logging.getLogger(__name__)
is_well_formed_link = re.compile(r'^https?://.+/.+$') # https: //example.com/hello
is_root_path = re.compile(r'^/.+$') # /some-text

def _news_scrapper(news_site_uid):
    host = config()['news_sites'][news_site_uid]['url']
    logging.info(f'Beginning scraper for: {host}')
    homepage = news.HomePage(news_site_uid, host)

    articles = []
    for link in homepage.article_links:
        article = _fetch_article(news_site_uid, host, link)
        if article:
            logger.info('Article fetched correctly!')
            articles.append(article)
    
    logger.info(f'{len(articles)} articles were obtained from {news_site_uid}')
    _save_article(news_site_uid, articles)

def _save_article(news_site_uid, articles):
    logger.info(f'Creating a csv file for: {news_site_uid}')
    now = datetime.datetime.now().strftime('%d_%m_%Y')
    out_file_name = f'{news_site_uid}_{now}_articles.csv'
    csv_headers = list(filter(lambda property: not property.startswith('_'), dir(articles[0])))
    with open(out_file_name, mode = 'w+',encoding= "utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)

        for article in articles:
            row = [str(getattr(article, prop)) for prop in csv_headers]
            writer.writerow(row)

def _fetch_article(news_site_uid, host, link):
    logger.info(f'Start fetching article at {link}')

    article = None
    try:
        article = news.ArticlePage(news_site_uid, _build_link(host,link))
    except (HTTPError, MaxRetryError) as e:
        logger.warning(f'Error while fechting the article', exc_info = False) 

    if article and not article.body:
        logger.warning('Invalid article, There is no body')
        return None
    
    return article

def _build_link(host, link):
    if is_well_formed_link.match(link):
        return link
    elif is_root_path.match(link):
        return f'{host}{link}'
    else:
        return '{host}/{uri}'.format(host = host, uri = link)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    news_site_choices = list(config()['news_sites'].keys())
    parser.add_argument('news_site',
                        help='The news site that you want to scrape',
                        choices=news_site_choices)

    args = parser.parse_args()
    _news_scrapper(args.news_site)