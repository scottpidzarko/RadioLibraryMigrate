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
from mutagen.id3 import ID3 as ID3
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
from fuzzywuzzy import fuzz

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
reForThe = re.compile('^the', re.IGNORECASE)
dryRun = False

def main():
    if(len(sys.argv) > 1 and (sys.argv[1] == "--dry-run" or sys.argv[2] == "--dry-run")):
        dryRun = True
    else:
        dryRun = False
        if( not query_yes_no("This is a *live* run. Are you sure?", "no")):
            print( "Aborting ..." )
            return

    writeLog("----------------------------------------------------------------")
    writeLog("---  Library Conversion run started at " + str(datetime.now()) + "---")
    writeLog("----------------------------------------------------------------")

    for path, dirs, files in os.walk(libary_basedir):
        print("Going into " + path)
        writeLog("Going into " + path)
        for f in files:
            writeLog("Processing: \"" + f + "\"")
            print("Processing: \"" + f + "\"");

            tagData = getMP3Data(path,f)
            if(not tagData):
                continue

            album_title = tagData['album_title']
            song_title = tagData['song_title']
            track_num = tagData['track_num']
            category = tagData['category']
            albumartist = tagData['albumartist']
            #Determine if the artist has "the" in their name/group
            #if so, will use "artist, the" structure
            artist = formatArtist(tagData['artist']);
            #for filepath moving - precompute
            uppercaseArtist = formatForDoubleFilePath(formatArtist(tagData['artist']))
            if(album_title == artist):
                selfTitled = 1
            elif(album_title == albumartist):
                selfTitled = 1
            else:
                selfTitled = 0
            compilation = tagData['compilation']
            length = tagData['length']
            genre = tagData['genre']
            year = tagData['year']

            writeLog("Artist: " + xstr(artist) + ", Album: " + xstr(album_title) + ", Title: " + xstr(song_title) + ", #" + xstr(track_num))
            print("Artist: " + artist + ", Album: " + album_title + ", Title: " + song_title + ", #" + str(track_num))

            #try and find the albumID for the song from the library table first with an exact match and then a fuzzy finder
            #and then try lastname, firstname alternatives with and without fuzzy matching

            sql = "SELECT id FROM library where title like %s;"
            data = executeSQL(sql, [album_title])

            if(data is not None and len(data) == 1):
                #Found a unique match
                writeLog("Exact Match Found for " + xstr(song_title))
                writeLog(data[0][0]);

                #move to correct folder
                if not albumartist:
                    dest_filename = moveLibrary(path,f,artist,uppercaseArtist,album_title,track_num,song_title)
                else:
                    dest_filename = moveLibrary(path,f,albumartist,formatForDoubleFilePath(albumartist),album_title,track_num,song_title)

                #Write to DB
                #DB will assign song ID so we're good
                sql = "INSERT INTO library_songs (library_id, artist, album_artist, album_title, song_title, track_num, genre, compilation, crtc, year, length, file_location, updated_at, created_at) " + \
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());"
                if(not dryRun):
                    executeSQL(sql, [data[0][0],artist, albumartist, album_title, song_title, track_num, genre, compilation, category, year, length, dest_filename])

            elif(data is not None and len(data) > 1):
                #Multiple albums with that name, try and match by artist
                writeLog("Multiple albums found for " + album_title)
                writeLog("Trying to match based on artist ...")
                sql = "SELECT %s FROM library where title like %s and artist like %s;"
                if not albumartist:
                    data = executeSQL(sql, ["id",album_title,artist])
                else:
                    data = executeSQL(sql, ["id",album_title,albumartist])

                if(data is not None and len(data) == 1):
                    ##Found a unique match
                    writeLog("Exact Match Found for " + xstr(song_title))
                    writeLog(data[0][0]);

                    #move to correct folder
                    if not albumartist:
                        dest_filename = moveLibrary(path,f,artist,uppercaseArtist,album_title,track_num,song_title)
                    else:
                        dest_filename = moveLibrary(path,f,albumartist,formatForDoubleFilePath(albumartist),album_title,track_num,song_title)

                    #Write to DB
                    #DB will assign song ID so we're good
                    sql = "INSERT INTO library_songs (library_id, artist, album_artist, album_title, song_title, track_num, genre, compilation, crtc, year, length, file_location, updated_at, created_at) " + \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());"
                    if(not dryRun):
                        executeSQL(sql, [data[0][0],artist, albumartist, album_title, song_title, track_num, genre, compilation, category, year, length, dest_filename])

                elif(data is not None and len(data) > 1):
                    #found many matches again
                    #no match, move to the "potential problems folder" and log, with potential matches using fuzzy finder
                    writeLog( "Too many Matches found for " + xstr(song_title))

                    #move to error folder
                    if not albumartist:
                        moveError(path,f,artist,uppercaseArtist,album_title,track_num,song_title)
                    else:
                        moveError(path,f,albumartist,formatForDoubleFilePath(albumartist),album_title,track_num,song_title)
                else:
                    #No matches found - title is matching multiple but can't find an artist name
                    #move into "inconclusive" folder
                    #no match, move to the "potential problems folder" and log, with potential matches using fuzzy finder
                    writeLog( "No match found for " + song_title)
                    #move to error folder
                    if not albumartist:
                        moveError(path,f,artist,uppercaseArtist,album_title,track_num,song_title)
                    else:
                        moveError(path,f,albumartist,formatForDoubleFilePath(albumartist),album_title,track_num,song_title)

            else:
                #try fuzzy matching:

                if(data is not None and len(data) == 1):
                    pass
                elif(data is not None and len(data) > 1):
                    pass
                else:
                    #try matching based on permutations of artist - ex. ADAM ANT vs. ANT, ADAM
                    #try with and without commas
                    if(data is not None and len(data) == 1):
                        pass
                    elif(data is not None and len(data) > 1):
                        pass
                    else:
                        #no match, move to the "potential problems folder" and log, with potential matches using fuzzy finder
                        writeLog( "No match found for " + xstr(song_title))
                        #move to error folder
                        if not albumartist:
                            moveError(path,f,artist,uppercaseArtist,album_title,track_num,song_title)
                        else:
                            moveError(path,f,albumartist,formatForDoubleFilePath(albumartist),album_title,track_num,song_title)

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
            #https://stackoverflow.com/questions/17861152/cursor-fetchall-vs-listcursor-in-python
            data = list(cursor)
            db.commit()
            db.close()

            writeLog("Query Returned: ")
            writeLog(data);
            return data

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
        writeLog("Executing the folowing SQL Query: ")
        writeLog(sqlquery)
        writeLog("With the following parameters: ")
        writeLog(tuple(params))
        if(not isinstance(params,list)):
            print("Please pass arguments as an array, ie. [param1, param2, param3, ...]")
            return False;
        paramsTuple = tuple(params);

        try:
            db = my.connect(db_host,db_username,db_password,db_schema)
            cursor = db.cursor()
            cursor.execute(sqlquery, paramsTuple)
            #https://stackoverflow.com/questions/17861152/cursor-fetchall-vs-listcursor-in-python
            data = list(cursor)
            db.commit()
            db.close()

            writeLog("Query Returned: ")
            writeLog(data);
            return data

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
        temp = ID3(os.path.normpath(path + "/" + f))
    except mutagen.mp3.HeaderNotFoundError as e:
        writeLog("HeaderNotFoundError")
        writeLog(e)
        return False
    try:
        ret['artist'] = audiofile['artist'][0]
    except KeyError as e:
        writeLog("File " + f + " has no artist tagged")
        ret[artist] = None
    try:
        ret['albumartist'] = audiofile['albumartist'][0]
    except KeyError as e:
        writeLog("File " + f + " has no albumartist tagged")
        ret['albumartist'] = None
    try:
        ret['album_title'] = audiofile['album'][0];
    except KeyError as e:
        writeLog("File " + f + " has no album title tagged")
        ret['album_title'] = None
    try:
        ret['song_title'] = audiofile['title'][0]
    except KeyError as e:
        writeLog("File " + f + " has no song tagged")
        ret['song_title'] = None
    try:
        #Python 3 only for line below, may cause problems otherwise
        #format adds the leading zero to single-digit #s
        ret['track_num'] = (audiofile['tracknumber'][0][0]).zfill(2)
    except KeyError as e:
        ret['track_num'] = None
        writeLog("File " + f + " has no tracknumber tagged")
    try:
        category = temp[u'COMM::eng'].text[0].lower()#[u'COMM:ID3v1 Comment:eng']
        #can safely default to category 20 since that's the most common

        if(fuzzyContains(category,"category",15)):
            if category[-1] is '1':
                ret['category'] = 10
            if category[-1] is '3':
                ret['category'] = 30
            if category[-1] is '4':
                ret['category'] = 40
            if category[-1] is '5':
                ret['category'] = 50
            else:
                ret['category'] = 20
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
        mood = audiofile['mood'][0]
        mood = mood.lower()
        ret['femcon'] = 0
        ret['cancon'] = 0
        ret['local'] = 0
        if(fuzzyContains(mood,"femcon",15)):
            ret['femcon'] = 1
        if(fuzzyContains(mood,"cancon",15)):
            ret['cancon'] = 1
        if(fuzzyContains(mood,"local",15)):
            ret['local'] = 1
    except KeyError as e:
        writeLog("File " + f + " has no mood (ie. Cancon/Femcon/Local) tagged")
        ret['femcon'] = 0
        ret['cancon'] = 0
        ret['local'] = 0
    return ret

