import logging
import os
import argparse
import sys
import time
from classes.Plotter import Plotter
from classes.TextPreprocessor import TextPreprocessor
from utils import (
    get_logger, load_config, get_data, get_comments, do_wordcount,
    create_nonexistent_dir, save_data
)


parser = argparse.ArgumentParser(
    description="""Count comments in a given post""")
parser.add_argument('-c', '--config', type=str, metavar='', required=True,
                    help='Specify the path of the configuration file')
args = parser.parse_args()
config_path = args.config
post_id = input("Provide post ID: ")
start = time.time()
logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Reading configuration file")
conf = load_config(config_path)
try:
    access_token = conf["access_token"]
    page_id = conf["page_id"]
    plots_dir_path = os.path.join(conf["plots_dir_path"], )
    data_dir_path = conf["data_dir_path"]
    n_top_words = conf["n_top_words"]
    wc_plot_filename = "{}_{}{}".format(conf["wc_plot_filename"], page_id + "_" + post_id, ".png")
    barplot_filename = "{}_{}{}".format(conf["barplot_filename"], page_id + "_" + post_id, ".png")
    data_filename = "{}_{}{}".format(conf["csv_prefix"], page_id + "_" + post_id, ".csv")
    wc_plot_filepath = os.path.join(plots_dir_path, wc_plot_filename)
    barplot_filepath = os.path.join(plots_dir_path, barplot_filename)
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
        "Check Facebook page https://www.facebook.com/"
        "virginia.raggi.m5sroma/posts/{}".format(post_id))
    sys.exit(0)
elif len(comments) == 1:
    logger.warning(
        "Found only 1 comments. Not enough data "
        "to make much sense. Plots will be made regardless")
else:
    logger.info("Got {} comments in {} seconds".format(
        len(comments), round((time.time() - local_start), 2)))
local_start = time.time()
preprocessed_comments = [TextPreprocessor(comm).preprocess() for comm in comments]
logger.info("Preprocessed {} comments out of {} in {} seconds".format(
    len(preprocessed_comments), len(comments), round((time.time() - local_start), 1)))
logger.info("Performing word count")
wordcount_data = do_wordcount(preprocessed_comments)
logger.info("Saving data to CSV with name {} ".format(data_filename))
create_nonexistent_dir(data_dir_path)
data_filepath = os.path.join(data_dir_path, data_filename)
save_data(wordcount_data, data_filepath)
logger.info("Saved {} words and their counts in {} ".format(
    len(wordcount_data), data_filepath))
logger.info("Making plots ")
unstemmed_comments = [TextPreprocessor(comm).base_preprocess() for comm in comments]
long_string = " ".join(uc for uc in unstemmed_comments)
create_nonexistent_dir(plots_dir_path)
p = Plotter(long_string, wordcount_data)
p.save_wordcloud_plot(wc_plot_filepath)
logger.info("Wordcloud plot saved at {}".format(wc_plot_filepath))
p.save_barplot(n_top_words, barplot_filepath)
logger.info("Bar plot saved at {}".format(barplot_filepath))
logger.info("\a\a\aDIN DONE!")
logger.info("Total time of execution: {} seconds".format(
    round((time.time() - start), 1)))
