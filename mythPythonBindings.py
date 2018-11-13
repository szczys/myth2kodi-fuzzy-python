from MythTV import MythDB
from MythTV import MythBE

mythConfig = '/home/mythtv/.mythtv/config.xml'
#mythConfig = '/home/mike/mythtv.xml'

import xml.etree.ElementTree as ET

def deleteProgram(basename):
    tree = ET.parse(mythConfig)
    root = tree.getroot()

    db1 = MythDB(args=(('DBHostName',root.find('Database').find('Host').text),
                       ('DBName',root.find('Database').find('DatabaseName').text),
                       ('DBUserName',root.find('Database').find('UserName').text),
                       ('DBPassword',root.find('Database').find('Password').text)))

    be1 = MythBE(db=db1)

    showInfoGen = db1.searchRecorded(basename=basename)
    showInfo = next(showInfoGen)
    showObject = be1.getRecording(showInfo['chanid'],showInfo['starttime'])

    deletedShow = be1.deleteRecording(showObject,force=True) #Return -1 means success


