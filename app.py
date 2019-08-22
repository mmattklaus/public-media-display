from flask import Flask, request, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import threading
import multiprocessing
import vlc
import time
import sys
if sys.version_info[0] == 2:  # the tkinter library changed it's name from Python 2 to 3.
    import Tkinter
    tkinter = Tkinter #I decided to use a library reference to avoid potential naming conflicts with people's programs.
else:
    import tkinter
from PIL import Image, ImageTk

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
ALLOWED_VIDEO_EXT = {'mp4', 'flv', 'mov', 'avi'}
ALLOWED_IMAGE_EXT = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS = ALLOWED_VIDEO_EXT.copy()
ALLOWED_EXTENSIONS.update(ALLOWED_IMAGE_EXT)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'lfosurtow6(&*&*&(ouwefhkusyiyo5yuoyrih'

current_process = None
temp_process = None

def allowed_file(filename, EXT_TYPES):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in EXT_TYPES


@app.route('/')
def home():
    return render_template('index.html', active_link='home')


@app.route('/about')
def about():
    return render_template('about.html', active_link='about')


@app.route('/services')
def service():
    return render_template('services.html', active_link='services')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        flash('Video not selected')
        return redirect(url_for('service'))
    file = request.files['video']
    if file.filename == '':
        flash('Video not selected')
        return redirect(url_for('service'))
    if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
        filename = secure_filename(file.filename)
        media_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(media_path)
        flash('Upload complete.')
        t = threading.Thread(target=play_content, args=(media_path,))
        t.start()
        # process = multiprocessing.Process(target=play_content, args=(media_path, ))
        #temp_process = process
        #process.start()
        # play_content(media_path)
        return redirect(url_for('service'))
    else:
        flash('Upload incomplete. Ensure that file extension is ' + ', '.join([e for e in ALLOWED_EXTENSIONS]))
        return redirect(url_for('service'))


# class MyThread(threading.Thread):#
    # def __init__(self, MyThread):
        


def play_content(media_path):
    global current_process
    thread = threading.currentThread()
    if current_process is not None:
        print(current_process.getName(), "----Name...")
        terminate_thread(current_process)
        print(current_process.getName(), "----Name...")
    current_process = thread
    # 1. Close all instances of player
    # 2. Check media type
    # 3. Open media in required program
    if allowed_file(media_path, ALLOWED_IMAGE_EXT):
        # Open image display
        pilImage = Image.open(media_path)
        showPIL(pilImage)
    elif allowed_file(media_path, ALLOWED_VIDEO_EXT):
        # Open video in player
        Instance = vlc.Instance('--fullscreen')
        player = Instance.media_player_new()
        Media = Instance.media_new(media_path)
        player.set_media(Media)
        player.play()
    pass

def showPIL(pilImage):
    root = tkinter.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.overrideredirect(1)
    root.geometry("%dx%d+0+0" % (w, h))
    root.focus_set()    
    root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))
    canvas = tkinter.Canvas(root,width=w,height=h)
    canvas.pack()
    canvas.configure(background='black')
    imgWidth, imgHeight = pilImage.size
    if imgWidth > w or imgHeight > h:
        ratio = min(w/imgWidth, h/imgHeight)
        imgWidth = int(imgWidth*ratio)
        imgHeight = int(imgHeight*ratio)
        pilImage = pilImage.resize((imgWidth,imgHeight), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(pilImage)
    imagesprite = canvas.create_image(w/2,h/2,image=image)
    root.mainloop()

import ctypes

def terminate_thread(thread):
    """Terminates a python thread from another thread.

    :param thread: a threading.Thread instance
    """
    if not thread.isAlive():
        return

    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        raise ValueError("nonexistent thread id")
    elif res > 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
    
if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='log.log', level=logging.DEBUG)
    app.run(host="0.0.0.0", debug=True)
