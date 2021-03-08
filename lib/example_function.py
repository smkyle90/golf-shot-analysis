"""An example function"""


def example_function(some_val):
    """This is an example function.

    Args:
        some_val (float): some value you want to do something with.

    Returns:
        some_str (str): a string you want to do something with.
    """

    if isinstance(some_val, float):
        return "The value was {} and is now in a string.".format(some_val)
    else:
        return None
