#!/usr/bin/env python
# encoding: utf-8
"""
trovebox-uploader.py

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

# Global
CHECK_DUPLICATES_LOCALLY = False
hashes = []


def is_folder(path):
    return os.path.isdir(path)

def is_image(file):
    valid_types = ["jpg","jpeg","gif","png"]
    image_type = imghdr.what(file)

    if image_type in valid_types:
        return True
    else:
        return False

def upload_folder(folder_path, tags=[]):
    uploaded_files = 0
    for file_path in scan_folder(folder_path):
        if is_image(file_path):
            if upload_photo(file_path, tags):
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

def upload_photo(path, tagslist=[]):
    sys.stdout.write('uploading ' + path + " ")

    # Convert list of tags to strings
    tags = ','.join([str(item) for item in tagslist])

    if CHECK_DUPLICATES_LOCALLY:
        if is_duplicate(path):
            sys.stdout.write('- already uploaded (local check) - Ok!\n')

            return False

    try:
        resp = client.photo.upload(path, tags=tags)
        #print resp
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

def get_photo_data():
    options = {"pageSize": "0"}
    photos = client.photos.list(options)
    return photos

def is_duplicate(photo):
    global hashes
    return hash_file(photo) in hashes

def get_hashes():
    hashes = []
    print "\nLoading photo data...\n"
    photos = get_photo_data()
    
    for photo in photos:
        hashes.append(str(photo.hash))
    return hashes

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

    args = parser.parse_args()
    global CHECK_DUPLICATES_LOCALLY
    global hashes

    CHECK_DUPLICATES_LOCALLY = args.check_duplicates_locally

    if args.check_duplicates_locally:
        hashes = get_hashes()

    tags = args.tags
    path = args.path

    if is_folder(path):
        uploaded_files = upload_folder(path, tags)
        print "\nUploaded", uploaded_files, "images from", path, "\n"
    else:
        upload_photo(path, tags)


if __name__ == '__main__':
    main()
