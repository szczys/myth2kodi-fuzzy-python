from __future__ import absolute_import, division, print_function, unicode_literals

#pip install tvdb_api
#pip install fuzzywuzzy

import tvdb_api
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import logging
import sys
from operator import itemgetter


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
    found = list()
    seasons = sorted(show.keys(),reverse=True)
    for season in seasons:
        for ep in show[season].keys():
            ratio = fuzz.partial_ratio(show[season][ep]['episodeName'],subtitle.decode("utf-8"))
            #print(ratio)
            if ratio > minRatio:
                found.append((season,ep,ratio))
                #print(found[-1])
    if len(found) == 0:
        return None
    else:
        topIdx = max(enumerate(map(itemgetter(-1), found)),key=itemgetter(1))[0]
        return found[topIdx]
        

def getShow(showTitle):
    t = tvdb_api.Tvdb(apikey=myth2kodiFuzzyPython_apikey)
    try:
        show = t[showTitle]
        return show
    except Exception as e:
        logging.exception("API Error: %s",type(e).__name__)
        return None    

def findEpisodeFilename(showTitle,epTitle,fuzzyRatio=85):
    #Get DB info
    show = getShow(showTitle)

    filenamePreamble = showTitle.replace(' ','_')

    logging.info("Trying exact match...")
    exactEpisode = exactMatch(testTitle,epTitle,show)
    if exactEpisode != None:
        logging.info("Exact match! Season: %d Episode: %d", showdata[0], showdata[1])
        return filenamePreamble + "-S" + str(showdata[0]) + "E" + str(showdata[1])
    
    logging.info("No exact match found. Trying fuzzy match...")
    fuzzyEpisode = fuzzyMatch(testTitle,epTitle,show,fuzzyRatio)
    if showdata != None:
        logging.info("Fuzzy match ratio: %d Season: %d Episode: %d", showdata[2], showdata[0], showdata[1])
        return filenamePreamble + "-S" + str(showdata[0]) + "E" + str(showdata[1])

    logging.info("No subtitle match could be found. Exiting.")
    return 0
            
def main():
    """Will return a tvshow name with season and episode number, or 0 if none is found
    errors will return an exit code of 1. Errors are logged to myth2kodiFuzzyPython.log

    Parameters: "Show Name" "Episode Description"
    Optional third parameter is a ratio from 0-100 on how close a fuzzy match will be:
    "Show Name" "Episode Description" 85
    """

    epName = sys.argv[2].decode('utf-8')
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
        print(findEpisodeFilename(sys.argv[1], epName, ratio))
        sys.exit(0)
    if len(sys.argv) == 0:
        print(findEpisodeFilename(sys.argv[1], epName))
        sys.exit(0)
    sys.exit(1)

if __name__ == '__main__':
        main()
