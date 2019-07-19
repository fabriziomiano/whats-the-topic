import argparse
import logging
import os
import sys
import time

import facebook

from classes.Plotter import Plotter
from classes.TextPreprocessor import TextPreprocessor
from utils import (
    get_logger, load_config, get_data, get_comments, do_wordcount,
    create_nonexistent_dir, save_data
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
    try:
        access_token = conf["access_token"]
        page_id = conf["page_id"]
        n_posts = conf["n_posts"]
        plots_dir_path = conf["plots_dir_path"]
        data_dir_path = conf["data_dir_path"]
        n_top_words = conf["n_top_words"]
        wc_plot_filename = "{}_{}.png".format(conf["wc_plot_filename"], str(n_posts))
        barplot_filename = "{}_{}.png".format(conf["barplot_filename"], str(n_posts))
        wc_plot_filepath = os.path.join(plots_dir_path, wc_plot_filename)
        barplot_filepath = os.path.join(plots_dir_path, barplot_filename)
        data_filename = "{}_{}.csv".format(conf["csv_prefix"], str(n_posts))
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
    logger.info("Getting the last {} posts".format(n_posts))
    local_start = time.time()
    posts = graph.get_connections(profile["id"], "posts", limit=n_posts)
    logger.info("Got {} posts".format(n_posts))
    data = []
    for post in posts["data"]:
        logger.info("Fetching data for post ID: {}".format(post["id"]))
        post_data = get_data(access_token, post["id"])
        data.extend(post_data)
    comments = get_comments(data)
    if len(comments) == 0:
        logger.error("No comments could be retrieved from the selected post")
        sys.exit(0)
    elif len(comments) == 1:
        logger.warning(
            "Found only 1 comments. Not enough data "
            "to make much sense. Plots will be made regardless")
    else:
        logger.info("Got {} comments from {} post(s) in {} seconds".format(
            len(comments), n_posts, round((time.time() - local_start), 1)))
    local_start = time.time()
    preprocessed_comments = [TextPreprocessor(comm).preprocess() for comm in comments]
    logger.info("Preprocessed {} comments out of {} in {} seconds".format(
        len(preprocessed_comments), len(comments), round((time.time() - local_start), 2)))
    wordcount_data = do_wordcount(preprocessed_comments)
    logger.info("Saving data to CSV with name {} ".format(data_filename))
    create_nonexistent_dir(data_dir_path)
    data_filepath = os.path.join(data_dir_path, data_filename)
    save_data(wordcount_data, data_filepath)
    logger.info("Saved {} words and their counts in {} ".format(
        len(wordcount_data), data_filepath))
    logger.info("Making plots")
    unstemmed_comments = [TextPreprocessor(comm).base_preprocess() for comm in comments]
    long_string = " ".join(uc for uc in unstemmed_comments)
    p = Plotter(long_string, wordcount_data)
    create_nonexistent_dir(plots_dir_path)
    p.save_wordcloud_plot(wc_plot_filepath)
    logger.info("Wordcloud plot saved at {}".format(wc_plot_filepath))
    p.save_barplot(n_top_words, barplot_filepath)
    logger.info("Bar plot saved at {}".format(barplot_filepath))
    logger.info("\aDIN DONE! in {} seconds".format(
        round((time.time() - start), 1)))


if __name__ == "__main__":
    main()