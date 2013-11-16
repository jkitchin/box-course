from distutils.core import setup
import os
  
setup(name = 'box_course',
      version=0.1,
      description='python scripts to run a course using box.com',
      url='http://github.com/jkitchin/box-course',
      maintainer='John Kitchin',
      maintainer_email='jkitchin@andrew.cmu.edu',
      license='GPL',
      platforms=['linux'],
      packages=['box_course'],
      scripts=['box_course/box-course.py'],
      long_description='''\
A command-line utility to setup and run a course using box.com

automates setting up a course structure on box.com from a roster file and configuration file. Facilitates assigning problems, and performing gradebook activities.
      ''')

# to push to pypi - python setup.py sdist upload
