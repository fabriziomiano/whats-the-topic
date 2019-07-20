import argparse
import logging
import os
import sys
import time

import facebook
import numpy as np
import pandas as pd

from utils import (
    get_logger, load_config, get_post_data, get_comments, check_n_posts
)


def main():
    parser = argparse.ArgumentParser(
        description="""Count comments in a given number of posts""")
    parser.add_argument(
        '-c', '--conf', type=str, metavar='', required=True,
        help='Specify the path of the configuration file')
    args = parser.parse_args()
    config_path = args.conf
    start = time.time()
    logger = get_logger(__name__)
    logger.setLevel(logging.DEBUG)
    conf = load_config(config_path)
    n_posts = input("Provide number of latest posts to analyze: ")
    check_n_posts(n_posts)
    try:
        access_token = conf["access_token"]
        page_id = conf["page_id"]
    except KeyError:
        logger.error(
            "Invalid configuration file. Please check template and retry")
        sys.exit(0)
    try:
        graph = facebook.GraphAPI(access_token)
        logger.info("Graph API connected")
        profile = graph.get_object(page_id)
    except facebook.GraphAPIError as e:
        logger.error("Could not log in. {}".format(e))
        sys.exit(0)
    local_start = time.time()
    posts = graph.get_connections(profile["id"], "posts", limit=n_posts)
    comments = []
    for post in posts["data"]:
        url_post = "https://www.facebook.com/posts/{}".format(post["id"])
        logger.info("Getting data for post {}".format(url_post))
        post_data = get_post_data(access_token, post["id"])
        post_comments = get_comments(post_data)
        if len(post_comments) == 0:
            logger.warning(
                """Apparently, there are no comments at the selected post
                Check the actual post on its Facebook page 
                https://www.facebook.com/posts/{}""".format(post["id"])
            )
        comments.extend(post_comments)
    if len(comments) == 0:
        logger.error("Could not get any comments. Exiting gracefully")
        sys.exit(0)
    elif len(comments) < 100:
        logger.warning(
            "Found {} comment(s). Not enough data "
            "to make much sense. Plots will be made regardless".format(
                len(comments)
            )
        )
    else:
        logger.info("Got {} comments from {} post(s) in {} seconds".format(
            len(comments), len(posts["data"]), round((time.time() - local_start), 1)))
    sentiments = np.zeros(len(comments))
    data = {
        "comment": comments,
        "sentiment": sentiments
    }
    df = pd.DataFrame(data, columns=["comment", "sentiment"])
    data_filename = "{}_comments.csv".format(len(comments))
    data_filepath = os.path.join(conf["data_dir_name"], data_filename)
    df.to_csv(data_filepath, index=False)
    logger.info("Saved {} comments in {} ".format(
        len(comments), data_filepath))
    logger.info("\a\a\aDIN DONE! in {} seconds".format(
        round((time.time() - start), 1)))


if __name__ == "__main__":
    main()
