#!/usr/bin/python

###########################
## Example Library usage ##
###########################

##Example ID3 library usage
#TODO

##Example MySQLdb usage:
##Install with pip install MySQL-python
##You may have to install additional packages with your OS package manager for this pip package to install correctly

## Open database connection
#db = MySQLdb.connect("localhost","testuser","test123","TESTDB" )

## prepare a cursor object using cursor() method
#cursor = db.cursor()

## execute SQL query using execute() method.
#cursor.execute("""SELECT name, phone_number
#                  FROM coworkers
#                  WHERE name=%s
#                  AND clue > %s
#                  LIMIT 5""",
#               (name, clue_threshold))

## Fetch a single row using fetchone() method.
#data = cursor.fetchone()

## disconnect from server
#db.close()

"""
Moving files:

ensure_dir(working_directory + "/" + arr[0] + "/" + arr[1] + "/" + arr[2] + "/")
        source_filename = os.path.normpath(staging_dir + "/" + file_name )
        dest_filename = os.path.normpath(working_directory + "/" + arr[0] + "/" + arr[1] + "/" + arr[2] + "/" + file_name)
        #move that file
        os.rename(source_filename,dest_filename)
"""
#############################################################################

##For yes/no prompt
import sys
##For File moves
import fnmatch
import os
import os.path
import shutil
##For MP3 ID3 tags
import mutagen
from mutagen.mp3 import EasyMP3 as eMP3
from mutagen.mp3 import MP3 as MP3
##for mysql database acces
import MySQLdb as my
##For fuzzy string finder
## Install with pip install fuzzywuzzy[speedup]
#Load db credentials from here
import config
#To get the current datetime
from datetime import datetime
#for regular expressions
import re
#sring utils
import string
import textwrap
#fuzzy matching
from fuzzysearch import find_near_matches
from fuzzywuzzy import process

#Get data from config
db_host = config.db_host
db_username = config.db_username
db_password = config.db_password
db_schema = config.db_schema

libary_basedir = config.libary_basedir
library_destination = config.library_destination
working_directory = config.working_directory
log_file = config.log_file
errorfiles = config.errorfile

#regex pattern for detecting "the" at the start of a string
reForThe = re.compile('^the', re.IGNORECASE);