#return id for row in SQL table with the column fuzzy equal to
#WARNING: NOT AT ALL SAFE TO INJECTION
#DO NOT USE WITH UNKNWOWN DATA
def fuzzySQLMatch(idcol, searchcol, table, searchstring, threshold):
    sql = "SELECT "+idcol+","+searchcol+" FROM "+table
    data = executeSQL(sql)
    ret=[]
    if data is None:
        return False
    for row in data:
        if fuzzyFuzzyMatches(row[1], searchstring, threshold):
            ret.append(row[0])
    return ret

#same function above but data source is not from a sql table
#used for testing above without having to deal with sql
#also if you ever want to do the above without sql
def fuzzyListMatch(data, searchstring, threshold):
    ret=[]
    if data is None:
        return False
    for row in data:
        if fuzzyMatches(row[1], searchstring, threshold):
            ret.append(row[0])
    return ret

#If the artist has a "The ______", change the name into "______, the"
def formatArtist(artist):
    try:
        if(reForThe.match(artist)):
            artist = artist[4:] + ", The"
        return artist
    except:
        writeLog("Error in formatArtist(" + xstr(artist) + ")")

#return empty string if string is of none type
def xstr(s):
    if s is None:
        return '---'
    return str(s)

# see https://stackoverflow.com/questions/62771/how-do-i-check-if-a-given-string-is-a-legal-valid-file-name-under-windows
def formatForDoubleFilePath(s):
    """Take a string and return a valid filename constructed from the string.
    The strings are used only for one/two character lengths so don't have to
    worry about DOS reserved names
    """
    try:
        #handle None type:
        s = xstr(s)
        invalid_chars = "<>:\"/\\|?*"
        filename = ""
        for c in s:
            if c not in invalid_chars:
                filename += c
            else:
                filename += '-'
        filename = filename.replace('.','') #no periods in the doubles as discussed
        filename = filename.replace(',','') #no commas in the doubles as discussed
        filename = filename.replace(' ','_') #can't have trailng space
        return filename.upper()[0:2]
    except TypeError as e:
        writeLog("Error in formatForDoubleFilePath(" + xstr(s) + "). The following error was thrown:")
        writeLog(e)
    except:
        writeLog("Unknown Error in formatForDoubleFilePath(" + xstr(s) + ")")

