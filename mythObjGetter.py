#!/usr/bin/python3

from mythPythonBindings import getProgramObjectFromFilename, getDbObject, getBeObject, deleteProgram
import pickle
import sys
import logging

def main():
    logging.basicConfig(filename="mythObjGetter.log")
    logging.info("Started: %s", str(sys.argv))
    if len(sys.argv) == 2:
        #testfilename="1212_20200824200000.ts"

        targetProgram = getProgramObjectFromFilename(sys.argv[1], getDbObject(), getBeObject())

        returnObj = dict()
        returnObj['title'] = targetProgram['title']
        returnObj['airdate'] = targetProgram['airdate']
        returnObj['subtitle'] = targetProgram['subtitle']
        if targetProgram == None:
            sys.exit(1)
        else:
            pickle.dump(returnObj, open("showObj.p","wb"), protocol=2)
            sys.exit(0)
    elif len(sys.argv) == 3:
        logging.info("3 arguments found")
        if sys.argv[2] == "DELETE":
            logging.info("argv[2] = %s", sys.argv[2])
            deleteProgram(sys.argv[1])
            sys.exit(0)
        else:
            sys.exit(3)
    else:
        sys.exit(2)

if __name__ == '__main__':
    main()
