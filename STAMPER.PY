#! /usr/bin/python
# -*- coding: utf-8 -*-
#   ____   _______      __         ___    ___    ___    ______    ____
#  /  __| |___ ___|    /  \       |   \  /   |  |   \  | |____|  |    \
#  | |       | |      / __ \      | |\ \/ /| |  | |\ | | |__     | |\  |
#   \ \      | |     / /  \ \     | | \__/ | |  | |/ | | |  |    | |/  |
#    \ \     | |    / /____\ \    | |      | |  |  _/  | |__|    |    /
#   __| |    | |   / /______\ \   | |      | |  | |    | |____   | |\ \
#  |___/     |_|  /_/        \_\  |_|      |_|  |_|    |______|  |_| \_\
# Stamper,
#this program is a modified version of "tkinter example for VLC Python bindings" and it inherts all of it's licenses.
# It's main purpouse is to create HTML files opening a video of your choice and pausing it at set points (called: STAMPS)
# "Open" and "Export" are located under "File" menu
# "Stamp" button adds a point at which the video should pause
# "Delete" will remove the current stamp, or if you're not currently on a stamp it will delete the last one on the list (presumably the last created)
# "Prev" and "Next" will move between frames, you may specify how many miliseconds per frame you video has in the mpf variable
# "PS" an "NS" will move you between stamps
# "Pointers" checkbox if selected will add three coloured cursors (You'll have to copy them to the same directory) 

#The HTML file will be named like the first word before any whitespaces in the name of the video (+.html)
#The title of will be the name of the video
#The video must be in the same directory as the HTML file, same gose for pointer files
 
# Based on:
# tkinter example for VLC Python bindings
# Copyright (C) 2015 the VideoLAN team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#
"""A simple example for VLC python bindings using tkinter. Uses python 3̶.̶4̶  3.6

Author of vlc tkinter example: Patrick Fay
Date: 23-09-2015
Author of Stamper: Paweł Chmielewski
Date: 06-05-2019
"""

# import external libraries
import vlc
import sys

if sys.version_info[0] < 3:
    import Tkinter as Tk
    from Tkinter import ttk
    from Tkinter.filedialog import askopenfilename
else:
    import tkinter as Tk
    from tkinter import ttk
    from tkinter.filedialog import askopenfilename

# import standard libraries
import os
import pathlib
from threading import Thread, Event
import time
import platform
mpf = 33 #Milisecond per frame
stamps = [0.0]
fnam = "unknown"
html0 = """<html>
<head>
<title>"""
#The style shall be changed at a later date
html1 = """</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
#myVideo {
    position: fixed;
	right: 0;
    bottom: 0;
  min-width: 100%;
    min-height: 100%;

}

</style>
</head>
<body>
"""

html2 = """
<script>
var video = document.getElementsByTagName("video")[0];
"""
html3 = """
    index = 0,
    currentStopTime = points[index];

// start video using: video.currentTime = points[0], then video.play()

// run this from a timeupdate event or per frame using requestAnimationFrame
video.ontimeupdate = function() {
    if (video.currentTime >= currentStopTime) {
        video.pause();
        if (points.length > ++index) {       
            currentStopTime = points[index]
        }
        else {                               
        }
    } else {
	}
};

function vidPlay(){
	if (video.paused){
	video.play();
	} else {
	video.pause();
	}
};
document.onkeydown = checkKey;

function checkKey(e) {

    e = e || window.event;
	
    if (e.keyCode == '70') {
        //f

		if (video.requestFullscreen) {
		video.requestFullscreen();
		} else if (video.mozRequestFullScreen) {
		video.mozRequestFullScreen();
		} else if (video.webkitRequestFullscreen) {
		  video.webkitRequestFullscreen();
		} else if (video.msRequestFullscreen) { 
		video.msRequestFullscreen();
}
    }
    else if (e.keyCode == '77') {
        //m
		if (video.muted) {
			video.muted = false;
		} else {
			video.muted = true;
		}
    }
    else if (e.keyCode == '37'||e.keyCode == '89' ||e.keyCode == '33	') {
       // back
	   if (index > 1) {
	   --index;
       var prind = --index;
	   currentStopTime = points[index];
	   video.currentTime = points[prind];
	   };
    }
    else if (e.keyCode == '39'||e.keyCode == '73') {
		//further
 	   if (index <= points.length) {
	   ++index;
       var prind = --index;
	   currentStopTime = points[index];
	   video.currentTime = points[prind];
	   };
    }

    else if (e.keyCode == '32'||e.keyCode == '85' ||e.keyCode == '34') {
	//continue
       video.play()
    }
"""
lasers = """
	else if (e.keyCode == '82'){
	//red laser
		document.body.style.cursor = "url(lasr.png), auto";
	}
	else if (e.keyCode == '71'){
	//green laser
		document.body.style.cursor = "url(lasg.png), auto";
	}
	else if (e.keyCode == '66'){
	//blue laser
		document.body.style.cursor = "url(lasb.png), auto";
	}
"""

