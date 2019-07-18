from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from wordcloud import WordCloud
from matplotlib import pyplot as plt
import facebook
import errno
import pandas as pd
import string
import json
import requests
import logging
import seaborn as sns
import os
import sys
import unicodedata


def get_logger(name):
    """ 
    Add a StreamHandler to a logger if still not added and
    return the logger
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.propagate = 1  # propagate to parent
        console = logging.StreamHandler()
        logger.addHandler(console)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)s] %(message)s')
        console.setFormatter(formatter)
    return logger


utils_log = get_logger(__name__)
utils_log.setLevel(logging.INFO)


def load_config(path):
    try:
        with open(path, "r") as conf_file:
            conf = json.load(conf_file)
            return conf
    except IOError:
        utils_log.error("Please check that conf file exists")
        sys.exit(0)


STEMMER = SnowballStemmer("italian")
with open("stoplist.json") as stop_in:
    STOPLIST = json.load(stop_in)
# STOPLIST = stopwords.words("italian") + stopwords.words("english")
# STOPLIST.extend(ADDITIONAL_STOPLIST)


def get_data(access_token, post_id):
    base_url = "https://graph.facebook.com/"
    comments_endpoint = (
        "/comments?fields=message,comments{message,comments}&summary=1&access_token="
    )
    comments_url = base_url + \
                post_id + \
                comments_endpoint + \
                access_token
    comments_data = requests.get(comments_url).json()
    data = []
    while True:
        try:
            data.extend(comments_data["data"])
            comments_data = requests.get(comments_data["paging"]["next"]).json()
        except KeyError:
            break
    return data


def get_comments(data):
    all_comments = []
    for comment in data:
        if "comments" in comment.keys():
            replies = comment["comments"]["data"]
            all_comments.extend(
                [reply["message"] for reply in replies])
        all_comments.append(comment["message"])
    return all_comments


def remove_non_ascii(text):
    """Remove non-ASCII characters from text"""
    tokens = text.split()
    onlyascii_tokens = []
    for token in tokens:
        token = unicodedata.normalize('NFKD', token).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        onlyascii_tokens.append(token)
    return " ".join(word for word in onlyascii_tokens)


def remove_punctuation(text):
    return text.translate(
        str.maketrans('', '', string.punctuation)
    )


def remove_stopwords(tokens, stoplist):
    text = " ".join(
        token for token in tokens
        if token not in stoplist
    )
    return text


def stem_text(tokens):
    text = " ".join(STEMMER.stem(t) for t in tokens)
    return text


def base_preproc(text, stoplist=STOPLIST):
    """
    """
    text = remove_non_ascii(text)
    text = text.lower()
    tokens = text.split()
    text = remove_stopwords(tokens, stoplist)
    text = remove_punctuation(text)
    return text


def preprocess(text, stoplist=STOPLIST):
    """
    """
    text = remove_non_ascii(text)
    text = text.lower()
    tokens = text.split()
    text = remove_stopwords(tokens, stoplist)
    text = remove_punctuation(text)
    tokens = text.split()
    text = stem_text(tokens)
    return text


def get_wordcount(preprocessed_comments):
    wordcount = {}
    for comment in preprocessed_comments:
        for word in comment.split():
            if word in wordcount:
                wordcount[word] += 1
            else:
                wordcount[word] = 1
    counts = [value for value in wordcount.values()]
    words = [key for key in wordcount.keys()]
    points = sorted(zip(words, counts),
                    key=lambda x: x[1], reverse=True)
    return points


def save_data(wordcount_data, data_filename):
    df = pd.DataFrame(wordcount_data, columns=["word", "count"])
    df.to_csv(data_filename, index=False)


def save_wordcloud_plot(long_string, path):
    wordcloud = WordCloud(
        background_color="black",
        contour_width=3,
        contour_color='steelblue'
    )
    wordcloud.generate(long_string)
    wordcloud.to_file(path)


def plot_wordcloud(long_string):
    wordcloud = WordCloud(
        background_color="black",
        contour_width=3,
        contour_color='steelblue'
    )
    wordcloud.generate(long_string)
    wordcloud.to_image()
    return wordcloud.to_image()


def save_barplot(wordcount_data, n_top_words, path): 
    df = pd.DataFrame(wordcount_data, columns=["word", "count"])     
    plt.figure(figsize=(n_top_words, 10))
    barplot = sns.barplot("word", "count", data=df[:n_top_words], palette="Blues_d")
    barplot.set_title("Top {} Words".format(n_top_words))
    plt.xticks(rotation=30)
    plt.xlabel("Word")
    plt.ylabel("Count", labelpad=60, rotation=0)
    plt.savefig(path)    


def create_nonexistent_dir(path, exc_raise=False):
    """
    Create directory from given path
    Return True if created, False if it exists
    """
    try:
        os.makedirs(path)
        utils_log.info("Created directory with path: {}".format(path))
        return path
    except OSError as e:
        if e.errno != errno.EEXIST:
            utils_log.exception(
                "Could not create directory with path: {}".format(path))
            if exc_raise:
                raise
        return None
