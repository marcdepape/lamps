#!/usr/bin/python3

import lamps
import time

stream = lamps.LampAudioStream()

stream.start('localhost')
time.sleep(5)

stream.volume = 0.25
time.sleep(5)

stream.start('localhost')
stream.volume = 1.5
time.sleep(5)

stream.stop()
time.sleep(5)
