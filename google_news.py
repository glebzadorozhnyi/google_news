from GoogleNews import GoogleNews
import requests
import re
from bs4 import BeautifulSoup
from collections import Counter
from tqdm import tqdm
import spacy
import time
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def get_links(theme='Russia', period='31d'):
    googlenews = GoogleNews(lang='en', region='US', period=period)
    googlenews.get_news(theme)
    return googlenews.get_links()


def get_keywords_from_links(links, keywords_out):
    counter = Counter()
    with tqdm(total=len(links), desc='Обход ссылок') as pbar:
        for link in links:
            pbar.update(1)
            link = 'https://' + link
            try:
                soup = BeautifulSoup(requests.get(link, timeout=10).text, 'lxml')
            except Exception:
                print('FAILED to open link: ', link)
                continue
            story_poll = soup.find_all('p')
            for paragraph in story_poll:
                b_soup = paragraph.find_all('b')
                paragraph = paragraph.text
                if b_soup:
                    for b in b_soup:
                        b = b.text
                        paragraph = paragraph.replace(b, '')
                paragraph = re.sub(r'[^\w\s-]', '', paragraph).strip().lower()
                if 'cookie' in paragraph or 'cookies' in paragraph:
                    continue
                doc = nlp(paragraph)
                pos_tag = ['PROPN', 'ADJ', 'NOUN']
                result = list()
                for token in doc:
                    if (token.text in nlp.Defaults.stop_words):
                        continue
                    if (token.pos_ in pos_tag):
                        result.append(token.lemma_)
                counter.update(result)
            with open(keywords_out, 'w', encoding='utf-8') as file:
                for i in counter.most_common():
                    file.writelines(i[0] + ' : ' + str(i[1]) + '\n')
            time.sleep(5)
    return


def filter_keywords(filepath, stopwords):
    with open(stopwords, 'r') as stp_wrds:
        x = stp_wrds.read().split()
        stopwords_set = set(x)
    with open(filepath, 'r') as f:
        x = f.read()
        x = x.splitlines()
        result = dict()
        for row in x:
            row = row.split()
            if row[0] in stopwords_set:
                continue
            result[row[0]] = float(row[2])
    with open(filepath, 'w') as file:
        for items, values in result.items():
            file.writelines(items + ' : ' + str(values) + '\n')


def read_keywords_file(filepath, N):
    with open(filepath, 'r') as f:
        x = f.read()
        x = x.splitlines()
        result = dict()
        for i in range(N):
            result[x[i].split()[0]] = float(x[i].split()[2])
        return result


nlp = spacy.load("en_core_web_lg")
links = get_links()
get_keywords_from_links(links, 'keywords.txt')
filter_keywords('keywords.txt', 'stopwords.txt')
keys = read_keywords_file('keywords.txt', 50)
wordcloud = WordCloud().generate_from_frequencies(keys, max_font_size=50)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
