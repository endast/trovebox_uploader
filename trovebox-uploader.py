#!/usr/bin/env python
# encoding: utf-8
"""
trovebox-uploader.py

version 0.2

Created by Magnus Wahlberg on 2013-11-27.
Copyright (c) 2012 Wahlberg Research And Development. All rights reserved.
"""

import os
import sys
import imghdr
import hashlib
import argparse
from trovebox import Trovebox
from trovebox.errors import TroveboxError, TroveboxDuplicateError
import unicodedata

# Init
try:
    client = Trovebox()
    client.configure(api_version=2)

except IOError, e:
    print 'Could not connect to Trovebox'
    print 'Please check ~/.config/trovebox/default. More info: https://github.com/photo/openphoto-python'
    raise e

def is_folder(path):
    return os.path.isdir(path)


def image_uploaded(photo):
    res = client.photos.list(hash=hash_file(photo))
    if len(res) > 0:
        return True
    return False

def is_image(file):
    valid_types = ["jpg","jpeg","gif","png"]
    image_type = imghdr.what(file)

    if image_type in valid_types:
        return True
    else:
        return False

def upload_folder(folder_path, tags=[], albums=[], public=False):
    uploaded_files = 0
    for file_path in scan_folder(folder_path):
        if is_image(file_path):
            if upload_photo(file_path, tags, albums, public):
                uploaded_files += 1

    return uploaded_files

def scan_folder(path):
    files = []

    if not os.path.exists(path):
        print path, "does not exist"
        return files

    for (dirpath, dirnames, filenames) in os.walk(path):    
        files.extend(os.path.join(dirpath, filename) for filename in filenames)         
    return files

def get_album_ids(album_names):
    albums = client.albums.list()
    album_ids = [] 

    for album_name in album_names:
        album_id = [album.id for album in albums if album.name == album_name] 
        if not album_id:
            sys.stdout.write("< No album named " + album_name + " ignoring > ")
        else:
            album_ids.append(album_id[0])

    return album_ids

def upload_photo(path, tagslist=[], albums=[], public=False):
    sys.stdout.write('uploading ' + path + " ")


    if albums:
        albums = get_album_ids(albums)


    # Convert list of tags to strings
    tags = list_to_string(tagslist)
    albums = list_to_string(albums)
    if CHECK_DUPLICATES_LOCALLY:
        if image_uploaded(path):
            sys.stdout.write('- already uploaded (preupload check) - Ok!\n')

            return False

    try:
        resp = client.photo.upload(path, tags=tags, albums=albums, permission=public)
    except TroveboxDuplicateError:
        sys.stdout.write('- already uploaded ')
    except TroveboxError, e:
        print e.message
        raise e
    except IOError, e:
        print e
        raise e

    sys.stdout.write('- Ok!\n')
    return True

def list_to_string(string_list):
    # Convert list to string
    joined_string = ','.join([str(item) for item in string_list])
    return joined_string

def hash_file(filepath):
    sha1 = hashlib.sha1()
    f = open(filepath, 'rb')
    try:
        sha1.update(f.read())
    finally:
        f.close()
    return sha1.hexdigest()

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", required=True, dest='path', help="Path to a file or directory to upload")
    parser.add_argument("-c", "--check-duplicates-locally", default=False, action="store_true", help="Check for aldready uploaded images locally, increases the time it takes initialize the program (depending on the number of files in your trovebox account) but will execute faster.")
    parser.add_argument("-t", "--tags", nargs='+',default=[], help="List of tags to add to the uploaded files")
    parser.add_argument("-a", "--albums", nargs='+',default=[], help="Albums to add the images to")
    parser.add_argument("-p", "--public",default=False,action="store_true", help="Make the images uploaded public, default False")

    args = parser.parse_args()
    global CHECK_DUPLICATES_LOCALLY

    CHECK_DUPLICATES_LOCALLY = args.check_duplicates_locally

    tags = args.tags
    path = args.path
    albums = args.albums
    public = args.public

    if is_folder(path):
        uploaded_files = upload_folder(path, tags, albums, public)
        print "\nUploaded", uploaded_files, "images from", path, "\n"
    else:
        upload_photo(path, tags, albums, public)


if __name__ == '__main__':
    main()
