import argparse
import logging
import os
import sys
import time

from classes.TextPreprocessor import TextPreprocessor
from classes.WordCloudPlotter import Plotter
from utils import (
    get_logger, load_config, get_post_data, get_comments, do_wordcount,
    create_nonexistent_dir, save_barplot, data_to_tsv
)


def main():
    parser = argparse.ArgumentParser(
        description="""Count comments in a given post""")
    parser.add_argument(
        '-c', '--conf', type=str, metavar='', required=True,
        help='Specify the path of the configuration file')
    args = parser.parse_args()
    config_path = args.conf
    start = time.time()
    logger = get_logger(__name__)
    logger.setLevel(logging.DEBUG)
    conf = load_config(config_path)
    post_id = ""
    while post_id == "":
        post_id = input("Provide post ID: ")
    try:
        access_token = conf["access_token"]
        page_id = conf["page_id"]
        n_top_words = conf["n_top_words"]
        data_dir_path = os.path.join(page_id, conf["data_dir_name"])
        data_filename = "{}_{}{}".format(conf["data_wc_prefix"], post_id, ".csv")
        plots_dir_path = os.path.join(page_id, conf["plots_dir_name"], "single_posts", post_id)
        wc_plot_filename = "{}_{}{}".format(conf["wc_plot_filename"], post_id, ".png")
        wc_plot_filepath = os.path.join(plots_dir_path, wc_plot_filename)
        barplot_filename = "{}_{}{}".format(conf["barplot_filename"], post_id, ".png")
        barplot_filepath = os.path.join(plots_dir_path, barplot_filename)
    except KeyError:
        logger.error(
            "Invalid configuration file. Please check template and retry")
        sys.exit(0)
    url_post = "https://www.facebook.com/posts/{}".format(post_id)
    logger.info("Getting data for post {}".format(url_post))
    actual_post_id = page_id + "_" + post_id
    local_start = time.time()
    data = get_post_data(access_token, actual_post_id)
    comments = get_comments(data)
    if len(comments) == 0:
        logger.error(
            """Apparently, there are no comments at the selected post
            Check the actual post on its Facebook page 
            https://www.facebook.com/{}/posts/{}""".format(page_id, post_id)
        )
        sys.exit(0)
    elif len(comments) < 100:
        logger.warning(
            "Got {} comments. Not enough data "
            "to make much sense. Plots will be made regardless".format(len(comments))
        )
    else:
        logger.info("Got {} comments in {} seconds".format(
            len(comments), round((time.time() - local_start), 2)))
    local_start = time.time()
    preprocessed_comments = [TextPreprocessor(comm).preprocess() for comm in comments]
    logger.info("Preprocessed {} comments out of {} in {} seconds".format(
        len(preprocessed_comments), len(comments), round((time.time() - local_start), 1)))
    logger.info("Performing word count")
    wordcount_data = do_wordcount(preprocessed_comments)
    create_nonexistent_dir(data_dir_path)
    data_filepath = os.path.join(data_dir_path, data_filename)
    columns = ["word", "count"]
    data_to_tsv(wordcount_data, columns, data_filepath)
    logger.info("Saved {} words and their counts in {} ".format(
        len(wordcount_data), data_filepath))
    create_nonexistent_dir(plots_dir_path)
    plot_labels = ["Words", "Counts"]
    save_barplot(wordcount_data, plot_labels, n_top_words, barplot_filepath)
    logger.info("Bar plot saved at {}".format(barplot_filepath))
    unstemmed_comments = [TextPreprocessor(comm).base_preprocess() for comm in comments]
    long_string = " ".join(uc for uc in unstemmed_comments)
    p = Plotter(long_string)
    p.save_wordcloud_plot(wc_plot_filepath)
    logger.info("Word Cloud plot saved at {}".format(wc_plot_filepath))
    logger.info("\a\a\aDIN DONE!")
    logger.info("Total time of execution: {} seconds".format(
        round((time.time() - start), 1)))


if __name__ == "__main__":
    main()
