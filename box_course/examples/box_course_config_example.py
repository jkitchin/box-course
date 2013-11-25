import os

# This is the url for getting your tokens from
AUTH_URL = 'https://gilgamesh.cheme.cmu.edu/cgi-bin/jkitchin-box'

# file where authorization tokens are stored
BOX_TOKEN = os.path.expanduser('~/Dropbox/token.json')

# Name of course
COURSE = '06-625'

# Root directory where local files are stored
LOCAL_COURSE_ROOT = 'C:/Users/jkitchin/Documents/My Box Files/' + COURSE
LOCAL_ASSESSMENT_ROOT = LOCAL_COURSE_ROOT + '/assessments'
LOCAL_PROBLEMS = LOCAL_COURSE_ROOT + '/problems'

# root directory for course on box
BOX_COURSE_ROOT = '/' + COURSE
BOX_ASSESSMENT_ROOT = BOX_COURSE_ROOT + '/assessments'


# Course roster, in format from fio
ROSTER = LOCAL_COURSE_ROOT + '/gradebook/roster-11-9-2013.dat'

EXTRA_ROSTER = [('F13', 'johnrkitchin@gmail.com', 'Kitchin', 'John')]

# make a list of TA email addresses
# TAS = ['jboes@andrew.cmu.edu']

def get_andrewids():
    # we get andrewids from the roster file
    ANDREWIDS = []
    with open(ROSTER) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
        
            fields = line.split(',')
            andrewid = fields[1]
            ANDREWIDS.append(andrewid)

    ANDREWIDS.sort()
    return ANDREWIDS

ANDREWIDS = get_andrewids()

# These are categories for each assessment, and what weight of the
# overall category is.
# [(category, weight)]
CATEGORIES = [('homework', 0.6),
              ('exam1', 0.1),
              ('exam2', 0.075),
              ('quizzes', 0.075),
              ('exam3', 0.15)]

# Each assignment is a tuple of (name, points, category, duedate)
# duedate is a tuple of (year, month, day)
# duedate is used to figure out which grades to get at some time.
ASSIGNMENTS = [('hello-world', 5, 'homework', None),
               ('nla-1', 5, 'homework', None),
               ('ode-1', 5, 'homework', None),
               ('cstr-1', 8, 'homework', None),
               ('pfr-1', 8, 'homework', None),
               ('update-pycse-1', 5, 'homework', None),
               ('const-p-batch', 8, 'homework', None),         # 9/13/2013
               ('cstr-pfr-1', 8, 'homework', None),            # 9/16/2013
               ('batch-nonconst-density', 8, 'homework', None),
               ('membrane-pressure', 8, 'homework', None),     # 9/20/2013
               ('cstr-mult-steady-state', 8, 'homework', None),# 9/23/2013
               ('cstr-mult-reactions-1', 8, 'homework', None), # 9/25/2013
               ('equil-1', 6, 'homework', None),               # 9/27/2013
               ('nist-dg-1', 8, 'homework', None),             # 9/30/2013
               ('nist-dg-2', 8, 'homework', None),             # 10/2/2013
               ('equil-2', 6, 'homework', None),               # 10/4/2013
               ('exam-1', 100, 'exam1', None),
               ('data-analysis-1', 4, 'homework', None),       # 10/14/2013
               ('data-analysis-3', 6, 'homework', None),       # 10/16/2013
               ('profit-pfr', 8, 'homework', None),            # 10/18/2013
               ('exam2-shomate', 15, 'exam2', None),
               ('exam2-gibbs', 15, 'exam2', None),
               ('exam2-uncert-eq', 25, 'exam2', None),
               ('exam2-mechanism', 25, 'exam2', None),
               ('exam2-gas', 20, 'exam2', None),
               ('eb-pfr-cstr', 10, 'homework', None),          #11/5/2013
               ('eb-inerts', 8, 'homework', None),             #11/7/2013
               ('eb-rev-pdrop', 8, 'homework', None),          #11/12/2013
               ('eb-cstr-exitT', 8, 'homework', None),         #11/14/2013
               ('exam3', 100, 'exam3', None),
               ]
