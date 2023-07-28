
import configparser
import sys
sys.path.insert(0, "../")

from my_module.things import WordSpam
import my_module.things

from unittest.mock import patch, MagicMock
from unittest import TestCase
import random


def test_config_ini_01():
    """
    test whether configparser from stdlib gets expected values.
    """
    conf_obj = configparser.ConfigParser()
    # read the ini configuration from a file named "test_config.ini"
    #conf_obj.read("./test_config.ini")

    # read the ini configuration string instead of reading from a file...
    conf_obj.read_string("""
    [global]
    username=mpenning
    ip_address=192.0.2.1

    [development]
    username=dpenning
    ip_address=192.0.2.2
    """)

    # Define expected results here...
    expected = {
        "global": {
            "username": "mpenning",
            "ip_address": "192.0.2.1",
        },
        "development": {
            "username": "dpenning",
            "ip_address": "192.0.2.2",
        },
    }

    uut = conf_obj
    assert uut["global"]["username"] == expected["global"]["username"]
    assert uut["global"]["ip_address"] == expected["global"]["ip_address"]
    assert uut["development"]["username"] == expected["development"]["username"]
    assert uut["development"]["ip_address"] == expected["development"]["ip_address"]

def test_spam_app_get_words_01():
    """
    The best option... patch 'random.choices()' inside
    'my_module/things.py' and then 'import foo as uut'.  This works because
    we patch 'random.choices()' inside 'my_module/things.py'
    **before** 'import foo'.

    'foo.py' uses 'random.choices()' when it calls
    'from my_module.things import random'.

    I like 'with patch()' as a context manager instead of an '@patch()'
    wrapper.  The 'with patch()' context manager has less magical
    syntax compared with an '@patch()' wrapper.
    """

    # import ../foo.py
    import foo as uut

    # Option 1, avoid creating an explicit MagicMock() ('patch()' creates the magicmock())
    # 'foo.py' -> 'my_module.things.wordspam()' -> my_module.things.random.choices()
    with patch(target="my_module.things.random.choices", return_value=["fish", "dish"]):

        # 'spam' is an instance of 'my_module.things.WordSpam()' in foo.py.
        # we are testing spam().get_words() inside 'foo.py'...
        assert uut.spam.get_words() == ["fish", "dish"]
        # 'del uut' (i.e. ../foo.py) offers maximum test assert isolation...
        del uut


    # import ../foo.py
    import foo as uut

    # Option 2, create an explicit MagicMock() called 'magic_mock_choices'
    # 'foo.py' -> 'my_module.things.wordspam()' -> my_module.things.random.choices()
    with patch(target="my_module.things.random.choices") as magic_mock_choices:

        # mock the return value of 'random.choices()' in 'my_module.things'
        magic_mock_choices.return_value = ["fish", "dish"]
        assert isinstance(magic_mock_choices, MagicMock)

        # 'spam' is an instance of 'my_module.things.wordspam()' in foo.py.
        # we are testing spam().get_words() inside 'foo.py'...
        assert uut.spam.get_words() == ["fish", "dish"]
        # 'del uut' (i.e. ../foo.py) offers maximum test assert isolation...
        del uut


class GoodTestRandomChoices_01(TestCase):

    def setUp(self):
        pass

    def test_spam_app_get_words_02(self, *args, **kwargs):
        # 'foo.py' -> 'my_module.things.WordSpam()' -> my_module.things.random.choices()
        with patch(target="my_module.things.random.choices", return_value=["fish", "dish"]):
            # Yes:        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            uut = my_module.things.WordSpam()
            assert uut.get_words(0) == ["fish", "dish"]

    def tearDown(self):
        pass


