import argparse
import logging
import os
import sys
import time

import facebook
import spacy

from utils import (
    get_logger, load_config, get_post_data, get_comments, save_barplot,
    create_nonexistent_dir, data_to_tsv, get_entities, count_entities,
    check_n_posts
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
    n_posts = check_n_posts()
    if not n_posts.isdigit() and n_posts != "-1":
        logger.error("Please give a number. Exiting")
        sys.exit(0)
    try:
        access_token = conf["access_token"]
        page_id = conf["page_id"]
        n_top_entities = conf["n_top_entities"]
        data_dir_path = os.path.join(page_id, conf["data_dir_name"])
        data_filename = "{}_{}.tsv".format(conf["data_entities_prefix"], str(n_posts))
        plots_dir_path = os.path.join(page_id, conf["plots_dir_name"])
        barplot_filename = "{}_{}posts_ner.png".format(conf["barplot_filename"], str(n_posts))
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
    if n_posts != "":
        logger.info("Getting the last {} posts".format(n_posts))
    else:
        logger.warning(
            "Requesting posts with no limits. "
            "This could be susceptible of limitations"
            " in the near future due to high rate"
        )
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
    entities = []
    for comment in comments:
        ents = get_entities(nlp, comment)
        entities.extend(ents)
    logger.info("Extracted {} entities out of {} comments in {} seconds".format(
        len(entities), len(comments), round((time.time() - local_start), 2)))
    entities_data = count_entities(entities)
    create_nonexistent_dir(data_dir_path)
    data_filepath = os.path.join(data_dir_path, data_filename)
    columns = ["entities", "count"]
    data_to_tsv(entities_data, columns, data_filepath)
    logger.info("Saved {} unique entities and their counts in {} ".format(
        len(entities_data), data_filepath))
    create_nonexistent_dir(plots_dir_path)
    plot_labels = ["Entities", "Counts"]
    save_barplot(entities_data, plot_labels, n_top_entities, barplot_filepath, type_="entities")
    logger.info("Bar plot saved at {}".format(barplot_filepath))
    logger.info("\a\a\aDIN DONE! in {} seconds".format(
        round((time.time() - start), 1)))


if __name__ == "__main__":
    main()
