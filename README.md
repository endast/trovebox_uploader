# Trovebox Uploader

## What is this?
This is a script for uploading images/folder of images to a Trovebox (https://github.com/photo) server.

## Requirements
* Python 2.7
* Trovebox Python Library 

## Installation
Install the Trovebox Python Library

    pip install trovebox 

Clone the repo or just download the file trovebox-uploader.py

    git clone https://github.com/endast/trovebox_uploader.git

## Usage

First make sure you have specified the credentials 
file in ``~/.config/trovebox/default``

    # ~/.config/trovebox/default
    host = your.host.com
    consumerKey = your_consumer_key
    consumerSecret = your_consumer_secret
    token = your_access_token
    tokenSecret = your_access_token_secret

for more info see https://github.com/photo/openphoto-python/

Simplest use case, just upload the specified image or folder of images:

    python trovebox-uploader.py -i path_to_image_or_folder

Adding the tags 42 and Panic to the image/images:

    python trovebox-uploader.py -i path_to_image_or_folder -t 42 Panic

Adding the image/images to album Dead_Parrot:

    python trovebox-uploader.py -i path_to_image_or_folder -a Dead_Parrot

Check if the image is a duplicate before uploading the image to the server, makes an extra request to the server. But can save you time, if you have duplicates in your source. Default off:

    python trovebox-uploader.py -i path_to_image_or_folder -c


Making the uploaded images public:
    
    python trovebox-uploader.py -i path_to_image_or_folder -p

Also upload subfoldrs from folder:
    
    python trovebox-uploader.py -i path_to_folder -r


You can of course combine all of the arguments:

    python trovebox-uploader.py -i black_knight.jpg -c -p -t pass none shall -a Grail


## Help
    usage: trovebox-uploader.py [-h] -i PATH [-c] [-t TAGS [TAGS ...]]
                                [-a ALBUMS [ALBUMS ...]] [-p]
    
    optional arguments:
      -h, --help            show this help message and exit
      -i PATH, --input PATH
                            Path to a file or directory to upload
      -c, --check-duplicates-locally
                            Check for aldready uploaded images locally, increases
                            number of request to the server, but can increase
                            speed if you have duplicates in the images you are
                            uploading.
      -t TAGS [TAGS ...], --tags TAGS [TAGS ...]
                            List of tags to add to the uploaded files
      -a ALBUMS [ALBUMS ...], --albums ALBUMS [ALBUMS ...]
                            Albums to add the images to
      -p, --public          Make the images uploaded public, default False
      -r, --recursive       Also upload subfolders if target is a folder, default False

## Pro tip
Using taskspooler you can queue upload jobs easily:

    ts python trovebox-uploader.py -i path_to_image_or_folder

To check the progress of your uploads just run:
    
    $ ts
    ID   State      Output               E-Level  Times(r/u/s)   Command [run=0/1]
    0    running   /tmp/ts-out.FdbteW   1        0.14/0.09/0.04 python trovebox-uploader.py -i path_to_image_or_folder
    1    queued   /tmp/ts-out.KsOrSJ   1        0.13/0.09/0.04 python trovebox-uploader.py -i knight.jpg
    2    finished   /tmp/ts-out.kjHEMT   1        0.14/0.09/0.04 python trovebox-uploader.py -i knights.jpg -t ni


You can install taskspooler on OSX with homebrew:

    brew install task-spooler

For more info on tasospooler visit: http://vicerveza.homeunix.net/~viric/soft/ts/

## Versions
0.3 - Added -r option, search subfolders

0.2 - Added support for permissions and albums

0.1 - First version