def test_spam_app_get_words_03():
    """
    A good option (because it doesn't use magical syntax)...
    use a 'with patch.object()' context manager to patch 'random.choices()'
    inside 'my_module/things.py' and then 'import foo'.

    'foo.py' uses 'random.choices()' when it calls
    'from my_module.things import '.
    """
    # Import ../foo.py
    import foo as uut

    # Use a context manager to patch `random.choices()` in `my_module/things.py`
    # 'foo.py' -> 'my_module.things.WordSpam()' -> my_module.things.random.choices()
    with patch.object(target=my_module.things.random, attribute="choices", return_value=["fish", "dish"]):
        # Mock the return value of 'random.choices()' in 'my_module.things'
        #    behind the scenes, 'patch()' creates a unittest.MagicMock() instance

        # 'spam' is an instance of 'my_module.things.WordSpam()' in foo.py.
        # We are testing ().get_words() inside 'foo.py'...
        assert uut.spam.get_words(2) == ["fish", "dish"]
        # 'del uut' (i.e. ../foo.py) offers maximum test assert isolation...
        del uut


@patch(target="my_module.things.random.choices")
# Patch `random.choices()` in `my_module/things.py`... this
# `@patch()` statement adds a magical virtual parameter called
# `mock_choices`.
def test_spam_app_get_words_04(mock_choices):
    # A virtual parameter      ^^^^^^^^^^^^
    #
    # @patch('my_module.things.random.choices') inserts a virtual
    # parameter above (which I call 'mock_choices')
    """
    Another good option... patch 'random.choices()' inside 'my_module/things.py'
    and then 'import foo'.

    'foo.py' uses 'random.choices()' when it calls
    'from my_module.things import '.
    """
    # here we mock 'my_module.things.random.choices()'...
    mock_choices.return_value = ["fish", "dish"]

    # Import ../foo.py after patching 'my_module.things.random.choices()'
    import foo as uut
    # 'spam' is an instance of 'my_module.things.WordSpam()' in foo.py.
    # We are testing ().get_words() inside 'foo.py'...
    assert uut.spam.get_words() == ["fish", "dish"]
    # 'del uut' (i.e. ../foo.py) offers maximum test assert isolation...
    del uut


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
    with patch(target="my_module.things.WordSpam.get_words", return_value=["fish", "dish"]):
        # Ick  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        uut = WordSpam()
        assert uut.get_words(0) == ["fish", "dish"]


def test_spam_app_get_words_06_antipattern():
    """
    Ick... Avoid patching the python stdlib directly; in this antipattern, we
    patch stdlib 'random.choices()'.  It's better to patch it locally in your own
    module (for the best option, refer to 'test_spam_app_get_words_01()' above...
    """
    # Try NOT to directly path python stdlib... you have no test case
    # isolation when patching python stdlib directly...
    #
    #
    # Use a context manager to patch `random.choices()` globally.
    # 'foo.py' -> 'my_module.things.WordSpam()' -> my_module.things.random.choices()
    with patch(target="random.choices") as mock_random_choices:
        # No   ^^^^^^^^^^^^^^^^ <- avoid directly patching python stdlib!
        mock_random_choices.return_value = ["fish", "dish"]
        uut = WordSpam()
        assert uut.get_words(0) == ["fish", "dish"]


@patch(target="my_module.things.random.choices", return_value=["fish", "dish"])
# Yes:        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
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
        uut = WordSpam()
        assert uut.get_words(0) == ["fish", "dish"]

    def tearDown(self):
        pass


@patch(target="my_module.things.random.choices", return_value=["fish", "dish"])
# Yes:        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
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
        """Test 'WordSpam().get_words()' directly in ../foo.py"""
        # Import ../foo.py after patching 'my_module.things.random.choices()'
        import foo as uut

        # 'spam' is an instance of 'my_module.things.WordSpam()' in foo.py.
        # We are testing ().get_words() inside '../foo.py'...
        assert uut.spam.get_words() == ["fish", "dish"]

        # 'del uut' (i.e. ../foo.py) offers maximum test assert isolation...
        del uut

    def tearDown(self):
        pass

@patch(target="my_module.things.WordSpam.get_words", return_value=["fish", "dish"])
# Ick:        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
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
        uut = WordSpam()
        assert uut.get_words(0) == ["fish", "dish"]

    def tearDown(self):
        pass
