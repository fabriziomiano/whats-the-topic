# FbPostTopicAna
Facebook post basic topic analysis

## Requirements

A Facebook API token from facebook for developers, 
Python3+, `virtualenv`

## What is it?
A simple tool to run a basic, very simple, 
topic analysis on facebook posts. 
It's pretty much a word counter that employs 
standard NLP pre-processing.

#### How does it do it?
It gets the data of given posts by calling
the Facebook GraphAPI. It performs text preprocessing
(tokenization, stopwords filtering, stemming) and makes plots:
a word cloud plot and a bar plot of the N most important words.
The tool can be configured in page id, single post id, number of
posts, etc. 
It can be run on the last n plots, or on a given post id.

## How to install
This tool was developed on Ubuntu 18.04 and has never been 
seriously tested. 
It requires Python3+ and `virtualenv`. 
With these two installed, simply clone the repo
and run `source install.sh`


## How to run
Two modes are allowed and they can be executed with the following 
(**remember to edit settings.conf**): 
##### Single-post using post ID
* `source by_id.sh settings.conf` 
##### Latest N posts
* `source latest.sh settings.conf` 

The tool will run until the settings requested are met or 
up until the max request rate that facebook applies is reached.

That's it!

## Credits
Thanks to the people who made 
this https://facebook-sdk.readthedocs.io/en/latest and 
this https://amueller.github.io/word_cloud
