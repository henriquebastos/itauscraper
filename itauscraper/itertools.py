"""Itertools recipies from Python documentation."""


def grouper(iterable, size=2):
    """
    Collect data into fixed-length chunks or blocks.
    grouper('ABCDEFGHI', 3) --> ABC DEF GHI
    """
    return zip(*[iter(iterable)] * size)
