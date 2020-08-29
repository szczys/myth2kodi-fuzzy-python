import subprocess
import os

workingDir = "/home/mythtv/myth2kodi-fuzzy-python/"
todelete = 'deleteList.txt'
runScript = 'mythObjGetter.py'
whichPython = '/usr/bin/python3'

try:
    with open(workingDir + todelete) as f:
        content = f.readlines()

    for show in content:
        process = [whichPython, workingDir + runScript, show.strip(), "DELETE"]
        subprocess.call(process)

    os.remove(workingDir + todelete)

except:
    pass
