from __future__ import absolute_import, print_function, unicode_literals
import unittest
from fabric.api import *
from fabric.contrib.console import confirm


class MyTests(unittest.TestCase):
        # pylint: disable=R0904

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_example(self):
        pass

env.hosts = ['bruno']
code_dir=/home/paulm/code/rt_scripts
def git_status():
    with cd(code_dir):
        result = run("git status")

if __name__ == "__main__":
        unittest.main()

