from unittest.mock import patch, MagicMock
from unittest import mock, TestCase
import random
import sys

sys.path.insert(0, "../")

# Even though we only import WordSpam(), python can access 'my_module.things'
# because of the way that Python handles namespaces...
from my_module.things import WordSpam
# This 'import my_module.things' import should not be skipped... it's required
# for the 'with patch.object()' call below...
import my_module.things

def test_foo_spam_get_words_01():
    """
    The very BEST option which has the least amount of magic syntax...
    use a @patch.object() context manager to patch 'random.choices()' inside
    'my_module/things.py' and then 'import foo'.  This works because
    we patch 'random.choices()' inside 'my_module/things.py' **before**
    'import foo'.

    'foo.py' uses 'random.choices()' when it calls
    'from my_module.things import WordSpam'.
    """
    # patch.object() 'my_module.things.random.choices()' in a context manager
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

def test_foo_spam_get_words_02():
    """
    The BETTER option... patch 'random.choices()' inside 'my_module.things'

    This is not as good as 'test_foo_spam_get_words_01()' above because this is
    not testing anything in '../foo.py'.
    """
    ## Yes
    with patch("my_module.things.random.choices") as mock_choices:
        # Yes  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ <- A) Do THIS!!!
        # Mock the return value of 'random.choices()' in 'my_module.things'
        mock_choices.return_value = ["fish", "dish"]

        spam = WordSpam()
        assert spam.get_words(0) == ["fish", "dish"]

@patch("my_module.things.random.choices")
def test_foo_spam_get_words_03(mock_choices):
    # A virtual parameter      ^^^^^^^^^^^^
    #
    # @patch('my_module.things.random.choices') inserts a virtual
    # parameter above (which I call 'mock_choices') in
    # 'test_foo_spam_get_words()'.
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
    # force it to return a predictable word list() so usage is predictable...
    with patch("my_module.things.WordSpam.get_words", return_value=["fish", "dish"]):
        # Ick  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        spam = WordSpam()
        assert spam.get_words(0) == ["fish", "dish"]


def test_wordspam_05_antipattern():
    """
    Always avoid patching the python stdlib directly; in this case, do NOT
    patch stdlib 'random.choices()'.  Patch it locally in your own module
    (for the best option, refer to 'test_foo_spam_get_words_01()' above...

    Globally patching 'random.choices()' is considered an patch / mock
    antipattern, because it globally patches python stdlib 'random.choices()'.
    Always try to patch as close to the user method as possible.
    """
    ## Try NOT to directly path python stdlib... you have no test case
    ## isolation when patching python stdlib directly...
    with patch("random.choices") as mock_random_choices:
        # No   ^^^^^^^^^^^^^^^^ <- avoid this!!
        mock_random_choices.return_value = ["fish", "dish"]
        spam = WordSpam()
        assert spam.get_words(0) == ["fish", "dish"]


@patch("my_module.things.random.choices", return_value=["fish", "dish"])
# Yes: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
class TestRandomChoices(TestCase):

    def setUp(self):
        pass

    def test_wordspam_01(self, *args, **kwargs):
        """Test 'WordSpam().get_words()' directly in ../foo.py"""
        # Import ../foo.py after patching 'my_module.things.random.choices()'
        import foo
        # 'spam' is an instance of 'my_module.things.WordSpam()' in foo.py.
        # We are testing WordSpam().get_words() inside 'foo.py'...
        assert foo.spam.get_words() == ["fish", "dish"]
        # 'del foo' offers MAXIMUM test assert isolation...
        del foo

    def tearDown(self):
        pass

@patch("my_module.things.WordSpam.get_words", return_value=["fish", "dish"])
# Ick: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
class TestWordSpamAntipattern(TestCase):

    def setUp(self):
        pass

    def test_wordspam_01(self, *args, **kwargs):
        """Test 'WordSpam().get_words()' directly (i.e. not in '../foo.py')"""
        spam = WordSpam()
        assert spam.get_words(0) == ["fish", "dish"]

    def tearDown(self):
        pass
