import json
import unicodedata
import string
from nltk.stem.snowball import SnowballStemmer
STEMMER = SnowballStemmer("italian")
with open("stoplist.json") as stop_in:
    STOPLIST = json.load(stop_in)


class TextPreprocessor(object):
    def __init__(self, text):
        self.text = text

    def remove_non_ascii(self):
        """
        Remove non-ASCII charachters from
        a given string

        :return: str
        """
        onlyascii_tokens = []
        for token in self.text.split():
            token = unicodedata.normalize('NFKD', token)\
                .encode('ascii', 'ignore').decode('utf-8', 'ignore')
            onlyascii_tokens.append(token)
        self.text = " ".join(token for token in onlyascii_tokens)

    def remove_stopwords(self):
        """
        Remove stopwords from a given string

        :return: str
        """
        tokens = [t for t in self.text.split()
                  if t not in STOPLIST]
        self.text = " ".join(t for t in tokens)

    def remove_punctuation(self):
        """
        Remove punctuation from a given string

        :return: str
        """
        tokens = [
            token.translate(str.maketrans("", "", string.punctuation))
            for token in self.text.split()
        ]
        self.text = " ".join(t for t in tokens)

    def stem_text(self):
        """
        Return a stemmed string

        :return: list of stemmed tokens
        """
        tokens = self.text.split()
        self.text = " ".join(STEMMER.stem(t) for t in tokens)

    def base_preprocess(self):
        """
        Perform standard NLP preprocessing:
        Tokenization, non-ASCII chars and stopwords removal

        :return: self.text
        """
        self.remove_punctuation()
        self.remove_non_ascii()
        self.remove_stopwords()
        return self.text

    def preprocess(self):
        """
        Perform base_preprocess() and stemming

        :return: self.text
        """
        self.base_preprocess()
        self.stem_text()
        return self.text
