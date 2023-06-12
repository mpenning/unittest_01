## Example

This example walks through various ways to optimize how unit tests are built.

Everything in the `tests/*.py` code hinges on where we patch tests.

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
