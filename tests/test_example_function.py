"""Test the example function
"""

import pytest


@pytest.mark.example
def test_example_function(some_val):
    from lib import example_function

    some_str = example_function(some_val)

    assert isinstance(some_str, str)
    assert some_str == "The value was {} and is now in a string.".format(some_val)

    bad_val = 5
    some_str = example_function(bad_val)

    assert some_str is None
