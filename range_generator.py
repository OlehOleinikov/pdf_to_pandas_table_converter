PAGES_IN_PART = 20
"""
small value makes it slowly (multiple opening file for each iteration)
large - may result in out-of-memory error from java machine
the value is also approximate. Used to generate pages ranges for convertion
"""


def _get_parts_count(pages_in_part: int, pages_total_count: int) -> int:
    """Determines the acceptable number of parts (based on the preferred number of pages per part)"""
    return int(pages_total_count/pages_in_part)


def _split_range(common_range, parts_count):
    """
    :param common_range: range-type list of positions (all file size = all pages + 1)
    :param parts_count: number of parts to divide
    :return: list of ranges objects (divided parts of common range)
    """
    k, m = divmod(len(common_range), parts_count)
    return list(common_range[i * k + min(i, m): (i + 1) * k + min(i + 1, m)] for i in range(parts_count))


def next_range_generator(pages_total, pages_in_part=PAGES_IN_PART):
    """Generates parts (ranges) of pages for convertion

    :param pages_total: count of pages in file
    :param pages_in_part: preferred number of pages in one part
    """
    if pages_in_part > pages_total:  # to prevent zero parts count (min one part)
        pages_in_part = pages_total
    parts_count = _get_parts_count(pages_in_part, pages_total)
    list_of_ranges = _split_range(range(1, pages_total+1), parts_count)
    n = 0
    ranges_count = parts_count
    while n < ranges_count:
        yield list_of_ranges[n]
        n += 1
