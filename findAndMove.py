from __future__ import print_function

from myth2kodiFuzzyPython import findEpisodeFilename, getSeriesName, deleteShow
import os
import sys
import subprocess
from shutil import copyfile
from fuzzy_logger import logging
#from mythPythonBindings import deleteProgram

recordingDir = "/Lenny/mythtv/"
storageDir = "/Lenny/videoLibrary/TV/"

#This fill will contain filenames of recordings copied to the library for deletion via a cron job (it's hack)
workingDir = "/home/mythtv/myth2kodi-fuzzy-python/"
todelete = 'deleteList.txt'

def main():
    recordingFile = sys.argv[1]
    showName = sys.argv[2]
    epName = sys.argv[3]
    logging.info("======================")
    logging.info("Attempting tvdb match to: %s :: %s :: %s", recordingFile, showName, epName)
    seriesName = getSeriesName(showName) #Use tvdb series name value for directory names to normalize capitalization
    if seriesName == None:
        logging.info("Couldn't retrieve series name from tvdb. Aborting.")
        sys.exit(1)    
    epFilename = findEpisodeFilename(seriesName,epName,recordingFilename=recordingFile)
    if epFilename != 0:
        if os.path.isdir(storageDir) == False:
            logging.info("storageDir doesn't exist, aborting.")
            sys.exit(1)
        if os.path.isdir(os.path.join(storageDir,seriesName)) == False:
            logging.info("making directory for this show: %s",os.path.join(storageDir,seriesName))
            os.mkdir(os.path.join(storageDir,seriesName),0o0777)
            os.chmod(os.path.join(storageDir,seriesName),0o0777)
        fileDestination = os.path.join(storageDir,seriesName,epFilename+os.path.splitext(recordingFile)[-1])
        if os.path.exists(fileDestination):
            logging.error("ERROR: aborting, file already exists at: %s", fileDestination)
            sys.exit(1)
        logging.info("Copying file: %s to: %s", recordingFile, fileDestination)
        copyfile(os.path.join(recordingDir,recordingFile),fileDestination)
        os.chmod(fileDestination,0o777)
        logging.info("File copied successfully")
        logging.info("Writing filename for deletion by cron job")
        with open(workingDir + todelete, 'a') as f:
            f.write(recordingFile + '\n')
	os.chmod(workingDir + todelete,0o777)
        '''
        logging.info("Deleting %s",recordingFile)
        systemCmd = '/usr/bin/python3 mythObjGetter.py ' + sys.argv[1] + ' DELETE'
        mythDeleteCode = os.system(systemCmd) 
        if (mythDeleteCode != 0):
            logging.info("Error: Unable to delete from mythv: %s | exit code: %d", recordingFile, mythDeleteCode)
            logging.info(systemCmd)
            sys.exit(1)
        logging.info("Operation complete. Exiting.")
        '''
        sys.exit(0)
    sys.exit(1)

if __name__ == '__main__':
        main()
