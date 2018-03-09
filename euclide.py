#! /usr/bin/env python

# good example of euclidian/bjorklund algorithm for pyo from (http://ajaxsoundstudio.com/pyodoc/api/classes/triggers.html)

from pyo import *

# custom server initialization for ubuntu 16.04 as of 3/09/2018
s = Server(sr=44100, nchnls=2, buffersize=256, duplex=1, audio='jack', jackname='pyo').boot()

# start the server
s.start()

# for the trigger envelope, set up the table of cosine interpolated segments (http://ajaxsoundstudio.com/pyodoc/api/classes/tables.html)
t = CosTable([(0,0), (100,1), (500,.3), (8191,0)])
# use Euclide to construct the beat
beat = Euclide(time=.125, taps=16, onsets=[8,7], poly=1).play()
# to pseudo-randomly generate the notes (http://ajaxsoundstudio.com/pyodoc/api/classes/triggers.html)
trmid = TrigXnoiseMidi(beat, dist=12, mrange=(60, 96))
# adjust the midi notes to hertz (http://ajaxsoundstudio.com/pyodoc/api/classes/utils.html?highlight=snap#pyo.Snap)
trhz = Snap(trmid, choice=[0,2,3,5,7,8,10], scale=1)
# generate an envelope reader using the Euclide beat and t (http://ajaxsoundstudio.com/pyodoc/api/classes/triggers.html?highlight=trigenv#pyo.TrigEnv)
tr2 = TrigEnv(beat, table=t, dur=beat['dur'], mul=beat['amp'])
# perform the Euclide beat envelopes, tr2, with frequencies defined by trhz
a = Sine(freq=trhz, mul=tr2*0.3).out()
# make sure things don't automatically shut down
s.gui(locals())
