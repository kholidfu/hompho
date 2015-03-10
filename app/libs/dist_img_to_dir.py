#!/usr/bin/python
# TODO: import sys.argv sebagai sumber dari image yang sudah discrapy
# TODO: hinder duplicate domain scraped?
# TODO: limit 10000 per folder

import imghdr
import subprocess
import random
import os
import shutil
import sys
from PIL import Image
import pymongo
import datetime


# target path: /tmp/assets/large/0000000/fname
# target path: /tmp/assets/medium
# target path: /tmp/assets/thumb


# database things
# c = pymongo.Connection()
# db = c["hompho"]


def resize_and_crop(img_path, modified_path, size, crop_type='top'):
    """
    Resize and crop an image to fit the specified size.

    args:
        img_path: path for the image to resize.
        modified_path: path to store the modified image.
        size: `(width, height)` tuple.
        crop_type: can be 'top', 'middle' or 'bottom', depending on this
            value, the image will cropped getting the 'top/left', 'midle' or
            'bottom/rigth' of the image to fit the size.
    raises:
        Exception: if can not open the file in img_path of there is problems
            to save the image.
        ValueError: if an invalid `crop_type` is provided.

    ex:
    resize_and_crop(source, destination, (570, 363), crop_type='middle')
    """
    # If height is higher we resize vertically, if not we resize horizontally
    img = Image.open(img_path)
    # Get current and desired ratio for the images
    img_ratio = img.size[0] / float(img.size[1])
    ratio = size[0] / float(size[1])
    #The image is scaled/cropped vertically or horizontally depending on the ratio
    if ratio > img_ratio:
        img = img.resize((size[0], size[0] * img.size[1] / img.size[0]),
                Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, img.size[0], size[1])
        elif crop_type == 'middle':
            box = (0, (img.size[1] - size[1]) / 2, img.size[0], (img.size[1] + size[1]) / 2)
        elif crop_type == 'bottom':
            box = (0, img.size[1] - size[1], img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    elif ratio < img_ratio:
        img = img.resize((size[1] * img.size[0] / img.size[1], size[1]),
                Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, size[0], img.size[1])
        elif crop_type == 'middle':
            box = ((img.size[0] - size[0]) / 2, 0, (img.size[0] + size[0]) / 2, img.size[1])
        elif crop_type == 'bottom':
            box = (img.size[0] - size[0], 0, img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    else :
        img = img.resize((size[0], size[1]),
                Image.ANTIALIAS)
        # If the scale is the same, we do not need to crop
    img.save(modified_path)


# dominant color finder start #
# tribute: http://charlesleifer.com/blog/using-python-and-k-means-to-find-the-dominant-colors-in-images/

from collections import namedtuple
from math import sqrt

Point = namedtuple('Point', ('coords', 'n', 'ct'))
Cluster = namedtuple('Cluster', ('points', 'center', 'n'))


def get_points(img):
    points = []
    w, h = img.size
    for count, color in img.getcolors(w * h):
        points.append(Point(color, 3, count))
    return points

rtoh = lambda rgb: '#%s' % ''.join(('%02x' % p for p in rgb))


def colorz(filename, n=3):
    img = Image.open(filename)
    img.thumbnail((200, 200))
    w, h = img.size

    points = get_points(img)
    clusters = kmeans(points, n, 1)
    rgbs = [map(int, c.center.coords) for c in clusters]
    return map(rtoh, rgbs)


def euclidean(p1, p2):
    return sqrt(sum([
        (p1.coords[i] - p2.coords[i]) ** 2 for i in range(p1.n)
    ]))


def calculate_center(points, n):
    vals = [0.0 for i in range(n)]
    plen = 0
    for p in points:
        plen += p.ct
        for i in range(n):
            vals[i] += (p.coords[i] * p.ct)
    return Point([(v / plen) for v in vals], n, 1)


def kmeans(points, k, min_diff):
    clusters = [Cluster([p], p, p.n) for p in random.sample(points, k)]

    while 1:
        plists = [[] for i in range(k)]

        for p in points:
            smallest_distance = float('Inf')
            for i in range(k):
                distance = euclidean(p, clusters[i].center)
                if distance < smallest_distance:
                    smallest_distance = distance
                    idx = i
            plists[idx].append(p)

        diff = 0
        for i in range(k):
            old = clusters[i]
            center = calculate_center(plists[i], old.n)
            new = Cluster(plists[i], center, old.n)
            clusters[i] = new
            diff = max(diff, euclidean(old.center, new.center))

        if diff < min_diff:
            break

    return clusters

# dominant color finder end #


container = []
dir_count = 101  # jumlah direktory
nums = 10000  # jumlah file per directory, so total == 1jt file


def dir_creation():
    """
    create directory if not exists 000000 - 1000000, kelipatan tiap 10000
    artinya di tiap direktori nantinya akan berisi 10000 gambar homebrenx
    :return:
    """
    for i in range(dir_count):
        dir_name = str(i * nums)
        max_len = len(str(nums * dir_count))
        # if the len is equal, add stright forward
        if len(dir_name) == max_len:
            container.append(dir_name)
        while len(dir_name) < max_len:
            # tambahkan angka 0 sampai len(dir_name) == max_len
            dir_name = "0" + dir_name
            if len(dir_name) == max_len:
                container.append(dir_name)
                break
    return container

dirs = dir_creation()

# now we have images, a lot of images, I want to move randomly
# each image to directory name we have created
# steps:
# for each image in list of images:
# - clear metadata
# - add metadata
# - create a folder (random) if not exists
# - shutil move image to random dirs
# - prevent duplicate filename
# - create thumbnail
# - insert into db
# hope this will distribute evenly

# create an assets dir container
# home = os.path.expanduser("~")
# home = os.path.dirname(os.path.abspath(__file__))  # ~/git/homedec/ atau jika di server ~/homedec/
home = os.getcwd()
asset_dir = os.path.join(home, "assets")

if not os.path.exists(os.path.join(asset_dir, "large")):
    os.makedirs(os.path.join(asset_dir, "large"))
if not os.path.exists(os.path.join(asset_dir, "medium")):
    os.makedirs(os.path.join(asset_dir, "medium"))
if not os.path.exists(os.path.join(asset_dir, "thumb")):
    os.makedirs(os.path.join(asset_dir, "thumb"))

## create a random choice directory if not exists
fname = sys.argv[1]

## number of image[s] to post
# num_imgs = int(sys.argv[2])

# get random dirs
random_dirs = random.choice(dirs)
# random_dirs = "0560000"

# building paths
path_to_exiftool = os.path.join(os.path.expanduser("~"), "Downloads/Image-ExifTool-9.71/./exiftool")
path_to_source_file = fname
path_to_target_dir = os.path.join(asset_dir, "large", random_dirs)
path_to_medium_dir = os.path.join(asset_dir, "medium", random_dirs)
path_to_thumb_dir = os.path.join(asset_dir, "thumb", random_dirs)

# create random dirs
if not os.path.exists(path_to_target_dir):
    os.makedirs(path_to_target_dir)
if not os.path.exists(path_to_medium_dir):
    os.makedirs(path_to_medium_dir)
if not os.path.exists(path_to_thumb_dir):
    os.makedirs(path_to_thumb_dir)

# clear and add additional meta data
### path_to_new_fname = os.path.join(path_to_target_dir, os.path.splitext(fname)[0] + "." + ftype)
exif_clear_meta_command = path_to_exiftool + " -all= -overwrite_original " + path_to_source_file
command_list = exif_clear_meta_command.split()
subprocess.call(command_list)

# get original filetype, hard code, mau gmn lagee?
ftype = subprocess.check_output(path_to_exiftool.split() + ["-*File*Type*"] + path_to_source_file.split())
ftype = ftype.split()[-1].lower()

# move the file
new_fname = os.path.splitext(os.path.basename(fname))[0] + "." + ftype
if not os.path.exists(os.path.join(path_to_target_dir, new_fname)):  # fname.jpeg
    shutil.move(fname, os.path.join(path_to_target_dir, new_fname))
# else if exists, resolve filename conflict then move
else:
    # resolve filename conflict
    name = os.path.basename(fname).rsplit(".", 1)[0]
    count = 0
    while True:
        count += 1
        new_fname = "%s-dupe%d.%s" % (name, count, ftype)
        if not os.path.exists(os.path.join(path_to_target_dir, new_fname)):
            shutil.move(fname, os.path.join(path_to_target_dir, new_fname))
            break

# thumbnailing goes here, nama thumbnail(medium) sesuai dengan nama yang sudah fix
# build necessary paths
path_to_ori_file = os.path.join(path_to_target_dir, new_fname)
path_to_medium_file = os.path.join(path_to_medium_dir, new_fname)
path_to_thumb_file = os.path.join(path_to_thumb_dir, new_fname)
# start thumbnailing
resize_and_crop(path_to_ori_file, path_to_medium_file, (842, 559), crop_type='middle')
resize_and_crop(path_to_ori_file, path_to_thumb_file, (370, 278), crop_type='middle')

# get dominant color
colors = []
try:
    colors = colorz(path_to_ori_file, 5)
except:
    pass

# inserting into mongo
# building all data needed
title = os.path.basename(path_to_ori_file).rsplit(".", 1)[0].replace("-", " ")
# category, deteksi jika ada keyword tertentu di filename
if "interior" in path_to_ori_file:
    category = "interior"
elif "bath" in path_to_ori_file:
    category = "bathroom"
elif "bed" in path_to_ori_file:
    category = "bedroom"
elif "element" in path_to_ori_file:
    category = "home element"
elif "kitchen" in path_to_ori_file:
    category = "kitchen"
elif "archit" in path_to_ori_file:
    category = "architecture"
elif "garden" in path_to_ori_file:
    category = "gardening"
elif "dining" in path_to_ori_file:
    category = "dining room"
elif "living" in path_to_ori_file:
    category = "living room"
elif "office" in path_to_ori_file:
    category = "office"
else:
    category = "others"

usernames = [
    "homekettle",
    "homeglide",
    "homedoylt",
    "cartloadhoe ",
    "homeagenda",
    "homefamily",
    "homeshrivel",
    "ponderhome",
    "homesloth",
    "homemuse",
    "homeslate",
    "knothome",
    "homedisgusing ",
    "descenthome",
    "homeharras",
    "homespan",
    "downhome",
    "homelead",
    "homekindle ",
    "homerag ",
    "huskhome",
    "hometroup",
    "homesimpliity ",
    "homepanel",
    "douthome",
    "homeimpatence ",
    "convertinghome",
    "homecharm",
    "virtuehome",
    "smuthhome",
    "fleethome",
    "homeprickl ",
    "homescolding",
    "homefanfare",
    "reamhome",
    "unctionhoe ",
    "hometeam",
    "homefelloship ",
    "homesiege",
    "chainhome",
    "homestand ",
    "hometrembling ",
    "corpshome ",
    "homefollowing ",
    "homebury ",
    "gagglehome ",
    "homenide ",
    "troublinghme ",
    "libraryhome",
    "cadgehom",
]

# db.home.insert({
#     "title": title,
#     "category": category,
#     "tags": [i.strip() for i in os.path.basename(path_to_ori_file).rsplit(".", 1)[0].split("-")],
#     "hits": 0,
#     "favor": 0,  # jumlah visitor yang memfavorite gambar ini
#     "fpath": os.path.join(random_dirs, new_fname),  # /084000/filename.jpeg, ntar tinggal nambahin /assets/large/ atau /assets/medium/ atau /assets/small/
#     "fsize": os.path.getsize(path_to_ori_file),
#     "fext": imghdr.what(path_to_ori_file),
#     "fresx": Image.open(path_to_ori_file).size[0],
#     "fresy": Image.open(path_to_ori_file).size[1],
#     "download": 0,  # download counter
#     "author": random.choice(usernames),
#     "added": datetime.datetime.now(),
#     "voteup": 0,
#     "votedown": 0,
#     "favorited_by": [],  # list username yang memfavorit wallpaper ini
#     "colors": colors,
# })
