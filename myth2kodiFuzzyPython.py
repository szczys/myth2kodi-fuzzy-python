from __future__ import absolute_import, division, print_function, unicode_literals

#pip install tvdb_api
#pip install fuzzywuzzy

import tvdb_api
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from fuzzy_logger import logging
import sys
from operator import itemgetter
from mythPythonBindings import getProgramObjectFromFilename, getDbObject, getBeObject


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

def searchByDate(showTitle,datestring):
    """
    Search theTvDb data structure for original air date
    Return show information object if found, None if not
    """
    thisShow = getShow(showTitle)
    foundShows = list()
    for season in thisShow.keys():
        for episode in thisShow[season].keys():
                if thisShow[season][episode]['firstAired'] == datestring:
                        logging.info("Found: %s",thisShow[season][episode]['episodeName'])
                        foundShows.append(thisShow[season][episode])
    return foundShows
			
    
def airdateFuzzyMatch(filename):
    """
    Compares airdate and fuzzy-matched title for identifying episodes
    
    When exactMatch doesn't work, this should be run before falling back to pure fuzzyMatch
    Consider 'Wheel of Fortune' -- episcodeNames will be "Weekly Theme 1", "Weekly Theme 2", etc.
    Trying to fuzzy match these will be difficult as only 1 character is different
    A better way is checking the airdate, and fuzzy matching to the title. Hits on both are adequate.
    """
    #Use MythTV Python Bindings to get show, episode, and airdate
    targetProgram = getProgramObjectFromFilename(filename, getDbObject(), getBeObject())
    if targetProgram == None:
        return None
    return targetProgram
    #Get thetvdb.com data structure for complete series
    showTitle = targetProgram['title']
    show = getShow(showTitle)
    #tvdb: was there an episode on our target airdate?
    
    #tvdb: do we have a high confience fuzzy match with the episodeName on that airdate?
    #return season, ep, and ratio, otherwise return None as we only care about that airdate
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
        logging.info("Exact match! Season: %d Episode: %d", exactEpisode[0], exactEpisode[1])
        return filenamePreamble + "-S" + str(exactEpisode[0]) + "E" + str(exactEpisode[1])
    
    logging.info("No exact match found. Trying fuzzy match...")
    fuzzyEpisode = fuzzyMatch(testTitle,epTitle,show,fuzzyRatio)
    if fuzzyEpisode != None:
        logging.info("Fuzzy match ratio: %d Season: %d Episode: %d", fuzzyEpisode[2], fuzzyEpisode[0], fuzzyEpisode[1])
        return filenamePreamble + "-S" + str(fuzzyEpisode[0]) + "E" + str(fuzzyEpisode[1])

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
