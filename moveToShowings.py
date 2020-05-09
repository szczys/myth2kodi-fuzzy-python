from MythTV import MythDB
from MythTV import MythBE

import sys
from shutil import copyfile
from fuzzy_logger import logging
from mythPythonBindings import *

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

    episodeObj = getProgramObjectFromFilename(recordingFile,getDbObject(), getBeObject())
    newFilename = "%s-%s-%s-%s___%s.ts" % (episodeObj['title'], str(episodeObj['syndicatedepisode']), episodeObj['subtitle'], str(episodeObj['airdate']), str(episodeObj['starttime']).replace(' ','_'))
 
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
    #deleteProgram(recordingFile)
    logging.info("Operation complete. Exiting.")
    sys.exit(0)

if __name__ == '__main__':
        main()
