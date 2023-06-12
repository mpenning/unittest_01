## Example

This example walks through various ways to optimize how unit tests are built.

Everything in the `tests/*.py` code hinges on where we patch code under test.

- Patching `random.choices()` is best in this example.  It provides predictable
  values which can be tested against. By patching `random.choices()`, we can test
  almost all code in `get_words()`.
- Patching `WordSpam().get_words()` is not as good; this is because it bypasses 
  tests of the logic contained in `get_words()`.

See the docstrings and tests in `tests/test_foo.py` for more concrete explanations.

### Code under test

The following code is all of what we are testing; it's quite trivial, which is good 
for the purposes of this example.

```python
# Filename: my_module/things.py
from typing import List
import random

class WordSpam(object):

    def __init__(self) -> None:
        """
        Boring example of code which will return some random words.
        This is a contrived object whose 'get_words()' method will
        be patched and tested.
        """
        self._words = [
            "fleas", "please", "cheese", "geez", "grease",
            "ease", "bees", "tease", "knees", "seas", "trees",
        ]

    def get_words(self, number_of_words: int=-1) -> List[str]:
        """
        Return a list of random words.  The number of words is determined
        by the 'number_of_words' parameter.

        This method will be patched and tested by modifying 'random.choices()'
        """
        if number_of_words == -1:
            number_of_words = len(self._words)

        #################################################################
        # Begin code which should be patched in our unit tests.
        these_choices = random.choices(self._words, k=number_of_words)
        # End code which should be patched in our unit tests.
        #################################################################
        return these_choices

    def __repr__(self):
        return "<WordSpam containing {} random words>".format(len(self._words))
```

### Unittest code

This is one of a few ways to test the code in `my_module/things.py`.

Assume that we put this in `tests/test_foo.py`.

```python
import sys
sys.path.insert(0, "../")

# Even though we only import WordSpam(), python can access 'my_module.things'
# because of the way that Python handles namespaces...
from my_module.things import WordSpam
# This 'import my_module.things' import should not be skipped... it's required
# for the 'with patch.object()' call below...
import my_module.things

from unittest.mock import patch
import random

def test_foo_spam_get_words_01():
    """
    The best option (because it doesn't use magical syntax)...
    use a 'with patch.object()' context manager to patch 'random.choices()'
    inside 'my_module/things.py' and then 'import foo'.  This works because
    we patch 'random.choices()' inside 'my_module/things.py' **before**
    'import foo'.

    Normally WordSpam().get_words() returns **random words**, but we want to
    force it to return a predictable word list() so usage is testable...

    'foo.py' uses 'random.choices()' when it calls
    'from my_module.things import WordSpam'.
    """
    with patch.object(my_module.things.random, "choices") as mock_choices:
        # Yes         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ <- A) Do THIS!!!
        # Mock the return value of 'random.choices()' in 'my_module.things'
        mock_choices.return_value = ["fish", "dish"]

        # Import ../foo.py after patching 'my_module.things.random.choices()'
        import foo
        # 'spam' is an instance of 'my_module.things.WordSpam()' in 'foo.py'.
        # We are testing WordSpam().get_words() inside 'foo.py'...
        assert foo.spam.get_words(2) == ["fish", "dish"]
        # 'del foo' offers MAXIMUM test assert isolation...
        del foo

def test_foo_spam_get_words_01():
    """
    Another way to only test `WordSpam().get_words()`...
    """
    with patch.object(my_module.things.random, "choices") as mock_choices:
        # Mock the return value of 'random.choices()' in 'my_module.things'
        mock_choices.return_value = ["fish", "dish"]

        spam = WordSpam()
        # `get_words()` is not random anymore because we patched() specific
        # values that will always be used... see below...
        assert spam.get_words() == ["fish", "dish"]

```
