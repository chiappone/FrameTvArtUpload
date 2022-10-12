import sys
import logging
import os
import wakeonlan

sys.path.append('../')

from samsungtvws import SamsungTVWS

logging.basicConfig(level=logging.INFO)


def __runAllApi():
    # Increase debug level
    
    # Normal constructor

    # Is art mode supported?
    info = tv.art().supported()
    logging.info(info)

    # List the art available on the device
    info = tv.art().available()
    logging.info(info)

    # Retrieve information about the currently selected art
    info = tv.art().get_current()
    logging.info(info)

    # Retrieve a thumbnail for a specific piece of art. Returns a JPEG.
    thumbnail = tv.art().get_thumbnail('SAM-F0206')

    # Set a piece of art
    tv.art().select_image('SAM-F0206')

    # Set a piece of art, but don't immediately show it if not in art mode
    tv.art().select_image('SAM-F0201', show=False)

    # Determine whether the TV is currently in art mode
    info = tv.art().get_artmode()
    logging.info(info)

    # Switch art mode on or off
    tv.art().set_artmode(True)
    tv.art().set_artmode(False)

    # Upload a picture
    file = open('test.png', 'rb')
    data = file.read()
    tv.art().upload(data)

    # If uploading a JPEG
    tv.art().upload(data, file_type='JPEG')

    # To set the matte to modern and apricot color
    tv.art().upload(data, matte='modern_apricot')

    # Delete an uploaded item
    tv.art().delete('MY-F0020')

    # Delete multiple uploaded items
    tv.art().delete_list(['MY-F0020', 'MY-F0021'])

    # List available photo filters
    info = tv.art().get_photo_filter_list()
    logging.info(info)

    # Apply a filter to a specific piece of art
    tv.art().set_photo_filter('SAM-F0206', 'ink')

def upload_jpeg(filename):
    tv = authenticate()
    logging.info("reading file: "+ filename)
    file = open(filename, 'rb')
    data = file.read()
    tv.art().upload(data, file_type='JPEG')

def check_art_mode():
    tv = authenticate()
    return tv.art().available()

def authenticate():
    token_file = os.path.dirname(os.path.realpath(__file__)) + '/tv-token.txt'
    tv = SamsungTVWS(host='192.168.7.249', port=8002, token_file=token_file)
    wakeonlan.send_magic_packet('a4:30:7a:3a:47:fd')

    return tv
    

def main():

    global tv
    tv = authenticate()

    #tv = SamsungTVWS('192.168.7.249')

    #token_file = os.path.dirname(os.path.realpath(__file__)) + '/tv-token.txt'
    #tv = SamsungTVWS(host='192.168.7.249', port=8002, token_file=token_file)

    # Toggle power
    info = tv.art().available()
    logging.info(info)

    #check_art = tv.art().available()
    #logging.info(check_art)


if __name__ == '__main__':
    main()