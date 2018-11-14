from MythTV import MythDB
from MythTV import MythBE

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
    
def deleteProgram(basename):
    """
    Delete the recording with filename==basename
    This deletes the physical file as well as the MythTV database entries
    """

    db1 = getDbObject
    be1 = MythBE(db=db1)

    showInfoGen = db1.searchRecorded(basename=basename)
    showInfo = next(showInfoGen)
    showObject = be1.getRecording(y['chanid'],y['starttime'])

    deletedShow = be1.deleteRecording(z,force=True) #Return -1 means success


