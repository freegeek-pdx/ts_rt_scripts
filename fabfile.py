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

# DO WE NEED THIS?
env.hosts = ['bruno']

code_dir=/home/paulm/code/rt_scripts
repository='rtscripts'

def git_status():
    with cd(code_dir):
        result = run("git status -z", capture=True)
        if len(result) != 0:
            abort('Aborting...uncommitted changes or files. Please commit any changes to git')
            return False
        else
            return True

def git_push(repo=repository):
    with cd(code_dir):
        result = run("git push " + repo)
        if result.failed:
            abort('Aborting...unable to push to repository: ' + repo)
            return False
        else
            return True

def copy_file_to_server(destfile='ticket_check'):
    # TODO scp file to server
    # specifying defalut server, server ob command line

def deploy:
    git_status()
    git_push()



if __name__ == "__main__":
        unittest.main()

