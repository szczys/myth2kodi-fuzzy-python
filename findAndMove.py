from __future__ import print_function

from myth2kodiFuzzyPython import findEpisodeFilename
import sys
import os
from shutil import copyfile
from fuzzy_logger import logging
from mythPythonBindings import deleteProgram

recordingDir = "/Lenny/mythtv/"
storageDir = "/Lenny/videoLibrary/TV/"

def main():
    recordingFile = sys.argv[1]
    showName = sys.argv[2].decode('utf-8')
    epName = sys.argv[3].decode('utf-8')
    epFilename = findEpisodeFilename(showName,epName,recordingFilename=recordingFile)
    if epFilename != "0":
        if os.path.isdir(storageDir) == False:
            logging.info("storageDir doesn't exist, aborting.")
            sys.exit(1)
        if os.path.isdir(os.path.join(storageDir,showName)) == False:
            logging.info("making directory for this show: %s",os.path.join(storageDir,showName))
            os.mkdir(os.path.join(storageDir,showName),0777)
            os.chmod(os.path.join(storageDir,showName),0o777)
        logging.info("copying file")
        fileDestination = os.path.join(storageDir,showName,epFilename+os.path.splitext(recordingFile)[-1])
        copyfile(os.path.join(recordingDir,recordingFile),fileDestination)
        os.chmod(fileDestination,0o777)
        logging.info("file copied to: %s",fileDestination)
        logging.info("deleting %s",recordingFile)
        deleteProgram(recordingFile)
        sys.exit(0)
    sys.exit(1)

if __name__ == '__main__':
        main()
