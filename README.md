# FBCommentsTopicAnalysis
Facebook comments basic topic analysis

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

This tool has been developed on Ubuntu 18.04 and has never been 
seriously tested. 
It requires Python3+ and `virtualenv`. 
With these two installed, simply clone the repo
and run `source install.sh`

#### Requirements

A Facebook API token from facebook for developers, 
Python3+, `virtualenv`


## How to run
Two modes are allowed and they can be executed with the following 
(**remember to edit settings.conf**): 
##### Single-post using post ID
* `source by_id.sh settings.conf` 
##### Latest N posts
* `source latest.sh settings.conf`

##### Named-Entity Recognition using spaCy
Additionally, it is possible to run Named-Entity Recognition using 
default spaCy models (supported: en, it). 
No Word Cloud option provided in this case
* `source ner.sh settings.conf`


### Considerations 
The tool is designed to run until the settings requested are met or 
up until the max request rate, that Facebook do apply, is reached.

That's it!

## Results 
Here there are two images of the plots that are produced 
by running the tool on this post:
https://www.facebook.com/GiveToTheNext/posts/477277113022512

#### Bar plot using the top 20 words

![alt_text](https://raw.githubusercontent.com/fabriziomiano/FBCommentsTopicAnalysis/master/sample_img/barplot_445363319547225_477277113022512.png)

#### Word cloud with no stemming 

![alt text](https://raw.githubusercontent.com/fabriziomiano/FBCommentsTopicAnalysis/master/sample_img/wc_445363319547225_477277113022512.png)


## Credits
Thanks to the people who made 
this https://facebook-sdk.readthedocs.io/en/latest and 
this https://amueller.github.io/word_cloud
