import sys
import time

def _docstring():
    """Dummy function to test the ``Google`` docstring.

    Yields:
        n (int): The upper limit of the range to generate, from 0 to `n` - 1.
        n (int): The upper limit of the range to generate, from 0 to `n` - 1.

    Yields:
        int: The next number in the range of 0 to `n` - 1.

    Examples:
        Examples should be written in doctest format, and should illustrate how
        to use the function.
        
        >>> print([i for i in example_generator(4)])
        [0, 1, 2, 3]
    """
    pass


def progressMeter():
    while True:
        for cursor in '|/-\\':
            yield cursor

spinner = progressMeter()


def taskProgress(task, percentDone):
    """
    """
    sys.stdout.write(spinner.__next__())
    sys.stdout.flush()
    time.sleep(0.8)
    sys.stdout.write('\b')