from MythTV.services_api import send as api
from myth2kodi_classes import Episode

backend = api.Send(host='krusty')

def getProgramFromFilename(filename) -> Episode | None:
    recorded = backend.send(endpoint='Dvr/GetRecordedList')
    targetProgram = None

    for p in recorded['ProgramList']['Programs']:
        if p['FileName'] == filename:
            targetProgram = p

    if targetProgram is None:
        return None

    episode = Episode(title=targetProgram['Title'],
                      episodeName=targetProgram["SubTitle"],
                      airdate=targetProgram["Airdate"],
                      description=targetProgram["Description"],
                      myth_dict=targetProgram)

    try:
        s = int(targetProgram['Season'])
        e = int(targetProgram['Episode'])
        if e == 0:
            logging.warn(f'Episode number is 0 for {targetProgram["Title"]} SubTitle: {targetProgram["SubTitle"]}')
        else:
            seasonStr = str(s).zfill(2)
            epNumStr = str(e).zfill(2)
            episode.epNum=f'S{seasonStr}E{epNumStr}'
            episode.setFilename()

    except:
        pass

    return episode


def deleteProgram(myth_dict):
    params = {
            'RecordedId' : myth_dict['Recording']['RecordedId'],
            'ChanId' : myth_dict['Channel']['ChanId'],
            'StartTime' : myth_dict['StartTime'],
            'ForceDelete' : False,
            'AllowRerecord' : False
            }
    return backend.send(endpoint='Dvr/DeleteRecording',
                        postdata=params,
                        opts={'wrmi':True}
                        )
