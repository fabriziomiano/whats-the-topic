import argparse
import logging
import os
import sys
import time

import facebook

from classes.TextPreprocessor import TextPreprocessor
from classes.WordCloudPlotter import Plotter
from utils import (
    get_logger, load_config, get_post_data, get_comments, do_wordcount,
    create_nonexistent_dir, save_data, save_barplot, check_n_posts
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
        n_top_words = conf["n_top_words"]
        data_dir_path = os.path.join(page_id, conf["data_dir_name"])
        data_filename = "{}_{}.csv".format(conf["data_wc_prefix"], str(n_posts))
        plots_dir_path = os.path.join(page_id, conf["plots_dir_name"])
        wc_plot_filename = "{}_{}posts.png".format(conf["wc_plot_filename"], str(n_posts))
        wc_plot_filepath = os.path.join(plots_dir_path, wc_plot_filename)
        barplot_filename = "{}_{}posts.png".format(conf["barplot_filename"], str(n_posts))
        barplot_filepath = os.path.join(plots_dir_path, barplot_filename)
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
    local_start = time.time()
    preprocessed_comments = [TextPreprocessor(comm).preprocess() for comm in comments]
    logger.info("Preprocessed {} comments out of {} in {} seconds".format(
        len(preprocessed_comments), len(comments), round((time.time() - local_start), 2)))
    wordcount_data = do_wordcount(preprocessed_comments)
    create_nonexistent_dir(data_dir_path)
    data_filepath = os.path.join(data_dir_path, data_filename)
    save_data(wordcount_data, data_filepath)
    logger.info("Saved {} words and their counts in {} ".format(
        len(wordcount_data), data_filepath))
    create_nonexistent_dir(plots_dir_path)
    save_barplot(wordcount_data, n_top_words, barplot_filepath)
    logger.info("Bar plot saved at {}".format(barplot_filepath))
    unstemmed_comments = [TextPreprocessor(comm).base_preprocess() for comm in comments]
    long_string = " ".join(uc for uc in unstemmed_comments)
    p = Plotter(long_string)
    p.save_wordcloud_plot(wc_plot_filepath)
    logger.info("Wordcloud plot saved at {}".format(wc_plot_filepath))
    logger.info("\a\a\aDIN DONE! in {} seconds".format(
        round((time.time() - start), 1)))


if __name__ == "__main__":
    main()
