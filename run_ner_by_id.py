import argparse
import logging
import os
import sys
import time

import spacy

from utils import (
    get_logger, load_config, get_data, get_comments, save_barplot,
    create_nonexistent_dir, save_data, get_entities, count_entities
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
    supported_languages = ["it", "en"]
    lang = input("Insert language (it, en): ")
    if lang not in supported_languages:
        logger.error("Please provide a valid language. Supported: 'en', 'it'")
        sys.exit(1)
    else:
        try:
            model = conf.get(lang)
            nlp = spacy.load(model)
        except OSError:
            logger.error("Could not find model in conf file. Please double check")
            sys.exit(0)
    post_id = ""
    while post_id == "":
        post_id = input("Provide post ID: ")
    try:
        access_token = conf["access_token"]
        page_id = conf["page_id"]
        n_top_entities = conf["n_top_entities"]
        data_dir_path = os.path.join(page_id, conf["data_dir_name"])
        data_filename = "{}_{}{}".format(conf["data_entities_prefix"], post_id, ".csv")
        plots_dir_path = os.path.join(page_id, conf["plots_dir_name"])
        barplot_filename = "{}_{}{}".format(conf["barplot_filename"], post_id, "_ner.png")
        barplot_filepath = os.path.join(plots_dir_path, barplot_filename)
    except KeyError:
        logger.error(
            "Invalid configuration file. Please check template and retry")
        sys.exit(0)
    actual_post_id = page_id + "_" + post_id
    url_post = "https://www.facebook.com/posts/{}".format(actual_post_id)
    logger.info("Getting data for post {}".format(url_post))
    local_start = time.time()
    data = get_data(access_token, actual_post_id)
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
    entities = []
    for comment in comments:
        ents = get_entities(nlp, comment)
        entities.extend(ents)
    logger.info("Extracted {} entities out of {} comments in {} seconds".format(
        len(entities), len(comments), round((time.time() - local_start), 2)))
    entities_data = count_entities(entities)
    create_nonexistent_dir(data_dir_path)
    data_filepath = os.path.join(data_dir_path, data_filename)
    save_data(entities_data, data_filepath)
    logger.info("Saved {} unique entities and their counts in {} ".format(
        len(entities_data), data_filepath))
    create_nonexistent_dir(plots_dir_path)
    save_barplot(entities_data, n_top_entities, barplot_filepath, type_="entities")
    logger.info("Bar plot saved at {}".format(barplot_filepath))
    logger.info("\a\a\aDIN DONE! in {} seconds".format(
        round((time.time() - start), 1)))


if __name__ == "__main__":
    main()
