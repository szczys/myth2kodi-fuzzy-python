from MythTV import MythDB
from MythTV import MythBE

import sys
import os
from shutil import copyfile
from fuzzy_logger import logging
from mythPythonServices import *

#This will move files that can't be automatically categorized to
#the showings directory, retaining as much useful info as possible
#
#This is intended to be run manually as a user job from mythweb

#Where to move the files:
storageDir = "/Lenny/videoLibrary/Showings/"

def main():
    recordingDir = sys.argv[1]
    recordingFile = sys.argv[2]
    logging.info("======================")
    logging.info("Attempting to move to showings: %s", recordingFile)

    targetProgram = getProgramFromFilename(recordingFile)

    newFilename = "%s-%s-%s-%s___%s.ts" % (targetProgram.title,
                                           targetProgram.myth_dict['ProgramId'],
                                           targetProgram.myth_dict['SubTitle'],
                                           targetProgram.airdate,
                                           targetProgram.myth_dict['StartTime'].replace(' ','_'))
 
    if os.path.isdir(storageDir) == False:
        logging.info("storageDir doesn't exist, aborting: %s", storageDir)
        sys.exit(1)
    fileSource = os.path.join(recordingDir,recordingFile)
    fileDestination = os.path.join(storageDir,newFilename)
    if os.path.exists(fileSource) == False:
        logging.error("ERROR: aborting, source file doesn't exist: %s", fileSource)
        sys.exit(1)
    if os.path.exists(fileDestination):
        logging.error("ERROR: aborting, file already exists at: %s", fileDestination)
        sys.exit(1)
    logging.info("Copying file: %s to: %s", fileSource, fileDestination)
    copyfile(fileSource,fileDestination)
    os.chmod(fileDestination,0o777)
    logging.info("File copied successfully")
    logging.info("Deleting %s",recordingFile)
    deleteProgram(targetProgram.myth_dict)
    logging.info("Operation complete. Exiting.")
    sys.exit(0)

if __name__ == '__main__':
        main()