def main():
    dryRun = False
    if(len(sys.argv) > 1 and (sys.argv[1] == "--dry-run" or sys.argv[2] == "--dry-run")):
        dryRun = True
    else:
        if( not query_yes_no("This is a *live* run. Are you sure?", "no")):
            print( "Aborting ..." )
            return

    writeLog("----------------------------------------------------------------")
    writeLog("---  Library Conversion run started at " + str(datetime.now()) + "---")
    writeLog("----------------------------------------------------------------")

    for path, dirs, files in os.walk(libary_basedir):
        writeLog("Going into " + path)
        for f in files:
            writeLog("Processing: \"" + f + "\"");

            tagData = getMP3Data(path,f)
            if(not tagData):
                continue
            print(tagData)

            album_title = tagData['album_title']
            song_title = tagData['song_title']
            track_num = tagData['track_num']
            category = tagData['category']
            #Determine if the artist has "the" in their name/group
            #if so, will use "artist, the" structure
            artist = formatArtist(tagData['artist']);
            #for filepath moving - precompute
            uppercaseArtist = formatForDoubleFilePath(tagData['artist'])
            if(album_title == artist):
                selfTitled = 1
            else:
                selfTitled = 0
            compilation = tagData['compilation']
            length = tagData['length']
            genre = tagData['genre']
            year = tagData['year']

            writeLog("Artist: " + artist + ", Album: " + album_title + ", Title: " + song_title + ", #" + str(track_num))

            #try and find the albumID for the song from the library table first with an exact match and then a fuzzy finder
            sql = "SELECT id FROM library where title like %s;"
            data = executeSQL(sql, [album_title])
            print(data)

            if(len(data) == 1):
                #Found a unique match
                writeLog("Exact Match Found for " + song_title)
                writeLog(data[0][0]);

                #move to correct folder
                source_filename = os.path.normpath(path + "/" + f)
                dest_filename = os.path.normpath(library_destination + "/" + uppercaseArtist[0:1] + "/" +
                 uppercaseArtist[0:2] + "/" + formatFileName(artist) + "/" + formatFileName(album_title) + "/" +
                 formatFileName(track_num + " " + artist + " - " + song_title))
                ensure_dir(os.path.dirname(dest_filename))
                if(not dryRun):
                    shutil.copy2(source_filename,dest_filename)

                writeLog("Copied " + source_filename + " to " + dest_filename)

                #Write to DB
                #DB will assign song ID so we're good
                sql = "INSERT INTO library_songs (library_id, artist, album_title, song_title, track_num, tracks_total, file_location, updated_at, created_at) " + \
                "VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW());"
                if(not dryRun):
                    executeSQL(sql, [data[0][0],artist, album_title, song_title, track_num[0], track_num[2:], dest_filename])

            elif(len(data) > 1):
                #Multiple albums with that name, try and match by artist
                writeLog("Multiple albums found for " + album_title)
                writeLog("Trying to match based on artist ...")
                sql = "SELECT %s FROM library where title like %s and artist like %s;"
                data = executeSQL(sql, ["id",album_title,artist])
                writeLog(data);

                if(len(data) == 1):
                    ##Found a unique match
                    writeLog("Exact Match Found for " + song_title)
                    writeLog(data[0][0]);

                    #move to correct folder
                    source_filename = os.path.normpath(path + "/" + f)
                    dest_filename = os.path.normpath(library_destination + "/" + uppercaseArtist[0:1] + "/" +
                     uppercaseArtist[0:2] + "/" + formatFileName(artist) + "/" + formatFileName(album_title) + "/" +
                     formatFileName(track_num + " " + artist + " - " + song_title))
                    ensure_dir(os.path.dirname(dest_filename))
                    if(not dryRun):
                        shutil.copy2(source_filename,dest_filename)

                    writeLog("Copied " + source_filename + " to " + dest_filename)

                    #Write to DB
                    #DB will assign song ID so we're good
                    sql = "INSERT INTO library_songs (library_id, artist, album_title, song_title, track_num, file_location, updated_at, created_at)"
                    "VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW());"
                    if(not dryRun):
                        executeSQL(sql, [data[0][0],artist, album_title, song_title, track_num, dest_filenam])

                elif(len(data) > 1):
                    #found many matches again
                    #no match, move to the "potential problems folder" and log, with potential matches using fuzzy finder
                    writeLog( "Too many Matches found for " + song_title)

                    #move to error folder
                    source_filename = os.path.normpath(path + "/" + f)
                    dest_filename = os.path.normpath(working_directory + "/" + errorfiles + "/" + uppercaseArtist[0:1] + "/" +
					 uppercaseArtist[0:2] + "/" + artist + "/" + track_num + " " + artist + " - " + song_title)
                    ensure_dir(os.path.dirname(dest_filename))
                    if(not dryRun):
                        shutil.copy2(source_filename,dest_filename)
                else:
                    #No matches found - title is matching multiple but can't find an artist name
                    #move into "inconclusive" folder
                    #no match, move to the "potential problems folder" and log, with potential matches using fuzzy finder
                    writeLog( "No match found for " + song_title)

                    #move to error folder
                    source_filename = os.path.normpath(path + "/" + f)
                    dest_filename = os.path.normpath(working_directory + "/" + errorfiles + "/" + uppercaseArtist[0:1] + "/"
					 + uppercaseArtist[0:2] + "/" + artist + "/" + track_num + " " + artist + " - " + song_title)
                    ensure_dir(os.path.dirname(dest_filename))
                    if(not dryRun):
                        shutil.copy2(source_filename,dest_filename)

            else:
                #no match, move to the "potential problems folder" and log, with potential matches using fuzzy finder
                writeLog( "No match found for " + song_title)

                #move to error folder

                source_filename = os.path.normpath(path + "/" + f)
                dest_filename = os.path.normpath(working_directory + "/" + errorfiles + "/" + uppercaseArtist[0:1]
				 + "/" + uppercaseArtist[0:2] + "/" + artist + "/" + track_num + " " + artist + " - " + song_title)
                ensure_dir(os.path.dirname(dest_filename))
                if(not dryRun):
                    shutil.copy2(source_filename,dest_filename)

