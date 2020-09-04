from bs4 import BeautifulSoup
from fuzzy_logger import logging
import requests
import string
import datetime
#pip3 install python-Levenshtein
#pip3 install fuzzywuzzy
from fuzzywuzzy import fuzz
from operator import itemgetter
from mythPythonBindings import getProgramObjectFromFilename, getDbObject, getBeObject, deleteProgram

showUrlPrefix = 'https://thetvdb.com/series/'
showUrlSuffix = '/allseasons/official'

def identifyMythtvEpisode(recordingFilename,fuzzyRatio=85):
    logging.info("Getting program info from mythtv using filename: %s", recordingFilename)
    targetProgram = getProgramObjectFromFilename(recordingFilename, getDbObject(), getBeObject())

    #Get DB info
    logging.info("Loading show info from tvdb: %s", targetProgram['title'])
    show = getShow(targetProgram['title'])

    filenamePreamble = show.title.replace(' ','_')

    logging.info("Trying exact match...")
    exactEpisode = exactMatch(show,targetProgram['subtitle'])
    if exactEpisode != None:
        logging.info("Exact match! %s", exactEpisode.epNum)
        exactEpisode.filename = filenamePreamble + '-' + fuzzyEpisode.epNum
        exactEpisode.seriestitle = show.title
        return exactEpisode
    logging.info("No exact match found.")

##    if (recordingFilename != None):
##        logging.info("Trying fuzzy match based on air date...")
##        fuzzyDate = airdateFuzzyMatch(recordingFilename,min(70,fuzzyRatio))
##        if fuzzyDate != None:
##            logging.info("Fuzzy matched with air date! Season: %d Episode: %d", fuzzyDate[0], fuzzyDate[1])
##            return filenamePreamble + "-S" + str(fuzzyDate[0]) + "E" + str(fuzzyDate[1])
##    logging.info("No fuzzy match based on air date.")

    logging.info("Trying fuzzy match of episode name.")
    fuzzyEpisode = fuzzyMatch(show,targetProgram['subtitle'],fuzzyRatio,targetProgram['airdate'])
    if fuzzyEpisode != None:
        logging.info("Fuzzyr match ratio: %s", fuzzyEpisode.epNum)
        fuzzyEpisode.filename = filenamePreamble + '-' + fuzzyEpisode.epNum
        fuzzyEpisode.seriestitle = show.title
        return fuzzyEpisode

    logging.info("No episode match could be found. Exiting.")
    return 0

def deleteMythRecording(basename):
    deleteProgram(basename)

def exactMatch(show, subtitle):
    for ep in reversed(show.episodes):
        if ep.episodeName == subtitle:
            return(ep)
    return None

def searchByDate(show,airdateObj):
    """
    Search theTvDb data structure for original air date
    Return list of episode objects if found, empty if not
    """
    foundEpisodes = list()
    
    for ep in show.episodes:
        try:
            tvdbAirdate = datetime.datetime.strptime(ep.airdate, '%B %d, %Y').date()
        except:
            #Skip this one. Good enough is good enough
            continue
            
        if tvdbAirdate == airdateObj:
            logging.info("Found: %s", ep.epNum)
            foundEpisodes.append(ep)        
    return foundEpisodes

def fuzzyScore(string1, string2):
    return fuzz.token_set_ratio(string1,string2)

def fuzzyMatch(show,subtitle,minRatio,airdateObj=None):
    found = list()
    bestRatio = 0
    for ep in show.episodes:
        ratio = fuzzyScore(ep.episodeName,subtitle)
        if ratio > bestRatio:
            bestRatio = ratio
        if ratio > minRatio:
            found.append((ep,ratio))
    if len(found) == 0:
        logging.info("fuzzyMatch found a ratio of %d, but that's below the minimum of %d.",bestRatio,minRatio)
        return None
    else:
        topIdxRatio = max(enumerate(map(itemgetter(-1), found)),key=itemgetter(1))
        sameScore = list()
        for result in found:
            if result[-1] == topIdxRatio[1]:
                sameScore.append(result)
        if len(sameScore) == 1:
            return sameScore[0][0]
        else:
            logging.info("Multiple matches with ratio of %d found!",topIdxRatio[1])
            logging.info("Source information: %s :: %s", show.title, subtitle)
            for scored in sameScore:
                logging.info("Matches with %s :: %s", scored[0].epNum, scored[0].episodeName)
            if isinstance(airdateObj, datetime.date):
                logging.info("Attempting to narrow by airdate: %s",airdateObj)
                airdateHits = searchByDate(show,airdateObj)
                dateFiltered = list()
                if len(airdateHits) != 0:
                    for ep in airdateHits:
                        for s in sameScore:
                            if s[0].epNum == ep.epNum:
                                dateFiltered.append(ep)
                    if len(dateFiltered) == 1:
                        logging.info("Success, episode identified by fuzzy match and airdate: %s", dateFiltered[0].epNum)
                        return dateFiltered[0]
                    else:
                        logging.info("Couldn't narrow results based on airdate")
            logging.info("Fuzzy match failed, this needs to be sorted out manually")
            return None

def getShow(showTitle):  
    html = getHtmlByTitle(showTitle)
    if html == None:
        logging.info("Cannot get show, not html returned from tvdb")
        return None
    
    soup = BeautifulSoup(html, 'lxml')
    
    showTitle = soup.find('div',{'class','crumbs'}).findAll('a')[2].text.strip()
    
    allEpisodes=soup.findAll("li", {"class", "list-group-item"})
    episodeList = []

    for e in allEpisodes:
        thisEp = Episode()
        
        try:
            thisEp.epNum = e.find("span",{"class", "episode-label"}).text
            thisEp.episodeName = e.find("a").text.strip()
            thisEp.airdate = e.find('ul').find('li').text
            thisEp.description = e.find('p').text

            episodeList.append(thisEp)
        except:
            #If there is any trouble getting date we just skip that episode (good enough is good enough)
            continue
    return Show(showTitle, episodeList)

def getHtmlByTitle(showTitle):
    if str(showTitle) == "":
        return None

    #format title for URL:
    t = showTitle.translate(str.maketrans('', '', string.punctuation)) #Strip punctuation
    t = t.lower().replace(' ','-') #lowercase and replace spaces with dashes

    try:
        r = requests.get(showUrlPrefix + t + showUrlSuffix)
        if r.status_code != 200:
            logging.error("ERROR %d: Show title didn't map perfectly to a tvdb series page", r.status_code)
            return None
        else:
            return r.content
    except:
        return None
    
class Show:
    def __init__(self, title, episodes=[]):
        self.title = title
        self.episodes = episodes

    def getByEpisodeNumber(self, episodeNumber):
        for e in self.episodes:
            if e.epNum == episodeNumber:
                return e
        return None

class Episode:
    def __init__(self, epNum=None, episodeName=None, airdate=None, description=None):
        self.epNum = epNum
        self.episodeName = episodeName
        self.airdate = airdate
        self.descriptio = description
