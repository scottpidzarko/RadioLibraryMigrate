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
#cursor.execute("SELECT VERSION()")

## Fetch a single row using fetchone() method.
#data = cursor.fetchone()

#print "Database version : %s " % data

## disconnect from server
#db.close()

#############################################################################

import fnmatch
import os
import shutil
import eyed3
import MySQLdb
#Load db credentials
import secrets

def main():
    audiofile = eyed3.load('pinkfloyd.mp3');
    print audiofile.tag.artist;
    print audiofile.tag.title;
    print audiofile.tag.track_num;

    # Open database connection
    db = MySQLdb.connect(secrets.db_host,secrets.db_username,secrets.db_password,secrets.db_schema)

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # execute SQL query using execute() method.
    cursor.execute("SELECT VERSION()")

    # Fetch a single row using fetchone() method.
    data = cursor.fetchone()

    print "Database version : %s " % data

    # disconnect from server
    db.close()

if __name__ == "__main__":
    main()
