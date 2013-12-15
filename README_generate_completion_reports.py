Dependencies
Python2.7
Python Requests
python-rt https://gitlab.labs.nic.cz/labs/python-rt
(should have a local copy installed on tsbackup, unntested with newer versions)
jsondb
request_tracker 
these last two are in the freegeek github repostitory

configure EMAIL, WEEKLYDB, MONTHLYDB on installed copy

use in cronjob with -m flag set 

there is an (untested) fabfile.cfg that can be used with fabfile.py to eas inastall

requires python-fabric
