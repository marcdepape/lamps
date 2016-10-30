from gi.repository import Gst, GObject
from time import sleep
from threading import Thread
from multiprocessing import Process, Queue
import gi

class LampStream(object):

    def __init__(self, rate):
        stream_pipeline = "rtspsrc name=\"source\" ! queue ! rtpvorbisdepay ! vorbisdec ! audioconvert ! audio/x-raw,format=S16LE,channels=2 ! volume name=\"gain\" ! level ! alsasink"

        self.stream = Gst.parse_launch(stream_pipeline)
        self.playing = False
        self.volume = 0.0
        self.rate = rate

    def state(self, play):
        self.playing = play.get()
        return self.playing

    def fade(self, vol, inOut):
        if inOut == "in":
            print "FADE IN!"
            #print "CURRENT VOLUME: " + str(self.volume)
            while self.volume < 1.50:
                self.volume = self.volume + 0.01
                #print str(self.volume)
                vol.put(self.volume)
                sleep(self.rate)
        elif inOut == "out":
            print "FADE OUT"
            #print "CURRENT VOLUME: " + str(self.volume)
            while self.volume > 0.01:
                self.volume = self.volume - 0.01
                #print str(self.volume)
                vol.put(self.volume)
                sleep(self.rate)
        else:
            pass

    def listen(self, vol, play, url):
        print "PLAYING! " + url
        self.volume = 0
        self.stream.get_by_name("source").set_property("location",url)
        self.stream.get_by_name("gain").set_property('volume', self.volume)

        while self.playing == False:
            self.stream.get_by_name("source").set_property("location",url)
            self.stream.set_state(Gst.State.PLAYING)
            info = self.stream.get_state(0)
            info = str(info[0]).split(" ")
            print info[1]
            while info[1] == "GST_STATE_CHANGE_ASYNC":
                info = self.stream.get_state(0)
                info = str(info[0]).split(" ")
            if info[1] == "GST_STATE_CHANGE_SUCCESS":
                print info[1]
                self.playing = True
                play.put(self.playing)
            else:
                print info[1]
                self.stream.set_state(Gst.State.NULL)

        while self.playing == True:
            self.volume = vol.get()
            if self.volume != self.stream.get_by_name("gain").get_property('volume'):
                self.stream.get_by_name("gain").set_property('volume', self.volume)