"""""
Runs the query given by sql query and the array of parameters given in params. Defaults to no parameters if none are passed
Example1:
    sql = "SELECT * FROM library where title like %s";
    data = executeSQL(sql, [album_title])
Example2:
    sql = "SELECT * FROM library where title like %s or title like %s";
    data = executeSQL(sql, [album_title, "A Midnights Summer Breeze"])
"""""
def executeSQL(sqlquery, params=None):
    if params is None:
        try:
            writeLog("Executing the following SQL Query: " + sqlquery);
            db = my.connect(db_host,db_username,db_password,db_schema)

            cursor = db.cursor()

            cursor.execute(sqlquery)

            db.commit()
            db.close()

            #https://stackoverflow.com/questions/17861152/cursor-fetchall-vs-listcursor-in-python
            return list(cursor)

        except my.DataError as e:
            writeLog("DataError")
            writeLog(e)

        except my.InternalError as e:
            writeLog("InternalError")
            writeLog(e)

        except my.IntegrityError as e:
            writeLog("IntegrityError")
            writeLog(e)

        except my.OperationalError as e:
            writeLog("OperationalError")
            writeLog(e)

        except my.NotSupportedError as e:
            writeLog("NotSupportedError")
            writeLog(e)

        except my.ProgrammingError as e:
            writeLog("ProgrammingError")
            writeLog(e)

        except :
            writeLog("Unknown error occurred")
    else:
        writeLog("Executing the folowing SQL Query: " + sqlquery)
        if(not isinstance(params,list)):
            print("Please pass arguments as an array, ie. [param1, param2, param3, ...]")
            return False;
        paramsTuple = tuple(params);

        try:
            db = my.connect(db_host,db_username,db_password,db_schema)

            cursor = db.cursor()

            cursor.execute(sqlquery, paramsTuple)

            db.commit()
            db.close()

            #https://stackoverflow.com/questions/17861152/cursor-fetchall-vs-listcursor-in-python
            return list(cursor)

        except my.DataError as e:
            writeLog("DataError")
            writeLog(e)

        except my.InternalError as e:
            writeLog("InternalError")
            writeLog(e)

        except my.IntegrityError as e:
            writeLog("IntegrityError")
            writeLog(e)

        except my.OperationalError as e:
            writeLog("OperationalError")
            writeLog(e)

        except my.NotSupportedError as e:
            writeLog("NotSupportedError")
            writeLog(e)

        except my.ProgrammingError as e:
            writeLog("ProgrammingError")
            writeLog(e)

        except :
            writeLog("Unknown error occurred")

def getMP3Data(path,f):
    ret = {}
    try:
        audiofile = eMP3(os.path.normpath(path + "/" + f));
    except mutagen.mp3.HeaderNotFoundError as e:
        writeLog("HeaderNotFoundError")
        writeLog(e)
        return False
    try:
        ret['artist'] = audiofile['artist'][0]
    except KeyError as e:
        writeLog("File " + f + " has no artist tagged")
        ret[artist] = ""
    try:
        ret['albumartist'] = audiofile['albumartist'][0]
    except KeyError as e:
        writeLog("File " + f + " has no albumartist tagged")
        ret['albumartist'] = ""
    try:
        ret['album_title'] = audiofile['album'][0];
    except KeyError as e:
        writeLog("File " + f + " has no album title tagged")
        ret['album_title'] = ""
    try:
        ret['song_title'] = audiofile['title'][0]
    except KeyError as e:
        writeLog("File " + f + " has no song tagged")
        ret['song_title'] = ""
    try:
        ret['track_num'] = audiofile['tracknumber'][0];
    except KeyError as e:
        ret['track_num'] = None
        writeLog("File " + f + " has no tracknumber tagged")
    temp = MP3(os.path.normpath(path + "/" + f))
    try:
        category = ""#temp["COMM:0:'eng'"]
        #can safely default to category 20 since that's the most common
        ##TODO: Better regex matching here
        if(category == "category 1"):
            ret['category'] = 10
        elif(category == "category 3"):
            ret['category'] = 30
        elif(category == "category 4"):
            ret['category'] = 40
        elif(category == "category 5"):
            ret['category'] = 50
        else:
            ret['category'] = 20
    except KeyError as e:
        writeLog("File " + f + " has no crtc category tagged")
        ret['category'] = None
    try:
        ret['year'] = audiofile['date'][0];
    except KeyError as e:
        writeLog("File " + f + " has no year tagged")
        ret['year'] = None
    try:
        ret['length'] = audiofile['length'][0]
    except KeyError as e:
        writeLog("File " + f + " has no length tagged")
        ret['length'] = None
    try:
        ret['compilation'] = audiofile['compilation'][0]
        if(ret['compilation'] == 1):
            ret['compilation'] = 1
        else:
            ret['compilation'] = 0
    except KeyError as e:
        ret['compilation'] = 0
        #print("File " + f + " has no comp flag tagged")
    try:
        ret['genre'] = audiofile['genre'][0]
    except KeyError as e:
        writeLog("File " + f + " has no genre tagged")
        ret['genre'] = None
    try:
        #ret['language'] = audiofile['language']
        pass
    except KeyError as e:
        print("File " + f + "has no language tagged")
    try:
        mood = audidofile['mood']
        mood = mood.lower()
    except KeyError as e:
        writeLog("File " + f + " has no mood (ie. Cancon/Femcon/Local) tagged")
        ret['femcon'] = 0
        ret['cancon'] = 0
        ret['local'] = 0
    return ret

