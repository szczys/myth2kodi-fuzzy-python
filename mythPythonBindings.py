from MythTV import MythDB
from MythTV import MythBE

from fuzzy_logger import logging
import os

mythConfig = '/home/mythtv/.mythtv/config.xml'
#mythConfig = '/home/mike/mythtv.xml'

import xml.etree.ElementTree as ET

def getCredentials(xmlfile):
    """
    Parse the XML file containing MythTV database login credentials
    This file is most commonly located at: /home/mythtv/.mythtv/config.xml
    """

    tree = ET.parse(mythConfig)
    root = tree.getroot()
    host = root.find('Database').find('Host').text
    dbname = root.find('Database').find('DatabaseName').text
    user = root.find('Database').find('UserName').text
    passwd = root.find('Database').find('Password').text
    return (host,dbname,user,passwd)

def getDbObject(credentials=getCredentials(mythConfig)):
    """
    Returns a MythTV database object (MythTV Python Bindings)
    Usage:
        myVar = getDbObject() #Use credentials located at mythConfig path

        myVar = getDbObject((hostname, databasename, username, password)) #Manually specify credentials
    """
    
    dbObj = MythDB(args=(('DBHostName',credentials[0]),
                       ('DBName',credentials[1]),
                       ('DBUserName',credentials[2]),
                       ('DBPassword',credentials[3])))
    return dbObj

def getBeObject(databaseObj=getDbObject()):
    return MythBE(db=databaseObj)

def getProgramObjectFromFilename(basename,dbObj,beObj):
    """
    Returns a MythTV program object (type is MythTV.mythproto.Program)
    Seem convoluted to have to search for it in this way... FIXME: better search?
    """
    basename = os.path.split(basename)[-1]
    showInfoGen = dbObj.searchRecorded(basename=basename)
    showInfo = next(showInfoGen,None)
    if showInfo == None:
        return None
    chanid = showInfo['chanid']
    starttime = showInfo['starttime']
    showObject = beObj.getRecording(chanid,starttime)
    return showObject
    
def deleteProgram(basename):
    """
    Delete the recording with filename==basename
    This deletes the physical file as well as the MythTV database entries
    """
    
    basename = os.path.split(basename)[-1]
    logging.info("Attempting to delete from mythtv: %s", basename)
    db1 = getDbObject()
    be1 = getBeObject(db1)

    showObject = getProgramObjectFromFilename(basename,db1,be1)
    if showObject == None:
        logging.info("Cannot delete show: Unable to get show object from mythtv: %s", basename)
        return

    logging.info("Deleting program: %s :: %s (filename %s)", showObject['title'], showObject['subtitle'], basename)
    deletedShow = be1.deleteRecording(showObject,force=True) #Return -1 means success
    if deletedShow == -1:
        logging.info("Successfully deleted program")
        


