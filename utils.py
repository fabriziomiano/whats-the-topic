import errno
import pandas as pd
import json
import requests
import logging
import os
import sys


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
            '%(asctime)s - %(name)s - [%(levelname)s] %(message)s')
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


def get_data(access_token, post_id):
    """
    Get the data for a given post_id, given
    a valid access token

    :param access_token: str
    :param post_id: str
    :return:
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


def do_wordcount(preprocessed_comments):
    """
    Perfom word count on a given list of words
    Return a sorted list of tuples(word, count)

    :param preprocessed_comments: list
    :return: list
    """
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
