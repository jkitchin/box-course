__version__ = '0.1'

import os

# load the config file, looking recursively up
dir, last = os.getcwd(), True
cfile = os.path.join(dir, 'box_course_config.py')

if os.path.exists(cfile):
    execfile(cfile)
else:

    while last:  #the last dir is empty at the root of the file system
        dir, last = os.path.split(dir)
        cfile = os.path.join(dir, 'box_course_config.py')
        if os.path.exists(cfile):
            execfile(cfile)
            break


