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
    def __init__(self, epNum=None, title=None, episodeName=None, airdate=None, description=None, myth_dict=dict()):
        self.title = title
        self.epNum = epNum
        self.episodeName = episodeName
        self.airdate = airdate
        self.description = description
        self.myth_dict = myth_dict
        self.filename = None

    def __str__(self):
        return f'Number: {self.epNum} | Title: {self.episodeName} | Air Date: {self.airdate} | Description: {self.description}'

    def setFilename(self, series_title=None):
        """Sets seriestitle and filename. Depends on epNum already being set. Returns True if successful, False if not"""
        if series_title != None:
            self.title = series_title
        if self.title != None and self.epNum != None:
            self.filename = self.title.replace(' ','_') + '-' + self.epNum
            return True
        else:
            return False
