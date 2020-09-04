from fuzzy_scraper import identifyMythtvEpisode, deleteMythRecording
import os
import sys
from shutil import copyfile
from fuzzy_logger import logging

recordingDir = "/Lenny/mythtv/"
storageDir = "/Lenny/videoLibrary/TV/"

def main():
    recordingFile = sys.argv[1]
    logging.info("======================")
    logging.info("Attempting tvdb match to: %s", recordingFile)
    matchedEpisode = identifyMythtvEpisode(recordingFilename=recordingFile)
    if matchedEpisode != None:
        if os.path.isdir(storageDir) == False:
            logging.info("storageDir doesn't exist, aborting.")
            sys.exit(1)
        if os.path.isdir(os.path.join(storageDir,matchedEpisode.seriestitle)) == False:
            logging.info("making directory for this show: %s",os.path.join(storageDir,matchedEpisode.seriestitle))
            os.mkdir(os.path.join(storageDir,matchedEpisode.seriestitle),0o0777)
            os.chmod(os.path.join(storageDir,matchedEpisode.seriestitle),0o0777)
        fileDestination = os.path.join(storageDir,matchedEpisode.seriestitle,matchedEpisode.filename+os.path.splitext(recordingFile)[-1])
        if os.path.exists(fileDestination):
            logging.error("ERROR: aborting, file already exists at: %s", fileDestination)
            sys.exit(1)
        logging.info("Copying file: %s to: %s", recordingFile, fileDestination)
        copyfile(os.path.join(recordingDir,recordingFile),fileDestination)
        os.chmod(fileDestination,0o777)
        logging.info("File copied successfully")
        logging.info("Deleting %s",recordingFile)
        deleteMythRecording(recordingFile)
        logging.info("Operation complete. Exiting.")

        sys.exit(0)
    sys.exit(1)

if __name__ == '__main__':
        main()