#If the artist has a "The ______", change the name into "______, the"
def formatArtist(artist):
    if(reForThe.match(artist)):
        artist = artist[4:] + ", The"
    return artist

# see https://stackoverflow.com/questions/62771/how-do-i-check-if-a-given-string-is-a-legal-valid-file-name-under-windows
def formatForDoubleFilePath(s):
    """Take a string and return a valid filename constructed from the string.
    The strings are used only for one/two character lengths so don't have to
    worry about DOS reserved names
    """
    invalid_chars = "<>:\"/\|?*"
    filename = ''.join(c for c in s if c not in invalid_chars)
    filename = filename.replace('.','') #no periods in the doubles as discussed
    filename = filename.replace(',','') #no commas in the doubles as discussed
    return filename.upper()

def formatFileName(s):
    """Take a string and return a valid filename constructed from the string.
Uses a whitelist approach: any characters not present in valid_chars are
removed.
Note: this method may produce invalid filenames such as ``, `.` or `..`
Be aware.

"""
    valid_chars = "-_()$!@#^&~`\+=[]}{'., %s%s" % (string.digits,'%')
    filename = ''.join(c for c in s if c in valid_chars or c.isalpha())
    badlist = ("CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5",
	 "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5",
	 "LPT6", "LPT7", "LPT8", "LPT9", "nul")
    if( filename.rsplit( ".", 1 )[ 0 ] in badlist):
        return "(bad filename)" + filename.rsplit( ".",1)[ 1 ]
    if ((filename == ".......") or (filename == "dir.exe")):
        return "(bad filename)" + filename.rsplit( ".",1)[ 1 ]
    #trim if it's too long
    return textwrap.shorten(filename, width=250, placeholder="...")

#helper function to ensure a certain directory f exists
#if it doesn't find it, it will make it
#Updated for python 3.2+
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
#This is the old python 2 version
#def ensure_dir(f):
#   d = os.path.dirname(f)
#    if not os.path.exists(d):
#       os.makedirs(d)

#Similar helper function to above, but instead returns T/F if a file exists or not at a specified location
def checkIfFile(fname):
    return os.path.isfile(fname)

#helper function to elicit a y/n response from the user given the question contained in the question string
#Python 3+
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).
    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def writeLog(instring):
    #write that we're starting a batch job to the log file
    try:
        if(checkIfFile(working_directory + "/" + log_file)):
            log = open( os.path.normpath( working_directory + "/" + log_file), 'a' )
        else:
            print("Creating Log File ...")
            ensure_dir(os.path.normpath(working_directory))
            log = open( os.path.normpath( working_directory + "/" + log_file), 'w+' )
    except FileNotFoundError:
        print( "Error: Log File does not appear to exist or you do not have the permissions to write to it!" )
        return
    log.write( "[" + str(datetime.now()) + "]" + "    ")
    log.write(str(instring) + "\n")
    log.close()

def fuzzyContains(qs, ls, threshold):
    '''fuzzy matches 'qs' in 'ls' and returns true if there is a match close enough
    '''
    for word, _ in process.extractBests(qs, (ls,), score_cutoff=threshold):
        #print('word {}'.format(word))
        for match in find_near_matches(qs, word, max_l_dist=1):
            match = word[match.start:match.end]
            #print('match {}'.format(match))
            index = ls.find(match)
            return True

    return False

if __name__ == "__main__":
    main()
