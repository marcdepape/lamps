from gi.repository import Gst, GObject
from time import sleep
from threading import Thread
from multiprocessing import Process, Queue
import gi

class AudioStream(object):

    def __init__(self):
        stream_pipeline = "rtspsrc name=\"source\" ! queue ! rtpvorbisdepay ! vorbisdec ! audioconvert ! audio/x-raw,format=S16LE,channels=2 ! volume name=\"gain\" ! level ! alsasink"

        self.stream = Gst.parse_launch(stream_pipeline)
        self.playing = False
        self.volume = 0.0

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
                sleep(0.05)
        elif inOut == "out":
            print "FADE OUT"
            #print "CURRENT VOLUME: " + str(self.volume)
            while self.volume > 0.01:
                self.volume = self.volume - 0.01
                #print str(self.volume)
                vol.put(self.volume)
                sleep(0.05)
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
            sleep(5)
            info = self.stream.get_state(0)
            info = str(info[0]).split(" ")
            print info[1]
            if info[1] == "GST_STATE_CHANGE_SUCCESS":
                self.playing = True
                play.put(self.playing)
            else:
                self.stream.set_state(Gst.State.NULL)

        while self.playing == True:
            self.volume = vol.get()
            if self.volume != self.stream.get_by_name("gain").get_property('volume'):
                self.stream.get_by_name("gain").set_property('volume', self.volume)
            else:
                pass

GObject.threads_init()
Gst.init(None)

mainloop = GObject.MainLoop()
m = Thread(name="mainloop", target=mainloop.run)
m.daemon = True
m.start()

this_stream = AudioStream()

if __name__ == '__main__':
    vol = Queue()
    play = Queue()
    t1 = Process(name='listen1', target=this_stream.listen, args=(vol, play, "rtsp://192.168.100.200:8554/mic",))
    print "START!"
    t1.start()
    sleep(5)
    print "SUCCESS?"
    while this_stream.state(play) == False:
        pass
    print "FADE IN!"
    this_stream.fade(vol, "in")
    sleep(5)
    this_stream.fade(vol, "out")
    sleep(1)
    print "STOP!"
    t1.terminate()
