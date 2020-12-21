import argparse
from urllib.parse import urlparse
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt="%d/%m/%Y %I:%M:%S")


logger = logging.getLogger(__name__)



def main(filename):
    logger.info('Starting cleaning process')

    df = _read_data(filename)
    newspaper_uid = _extract_newspaper_uid(filename)
    df = _add_newspaper_uid_column(df, newspaper_uid)
    df = _extract_host(df)

    return df

def _read_data(filename):
    logger.info(f'Reading file: {filename}')

    return pd.read_csv(filename, encoding = 'utf-8')

def _extract_newspaper_uid(filename):
    logger.info('Extracting newspaper uid')
    newspaper_uid = filename.split('_')[0]

    logger.info(f'Newspaper uid detected: {newspaper_uid}')
    return newspaper_uid

def _add_newspaper_uid_column(df, newspaper_uid):
    logger.info(f'Filling newspaper_uid column with: {newspaper_uid}')
    df['newspaper_uid'] = newspaper_uid

    return df

def _extract_host(df):
    logger.info('Extracting host from URL')
    df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)
    
    return df

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help='The path to the dirty data')
    args = parser.parse_args()
    df = main(args.filename)
    print(df)