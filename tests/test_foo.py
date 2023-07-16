
import sys
sys.path.insert(0, "../")

# Even though we only import (), python can access 'my_module.things'
# because of the way that Python handles namespaces...
from my_module.things import WordSpam
# This 'import my_module.things' import should not be skipped... it's required
# for the 'with patch.object()' call below...
import my_module.things

from unittest.mock import patch, MagicMock
from unittest import TestCase
import random

def test_spam_app_get_words_01():
    """
    The best option... patch 'random.choices()' inside
    'my_module/things.py' and then 'import foo'.  This works because
    we patch 'random.choices()' inside 'my_module/things.py' 
    **before** 'import foo'.

    'foo.py' uses 'random.choices()' when it calls
    'from my_module.things import random'.

    I like 'with patch()' as a context manager instead of an '@patch()'
    wrapper.  The 'with patch()' context manager has less magical
    syntax compared with an '@patch()' wrapper.
    """
    # Normally ().get_words() returns **random words**, but we want to
    # force it to return a predictable word list() so usage is testable...
    #
    # Use a context manager to patch `random.choices()` in `my_module/things.py`
    # this context manager is called `mock_choices`.
    #

    # Option 1, avoid creating an explicit MagicMock() ('patch()' creates the MagicMock())
    # 'foo.py' -> 'my_module.things.WordSpam()' -> my_module.things.random.choices()
    with patch("my_module.things.random.choices", return_value=["fish", "dish"]):

        # Import ../foo.py after patching 'my_module.things.random.choices()'
        import foo
        # 'spam' is an instance of 'my_module.things.WordSpam()' in foo.py.
        # We are testing ().get_words() inside 'foo.py'...
        assert foo.spam.get_words() == ["fish", "dish"]
        # 'del foo' offers MAXIMUM test assert isolation...
        del foo

    # Option 2, create an explicit MagicMock() called 'magic_mock_choices'
    # 'foo.py' -> 'my_module.things.WordSpam()' -> my_module.things.random.choices()
    with patch("my_module.things.random.choices") as magic_mock_choices:
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

class GoodTestRandomChoices_01(TestCase):

    def setUp(self):
        pass

    def test_spam_app_get_words_02(self, *args, **kwargs):
        # 'foo.py' -> 'my_module.things.WordSpam()' -> my_module.things.random.choices()
        with patch("my_module.things.random.choices", return_value=["fish", "dish"]):
            # Yes: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            spam = my_module.things.WordSpam()
            assert spam.get_words(0) == ["fish", "dish"]

    def tearDown(self):
        pass


def test_spam_app_get_words_03():
    """
    A good option (because it doesn't use magical syntax)...
    use a 'with patch.object()' context manager to patch 'random.choices()'
    inside 'my_module/things.py' and then 'import foo'.  This works because
    we patch 'random.choices()' inside 'my_module/things.py' **before**
    'import foo'.

    'foo.py' uses 'random.choices()' when it calls
    'from my_module.things import '.
    """
    # Use a context manager to patch `random.choices()` in `my_module/things.py`
    # 'foo.py' -> 'my_module.things.WordSpam()' -> my_module.things.random.choices()
    with patch.object(my_module.things.random, "choices", return_value=["fish", "dish"]):
        # Mock the return value of 'random.choices()' in 'my_module.things'
        #    behind the scenes, 'patch()' creates a unittest.MagicMock() instance

        # Import ../foo.py after patching 'my_module.things.random.choices()'
        import foo
        # 'spam' is an instance of 'my_module.things.WordSpam()' in foo.py.
        # We are testing ().get_words() inside 'foo.py'...
        assert foo.spam.get_words(2) == ["fish", "dish"]
        # 'del foo' offers MAXIMUM test assert isolation...
        del foo


@patch("my_module.things.random.choices")
# Patch `random.choices()` in `my_module/things.py`... this
# `@patch()` statement adds a virtual parameter called
# `mock_choices`.
#
# This behavior is a bit magical and I'm not fond of the technique...
# I prefer `patch()` as a context-manager (see above).
def test_spam_app_get_words_04(mock_choices):
    # A virtual parameter      ^^^^^^^^^^^^
    #
    # @patch('my_module.things.random.choices') inserts a virtual
    # parameter above (which I call 'mock_choices')
    """
    Another good option... patch 'random.choices()' inside 'my_module/things.py'
    and then 'import foo'.  This works because we patch 'random.choices()'
    inside 'my_module/things.py' **before** 'import foo'.

    'foo.py' uses 'random.choices()' when it calls
    'from my_module.things import '.
    """
    # here we mock 'my_module.things.random.choices()'...
    mock_choices.return_value = ["fish", "dish"]

    # Import ../foo.py after patching 'my_module.things.random.choices()'
    import foo
    # 'spam' is an instance of 'my_module.things.WordSpam()' in foo.py.
    # We are testing ().get_words() inside 'foo.py'...
    assert foo.spam.get_words() == ["fish", "dish"]
    # 'del foo' offers MAXIMUM test assert isolation...
    del foo


