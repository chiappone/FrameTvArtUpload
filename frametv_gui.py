from multiprocessing.connection import wait
from time import sleep
import PySimpleGUI as sg
# import PySimpleGUIQt as sg
import os.path
import PIL.Image
import io
import base64
import frametv_uploader
import samsung_api

"""
    Demo for displaying any format of image file.
    
    Normally tkinter only wants PNG and GIF files.  This program uses PIL to convert files
    such as jpg files into a PNG format so that tkinter can use it.
    
    The key to the program is the function "convert_to_bytes" which takes a filename or a 
    bytes object and converts (with optional resize) into a PNG formatted bytes object that
    can then be passed to an Image Element's update method.  This function can also optionally
    resize the image.
    
    Copyright 2020 PySimpleGUI.org
"""

sg.theme('dark grey 9')
#animate = True

def convert_to_bytes(file_or_bytes, resize=None):
    '''
    Will convert into bytes and optionally resize an image that is a file or a base64 bytes object.
    Turns into  PNG format in the process so that can be displayed by tkinter
    :param file_or_bytes: either a string filename or a bytes base64 image object
    :type file_or_bytes:  (Union[str, bytes])
    :param resize:  optional new size
    :type resize: (Tuple[int, int] or None)
    :return: (bytes) a byte-string object
    :rtype: (bytes)
    '''
    if isinstance(file_or_bytes, str):
        img = PIL.Image.open(file_or_bytes)
    else:
        try:
            img = PIL.Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
        except Exception as e:
            dataBytesIO = io.BytesIO(file_or_bytes)
            img = PIL.Image.open(dataBytesIO)

    cur_width, cur_height = img.size
    if resize:
        img = img.resize((int(resize[0]), int(resize[1])), PIL.Image.ANTIALIAS)
        #scale = min(new_height/cur_height, new_width/cur_width)
        #img = img.resize((int(cur_width*scale), int(cur_height*scale)), PIL.Image.ANTIALIAS)
    with io.BytesIO() as bio:
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()

def do_upload():
    # print(f'File to upload {filename}')
    frametv_uploader.start_with_file(filename, True, False)

def test_connection():
    try:
        samsung_api.check_art_mode()
        window['-TOUT-'].update('Connection Established')
    except Exception as E:
        print(f'Exception {E}')
        window['-TOUT-'].update('Connection Failure')

def load_and_resize_image():
    try:
        # print(f'File to resize {filename}')
        window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=(3840, 2160)))
    except Exception as E:
        print(f'** Error {E} **')
        pass        # something weird happened making the full filename

def show_loading_image(text):
    sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, text, time_between_frames=100)
    window.write_event_value('-ANIMATE-', text)

# --------------------------------- Define Layout ---------------------------------

# First the window layout...2 columns

left_col = [[sg.Text('Folder'), sg.In(size=(25,1), enable_events=True ,key='-FOLDER-'), sg.FolderBrowse()],
            [sg.Listbox(values=[], enable_events=True, size=(40,20),key='-FILE LIST-')],
            [sg.Button('Test FrameTV Connection'), sg.Button('Upload')]]

# For now will only show the name of the file that was chosen
images_col = [[sg.Text(size=(80,1), key='-TOUT-')],
              [sg.Image(key='-IMAGE-')]]

# ----- Full layout -----
layout = [[sg.Column(left_col, element_justification='c'), sg.VSeperator(),sg.Column(images_col, element_justification='c')]]

# --------------------------------- Create Window ---------------------------------
window = sg.Window('JPEG Image Uploader for FrameTV', layout,resizable=True)


# ----- Run the Event Loop -----
# --------------------------------- Event Loop ---------------------------------
while True:
    event, values = window.Read(timeout=100)

    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == '-DONE-':
        animate = False
        sg.popup_animated(None)
    elif event == 'Upload':
        window.perform_long_operation(do_upload, '-DONE-')
        animate = True
        show_loading_image('Uploading to FrameTV')
    elif event == 'Test FrameTV Connection':
        window.perform_long_operation(test_connection, '-DONE-')
        animate = True
        show_loading_image('Connecting')
    elif event == '-FOLDER-':                         # Folder name was filled in, make a list of files in the folder
        folder = values['-FOLDER-']
        try:
            file_list = os.listdir(folder)         # get list of files in folder
        except:
            file_list = []
        fnames = [f for f in file_list if os.path.isfile(
            os.path.join(folder, f)) and f.lower().endswith((".jpg", "jpeg"))]
        window['-FILE LIST-'].update(fnames)
    elif event == '-FILE LIST-':    # A file was chosen from the listbox
        filename = os.path.join(values['-FOLDER-'], values['-FILE LIST-'][0])
        window['-TOUT-'].update(filename)
        window.perform_long_operation(load_and_resize_image, '-DONE-')
        animate = True
        show_loading_image('Loading Image')
    elif event == '-ANIMATE-':
        if animate:
            show_loading_image(values.get(event))

        

# --------------------------------- Close & Exit ---------------------------------
window.close()