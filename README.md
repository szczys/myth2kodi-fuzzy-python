# myth2kodi-fuzzy-python

This Program will match recordings from MythTV to entries in thetvdb.com for accurate cataloging with Kodi/Plex/Etc.

Matching priority happens in this order:
- Episode title will try to be matched exactly with tvdb information
- Episode air date will be used to then fuzzy-match the episode title
- General fuzzy match will be performed on the episode title and all series episodes from tvdb

## Aug2020 Update: the Jenky hack ##

After upgrading to MythTV 0.31 (Mint 20 based on Ubuntu 20.04) this program needed to move to Python3.

However, theTVdb is phasing out free access to their API. You can no longer get an API key without paying a subscription fee. The old API key for Python2 will continue to work until sometime in 2021. The caveat is that MythTV Python bindings are now Python 3. So I hacked to get around it. This is really bad and I'm sorry:

* python2 used to run findAndMove.py
* findAndMove calls os.system to run mythbindings using python3, writing a Pickle (version 2) file with the show info from MythTV
* pickle file is ready to get data from tvdb_api, fuzzy matching and copying to the library
* for some reason I couldn't delete from mythtv using this scheme, so a subsequent hack writes the filename to a file and a cron job comes by every half hour and deletes it:
  * `*/30 * * * * /usr/bin/python3 /home/mythtv/myth2kodi-fuzzy-python/deleteFiles.py`

Dirty, dirty, dirty hack... but it works until I think up a solution (or bite the bulled and subscribe to the api?)

## Usage

To identify a recording and move it to your library, pass findAndMove.py the filename, show title, and episode title.

Run as a User Job from MythTV:
```
/usr/bin/python /home/mythtv/myth2kodi-fuzzy-python/findAndMove.py "%FILE%" "%TITLE%" "%SUBTITLE%"
```

You must set the following values:

- Directory where recordings are stored is `recordingDir` in findAndMove.py
- Library directory for storing TV shows i `storageDir` in findAndMove.py
- MythTV db credential xml file is `mythConfig` in mythPythonBindings.py

## Moving files to Showings

When a file is not moved automatically, it't nice to have a manual option to get it out of Mythtv and into the library hiearchy. This is what the moveToShowins.py is for. And in many cases, the `syndicatedepisode` value put into the title of these files will make them automatically scraped by Plex after moving. Here's the user job for this task:

```
/usr/bin/python /home/mythtv/myth2kodi-fuzzy-python/moveToShowings.py "%DIR%" "%FILE%"
```