def test_spam_app_get_words_05():
    """
    Ick... this is gross.  Why?  Because we are barely testing anything in
    '().get_words()'.  All we did is patch() '().get_words()'
    to return a certain value.
    """
    # Normally ().get_words() returns **random words**, but we want to
    # force it to return a predictable word list() so usage is testable...
    #
    # 'foo.py' -> 'my_module.things.WordSpam()' -> my_module.things.random.choices()
    with patch("my_module.things.WordSpam.get_words", return_value=["fish", "dish"]):
        # Ick  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        spam = WordSpam()
        assert spam.get_words(0) == ["fish", "dish"]


def test_spam_app_get_words_06_antipattern():
    """
    Ick... Avoid patching the python stdlib directly; in this antipattern, we
    patch stdlib 'random.choices()'.  It's better to patch it locally in your own
    module (for the best option, refer to 'test_spam_app_get_words_01()' above...

    Globally patching 'random.choices()' is considered a patch antipattern, because 
    it patches python stdlib 'random.choices()' everywhere.
    """
    # Try NOT to directly path python stdlib... you have no test case
    # isolation when patching python stdlib directly...
    #
    #
    # Use a context manager to patch `random.choices()` globally.
    # 'foo.py' -> 'my_module.things.WordSpam()' -> my_module.things.random.choices()
    with patch("random.choices") as mock_random_choices:
        # No   ^^^^^^^^^^^^^^^^ <- avoid directly patching python stdlib!
        mock_random_choices.return_value = ["fish", "dish"]
        spam = WordSpam()
        assert spam.get_words(0) == ["fish", "dish"]


@patch("my_module.things.random.choices", return_value=["fish", "dish"])
# Yes: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
class GoodTestRandomChoices_02(TestCase):
    """
    Good example.  Why?  Because the `@patch()` class wrapper is patching
    `random.choices()` in `my_module/things.py`.  This patches in the best
    way... it changes 'my_module.things.random.choices()' (which is used by
    '().get_words()') to return fixed (i.e. non-random) value.

    Refer to the '@patch()' wrapper above to see where the patch is applied.
    """

    def setUp(self):
        pass

    def test_spam_app_get_words_07(self, *args, **kwargs):
        spam = WordSpam()
        assert spam.get_words(0) == ["fish", "dish"]

    def tearDown(self):
        pass


@patch("my_module.things.random.choices", return_value=["fish", "dish"])
# Yes: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
class GoodTestRandomChoices_03(TestCase):
    """
    Good example.  Why?  Because the `@patch()` class wrapper is patching
    `random.choices()` in `my_module/things.py`.  This patches in the best
    way... it changes 'my_module.things.random.choices()' (which is used by
    '().get_words()') to return fixed (i.e. non-random) value.

    Refer to the '@patch()' wrapper above to see where the patch is applied.
    """

    def setUp(self):
        pass

    def test_spam_app_get_words_08(self, *args, **kwargs):
        """Test '().get_words()' directly in ../foo.py"""
        # Import ../foo.py after patching 'my_module.things.random.choices()'
        import foo
        # 'spam' is an instance of 'my_module.things.WordSpam()' in foo.py.
        # We are testing ().get_words() inside '../foo.py'...
        assert foo.spam.get_words() == ["fish", "dish"]
        # 'del foo' offers MAXIMUM test assert isolation...
        del foo

    def tearDown(self):
        pass

@patch("my_module.things.WordSpam.get_words", return_value=["fish", "dish"])
# Ick: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
class IckyTest_01(TestCase):
    """
    Ick... this is gross.  Why?  Because we are barely testing anything in
    '().get_words()'.  All we did is mock `().get_words()`
    to return a certain value.

    The `GoodTestRandomChoices_01()` and `GoodTestRandomChoices_02()` class
    above patches in the best way... it changes
    `my_module.things.random.choices()` to return fixed (i.e. non-random)
    values.

    This class also returns fixed values, but it does so by testing much
    less code in '()'.
    """

    def setUp(self):
        pass

    def test_spam_app_get_words_09(self, *args, **kwargs):
        """Test '().get_words()' (i.e. not in '../foo.py')"""
        spam = WordSpam()
        assert spam.get_words(0) == ["fish", "dish"]

    def tearDown(self):
        pass
