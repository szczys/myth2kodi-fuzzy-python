from mythPythonServices import getProgramFromFilename, deleteProgram
from myth2kodi_classes import Show, Episode

from bs4 import BeautifulSoup
from fuzzy_logger import logging
import requests
import string
import datetime

#pip3 install python-Levenshtein
#pip3 install fuzzywuzzy
from fuzzywuzzy import fuzz
from operator import itemgetter

showUrlPrefix = 'https://thetvdb.com/series/'
showUrlSuffix = '/allseasons/official'

def identifyMythtvEpisode(recordingFilename,fuzzyRatio=74) -> Episode | None:
    logging.info("Getting program info from mythtv using filename: %s", recordingFilename)

    targetProgram = getProgramFromFilename(recordingFilename)

    if targetProgram is None:
        logging.error(f"Mythtv cannot find program based on filename: {recordingFilename}")
        return None

    if targetProgram.epNum is not None:
        logging.info(f'Found: {targetProgram.myth_dict["Title"]} '
                     f'Season: {targetProgram.myth_dict["Season"]} '
                     f'Episode: {targetProgram.myth_dict["Episode"]} '
                     f'SubTitle: {targetProgram.myth_dict["SubTitle"]}'
                     )
        return targetProgram

    logging.info(f"Mythtv season/episode number not found for {targetProgram.title}, {targetProgram.episodeName}")

    #Get DB info
    logging.info("Loading show info from tvdb: %s", targetProgram.title)
    show = getShow(targetProgram.title)

    #Try exact expisode title match
    logging.info(f"Target episode name: {targetProgram.episodeName}")
    logging.info("Trying exact match...")
    exactEpisode = exactMatch(show, targetProgram.episodeName)
    if exactEpisode != None:
        logging.info("Exact match! %s", exactEpisode.epNum)
        filenameIsSet = exactEpisode.setFilename(show.title)
        if filenameIsSet:
            exactEpisode.myth_dict = targetProgram.myth_dict
            return exactEpisode
        else:
            logging.info("Error: failed to set filename from exact match data")
    logging.info("No exact match found.")

    logging.info("Trying fuzzy match of episode name.")
    fuzzyEpisode = fuzzyMatch(show,
                              targetProgram.episodeName,
                              fuzzyRatio,
                              targetProgram.airdate)
    if fuzzyEpisode != None:
        logging.info("Fuzzy match ratio: %s", fuzzyEpisode.epNum)
        filenameIsSet = fuzzyEpisode.setFilename(show.title)
        if filenameIsSet:
            fuzzyEpisode.myth_dict = targetProgram.myth_dict
            return fuzzyEpisode
        else:
            logging.info("Error: failed to set filename from fuzzy match data")

    logging.info("No episode match could be found. Exiting.")
    return None

def deleteMythRecording(basename):
    deleteProgram(basename)

def exactMatch(show, subtitle):
    for ep in reversed(show.episodes):
        if ep.episodeName == subtitle:
            return ep
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
    return fuzz.token_sort_ratio(string1,string2)

def fuzzyMatch(show, subtitle, minRatio, airdateObj=None):
    found = list()
    bestRatio = 0
    bestEp = None
    for ep in show.episodes:
        ratio = fuzzyScore(ep.episodeName,subtitle)
        if ratio > bestRatio:
            bestRatio = ratio
            bestEp = ep
        if ratio > minRatio:
            found.append((ep,ratio))

    if len(found) == 0:
        logging.info(f"fuzzyMatch found a ratio of {bestRatio}, but that's below the minimum of {minRatio}.")
        if bestEp is not None:
            logging.info(f"Closet match was: {bestRatio} :: {bestEp.episodeName}")
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
            thisEp.title = showTitle
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
