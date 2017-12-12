import mido


#4d54 6864 0000 0006 0001 0002 0100 4d54



midi = mido.MidiFile('ns0293.mid')

for i, track in enumerate(midi.tracks):
	print 'Track {}: {}'.format(i,track.name)
	for msg in track:
		print msg





