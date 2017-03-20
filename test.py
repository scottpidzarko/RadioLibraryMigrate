#!/usr/bin/python

###########################
## Example Library usage ##
###########################

##Example ID3 library usage
## install with pip install eyed3
## Use python 2.7.X
## Documentation at: http://eyed3.nicfit.net/#documentation-index
#
#import eyed3
#
##Setting a tag
#
#audiofile = eyed3.load("song.mp3")
#audiofile.tag.artist = u"Nobunny"
#audiofile.tag.album = u"Love Visions"
#audiofile.tag.album_artist = u"Various Artists"
#audiofile.tag.title = u"I Am a Girlfriend"
#audiofile.tag.track_num = 4
#audiofile.tag.save()
#
##Getting a tag
##audiofile = eyed3.load("song.mp3")
#print audiofile.tag.artist;
#print audiofile.tag.title;
#print audiofile.tag.track_num;
#etc

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
import shutil
##For MP3 ID3 tags
import eyed3
##for mysql database acces
import MySQLdb as my
##For fuzzy string finder
## Install with pip install fuzzywuzzy[speedup]
#Load db credentials from here
import secrets
#To get the current datetime
from datetime import datetime

#root folder of library to organize
libary_basedir = "/home/scott/git/RadioLibraryMigrate/LibraryTest"

#working_directory, where the log file is put and any other generated assets
working_directory = "/home/scott/git/RadioLibraryMigrate/log"

#log file name
#for now, we don't have the option of disabling this
log_file = "libraryMigrate-log.txt"

def test():
    audiofile = eyed3.load('test.mp3');
    print audiofile.tag.artist;
    print audiofile.tag.title;
    print audiofile.tag.track_num;

    # execute SQL query using execute() method.
    data = executeSQL("SELECT VERSION()");

    writeLog("Database version : %s " % data);


def main():

    for path, dirs, files in os.walk(libary_basedir):
        writeLog("Going into " + path)
        for f in files:
            writeLog("Processing: \"" + f + "\"");
            audiofile=eyed3.load(os.path.normpath(path + "/" + f));
            artist =  audiofile.tag.artist;
            album_title =  audiofile.tag.album;
            song_title = audiofile.tag.title;
            track_num = audiofile.tag.track_num[0];
            writeLog("Artist: " + artist + ", Album: " + album_title + ", Title: " + song_title + ", #" + str(track_num))

            #try and find the albumID for the song from the library table first with an exact match and then a fuzzy finder
            ## also wtf is the title S/T?
            sql = "SELECT %s FROM library where title like %s;"
            data = executeSQL(sql, [id,album_title])
            writeLog(data);

            if(len(data) == 1):
                #Found a unique match
                writeLog("Match Found for " + song_title)
                #Write to DB

                #move to correct folder

                #Determine if the artist has "the" in their name/group
                #if so, will use "artist, the" structure
                #if(artist.split(0,2) == "the" || artist.split(0,2) == "The" )
            elif(len(data) > 1):
                for i in data:
                    print i
                #Multiple albums with that name, try and match by artist
                print("Multiple albums found for %s", album_title)
                print("Trying to match based on artist ...")
                sql = "SELECT %s FROM library where title like %s and artist like %s;"
                data = executeSQL(sql, ["id",album_title,artist])
                print data;
            else:
                #no match, move to the "potential problems folder" and log, with potential matches using fuzzy finder
                print "No exact match found for " + song_title

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
            print sqlquery
            db = my.connect(secrets.db_host,secrets.db_username,secrets.db_password,secrets.db_schema)

            cursor = db.cursor()

            cursor.execute(sqlquery)

            #https://stackoverflow.com/questions/17861152/cursor-fetchall-vs-listcursor-in-python
            return list(cursor)

            db.close()

        except my.DataError as e:
            print("DataError")
            print(e)

        except my.InternalError as e:
            print("InternalError")
            print(e)

        except my.IntegrityError as e:
            print("IntegrityError")
            print(e)

        except my.OperationalError as e:
            print("OperationalError")
            print(e)

        except my.NotSupportedError as e:
            print("NotSupportedError")
            print(e)

        except my.ProgrammingError as e:
            print("ProgrammingError")
            print(e)

        except :
            print("Unknown error occurred")
    else:
        print sqlquery
        if(not isinstance(params,list)):
            print("Please pass arguments as an array, ie. [param1, param2, param3, ...]")
            return False;
        paramsTuple = tuple(params);
        print paramsTuple

        try:
            db = my.connect(secrets.db_host,secrets.db_username,secrets.db_password,secrets.db_schema)

            cursor = db.cursor()

            cursor.execute(sqlquery, paramsTuple)

            #https://stackoverflow.com/questions/17861152/cursor-fetchall-vs-listcursor-in-python
            return list(cursor)

            db.close()

        except my.DataError as e:
            print("DataError")
            print(e)

        except my.InternalError as e:
            print("InternalError")
            print(e)

        except my.IntegrityError as e:
            print("IntegrityError")
            print(e)

        except my.OperationalError as e:
            print("OperationalError")
            print(e)

        except my.NotSupportedError as e:
            print("NotSupportedError")
            print(e)

        except my.ProgrammingError as e:
            print("ProgrammingError")
            print(e)

        except :
            print("Unknown error occurred")

#helper function to ensure the working directory exists where f is the input directory
def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

#helper function to elicit a y/n response from the user given the question contained in the question string
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
        log = open( os.path.normpath( working_directory + "/" + log_file), 'a' )
    except IOError:
        print "Error: Log File does not appear to exist or you do not have the permissions to write to it!."
        return
    log.write( "[" + str(datetime.now()) + "]" + "    ")
    log.write(instring + "\n")
    log.close()

if __name__ == "__main__":
    test()