def formatFileDirectory(s):
    """Take a string and return a valid dirname constructed from the string.
    Uses a whitelist approach: any characters not present in valid_chars are
    removed.
    Note: this method may produce invalid filenames such as ``, `.` or `..`
    Be aware.
    """
    try:
        #handle None type:
        s = xstr(s)
        valid_chars = "-_()$!@#^&~`+=[]}{\'., %s%s" % (string.digits,'%')
        filename = ""
        for c in s:
            if c in valid_chars or c.isalpha():
                filename += c
            else:
                filename += '-'
        badlist = ("CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5",
         "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5",
         "LPT6", "LPT7", "LPT8", "LPT9", "nul")
        if( filename.rsplit( ".", 1 )[ 0 ] in badlist):
            return "(bad filename)." + filename.rsplit( ".",1)[ 1 ]
        if ((filename == ".......") or (filename == "dir.exe")):
            return "(bad filename)." + filename.rsplit( ".",1)[ 1 ]

        # can't have trailing dots in directories
        filename = filename.rstrip('.')
        #can't have trailing spaces because win API
        filename = filename.rstrip(' ')

        #trim if it's too long
        #assume directory so no splitting on extension not necessary
        if(len(filename) > 250):
            return filename + "..."
        else:
            return filename
    except TypeError as e:
        writeLog("Error in formatFileDirectory(" + xstr(s) + "). The following error was thrown:")
        writeLog(e)
    except:
        writeLog("Unknown Error in formatFileDirectory(" + xstr(s) + ")")

def formatFileName(s):
    """Take a string and return a valid filename constructed from the string.
    Uses a whitelist approach: any characters not present in valid_chars are
    removed.
    Note: this method may produce invalid filenames such as ``, `.` or `..`
    Be aware.
    """
    try:
        #handle None type:
        s = xstr(s)
        valid_chars = "-_()$!@#^&~`+=[]}{\'., %s%s" % (string.digits,'%')
        filename = ""
        for c in s:
            if c in valid_chars or c.isalpha():
                filename += c
            else:
                filename += '-'
        badlist = ("CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5",
         "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5",
         "LPT6", "LPT7", "LPT8", "LPT9", "nul")
        if( filename.rsplit( ".", 1 )[ 0 ] in badlist):
            return "(bad filename)." + filename.rsplit( ".",1)[1]
        if ((filename == ".......") or (filename == "dir.exe")):
            return "(bad filename)." + filename.rsplit( ".",1)[1]

        #can't have trailing spaces because win API
        filename = filename.rstrip(' ')

        #trim if it's too long
        if(len(filename) > 250):
            return os.path.splitext(filename)[0][0:247] + "..." + os.path.splitext(filename)[1]
        else:
            return filename
    except TypeError as e:
        writeLog("Error in formatFileName(" + xstr(s) + "). The following error was thrown:")
        writeLog(e)
    except:
        writeLog("Unknown Error in formatFileName(" + xstr(s) + ")")

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

