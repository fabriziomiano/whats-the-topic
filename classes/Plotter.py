import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from wordcloud import WordCloud


class Plotter(object):
    def __init__(self, long_string, wordcount_data):
        """
        :param long_string:  str: Whitespace concatenation of
            all the words in a given corpus
        :param wordcount_data: list of tuples(word, wordcount)
        """
        self.long_string = long_string
        self.wordcount_data = wordcount_data

    def save_wordcloud_plot(self, path):
        """
        Save wordcloud basic image

        :param path: str: output file path
        :return: None
        """
        wc = WordCloud(
            background_color="black",
            contour_width=3,
            contour_color='steelblue'
        )
        wc.generate(self.long_string)
        wc.to_file(path)

    def plot_wordcloud(self):
        """
        Wrapper of WordCloud.to_image() method

        :return: WordCloud.to_image() instance
        """
        wc = WordCloud(
            background_color="black",
            contour_width=3,
            contour_color='steelblue'
        )
        wc.generate(self.long_string)
        wc.to_image()
        return wc.to_image()

    def save_barplot(self, n_top_words, path):
        """
        Save bar plot of given word count data

        :param n_top_words: int number of top words to plot
        :param path:
        :return:
        """
        df = pd.DataFrame(self.wordcount_data, columns=["word", "count"])
        plt.figure(figsize=(n_top_words, 10))
        barplot = sns.barplot("word", "count", data=df[:n_top_words], palette="Blues_d")
        barplot.set_title("Top {} Words".format(n_top_words))
        plt.xticks(rotation=30)
        plt.xlabel("Word")
        plt.ylabel("Count", labelpad=60, rotation=0)
        plt.savefig(path)
