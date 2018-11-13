from __future__ import print_function

#pip install tvdb_api
#pip install fuzzywuzzy

import tvdb_api
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import logging
import sys


logging.basicConfig(filename='myth2kodiFuzzyPython.log',format='%(asctime)s %(message)s',level=logging.INFO)

myth2kodiFuzzyPython_apikey ='0E2AC500-E296-4756-BE20-6B5D192622E6'

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
    t = tvdb_api.Tvdb(apikey=myth2kodiFuzzyPython_apikey)
    try:
        show = t[showTitle]
    except Exception as e:
        logging.exception("API Error: %s",type(e).__name__)
        return 0

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
    """Will return a tvshow name with season and episode number, or 0 if none is found
    errors will return an exit code of 1. Errors are logged to myth2kodiFuzzyPython.log

    Parameters: "Show Name" "Episode Description"
    Optional third parameter is a ratio from 0-100 on how close a fuzzy match will be:
    "Show Name" "Episode Description" 85
    """
    if len(sys.argv) < 3:
        logging.error("ERROR: Too few arguments. Expected at least 2, got %d",len(sys.argv)-1)
        sys.exit(1)
    if len(sys.argv) > 4:
        logging.error("ERROR: Too many arguments. Expected 2 or 3, got %d",len(sys.argv)-1)
        sys.exit(1)
    if len(sys.argv) == 4:
        try:
            ratio = int(sys.argv[3])
        except:
            logging.error("ERROR: Expected third argument to be a number but it was %s",sys.argv[3])
            sys.exit(1)
        print(findEpisodeData(sys.argv[1], sys.argv[2], ratio))
        sys.exit(0)
    if len(sys.argv) == 0:
        print(findEpisodeData(sys.argv[1], sys.argv[2]))
        sys.exit(0)
    sys.exit(1)

if __name__ == '__main__':
        main()