def restore_windows_1252_characters(s):
    """Replace C1 control characters in the Unicode string s by the
    characters at the corresponding code points in Windows-1252,
    where possible.

    """
    import re
    def to_windows_1252(match):
        try:
            return bytes([ord(match.group(0))]).decode('windows-1252')
        except UnicodeDecodeError:
            # No character at the corresponding code point: remove it.
            return ''
    return re.sub(r'[\u0080-\u0099]', to_windows_1252, s)

def writeLog(instring):
    if isinstance(instring,str):
        instring = restore_windows_1252_characters(instring)
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
    #xstr handles none type
    log.write(xstr(instring) + "\n")
    log.close()

def fuzzyMatches(stringone,stringtwo,threshold):
    #optimize
    if(stringone == stringtwo):
        return True
    elif(stringone is None or stringtwo is None):
        return False

    #ordering direct check with commas. optimize more
    try:
        if(stringone == stringtwo.split(' ',1)[1] + ', ' + stringtwo.split(' ',1)[0]):
            return True
        if(stringtwo == stringone.split(' ')[1] + ', ' + stringone.split(' ',1)[0]):
            return True
    except IndexError:
        pass
    #apply bucketing - optimize if the two strings are largely diffierent in size
    #set this to four characters for now
    if(len(stringone) > len(stringtwo) + 4):
        return False
    if(len(stringone) > len(stringtwo) + 4):
        return False

    #handle None values, convert to lower because capitalization
    #isn't important with our dataset. Strip leading and tailing whitespace too
    stringone=xstr(stringone).rstrip(" ").lstrip(" ").lower()
    stringtwo=xstr(stringtwo).rstrip(" ").lstrip(" ").lower()

    #Simple ratio
    if(fuzz.ratio(stringone, stringtwo) > threshold):
        return True

    #match different ordering - firstname lastname matches lastname, firstname
    #be stricter on this
    threshold = threshold + 15
    if threshold > 95:
        threshold = 95
    if(fuzz.token_set_ratio(stringone,stringtwo) > threshold+15):
        return True

    #catchall
    return False

#For needle in a haystack searches, not quite what we need!
def fuzzyContains(qs, ls, threshold):
    '''fuzzy matches 'qs' in 'ls' and returns true if there is a match close enough
    '''
    #handle None values
    qs = xstr(qs)
    ls = xstr(ls)

    for word, _ in process.extractBests(str(qs), (str(ls),), score_cutoff=threshold):
        #print('word {}'.format(word))
        for match in find_near_matches(str(qs), word, max_l_dist=1):
            match = word[match.start:match.end]
            #print('match {}'.format(match))
            index = str(ls).find(match)
            return True

    return False

def moveLibrary(path,f,artist,uppercaseArtist,album_title,track_num,song_title):
    source_filename = os.path.normpath(path + "/" + f)
    dest_filename = os.path.normpath(library_destination + "/" + uppercaseArtist[0:1] + "/" +
     uppercaseArtist[0:2] + "/" + formatFileDirectory(artist) + "/" + formatFileDirectory(album_title) + "/" +
     formatFileName(track_num) + " " + formatFileName(artist) + " - " + formatFileName(song_title) + ".mp3")
    ensure_dir(os.path.dirname(dest_filename))
    if(not dryRun):
        shutil.copy2(source_filename,dest_filename)
    writeLog("Copied " + source_filename + " to " + dest_filename)

    return dest_filename

def moveError(path,f,artist,uppercaseArtist,album_title,track_num,song_title):
    source_filename = os.path.normpath(path + "/" + f)
    dest_filename = os.path.normpath(working_directory + "/" + errorfiles + "/" + uppercaseArtist[0:1] + "/" +
     uppercaseArtist[0:2] + "/" + formatFileDirectory(artist) + "/" + formatFileDirectory(album_title) + "/" +
     formatFileName(track_num) + " " + formatFileName(artist) + " - " + formatFileName(song_title) + ".mp3")
    ensure_dir(os.path.dirname(dest_filename))
    if(not dryRun):
        shutil.copy2(source_filename,dest_filename)
    writeLog("Copied " + source_filename + " to " + dest_filename)

if __name__ == "__main__":
    main()
