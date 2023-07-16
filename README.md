## Example

This example walks through various ways to optimize how unit tests are built.

The code we are testing is at the bottom of this README.

Everything in the `tests/*.py` code hinges on where we patch code under test.

- Patching `random.choices()` is best in this example.  It provides predictable
  values which can be tested against.
- Patching `WordSpam().get_words()` is not as good; this is because it bypasses 
  tests of the logic contained in `get_words()`.

See the docstrings and tests in `tests/test_foo.py` for more concrete explanations.

### Unittest code

The following illustrate a few ways to test the code in `my_module/things.py`.
One of the most problematic things about testing `WordSpam().get_words()` is
that it picks words at random; random behavior makes it impossible
to build good unit tests... consequently my tests patch `WordSpam()` such
that it returns a predictable value.

The following tests patch `random.choices()` in `my_module/things.py`.

Assume that we put the following in `tests/test_foo.py`.

```python
import sys
sys.path.insert(0, "../")

# Even though we only import WordSpam(), python can access 'my_module.things'
# because of the way that Python handles namespaces...
import my_module.things import WordSpam
# This 'import my_module.things' import should not be skipped... it's required
# for the 'with patch.object()' call below...
import my_module.things

from unittest.mock import patch, MagicMock
import random



def test_foo_spam_get_words_01():
    """
    The best option... patch 'random.choices()' inside 'my_module/things.py'
    to return a predictable value when 'random.choices()' is called.  We
    must call 'import foo' **after** calling 'random.choices()'.

    I like 'with patch()' as a context manager instead of an '@patch()'
    decorator because 'with patch()' doesn't have unusual syntax.  The
    '@patch()' property introduces a new argument in the method call.
    """
    # Using a context manager to patch `random.choices()` in `my_module/things.py`

    # Option 1, avoid creating an explicit MagicMock(). 'with patch()' creates
    # a MagicMock()
    with patch("my_module.things.random.choices", return_value=["fish", "dish"]):

        # Import ../foo.py after patching 'my_module.things.random.choices()'
        import foo
        # 'spam' is an instance of 'my_module.things.WordSpam()' in foo.py.
        # We are testing WordSpam().get_words() inside 'foo.py'...
        assert foo.spam.get_words() == ["fish", "dish"]
        # 'del foo' offers MAXIMUM test assert isolation...
        del foo

    # Option 2, create an explicit MagicMock() called 'magic_mock_choices'
    with patch("my_module.things.random.choices") as magic_mock_choices:
        # Mock the return value of 'random.choices()' in 'my_module.things'
        magic_mock_choices.return_value = ["fish", "dish"]
        assert isinstance(magic_mock_choices, MagicMock)

        # Import ../foo.py after patching 'my_module.things.random.choices()'
        import foo
        # 'spam' is an instance of 'my_module.things.WordSpam()' in foo.py.
        # We are testing WordSpam().get_words() inside 'foo.py'...
        assert foo.spam.get_words() == ["fish", "dish"]
        # 'del foo' offers MAXIMUM test assert isolation...
        del foo


def test_foo_spam_get_words_02():
    """
    A good option (because it doesn't use magical syntax)...
    We must call 'import foo' **after** calling 'random.choices()'.

    'foo.py' uses 'random.choices()' when it calls
    'from my_module.things import WordSpam'.
    """
    # Normnally WordSpam().get_words() returns **random words**, but I'm
    # forcing it to return a predictable word list() so usage is testable...
    #
    # Using a context manager to patch `random.choices()` in `my_module/things.py`
    with patch.object(my_module.things.random, "choices", return_value=["fish", "dish"]):
        # Mock the return value of 'random.choices()' in 'my_module.things'
        #    behind the scenes, 'patch()' creates a unittest.MagicMock() instance

        # Import ../foo.py after patching 'my_module.things.random.choices()'
        import foo
        # 'spam' is an instance of 'my_module.things.WordSpam()' in 'foo.py'.
        # We are testing WordSpam().get_words() inside 'foo.py'...
        assert foo.spam.get_words(2) == ["fish", "dish"]
        # 'del foo' offers MAXIMUM test assert isolation...
        del foo

@patch("my_module.things.random.choices")
# This behavior is a bit magical and I'm not fond of the technique...
# I prefer `patch()` as a context-manager (see above).
def test_foo_spam_get_words_03(mock_choices):
    # A virtual parameter  ->  ^^^^^^^^^^^^
    #
    # @patch('my_module.things.random.choices') inserts a virtual
    # parameter above (which I call 'mock_choices')
    """
    The GOOD option... patch 'random.choices()' inside 'my_module/things.py'
    and then 'import foo'.  This works because we patch 'random.choices()'
    inside 'my_module/things.py' **before** 'import foo'.

    'foo.py' uses 'random.choices()' when it calls
    'from my_module.things import WordSpam'.
    """
    # here we mock 'my_module.things.random.choices()'...
    mock_choices.return_value = ["fish", "dish"]

    # Import ../foo.py after patching 'my_module.things.random.choices()'
    import foo
    # 'spam' is an instance of 'my_module.things.WordSpam()' in foo.py.
    # We are testing WordSpam().get_words() inside 'foo.py'...
    assert foo.spam.get_words() == ["fish", "dish"]
    # 'del foo' offers MAXIMUM test assert isolation...
    del foo


def test_wordspam_04():
    """
    Ick... this is gross.  Why?  Because we are barely testing anything in
    'WordSpam().get_words()'.  All we did is patch() 'WordSpam().get_words()'
    to return a certain value.
    """
    # Normally WordSpam().get_words() returns **random words**, but we want to
    # force it to return a predictable word list() so usage is testable...
    #
    # Use a context manager to patch `WordSpam().get_words()` in
    # `my_module/things.py`.
    with patch("my_module.things.WordSpam.get_words", return_value=["fish", "dish"]):
        # Ick  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        spam = WordSpam()
        assert spam.get_words(0) == ["fish", "dish"]


def test_wordspam_05_antipattern():
    """
    Ick... Avoid patching the python stdlib directly; in this antipattern, we
    patch stdlib 'random.choices()'.  It's better to patch it locally in your own
    module (for the best option, refer to 'test_foo_spam_get_words_01()' above...

    Globally patching 'random.choices()' is considered a patch antipattern, because 
    it patches python stdlib 'random.choices()' everywhere.
    """
    # Try NOT to directly path python stdlib... you have no test case
    # isolation when patching python stdlib directly...
    #
    #
    # Use a context manager to patch `random.choices()` globally.
    # `patch("random.choices")` everywhere is an antipattern for normal
    # test practice.
    with patch("random.choices") as mock_random_choices:
        # No   ^^^^^^^^^^^^^^^^ <- avoid directly patching python stdlib!
        mock_random_choices.return_value = ["fish", "dish"]
        spam = WordSpam()
        assert spam.get_words(0) == ["fish", "dish"]

@patch("my_module.things.random.choices", return_value=["fish", "dish"])
# Yes: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
class GoodTestRandomChoices_01(TestCase):
    """
    Good example.  Why?  Because the `@patch()` class wrapper is patching
    `random.choices()` in `my_module/things.py`.  This patches in the best
    way... it changes 'my_module.things.random.choices()' (which is used by
    'WordSpam().get_words()') to return fixed (i.e. non-random) value.

    Refer to the '@patch()' wrapper above to see where the patch is applied.
    """

    def setUp(self):
        pass

    def test_foo_spam_get_words_06(self, *args, **kwargs):
        spam = WordSpam()
        assert spam.get_words(0) == ["fish", "dish"]

    def tearDown(self):
        pass


@patch("my_module.things.random.choices", return_value=["fish", "dish"])
# Yes: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
class GoodTestRandomChoices_02(TestCase):
    """
    Good example.  Why?  Because the `@patch()` class wrapper is patching
    `random.choices()` in `my_module/things.py`.  This patches in the best
    way... it changes 'my_module.things.random.choices()' (which is used by
    'WordSpam().get_words()') to return fixed (i.e. non-random) value.

    Refer to the '@patch()' wrapper above to see where the patch is applied.
    """

    def setUp(self):
        pass

    def test_foo_spam_get_words_07(self, *args, **kwargs):
        """Test 'WordSpam().get_words()' directly in ../foo.py"""
        # Import ../foo.py after patching 'my_module.things.random.choices()'
        import foo
        # 'spam' is an instance of 'my_module.things.WordSpam()' in ../foo.py.
        # We are testing WordSpam().get_words() inside '../foo.py'...
        assert foo.spam.get_words() == ["fish", "dish"]
        # 'del foo' offers MAXIMUM test assert isolation...
        del foo

    def tearDown(self):
        pass

@patch("my_module.things.WordSpam.get_words", return_value=["fish", "dish"])
# Ick: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
class IckyTestWordSpam(TestCase):
    """
    Ick... this is gross.  Why?  Because we are barely testing anything in
    'WordSpam().get_words()'.  All we did is mock `WordSpam().get_words()`
    to return a certain value.

    The `GoodTestRandomChoices_01()` and `GoodTestRandomChoices_02()` class
    above patches in the best way... it changes
    `my_module.things.random.choices()` to return fixed (i.e. non-random)
    values.

    This class also returns fixed values, but it does so by testing much
    less code in 'WordSpam()'.
    """

    def setUp(self):
        pass

    def test_foo_spam_get_words_08(self, *args, **kwargs):
        """Test 'WordSpam().get_words()' (i.e. not in '../foo.py')"""
        spam = WordSpam()
        assert spam.get_words(0) == ["fish", "dish"]

    def tearDown(self):
        pass

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
