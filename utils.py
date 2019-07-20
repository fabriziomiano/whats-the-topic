import errno
import json
import logging
import os
import sys
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns

from classes.TextPreprocessor import TextPreprocessor


def get_logger(name):
    """
    Add a StreamHandler to a logger if still not added and
    return the logger

    :param name:
    :return: logging.getLogger object
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.propagate = 1  # propagate to parent
        console = logging.StreamHandler()
        logger.addHandler(console)
        formatter = logging.Formatter(
            '[%(asctime)s] - %(name)s - [%(levelname)s] %(message)s')
        console.setFormatter(formatter)
    return logger


utils_log = get_logger(__name__)
utils_log.setLevel(logging.INFO)


def load_config(path):
    """
    Return a dict for a given json path

    :param path:
    :return: dict
    """
    try:
        with open(path, "r") as conf_file:
            conf = json.load(conf_file)
            return conf
    except IOError:
        utils_log.error("Please check that conf file exists")
        sys.exit(0)


def get_post_data(access_token, post_id):
    """
    Get the data for a given post_id, given
    a valid access token

    :param access_token: str
    :param post_id: str
    :return data: post data dict
    """
    base_url = "https://graph.facebook.com/"
    comments_endpoint = (
        "/comments?fields=message,comments{message,comments}&summary=1&access_token="
    )
    comments_url = (
            base_url + post_id +
            comments_endpoint +
            access_token
    )
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
    """
    Get all the comments for a given facebook post
    data dict
    :param data: dict
    :return: list; list of comments
    """
    all_comments = []
    for comment in data:
        if "comments" in comment.keys():
            replies = comment["comments"]["data"]
            all_comments.extend(
                [reply["message"] for reply in replies])
        all_comments.append(comment["message"])
    return all_comments


def do_wordcount(comments):
    """
    Perfom word count on a given list of words
    Return a sorted list of tuples(word, count)

    :param comments: list
    :return: list
    """
    return Counter(" ".join(comments).split()).most_common()


def save_data(wordcount_data, data_filename):
    """
    Save a CSV file of a given word count data

    :param wordcount_data: list of tuples(word, count)
    :param data_filename: str
    :return: None
    """
    df = pd.DataFrame(wordcount_data, columns=["word", "count"])
    df.to_csv(data_filename, index=False)


def create_nonexistent_dir(path, exc_raise=False):
    """
    Create a directory from a given path if it does not exist.
    If exc_raise is False, no exception is raised

    """
    try:
        os.makedirs(path)
        utils_log.info("Created directory with path: {}".format(path))
    except OSError as e:
        if e.errno != errno.EEXIST:
            utils_log.exception(
                "Could not create directory with path: {}".format(path))
            if exc_raise:
                raise


def get_entities(nlp, comment):
    """
    Return list of entities in a given text
    :param comment:
    :param nlp:
    :return: list

    example on how to add exception:

    nlp.tokenizer.add_special_case(
        'india', [
            {
                ORTH: 'india',
                LEMMA: 'India',
                TAG: 'NNP',
                ENT_TYPE: 'GPE',
                ENT_IOB: 3
            }
        ]
    )
    """
    tp = TextPreprocessor(comment)
    comment = tp.remove_non_ascii()
    if comment is not None and len(comment) > 3:
        doc = nlp(comment)
        entities = [
            ent.text for ent in doc.ents
            if len(ent.text) > 3
        ]
    else:
        entities = []
    return entities


def count_entities(entities):
    """
    Return entity cound
    :param entities:
    :return:
    """
    return Counter(entities).most_common()


def save_barplot(data, n_max, path, type_="Words"):
    """
    Save bar plot of given word count data

    :param data: list of tuples
    :param n_max: int n_max of object in dataset
    :param path: str file path
    :param type_: optional str: type to plot
    :return: None
    """
    df = pd.DataFrame(data, columns=["word", "count"])
    plt.figure(figsize=(n_max, 10))
    barplot = sns.barplot("word", "count", data=df[:n_max], palette="Blues_d")
    barplot.set_title("Top {} {}".format(n_max, type_))
    plt.xticks(rotation=30)
    plt.xlabel("Word")
    plt.ylabel("Count", labelpad=60, rotation=0)
    plt.savefig(path)


def check_n_posts(n_posts):
    is_sure = "n"
    while n_posts == "" and is_sure == "n":
        message = (
            """
            No limit on number of posts was chosen.
            This means that the tool will perform requests
            at the Facebook servers until the maximum number of requests
            is reached. At that point you'll have to wait at least 50 minutes
            to run it again. Are you still thinking of doing this? y/n: """
        )
        is_sure = input(message)
        if is_sure == "y":
            utils_log.warning("Alright! Let's get as much as we've got left")
            break
        elif is_sure == "n":
            n_posts = input("Good, then provide number of latest posts to analyze: ")
        else:
            is_sure = input(message)
