# myth2kodi-fuzzy-python

This Program will match recordings from MythTV to entries in thetvdb.com for accurate cataloging with Kodi/Plex/Etc.

Matching priority happens in this order:
- Episode title will try to be matched exactly with tvdb information
- Episode air date will be used to then fuzzy-match the episode title
- General fuzzy match will be performed on the episode title and all series episodes from tvdb

## Upgraded to Python3 and Moved from API to Web ##

MythTV 0.31 has moved move Python3 and so has this script. TheTVdb is phasing out free access to their API so this script now uses the web interface to match show data:

## Usage

To identify a recording and move it to your library, pass findAndMove.py the filename, show title, and episode title.

Run as a User Job from MythTV:
```
/usr/bin/python2 /home/mythtv/myth2kodi-fuzzy-python/findAndMove.py "%FILE%"
```

You must set the following values:

- Directory where recordings are stored is `recordingDir` in findAndMove.py
- Library directory for storing TV shows i `storageDir` in findAndMove.py
- MythTV [db credential xml file](https://www.mythtv.org/wiki/Config.xml) is `mythConfig` in mythPythonBindings.py

## Moving files to Showings

When a file is not moved automatically, it't nice to have a manual option to get it out of Mythtv and into the library hiearchy. This is what the moveToShowins.py is for. And in many cases, the `syndicatedepisode` value put into the title of these files will make them automatically scraped by Plex after moving. Here's the user job for this task:

```
/usr/bin/python3 /home/mythtv/myth2kodi-fuzzy-python/moveToShowings.py "%DIR%" "%FILE%"
```
