import facebook
import json
import requests
import pandas as pd
import logging
import sys
import os
import argparse
import sys
import time
from utils import (
    get_data, get_comments, preprocess, get_logger,
    get_wordcount, save_data, save_wordcloud_plot,
    save_barplot, create_nonexistent_dir, base_preproc,
    load_config
)


def main(config_path, post_id):
    start = time.time()
    logger = get_logger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.info("Reading configuration file")
    conf = load_config(config_path)
    try:
        access_token = conf["access_token"]
        page_id = conf["page_id"]
        plots_dir_path = conf["plots_dir_path"]
        data_dir_path = conf["data_dir_path"]
        n_top_words = conf["n_top_words"]
        wc_plot_filename = "{}_{}{}".format(
            conf["wc_plot_filename"],
            page_id + "_" + post_id,
            ".png"
        )
        barplot_filename = "{}_{}{}".format(
            conf["barplot_filename"],
            page_id + "_" + post_id,
            ".png"
        )
        data_filename = "{}_{}{}".format(
            conf["csv_prefix"],
            page_id + "_" + post_id,
            ".csv"
        )
    except KeyError:
        logger.error(
            "Invalid configuration file. Please check template and retry")
        sys.exit(0)
    logger.info("Getting data for post with ID: {}".format(post_id))
    actual_post_id = page_id + "_" + post_id
    local_start = time.time()
    data = get_data(access_token, actual_post_id)
    comments = get_comments(data)
    if len(comments) == 0:
        logger.error(
            "Apparently, there are no comments at the selected post. "
            "Check "
        )
        sys.exit(0)
    if len(comments) == 1:
        logger.warning(
            "Found only 1 comments. Not enough data "
            "to make much sense. Plots will be made regardless")
    logger.info("Got {} comments in {} seconds".format(
        len(comments), round((time.time() - local_start), 2)))
    logger.info("Pre processing comments")
    preprocessed_comments = [preprocess(comm) for comm in comments]
    logger.info("Preprocessed {} comments out of {} in {} seconds".format(
        len(preprocessed_comments), len(comments), round((time.time() - local_start), 1)))
    logger.info("Performing word count")
    wordcount_data = get_wordcount(preprocessed_comments)
    logger.info("Saving data to CSV with name {} ".format(data_filename))
    create_nonexistent_dir(data_dir_path)
    data_filepath = os.path.join(data_dir_path, data_filename)
    save_data(wordcount_data, data_filepath)
    logger.info("Saved {} words and their counts in {} ".format(
        len(wordcount_data), data_filepath))
    logger.info("Making plots ")
    unstemmed_comments = [base_preproc(comm) for comm in comments]
    long_string = " ".join(uc for uc in unstemmed_comments)
    create_nonexistent_dir(plots_dir_path)
    wc_plot_filepath = os.path.join(plots_dir_path, wc_plot_filename)
    barplot_filepath = os.path.join(plots_dir_path, barplot_filename)
    save_wordcloud_plot(long_string, wc_plot_filepath)
    logger.info("Wordcloud plot saved in {}".format(wc_plot_filepath))
    save_barplot(wordcount_data, n_top_words, barplot_filepath)
    logger.info("Bar plot saved in {}".format(barplot_filepath))
    logger.info("\aDIN DONE!")
    logger.info("Total time of execution: {} seconds".format(
        round((time.time() - start), 1)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""Count comments in a given post""")
    parser.add_argument('-c', '--config', type=str, metavar='', required=True,
                        help='Specify the path of the configuration file')
    args = parser.parse_args()
    CONFIG_PATH = args.config
    post_id = input("Provide post ID: ")
    main(CONFIG_PATH, post_id)
