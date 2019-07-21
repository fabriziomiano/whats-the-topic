from wordcloud import WordCloud


class Plotter(object):
    def __init__(self, long_string):
        """
        :param long_string:  str: Whitespace concatenation of
            all the words in a given corpus
        """
        self.long_string = long_string

    def save_wordcloud_plot(self, path):
        """
        Save wordcloud basic image

        :param path: str: output file path
        :return: None
        """
        wc = WordCloud(
            width=800,
            height=600,
            background_color="black",
            contour_width=3,
            contour_color="steelblue"
        )
        wc.generate(self.long_string)
        wc.to_file(path)

    def plot_wordcloud(self):
        """
        Wrapper of WordCloud.to_image() method

        :return: WordCloud.to_image() instance
        """
        wc = WordCloud(
            width=800,
            height=600,
            background_color="black",
            contour_width=3,
            contour_color='steelblue'
        )
        wc.generate(self.long_string)
        wc.to_image()
        return wc.to_image()
