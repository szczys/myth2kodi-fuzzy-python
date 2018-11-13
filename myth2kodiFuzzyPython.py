from __future__ import print_function

#pip install tvdb_api
#pip install fuzzywuzzy

import tvdb_api
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import logging

logging.basicConfig(filename='example.log',level=logging.INFO)

#Test Values
testTitle = 'Late Night with Seth Meyers'
testSubtitle = "Claire Foy Lucas Hedges boygenius Franklin Vanderbilt"

def exactMatch(title,subtitle,show):
    seasons = sorted(show.keys(),reverse=True)
    for season in seasons:
        for ep in show[season].keys():
            if show[season][ep]['episodeName'] == subtitle:
                return(season,ep)
    return None

def fuzzyMatch(title,subtitle,show,minRatio):
    seasons = sorted(show.keys(),reverse=True)
    for season in seasons:
        for ep in show[season].keys():
            ratio = fuzz.ratio(show[season][ep]['episodeName'],subtitle)
            if ratio > 85:
                return(season,ep,ratio)
    return None

def findEpisodeData(showTitle,epTitle,fuzzyRatio=95):
    #Get DB info
    t = tvdb_api.Tvdb()
    show = t[showTitle]

    filenamePreamble = showTitle.replace(' ','_')

    logging.info("Trying exact match...")
    showdata = exactMatch(testTitle,testSubtitle,show)
    if showdata == None:
        logging.info("No exact match found. Trying fuzzy match...")
        showdata = fuzzyMatch(testTitle,testSubtitle,show,fuzzyRatio)
        if showdata == None:
            logging.info("No subtitle match could be found. Exiting.")
            return 0
        else:
            logging.info("Fuzzy match ratio: %d Season: %d Episode: %d", showdata[2], showdata[0], showdata[1])
            return filenamePreamble + "-S" + str(showdata[0]) + "E" + str(showdata[1])
    else:
        logging.info("Exact match! Season: %d Episode: %d", showdata[0], showdata[1])
        return filenamePreamble + "-S" + str(showdata[0]) + "E" + str(showdata[1])
            
def main():
    return findEpisodeData(testTitle,testSubtitle)
