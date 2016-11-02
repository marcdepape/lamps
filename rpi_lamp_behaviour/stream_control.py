from gi.repository import Gst, GObject
from time import sleep
from threading import Thread
from multiprocessing import Process, Queue
import gi

class LampStream(object):

    def __init__(self, rate, peak):
        stream_pipeline = "rtspsrc latency=250 name=\"source\" ! queue ! rtpvorbisdepay ! vorbisdec ! audioconvert ! audio/x-raw,format=S16LE,channels=2 ! volume name=\"gain\" ! level ! alsasink"

        self.is_live = True
        self.stream = Gst.parse_launch(stream_pipeline)
        self.playing = False
        self.volume = 0.0
        self.peak = peak
        self.rate = rate

        self.lamp_stream = ""
        self.vol = Queue()
        self.play = Queue()

    def state(self, play):
        self.playing = play.get()
        return self.playing

    def start_stream(self, url):
        url = "rtsp://" + url + ":8554/mic"
        self.lamp_stream = Process(name='listen', target=self.listen, args=(url,))
        self.lamp_stream.daemon = True
        #print "START!"
        self.lamp_stream.start()
        while self.state(self.play) == False:
            pass
        self.fade("in")
        self.is_live = True
        while self.is_live == True:
            pass
        #print "END THREAD!"

    def stop_stream(self):
        print "STOP!"
        self.fade("out")
        self.lamp_stream.terminate()
        self.is_live = False

    def fade(self, inOut):
        if inOut == "in":
            #print "FADE IN!"
            #print "CURRENT VOLUME: " + str(self.volume)
            while self.volume < self.peak:
                self.volume = self.volume + 0.01
                self.vol.put(self.volume)
                sleep(self.rate)
            #print "END VOLUME: " + str(self.volume)
        elif inOut == "out":
            #print "FADE OUT!"
            #print "CURRENT VOLUME: " + str(self.volume)
            while self.volume > 0.01:
                self.volume = self.volume - 0.01
                self.vol.put(self.volume)
                sleep(self.rate)
            #print "END VOLUME: " + str(self.volume)
        else:
            pass

    def listen(self, url):
        print "STREAM: " + url
        self.volume = 0
        self.playing = False
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
                self.play.put(self.playing)
            else:
                print info[1]
                self.stream.set_state(Gst.State.NULL)

        while self.playing == True:
            self.volume = self.vol.get()
            if self.volume != self.stream.get_by_name("gain").get_property('volume'):
                self.stream.get_by_name("gain").set_property('volume', self.volume)
