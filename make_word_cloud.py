import codecs
import random
import re

import arabic_reshaper
import numpy as np
import tweepy
from PIL import Image
from bidi.algorithm import get_display
from hazm import *
from wordcloud_fa import WordCloudFa

word_cloud_address = 'tweet.jpg'

BACKGROUND_COLOR = "white"
COLOR_MAP = "autumn"
cmaps = ['Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
         'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
         'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
         'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
         'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
         'hot', 'afmhot', 'gist_heat', 'copper']

FONT_PATH = "XTitre.TTF"
MASK_PATH = "mask.png"

STOPWORDS_PATH = "stopwords.dat"


def save_word_cloud(user_name: str, api):
    raw_tweets = []
    for tweet in tweepy.Cursor(api.user_timeline, id=user_name).items():
        raw_tweets.append(tweet.text)

    # Normalize words
    tokenizer = WordTokenizer()
    lemmatizer = Lemmatizer()
    normalizer = Normalizer()
    stopwords = set(list(map(lambda w: w.strip(), codecs.open(STOPWORDS_PATH, encoding='utf8'))))
    words = []
    for raw_tweet in raw_tweets:
        raw_tweet = re.sub(r"[,.;:?!،()]+", " ", raw_tweet)
        raw_tweet = re.sub('[^\u0600-\u06FF]+', " ", raw_tweet)
        raw_tweet = re.sub(r'[\u200c\s]*\s[\s\u200c]*', " ", raw_tweet)
        raw_tweet = re.sub(r'[\u200c]+', " ", raw_tweet)
        raw_tweet = re.sub(r'[\n]+', " ", raw_tweet)
        raw_tweet = re.sub(r'[\t]+', " ", raw_tweet)
        raw_tweet = normalizer.normalize(raw_tweet)
        raw_tweet = normalizer.character_refinement(raw_tweet)
        tweet_words = tokenizer.tokenize(raw_tweet)
        tweet_words = [lemmatizer.lemmatize(tweet_word).split('#', 1)[0] for tweet_word in tweet_words]
        tweet_words = list(filter(lambda x: x not in stopwords, tweet_words))
        words.extend(tweet_words)

    if len(words) == 0:
        return

    # Build word_cloud
    mask = np.array(Image.open(MASK_PATH))
    clean_string = ' '.join([str(elem) for elem in words])
    clean_string = arabic_reshaper.reshape(clean_string)
    clean_string = get_display(clean_string)
    word_cloud = WordCloudFa(persian_normalize=False, mask=mask, colormap=random.sample(cmaps, 1)[0],
                             background_color=BACKGROUND_COLOR, include_numbers=False, font_path=FONT_PATH,
                             no_reshape=True, max_words=1000, min_font_size=2)
    wc = word_cloud.generate(clean_string)
    image = wc.to_image()
    image.save(word_cloud_address)

