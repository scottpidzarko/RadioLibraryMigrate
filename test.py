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

#############################################################################

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

#root folder of library
libary_basedir = "/home/scott/git/RadioLibraryMigrate/LibraryTest"

def test():
    audiofile = eyed3.load('test.mp3');
    print audiofile.tag.artist;
    print audiofile.tag.title;
    print audiofile.tag.track_num;

    # execute SQL query using execute() method.
    data = executeSQL("SELECT VERSION()");

    print "Database version : %s " % data


def main():

    for path, dirs, files in os.walk(libary_basedir):
        print "Going into " + path
        for f in files:
            print "Processing: \"" + f + "\"";
            audiofile=eyed3.load(os.path.normpath(path + "/" + f));
            artist =  audiofile.tag.artist;
            album_title =  audiofile.tag.album;
            song_title = audiofile.tag.title;
            track_num = audiofile.tag.track_num[0];
            print "Artist: " + artist + ", Album: " + album_title + ", Title: " + song_title + ", #" + str(track_num);

            #try and find the albumID for the song from the library table first with an exact match and then a fuzzy finder
            ## also wtf is the title S/T?
            sql = "SELECT * FROM library where title like %s";
            data = executeSQL(sql, [album_title])

            #Found a match
            if(data):
                print "Match Found for " + song_title
                #Write to DB

                #move to correct folder

                #if(artist.split(0,2) == "the" || artist.split(0,2) == "The" )
            else:
                print "No exact match found for " + song_title
                #no match, move to the "potential problems folder"

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

if __name__ == "__main__":
    main()
