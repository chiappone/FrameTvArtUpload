import csv
import getopt
import os
import sys
from math import floor, trunc
from xmlrpc.client import boolean

import requests
from PIL import Image
from PIL import ImageFilter

import samsung_api


def check_artists(artist, artists):
    if (len(artists) == 0):
        return True
    else:
        return artist in artists


def check_types(piece_type, types):
    if (len(types) == 0):
        return True
    else:
        return piece_type in types


def check_object_num(object_num, num_list):
    return object_num in num_list


# returns list of csv lines that the artist matches


def match_lines(met_csv, artists, types, list_file):
    lines = []

    print(artists)
    if (list_file != ""):
        f = open(list_file, 'r')
        obj_num_list = []
        for line in f:
            obj_num_list.append(line.strip())

        for row in met_csv:
            if (check_object_num(row[0], obj_num_list)):
                lines.append(row)
    else:
        for row in met_csv:
            if (check_artists(row[14], artists) and check_types(row[24], types)):
                lines.append(row)

    return lines


def download_image(image_url, image_name, id):
    response = requests.get(image_url, stream=True)
    im = Image.open(response.raw) if response.status_code == 200 else None
    transform_image(im, image_name, id)


def truncate(number, decimals=0):
    factor = 10.0 ** decimals
    return trunc(number * factor) / factor


def transform_image(im, img_filepath, id):
    file_path = os.path.dirname(os.path.abspath(img_filepath))
    artist_file_path = os.path.join(file_path, artist)
    img_filename = os.path.basename(img_filepath)
    os.mkdir(artist_file_path) if not os.path.exists(artist_file_path) else None
    im_w, im_h = im.size
    saved_filename = os.path.splitext(artist_file_path + "/" + img_filename[:100])[0] + str(id) + ".jpg"
    saved_stretch_filename = os.path.splitext(artist_file_path + "/" + img_filename[:100])[0] + str(id) + "_stretched.jpg"
    ratio = im_w / im_h
    
    # check if image is 16:9 to apply transformation
    if (truncate(ratio, 2) != truncate(16 / 9, 2)):
        all_169 = False
    # create background by upscaling original image and blurring it
    im_w, im_h = im.size
    bg = im.resize((floor(im_w * (16 / 9 * 2)), floor(im_h * (16 / 9 * 2))))
    bg_w, bg_h = bg.size
    # bg = bg.filter(ImageFilter.GaussianBlur(radius=100))
    bg = Image.new('RGB', (bg_w, bg_h))
    # paste original image
    offset = ((bg_w - im_w) // 2, (bg_h - im_h) // 2)
    bg.paste(im, offset)


    # crop to 16:9
    left = (bg_w - floor(im_h * (16 / 9))) / 2
    top = (bg_h - im_h) / 2
    right = (bg_w + floor(im_h * (16 / 9))) / 2
    bottom = (bg_h + im_h) / 2
    dst = bg.crop((left, top, right, bottom))

    stretch_img = im.resize((3840, 2160))
    new_dst = dst.resize((3840, 2160))
    # save img
    print("\n-----------------------------------\n")
    print(saved_filename)
    new_dst.save(saved_filename)
    stretch_img.save(saved_stretch_filename)

    if upload_gd:
        gdrive_api.upload_jpeg(saved_filename)
        gdrive_api.upload_jpeg(saved_stretch_filename)
    if upload_tv:
        samsung_api.upload_jpeg(saved_stretch_filename)
    

def start_with_file(file, do_upload_tv, do_upload_gd):
    global artist
    global upload_tv
    global upload_gd
    img = Image.open(file)
    artist = "FrameTV"
    upload_tv = do_upload_tv
    upload_gd = do_upload_gd
    transform_image(img, file, 0)

def main(argv):

    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "a:t:l:s:f:gd:tv", ["artist=", "type=", "list=", "search=", "file="])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    global artist
    global search
    global upload_tv
    global upload_gd
    met_csv_file = ""
    out_dir = ""
    list_file = ""
    artists = []
    types = []
    file = None
    upload_tv = False
    upload_gd = False
    

    print("Opts")
    print(opts)

    for opt, arg in opts:
        if opt == "-gd":
            upload_gd = True
        elif opt == "-tv":
            upload_tv = True
        elif opt in ("--artist", "-a"):
            artists = arg.split(':')
            print("Artist in arg")
            print(artists)
        elif opt in ("--type", "-t"):
            types = arg.split(":")
        elif opt in ("--list", "-l"):
            list_file = arg
        elif opt in ("--search", "-s"):
            search = arg
            artists = [search]
        elif opt in ("--file", "-f"):
            file = arg


    # met_csv = csv.reader(open(met_csv_file, 'rb'), delimiter=',')

    # csv_lines = match_lines(met_csv, artists, types, list_file)

    if file:
        start_with_file(file)
    else:
        artist = artists[0]
        print("Artist to search for:")
        print(artist)


if __name__ == "__main__":
    main(sys.argv[1:])
