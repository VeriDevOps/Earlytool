import uuid
from collections import UserDict
from statistics import mean, pstdev
from itertools import islice, zip_longest


class DequeDict(UserDict):

    def __init__(self, *args, **kwargs):
        self.maxlen = kwargs.pop("maxlen", 0)
        super().__init__(*args, **kwargs)

    def put(self, key, value):
        try:
            self.data.pop(key)
        except KeyError:
            # We didn't find that flow
            # If the Queue is full, we remove an item in LIFO order
            if 0 < self.maxlen <= len(self.data):
                self.data.pop(list(self.data)[0])
        finally:
            # Move the flow to the top
            self.data[key] = value


def grouper(iterable, n, max_groups=0, fillvalue=None):
    """Collect data into fixed-length chunks or blocks"""

    if max_groups > 0:
        iterable = islice(iterable, max_groups * n)

    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def random_string():
    return uuid.uuid4().hex[:6].upper().replace("0", "X").replace("O", "Y")


def get_statistics(alist: list):
    """Get summary statistics of a list"""
    iat = dict()
    if len(alist) > 1:
        iat["total"] = sum(alist)
        iat["max"] = max(alist)
        iat["min"] = min(alist)
        iat["mean"] = mean(alist)
        iat["std"] = pstdev(alist)
    else:
        iat["total"] = 0
        iat["max"] = 0
        iat["min"] = 0
        iat["mean"] = 0
        iat["std"] = 0
    return iat
