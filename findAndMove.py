from __future__ import print_function

from myth2kodiFuzzyPython import findEpisodeData
import sys
from shutil import copyfile

recordingDir = "/Lenny/mythtv/"
storageDir = "/Lenny/videoLibrary/TV/"

def main():
    recordingFile = sys.argv[1]
    showName = sys.argv[2]
    epName = sys.argv[3]
    epFilename = findEpisodeData("Late Night with Seth Meyers","Claire Foy Lucas Hedges boygenius Franklin Vanderbilt")
    if epFilename != "0":
        if os.path.isdir(storageDir) == False:
            print("storageDir doesn't exist, aborting.")
            sys.exit(1)
        if os.path.isdir(os.path.join(storageDir,showName)) == False:
            print("making directory for this show: %s",os.path.join(storageDir,showName))
            os.mkdir(os.path.join(storageDir,showName))
        print("copying file")
        fileDestination = os.path.join(storageDir,showName,epFilename,os.path.splitext(recordingFile)[-1])
        copyfile(os.path.join(recordingDir,recordingFile),fileDestination)
        print("file copied to: %s",fileDestination)
        sys.exit(0)
    sys.exit(1)

if __name__ == '__main__':
        main()
