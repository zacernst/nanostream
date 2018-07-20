"""
Classes that can be instantiated in a ``NanoStreamGraph`` to
read and write files.
"""

import random
import hashlib
from nanostream_processor import *

class FileReader(NanoStreamProcessor):
    """
    Reads a file and passes its contents down the pipeline.
    """

    def process_item(self, item):
        """
        Reads a file into memory.

        Args:
            item (str): Filename
        """

        with open(item, 'r') as nano_file:
            contents = nano_file.read()
        return contents


def random_hash(seed=None):
    """
    Returns a random hash; usually for naming files uniquely.
    """

    return hashlib.md5(seed or str(random.random())).hexdigest()


class FileWriter(NanoStreamProcessor):
    """
    Writes the message to a file with a random name in a specified
    directory.
    """

    def __init__(self, path=None):
        """
        Initializer.

        Args:
            path (str): Directory path for the file.
        """

        self.path = path or '.'
        super(FileWriter, self).__init__()

    def process_item(self, item):
        """
        Writes the file to the ``self.path`` directory, with a random
        filename generated by the ``random_hash`` function.
        """
        with open('/'.join([self.path, random_hash()]), 'w') as nano_file:
            print('file writer: ', item)
            nano_file.write(item)
        return item
