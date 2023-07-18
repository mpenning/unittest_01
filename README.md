## Example

This example walks through various ways to optimize how unit tests are built.

The code we are testing is at the bottom of this README.

Everything in the `tests/*.py` code hinges on where we patch code under test.

- Patching `my_module.things.random.choices()` is best in this example.  It
  provides predictable values which can be tested against.
- Patching `my_module.things.WordSpam().get_words()` is not as good because
  the test mock bypasses the logic contained in `get_words()`.

See the docstrings and tests in `tests/test_foo.py` for more concrete explanations.

### Unittest code

The following illustrate a few ways to test the code in `my_module/things.py`.

The following tests patch `random.choices()` in `my_module/things.py`.

Assume that we put the following in `tests/test_foo.py`.

```python
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, "../")

def test_example():
    # Option 1, avoid creating an explicit MagicMock() ('patch()' creates the MagicMock())
    # 'foo.py' -> 'my_module.things.WordSpam()' -> my_module.things.random.choices()
    with patch(target="my_module.things.random.choices", return_value=["fish", "dish"]):

        # Import ../foo.py after patching 'my_module.things.random.choices()'
        import foo
        # 'spam' is an instance of 'my_module.things.WordSpam()' in foo.py.
        # We are testing ().get_words() inside 'foo.py'...
        assert foo.spam.get_words() == ["fish", "dish"]
        # 'del foo' offers MAXIMUM test assert isolation...
        del foo

    # Option 2, create an explicit MagicMock() called 'magic_mock_choices'
    # 'foo.py' -> 'my_module.things.WordSpam()' -> my_module.things.random.choices()
    with patch(target="my_module.things.random.choices") as magic_mock_choices:
        # Mock the return value of 'random.choices()' in 'my_module.things'
        magic_mock_choices.return_value = ["fish", "dish"]
        assert isinstance(magic_mock_choices, MagicMock)

        # Import ../foo.py after patching 'my_module.things.random.choices()'
        import foo
        # 'spam' is an instance of 'my_module.things.WordSpam()' in foo.py.
        # We are testing ().get_words() inside 'foo.py'...
        assert foo.spam.get_words() == ["fish", "dish"]
        # 'del foo' offers MAXIMUM test assert isolation...
        del foo

```

### Code under test

The following code is all of what I want to test; `WordSpam()` is quite trivial, 
which is good for the purposes of this example.

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
