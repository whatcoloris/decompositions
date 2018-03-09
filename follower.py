#! /usr/bin/env python
######################################################################
# adapted from tuner.py - a minimal command-line guitar/ukulele tuner in Python.
# Requires numpy and pyaudio.
# thanks to Matt Zucker for this code!!!!!
######################################################################
# COMPOSER'S NOTE: this could TOTALLY be used to do a bizarre version of
# Robert Ashley's "The Wolfman" which did not focus on feedback or
# amplification systems but rather on note detection and software systems
# the principal and intensity are remarkably similar

import numpy as np
import pyaudio
from pyo import *

# Set Up Server for ubuntu 16.04 as of 3/9/2018
s = Server(sr=44100, nchnls=2, buffersize=256, duplex=1, audio='jack', jackname='pyo')
# we're not using a midi device but if we were it would be inititalized here
#s.setMidiInputDevice(2) # Change as required
# boot the server
s.boot()

######################################################################
# INITITAL COMMENTS FROM tuner.py
# Feel free to play with these numbers. Might want to change NOTE_MIN
# and NOTE_MAX especially for guitar/bass. Probably want to keep
# FRAME_SIZE and FRAMES_PER_FFT to be powers of two.

NOTE_MIN = 1       #
NOTE_MAX = 120       #
FSAMP = 22050       # Sampling frequency in Hz
FRAME_SIZE = 1024   # How many samples per frame?
FRAMES_PER_FFT = 16 # FFT takes average across how many frames?

######################################################################
# INITITAL COMMENTS FROM tuner.py
# Derived quantities from constants above. Note that as
# SAMPLES_PER_FFT goes up, the frequency step size decreases (so
# resolution increases); however, it will incur more delay to process
# new sounds.

SAMPLES_PER_FFT = FRAME_SIZE*FRAMES_PER_FFT
FREQ_STEP = float(FSAMP)/SAMPLES_PER_FFT

######################################################################
# INITITAL COMMENTS FROM tuner.py
# For printing out notes

NOTE_NAMES = 'C C# D D# E F F# G G# A A# B'.split()

######################################################################
# INITITAL COMMENTS FROM tuner.py
# These three functions are based upon this very useful webpage:
# https://newt.phys.unsw.edu.au/jw/notes.html

def freq_to_number(f): return 69 + 12*np.log2(f/440.0)
def number_to_freq(n): return 440 * 2.0**((n-69)/12.0)
def note_name(n): return NOTE_NAMES[n % 12] + str(n/12 - 1)

# INITITAL COMMENTS FROM tuner.py
# Get min/max index within FFT of notes we care about.
# See docs for numpy.rfftfreq()
def note_to_fftbin(n): return number_to_freq(n)/FREQ_STEP
imin = max(0, int(np.floor(note_to_fftbin(NOTE_MIN-1))))
imax = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(NOTE_MAX+1))))

# INITITAL COMMENTS FROM tuner.py
# Allocate space to run an FFT.
buf = np.zeros(SAMPLES_PER_FFT, dtype=np.float32)
num_frames = 0

# INITITAL COMMENTS FROM tuner.py
# Initialize audio
stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                channels=1,
                                rate=FSAMP,
                                input=True,
                                frames_per_buffer=FRAME_SIZE)

stream.start_stream()

# INITITAL COMMENTS FROM tuner.py
# Create Hanning window function
window = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, SAMPLES_PER_FFT, False)))

# INITITAL COMMENTS FROM tuner.py
# Print initial text
print 'sampling at', FSAMP, 'Hz with max resolution of', FREQ_STEP, 'Hz'
print

# start server!
s.start()

# we're not using MIDI, but if we were...
# Set Up MIDI
#midi = Notein()

# could this also be an envelope table/reader?
# ADSR
amp = 1.0

# initial pitch value
# Pitch
pitch = 62

# generate the wavetable to use for synthesis
# Table
wave = SquareTable()

# make the oscillator that will play the pitch being followed
osc = Osc(wave, freq=pitch, mul=amp)

# INITITAL COMMENTS FROM tuner.py
# As long as we are getting data:
while stream.is_active():

    # Shift the buffer down and new data in
    buf[:-FRAME_SIZE] = buf[FRAME_SIZE:]
    buf[-FRAME_SIZE:] = np.fromstring(stream.read(FRAME_SIZE), np.int16)

    # Run the FFT on the windowed buffer
    fft = np.fft.rfft(buf * window)

    # Get frequency of maximum response in range
    freq = (np.abs(fft[imin:imax]).argmax() + imin) * FREQ_STEP

    # Get note number and nearest note
    n = freq_to_number(freq)
    n0 = int(round(n))

#    # Osc
#    osc = Osc(wave, freq=int(round(freq)), mul=amp)
    # change the frequency of the Osc osc depending on what is detected
    osc.freq = int(round(freq))

    # add reverb because... reverb
    # FX
    verb = Freeverb(osc).out()

    # play the oscillator not sure if these out declarations should be elsewhere
    osc.out()
    # this part not necessary as we are within the stream.is_active() while loop
    # s.gui(locals()) # Prevents immediate script termination.

    # INITITAL COMMENTS FROM tuner.py
    # Console output once we have a full buffer
    num_frames += 1

    if num_frames >= FRAMES_PER_FFT:
        print 'freq: {:7.2f} Hz     note: {:>3s} {:+.2f}'.format(
freq, note_name(n0), n-n0)
