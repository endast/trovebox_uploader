#!/usr/bin/env python
# encoding: utf-8
"""
trovebox-uploader.py

version 0.3.1

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

# Init
try:
    client = Trovebox()
    client.configure(api_version=2)

except IOError, E:
    print 'Could not connect to Trovebox'
    print 'Please check ~/.config/trovebox/default. More info: https://github.com/photo/openphoto-python'
    raise E

def is_folder(path):
    return os.path.isdir(path)


def image_uploaded(photo):
    res = client.photos.list(hash=hash_file(photo))
    if len(res) > 0:
        return True
    return False

def is_image(file):
    valid_types = ["jpg", "jpeg", "gif", "png"]
    try:
        image_type = imghdr.what(file)
    except IOError, e:
        return False

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
    for file in os.listdir(path):
        files.append(os.path.join(path, file))
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
        client.photo.upload(path.decode(sys.getfilesystemencoding()), tags=tags, albums=albums, permission=public)
    except TroveboxDuplicateError:
        if update_metadata:
            sys.stdout.write('- already uploaded, updating metadata - Ok')
            update_photo_metadata(path, tags, albums, public)
        else:
            sys.stdout.write('- already uploaded - Ok')
    except TroveboxError, e:
        print e.message
    except IOError, e:
        sys.stdout.write('- Failed!\n')
        print e

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

def recursive_search(rootdir):
    return [f[0] for f in os.walk(rootdir)]

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", required=True, dest='path', help="Path to a file or directory to upload. If directory, only uploads file in top level. To scan subfolders use -r")
    parser.add_argument("-c", "--check-duplicates-locally", default=False, action="store_true", help="Check for aldready uploaded images locally, increases number of request to the server, but can increase speed if you have duplicates in the images you are uploading.")
    parser.add_argument("-t", "--tags", nargs='+', default=[], help="List of tags to add to the uploaded files")
    parser.add_argument("-a", "--albums", nargs='+', default=[], help="Albums to add the images to")
    parser.add_argument("-p", "--public", default=False, action="store_true", help="Make the images uploaded public, default False")
    parser.add_argument("-r", "--recursive", default=False, action="store_true", help="Also upload subfolders if target is a folder, default False")

    args = parser.parse_args()
    global CHECK_DUPLICATES_LOCALLY

    CHECK_DUPLICATES_LOCALLY = args.check_duplicates_locally

    tags = args.tags
    path = args.path
    albums = args.albums
    public = args.public
    recursive = args.recursive
    
    if is_folder(path):
        if recursive:
            for folder in recursive_search(path):
                uploaded_files = upload_folder(folder, tags, albums, public)
                print "\nUploaded", uploaded_files, "images from", folder, "\n"
        else:
            uploaded_files = upload_folder(path, tags, albums, public)
            print "\nUploaded", uploaded_files, "images from", path, "\n"
    else:
        upload_photo(path, tags, albums, public)


if __name__ == '__main__':
    main()
