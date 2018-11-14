"""
Simple logging file to include from other myth2kodi-fuzzy-python files
"""

import logging
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
logfile = os.path.join(dir_path,'myth2kodiFuzzyPython.log')
logging.basicConfig(filename=logfile,format='%(asctime)s %(message)s',level=logging.INFO)
