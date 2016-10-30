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

        bus = self.stream.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.stream.set_state(Gst.State.NULL)
            print message
        elif t == Gst.MessageType.ERROR:
            self.stream.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print "Error: %s" % err, debug

    def fade(self, q, inOut):
        if inOut == "in":
            print "FADE IN!"
            print "CURRENT VOLUME: " + str(self.volume)
            while self.volume < 1.50:
                self.volume = self.volume + 0.01
                print str(self.volume)
                q.put(self.volume)
                sleep(0.05)
        elif inOut == "out":
            print "FADE OUT"
            print "CURRENT VOLUME: " + str(self.volume)
            while self.volume > 0.01:
                self.volume = self.volume - 0.01
                print str(self.volume)
                q.put(self.volume)
                sleep(0.05)
        else:
            pass

    def listen(self, q, url):
        print "PLAYING! " + url

        self.playing = True
        self.volume = 0
        self.stream.get_by_name("source").set_property("location",url)
        self.stream.get_by_name("gain").set_property('volume', self.volume)
        self.stream.set_state(Gst.State.PLAYING)
        while self.playing == True:
            self.volume = q.get()
            if self.volume != self.stream.get_by_name("gain").get_property('volume'):
                self.stream.get_by_name("gain").set_property('volume', self.volume)
            else:
                pass

GObject.threads_init()
Gst.init(None)

mainloop = GObject.MainLoop()
Thread(name="mainloop", target=mainloop.run).start()

this_stream = AudioStream()

if __name__ == '__main__':
    while True:
        q = Queue()
        t1 = Process(name='listen1', target=this_stream.listen, args=(q, "rtsp://192.168.100.162:8554/mic",))
        print "START!"
        t1.start()
        sleep(5)
        print "VOLUME!"
        this_stream.fade(q, "in")
        sleep(5)
        this_stream.fade(q, "out")
        sleep(1)
        print "STOP!"
        t1.terminate()

        q = Queue()
        t1 = Process(name='listen1', target=this_stream.listen, args=(q, "rtsp://192.168.100.117:8554/mic",))
        print "START!"
        t1.start()
        sleep(5)
        print "VOLUME!"
        this_stream.fade(q, "in")
        sleep(5)
        this_stream.fade(q, "out")
        sleep(1)
        print "STOP!"
        t1.terminate()

        q = Queue()
        t1 = Process(name='listen1', target=this_stream.listen, args=(q, "rtsp://192.168.100.189:8554/mic",))
        print "START!"
        t1.start()
        sleep(5)
        print "VOLUME!"
        this_stream.fade(q, "in")
        sleep(5)
        this_stream.fade(q, "out")
        sleep(1)
        print "STOP!"
        t1.terminate()
