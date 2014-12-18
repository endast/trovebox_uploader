#!/usr/bin/env python
# encoding: utf-8
"""
trovebox-uploader.py

version 0.4.2

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
    print 'Please check ~/.config/trovebox/default.'
    print 'More info: https://github.com/photo/openphoto-python'
    raise E

def is_folder(path):
    return os.path.isdir(path)


def image_uploaded(photo, return_data=False):
    res = client.photos.list(hash=hash_file(photo))

    if return_data:
        return res

    if len(res) > 0:
        return True
    return False

def is_image(file_path):
    valid_types = ["jpg", "jpeg", "gif", "png"]
    try:
        image_type = imghdr.what(file_path)
    except IOError, E:
        return False

    if image_type in valid_types:
        return True
    else:
        return False

def upload_folder(folder_path, tagslist=[], albums=[],
    public=False, update_metadata=False):

    if albums:
        albums = get_album_ids(albums)

    # Convert list of tags to strings
    tags = list_to_string(tagslist)
    albums = list_to_string(albums)

    uploaded_files = 0
    for file_path in scan_folder(folder_path):
        if is_image(file_path):
            if upload_photo(file_path, tags, albums, public, update_metadata):
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
    albums = client.albums.list(pageSize=1000)
    album_ids = []

    for album_name in album_names:
        album_id = [album.id for album in albums if album.name == album_name]
        if not album_id:
            sys.stderr.write("< No album named " + album_name + " ignoring > ")
        else:
            album_ids.append(album_id[0])

    return album_ids

def upload_single_photo(path, tagslist=[], albums=[],
    public=False, update_metadata=False):

    if albums:
        albums = get_album_ids(albums)

    # Convert list of tags to strings
    tags = list_to_string(tagslist)
    albums = list_to_string(albums)

    upload_photo(path, tags, albums, public, update_metadata)

def upload_photo(path, tags, albums, public, update_metadata):

    sys.stderr.write('uploading ' + path + " ")

    if CHECK_DUPLICATES_LOCALLY:
        if image_uploaded(path):
            if update_metadata:
                sys.stderr.write('- already uploaded (preupload check), updating metadata')
                update_photo_metadata(path, tags, albums, public)
                return False
            else:
                sys.stderr.write('- already uploaded (preupload check) - Ok!\n')
                return False

    try:
        client.photo.upload(path.decode(sys.getfilesystemencoding()),
            tags=tags, albums=albums, permission=public)

        sys.stderr.write('- Ok!\n')

    except TroveboxDuplicateError:
        if update_metadata:
            sys.stderr.write('- already uploaded, updating metadata')
            update_photo_metadata(path, tags, albums, public)
            return False
        else:
            sys.stderr.write('- already uploaded - Ok\n')
    except TroveboxError, e:
        print e.message
    except IOError, e:
        sys.stderr.write('- Failed!\n')
        print e

    return True

def update_photo_metadata(path, tags, albums, public):
    photo = image_uploaded(path, True)
    
    # Add albums if needed
    if albums:
        for album in albums.split(","):
            try:
                client.album.add(album, photo, "photo")
            except TroveboxError, e:
                print e
                sys.stderr.write('- Failed!\n')

    try:
        client.photo.update(photo[0], tags=tags, permission=public)
        sys.stderr.write(' - Ok\n')
    except TroveboxError, e:
        sys.stderr.write('- Failed!\n')
        print e.message
    except IOError, e:
        sys.stderr.write('- Failed!\n')
        print e

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
    parser.add_argument("-u", "--update-metadata", default=False, action="store_true", help="Also update metadata for images aldready uploaded. (Tags, albums etc)")

    args = parser.parse_args()
    
    global CHECK_DUPLICATES_LOCALLY

    CHECK_DUPLICATES_LOCALLY = args.check_duplicates_locally

    tags = args.tags
    path = args.path
    albums = args.albums
    public = args.public
    recursive = args.recursive
    update_metadata = args.update_metadata
    
    if is_folder(path):
        if recursive:
            for folder in recursive_search(path):
                uploaded_files = upload_folder(folder, tags, albums, public, update_metadata)
                print "\nUploaded", uploaded_files, "images from", folder, "\n"
        else:
            uploaded_files = upload_folder(path, tags, albums, public, update_metadata)
            print "\nUploaded", uploaded_files, "images from", path, "\n"
    else:
        upload_single_photo(path, tags, albums, public, update_metadata)


if __name__ == '__main__':
    main()
