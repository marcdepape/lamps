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
        self.fading_in = False
        self.fading_out = False
        self.peak = peak
        self.rate = rate
        self.current = ""
        self.log = "Starting stream..."

        self.lamp_stream = None
        self.vol = Queue()
        self.play = Queue()

    def state(self, play):
        self.playing = play.get()
        return self.playing

    def status(self):
        if self.current != self.log:
            self.current = self.log
            print self.current
            return self.current
        else:
            return self.current

    def start_stream(self, url):
        self.log = str(url)
        self.status()
        url = "rtsp://" + url + ":8554/mic"
        self.lamp_stream = Process(name='listen', target=self.listen, args=(url,))
        self.lamp_stream.daemon = True
        self.lamp_stream.start()
        while self.state(self.play) == False:
            pass
        self.fade("in")
        self.is_live = True
        while self.is_live == True:
            pass

    def stop_stream(self):
        self.log = "STOPPING..."
        self.status()
        self.fade("out")
        self.lamp_stream.terminate()
        self.is_live = False

    def fade(self, inOut):
        if inOut == "in":
            self.log = "FADE IN"
            self.status()
            self.fading_in = True
            while self.volume < self.peak and self.fading_out != True:
                self.volume = self.volume + 0.01
                self.vol.put(self.volume)
                self.log = "+ {}".format(self.volume)
                self.status()
                sleep(self.rate)
            self.fading_in = False
        elif inOut == "out":
            self.fading_out = True
            self.log = "FADE OUT"
            self.status()
            while self.volume > 0.01 and self.fading_in != True:
                self.volume = self.volume - 0.01
                self.vol.put(self.volume)
                self.log = "- {}".format(self.volume)
                self.status()
                sleep(self.rate)
            self.fading_out = False
        else:
            pass

    def listen(self, url):
        self.log = "STREAM: {}".format(url)
        self.volume = 0
        self.playing = False
        self.stream.get_by_name("source").set_property("location",url)
        self.stream.get_by_name("gain").set_property('volume', self.volume)

        while self.playing == False:
            self.stream.get_by_name("source").set_property("location",url)
            self.stream.set_state(Gst.State.PLAYING)
            info = self.stream.get_state(0)
            info = str(info[0]).split(" ")
            while info[1] == "GST_STATE_CHANGE_ASYNC":
                #print info[1]
                info = self.stream.get_state(0)
                info = str(info[0]).split(" ")
                self.log = "ASYNC..."
                self.status()
            if info[1] == "GST_STATE_CHANGE_SUCCESS":
                #print info[1]
                self.log = "SUCCESS"
                self.status()
                self.playing = True
                self.play.put(self.playing)
            else:
                #print info[1]
                self.log = str(info[1])
                self.status()
                self.stream.set_state(Gst.State.NULL)

        while self.playing == True:
            self.volume = self.vol.get()
            if self.volume != self.stream.get_by_name("gain").get_property('volume'):
                self.stream.get_by_name("gain").set_property('volume', self.volume)
