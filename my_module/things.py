
import random

class WordSpam(object):

    def __init__(self) -> None:
        """
        Boring example of code which will return some random words.
        This is a contrived object whose 'get_words()' method will
        be mocked and tested.
        """
        self._words = [
            "fleas", "please", "cheese", "geez", "grease",
            "ease", "bees", "tease", "knees", "seas", "trees",
        ]

    def get_words(self, number_of_words: int=-1) -> list:
        """
        Return a list of random words.  The number of words is determined
        by the 'number_of_words' parameter.

        This method will be mocked and tested when we patch and mock
        'random.choices()'
        """
        if number_of_words == -1:
            number_of_words = len(self._words)
        #these_choices = random.choices(self._words, k=number_of_words)
        these_choices = random.choices(self._words, k=number_of_words)
        return these_choices

    def __repr__(self):
        return "<WordSpam containing {} random words>".format(len(self._words))