html4 = """
	else if (e.keyCode == '69'){
	//no laser
		document.body.style.cursor = "none";
	}
    else if (e.keyCode == '84') {
       // beginning
	   index = 1
	   currentStopTime = points[2];
	   video.currentTime = points[index];
	   }
    else if (e.keyCode == '79') {
		//end
 	   index = points.length;
       var prind = --index;
	   currentStopTime = points[index];
	   video.currentTime = points[prind];
    };
}
</script>
</body>
</html>"""


las = 0
class ttkTimer(Thread):
    """a class serving same function as wxTimer... but there may be better ways to do this
    """
    def __init__(self, callback, tick):
        Thread.__init__(self)
        self.callback = callback
        self.stopFlag = Event()
        self.tick = tick
        self.iters = 0

    def run(self):
        while not self.stopFlag.wait(self.tick):
            self.iters += 1
            self.callback()

    def stop(self):
        self.stopFlag.set()

    def get(self):
        return self.iters

class Player(Tk.Frame):
    """The main window has to deal with events.
    """
    def __init__(self, parent, title=None):
        global las
        Tk.Frame.__init__(self, parent)

        self.parent = parent

        if title == None:
            title = "tk_vlc"
        self.parent.title(title)
        las = Tk.IntVar()
        # Menu Bar
        #   File Menu
        menubar = Tk.Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu = Tk.Menu(menubar)
        fileMenu.add_command(label="Open", underline=0, command=self.OnOpen)
        fileMenu.add_command(label="Export", underline=1, command=self.OnExport)        
        fileMenu.add_command(label="Exit", underline=1, command=_quit)
        menubar.add_cascade(label="File", menu=fileMenu)

        # The second panel holds controls
        self.player = None
        self.videopanel = ttk.Frame(self.parent)
        self.canvas = Tk.Canvas(self.videopanel).pack(fill=Tk.BOTH,expand=1)
        self.videopanel.pack(fill=Tk.BOTH,expand=1)
        ctrlpanel = ttk.Frame(self.parent)
        
        laschk = ttk.Checkbutton(ctrlpanel, text="Pointers", variable=las)

        self.volume_var = Tk.IntVar()
        self.volslider = Tk.Scale(ctrlpanel, variable=self.volume_var, command=self.volume_sel,
                from_=0, to=100, orient=Tk.HORIZONTAL, length=100)
        self.volslider.pack(side=Tk.LEFT)
        laschk.pack(side=Tk.LEFT)

        ctrlpanel.pack(side=Tk.BOTTOM)
        ctrlpanel0 = ttk.Frame(self.parent)
        pause  = ttk.Button(ctrlpanel0, text="Pause", command=self.OnPause)
        play   = ttk.Button(ctrlpanel0, text="Play", command=self.OnPlay)
        stop   = ttk.Button(ctrlpanel0, text="Stop", command=self.OnStop)
        volume = ttk.Button(ctrlpanel0, text="Volume", command=self.OnSetVolume)


        pause.pack(side=Tk.LEFT)
        play.pack(side=Tk.LEFT)
        stop.pack(side=Tk.LEFT)

        #volume.pack(side=Tk.LEFT)



        ctrlpanel0.pack(side=Tk.BOTTOM)

        ctrlpanel1 = ttk.Frame(self.parent)
        nstamp = ttk.Button(ctrlpanel1, text="NS", command=self.OnNextStamp)
        rm = ttk.Button(ctrlpanel1, text="Delete", command=self.OnDelete)
        pstamp = ttk.Button(ctrlpanel1, text="PS", command=self.OnPrevStamp)
        pstamp.pack(side=Tk.LEFT)
        rm.pack(side=Tk.LEFT)
        nstamp.pack(side=Tk.LEFT)
        ctrlpanel1.pack(side=Tk.BOTTOM)



        ctrlpanel2 = ttk.Frame(self.parent)

        pf = ttk.Button(ctrlpanel2, text="Prev", command=self.OnPrevFrame)
        stamp = ttk.Button(ctrlpanel2, text="Stamp", command=self.OnAddStamp)
        nf = ttk.Button(ctrlpanel2, text="Next", command=self.OnNextFrame)
       

        pf.pack(side=Tk.LEFT)
        stamp.pack(side=Tk.LEFT)

        nf.pack(side=Tk.LEFT)
        

        ctrlpanel2.pack(side=Tk.BOTTOM)

        ctrlpanel3 = ttk.Frame(self.parent)
        self.scale_var = Tk.DoubleVar()
        self.timeslider_last_val = ""
        self.timeslider = Tk.Scale(ctrlpanel3, variable=self.scale_var, command=self.scale_sel,
                from_=0, to=1000, orient=Tk.HORIZONTAL, length=500)
        self.timeslider.pack(side=Tk.BOTTOM, fill=Tk.X,expand=1)
        self.timeslider_last_update = time.time()
        ctrlpanel3.pack(side=Tk.BOTTOM,fill=Tk.X)


        # VLC player controls
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()

        # below is a test, now use the File->Open file menu
        #media = self.Instance.media_new('output.mp4')
        #self.player.set_media(media)
        #self.player.play() # hit the player button
        #self.player.video_set_deinterlace(str_to_bytes('yadif'))

        self.timer = ttkTimer(self.OnTimer, 1.0)
        self.timer.start()
        self.parent.update()

        #self.player.set_hwnd(self.GetHandle()) # for windows, OnOpen does does this


    def OnExit(self, evt):
        """Closes the window.
        """
        self.Close()

    def OnOpen(self):
        """Pop up a new dialow window to choose a file, then play the selected file.
        """
        # if a file is already running, then stop it.
        self.OnStop()
        global fnam
        # Create a file dialog opened in the current home directory, where
        # you can display all kind of files, having as title "Choose a file".
        p = pathlib.Path(os.path.expanduser("~"))
        fullname =  askopenfilename(initialdir = p, title = "choose your file",filetypes = (("all files","*.*"),("mp4 files","*.mp4")))
        if os.path.isfile(fullname):
            dirname  = os.path.dirname(fullname)
            filename = os.path.basename(fullname)
            fnam = filename
            # Creation
            self.Media = self.Instance.media_new(str(os.path.join(dirname, filename)))
            self.player.set_media(self.Media)
            # Report the title of the file chosen
            #title = self.player.get_title()
            #  if an error was encountred while retriving the title, then use
            #  filename
            #if title == -1:
            #    title = filename
            #self.SetTitle("%s - tkVLCplayer" % title)

            # set the window id where to render VLC's video output
            if platform.system() == 'Windows':
                self.player.set_hwnd(self.GetHandle())
            else:
                self.player.set_xwindow(self.GetHandle()) # this line messes up windows
            # FIXME: this should be made cross-platform
            self.OnPlay()

            # set the volume slider to the current volume
            #self.volslider.SetValue(self.player.audio_get_volume() / 2)
            self.volslider.set(self.player.audio_get_volume())

    def OnPlay(self):
        """Toggle the status to Play/Pause.
        If no file is loaded, open the dialog window.
        """
        # check if there is a file to play, otherwise open a
        # Tk.FileDialog to select a file
        if not self.player.get_media():
            self.OnOpen()
        else:
            # Try to launch the media, if this fails display an error message
            if self.player.play() == -1:
                self.errorDialog("Unable to play.")

    def GetHandle(self):
        return self.videopanel.winfo_id()

    #def OnPause(self, evt):
    def OnPause(self):
        """Pause the player.
        """
        self.player.pause()

    def OnStop(self):
        """Stop the player.
        """
        self.player.stop()
        # reset the time slider
        self.timeslider.set(0)

    def OnTimer(self):
        """Update the time slider according to the current movie time.
        """
        if self.player == None:
            return
        # since the self.player.get_length can change while playing,
        # re-set the timeslider to the correct range.
        length = self.player.get_length()
        dbl = length * 0.001
        self.timeslider.config(to=dbl)

        # update the time on the slider
        tyme = self.player.get_time()
        if tyme == -1:
            tyme = 0
        dbl = tyme * 0.001
        self.timeslider_last_val = ("%.0f" % dbl) + ".0"
        # don't want to programatically change slider while user is messing with it.
        # wait 2 seconds after user lets go of slider
        if time.time() > (self.timeslider_last_update + 2.0):
            self.timeslider.set(dbl)


    def scale_sel(self, evt):
        if self.player == None:
            return
        nval = self.scale_var.get()
        sval = str(nval)
        if self.timeslider_last_val != sval:
            # this is a hack. The timer updates the time slider.
            # This change causes this rtn (the 'slider has changed' rtn) to be invoked.
            # I can't tell the difference between when the user has manually moved the slider and when
            # the timer changed the slider. But when the user moves the slider tkinter only notifies
            # this rtn about once per second and when the slider has quit moving.
            # Also, the tkinter notification value has no fractional seconds.
            # The timer update rtn saves off the last update value (rounded to integer seconds) in timeslider_last_val
            # if the notification time (sval) is the same as the last saved time timeslider_last_val then
            # we know that this notification is due to the timer changing the slider.
            # otherwise the notification is due to the user changing the slider.
            # if the user is changing the slider then I have the timer routine wait for at least
            # 2 seconds before it starts updating the slider again (so the timer doesn't start fighting with the
            # user)
            self.timeslider_last_update = time.time()
            mval = "%.0f" % (nval * 1000)
            self.player.set_time(int(mval)) # expects milliseconds


    def volume_sel(self, evt):
        if self.player == None:
            return
        volume = self.volume_var.get()
        if volume > 100:
            volume = 100
        if self.player.audio_set_volume(volume) == -1:
            self.errorDialog("Failed to set volume")



    def OnToggleVolume(self, evt):
        """Mute/Unmute according to the audio button.
        """
        is_mute = self.player.audio_get_mute()

        self.player.audio_set_mute(not is_mute)
        # update the volume slider;
        # since vlc volume range is in [0, 200],
        # and our volume slider has range [0, 100], just divide by 2.
        self.volume_var.set(self.player.audio_get_volume())

    def OnSetVolume(self):
        """Set the volume according to the volume sider.
        """
        volume = self.volume_var.get()
        # vlc.MediaPlayer.audio_set_volume returns 0 if success, -1 otherwise
        if volume > 100:
            volume = 100
        if self.player.audio_set_volume(volume) == -1:
            self.errorDialog("Failed to set volume")

    def OnAddStamp(self):
        vidtim = self.player.get_time() * 0.001
        if vidtim != stamps[-1]:
            stamps.append(vidtim)
            stamps.sort()
            print(stamps)

    def OnNextFrame(self):
        global mpf
        nftime = self.player.get_time() + mpf
        self.player.set_time(nftime)


    def OnPrevFrame(self):
        global mpf
        nftime = self.player.get_time() - mpf
        self.player.set_time(nftime)

    def OnDelete(self):
        global stamps
        curtim = self.player.get_time()
        if len(stamps) > 1:
            if self.player.get_state() == vlc.State.Paused:
                for i in stamps:
                    if int(i*1000) == curtim:
                        stamps.remove(i)
                        break
                
            else:
                stamps = stamps[:-1]
            print(stamps)

    def OnNextStamp(self):
        global stamps
        curtim = self.player.get_time()
        for i in stamps:
            i = int(i*1000)
            if i > curtim:
                print(i)
                self.player.set_time(i)
                print(self.player.get_state())
                if self.player.get_state() != vlc.State.Paused:

                    print("paused")
                    self.player.pause()
                break

    def OnPrevStamp(self):
        global stamps
        curtim = self.player.get_time()
        for i in stamps[::-1]:
            i = int(i*1000)
            if i < curtim:
                print(i)
                self.player.set_time(i)
                print(self.player.get_state())
                if self.player.get_state() != vlc.State.Paused:

                    print("paused")
                    self.player.pause()
                break
    def OnExport(self):

        global fnam
        global las
        htmlfile = open(fnam.split()[0]+".html", "w")
        print("Exporting "+ fnam[:-4] +"...")
        htmlfile.write(html0)
        htmlfile.write(fnam)
        htmlfile.write(html1)
        htmlfile.write("""<video autoplay name="video" preload="auto" id="myVideo" onclick="video.play()" src="""+fnam+""" ></video>""")
        htmlfile.write(html2)
        htmlfile.write("var points = "+ str(stamps)+",")
        htmlfile.write(html3)
        print(las.get())
        if las.get():
            htmlfile.write(lasers)
            print("Please import images!")
        htmlfile.write(html4)
        htmlfile.close()
        print("Done.")
    def errorDialog(self, errormessage):
        """Display a simple error dialog.
        """
        Tk.tkMessageBox.showerror(self, 'Error', errormessage)

def Tk_get_root():
    if not hasattr(Tk_get_root, "root"): #(1)
        Tk_get_root.root= Tk.Tk()  #initialization call is inside the function
    return Tk_get_root.root

def _quit():
    print("_quit: bye")
    root = Tk_get_root()
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate
    os._exit(1)

if __name__ == "__main__":
    # Create a Tk.App(), which handles the windowing system event loop
    root = Tk_get_root()
    root.protocol("WM_DELETE_WINDOW", _quit)

    player = Player(root, title="tkinter vlc")
    # show the player window centred and run the application
    root.mainloop()
