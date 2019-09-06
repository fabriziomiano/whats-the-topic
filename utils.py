import csv
import errno
import json
import logging
import os
import sys
from collections import Counter

import matplotlib.pyplot as plt
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
        if comment["message"] != "":
            all_comments.append(comment["message"])
        else:
            continue
    return all_comments


def do_wordcount(comments):
    """
    Perfom word count on a given list of words
    Return a sorted list of tuples(word, count)

    :param comments: list
    :return: list
    """
    return Counter(" ".join(comments).split()).most_common()


def data_to_tsv(data, columns, outfile_path):
    """
    Write data to a CSV file.

    :param data: iterable with data
    :param columns: list of columns name (header)
    :param outfile_path: str output file path
    :return: None
    """
    with open(outfile_path, "w", encoding="utf-8") as csv_file:
        w = csv.writer(csv_file, delimiter="\t")
        w.writerow(columns)
        w.writerows(data)


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


def save_barplot(data, labels, n_max, path, type_="Words"):
    """
    Save bar plot of given data in format list(tuples)

    :param data: list of tuples
    :param labels: list: x and y axis labels in this order
    :param n_max: int: max number of elements
    :param path: str: output file path
    :param type_: str, optional
    :return: None
    """
    x, y = zip(*data)
    sns.set(style="whitegrid")
    plt.figure(figsize=(n_max, 10))
    ax = sns.barplot(
        list(y)[:n_max],
        list(x)[:n_max],
        palette="Blues_d")
    ax.set_title("Top {} {}".format(n_max, type_), fontsize=18)
    plt.xticks(fontsize=18)
    plt.xticks(fontsize=18)
    plt.xlabel(labels[1], fontsize=18)
    plt.ylabel(labels[0], fontsize=18, labelpad=20, rotation=90)
    plt.savefig(path)


def check_n_posts():
    """
    Check that the number of posts to run on
    is given correctly

    :return: str
    """
    n_posts = input("Provide number of latest posts to analyze: ")
    is_sure = "n"
    while n_posts in ["", "0", "-1"] and is_sure == "n":
        if n_posts in ["", "0"]:
            message = (
                "An empy/zero answer defaults to 25 posts. Happy with this? y/n: "
            )
        else:
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
            if n_posts == "-1":
                utils_log.warning("Alright! Let's get as much as we're allowed")
            elif n_posts in ["", "0"]:
                utils_log.info("Default to 25 posts")
            break
        elif is_sure == "n":
            n_posts = input("Good, then provide number of latest posts to analyze: ")
        else:
            is_sure = input(message)
            if is_sure == "y":
                break
            else:
                is_sure = "n"
    return n_posts
