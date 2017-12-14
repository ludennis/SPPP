import argparse
import re

#CONSTANTS to tweak
# TAIL_GAP_MSEC => Something to do with notes being played closed to each
# MIN_NOTE_DUR => min time for a note to be playable
# HOLD_DELAY_POWER_START_MSEC => time when solarnoid will start holding
# HOLD_DELAY_POWER => power when the solarnoid is holding
# COM_SERIAL => serial number when connecting to Arduino
# SUSTAIN_NOTE => the note that a sustain will be used 

TAIL_GAP_MSEC = 250
MIN_NOTE_DUR = 140
HOLD_DELAY_POWER_START_MSEC = 170
HOLD_DELAY_POWER = 50
COM_SERIAL = 'COM11'
SUSTAIN_NOTE = 150

#KEY_SCALE will multiply the value set to the corresponding key
KEY_SCALE = [0, 
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,					  #ignore
			 
			 
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 1 keys 24-35
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 2 keys 36-47
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 3 keys 48-59
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 4 keys 60-71
			 0.99,0.99,0.99,0.98,0.98,0.98,0.97,0.97,0.97,0.96,0.96,0.96, #Octave 5 keys 72-83
			 0.95,0.95,0.95,0.94,0.94,0.94,0.93,0.93,0.93,0.92,0.92,0.92, #Octave 6 keys 84-96
			 
			 
			 0,0,0,0,         #ignore, this is up to 100
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0]     #ignore this is up to 150

KEY_OFFSET = [0, 
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,				      #ignore
			 
			 
			  11, 10, 10, 10,  9,  9,  9,  8,  8,  8,  7,  7, #Octave 1 keys 24-35
			   7,  6,  6,  6,  5,  5,  5,  4,  4,  4,  3,  3, #Octave 2 keys 36-47
			   3,  2,  2,  2,  1,  1,  1,  0,  0, -1, -1, -1, #Octave 3 keys 48-59
			  -1, -2, -2, -2, -2, -3, -3, -3, -4, -4, -4, -4, #Octave 4 keys 60-71
			  -5, -5, -5, -5, -6, -6, -6, -6, -7, -7, -7, -7, #Octave 5 keys 72-83
			  -8, -8, -8, -8, -9, -9, -9, -9,-10,-10,-10,-10, #Octave 6 keys 84-96
			 
			 
			 0,0,0,0,                 #ignore, this is up to 100
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0]     #ignore this is up to 150


def writeHeader(write_file):
	write_file.write('import serial\n')
	write_file.write('import time\n')
	write_file.write('ser = serial.Serial(\'{0}\', 115200, timeout=5)\n'.format(COM_SERIAL))
	write_file.write('time.sleep(1)\n\n')
	write_file.write('#<time,key,power>\n')

def writeKey(write_file,time,key,power,hold=False):
	write_file.write('ser.write(\'<{0},{1},{2}>\')\n'.format(time,key,power))
	if(hold==True and power > 3):
		write_file.write('ser.write(\'<{0},{1},{2}>\')\n'.format(HOLD_DELAY_POWER_START_MSEC,key,HOLD_DELAY_POWER))
	write_file.write('ser.readline()\n')

def adjust_note_vol(note,avg):
	note['val'] = int((note['val']-avg) * KEY_SCALE[note['note']] + KEY_OFFSET[note['note']] + avg)
	return note

def compress_note(note,tmax,tmin):
	note['val'] = tmax if note['val'] > tmax else tmin
	return note

parser = argparse.ArgumentParser(description='Parses Midi Text file into Python commands for Arduino')
parser.add_argument('-test', nargs='*', action='store', help='-test [start_key] [end_key] [pwr] [delay_time] or -test [start_key] [end_key] [min_pwr] [max_pwr] [inc_pwr] [delay_time]')
parser.add_argument('input_file', metavar='input', type=str, nargs='?', help='the name of the input midi text file')
parser.add_argument('--tmax',type=int,default=180,help='--tmax=[target_max_power]')
parser.add_argument('--tmin',type=int,default=105,help='--tmin=[target_min_power]')
args = parser.parse_args()

if(args.input_file):

	read_file = open(args.input_file, 'r')

	notes = []
	num_of_notes = 0
	sum_vol = 0

	for line in read_file:
		NoteOn =  re.match(r'[0-9]+,Min:Sec:Msec=(?P<min>[0-9]+):(?P<sec>[0-9]+):(?P<msec>[0-9]+),(?P<action>[a-zA-Z]+) chan: 1 note: (?P<note>[0-9]+) vol: (?P<val>[0-9]+) dur: (?P<dur>[0-9]+)$',line)
		NoteOff = re.match(r'[0-9]+,Min:Sec:Msec=(?P<min>[0-9]+):(?P<sec>[0-9]+):(?P<msec>[0-9]+),(?P<action>[a-zA-Z]+) chan: 1 note: (?P<note>[0-9]+)$',line)
		Sustain = re.match(r'[0-9]+,Min:Sec:Msec=(?P<min>[0-9]+):(?P<sec>[0-9]+):(?P<msec>[0-9]+),(?P<action>[a-zA-Z]+) chan: 1 value: (?P<val>[0-9]+)$',line)

		match = sorted([NoteOn,NoteOff,Sustain],reverse=True)[0]
		if match:
			d = match.groupdict()
			timestamp = int(d['min']) * 60000 + int(d['sec']) * 1000 + int(d['msec'])
			notes.append({'time':timestamp,
						  'note':int(d['note']) if 'note' in d else SUSTAIN_NOTE,
						  'val':int(d['val']) if 'val' in d else int(0),
						  'action':d['action']})
			if d['action'] == 'NoteOn': 
				num_of_notes+=1 
				sum_vol+=int(d['val']) 
		else:
			continue

	avg_vol = sum_vol/num_of_notes
	notes=filter(lambda x:x['action']=='NoteOn' or x['action']=='NoteOff' or x['action']=='Sustain',notes)

	#Normalize all notes:
	#	1. move tmax,tmin,notes,avg so that the avg is 0
	#		a. tmax = tmax - tmin - (tmax-tmin) / 2 = tmax - tmin - tmax/2 + tmin/2 = tmax/2 - tmin/2 = (tmax-tmin)/2
	#		b. tmin = tmin - tmin - (tmax-tmin) / 2 = tmin/2 - tmax/2 = (tmin-tmax)/2
	#		c. note = note - avg
	#	2. squeeze all notes so that 80% remain inside [tmin,tmax]
	#		a. sort all NoteOn according to value and the 10% highest and 10% lowest
	#		b. calculate the multiplier for 10% high to reach tmax and 10% min to reach tmin
	#			- for note['val'] < 0 ====> note['val'] = tmin/notes[low10%]
	#			- for note['val'] > 0 ====> note['val'] = tmax/notes[high10%] 
	#		c. multiple all notes above 0 with (+)multiplier and all notes under zero with (-)multiplier
	#	3. compress all peaky notes to tmax or tmin
	#	4. bring them back with the desired tmax and tmin (by adding orig_tmax - tmax or something like that)
	# 	5. apply preset profile of notes after this

	tmax, tmin = (args.tmax-args.tmin)/2.0, (args.tmin-args.tmax)/2.0
	for note in notes:
		if note['action']=='NoteOn': note['val'] -= avg_vol

	notes.sort(key=lambda x: (x['action'],x['val']))

	ten_percent = num_of_notes / 10
	low_multiplier, high_multiplier = 0.0, 0.0
	for index, note in enumerate(filter(lambda x:x['action']=='NoteOn' and x['val'] < 0,notes)):
		if index<ten_percent: note['val'] = tmin;
		elif index==ten_percent: 
			low_multiplier = tmin/note['val']
		else: note['val'] = note['val'] * low_multiplier

	for index, note in enumerate(filter(lambda x:x['action']=='NoteOn' and x['val'] >= 0, reversed(notes))):
		if index<ten_percent: note['val'] = tmax;
		elif index==ten_percent: 
			high_multiplier=tmax/note['val']
		else: note['val'] = note['val'] * high_multiplier

	for index, note in enumerate(filter(lambda x:x['action']=='NoteOn', notes)):
		note['val'] = int(note['val'] + args.tmax - tmax)
		note=adjust_note_vol(note=note,avg=avg_vol)


	# 1. cut the tail(end) of a note when it's immediately played again in 50ms 
	#	 if diff(timestamp(NoteOff) - timestamp(NoteOn) < 50ms) then timestamp(NoteOff) - 50ms
	# 2. adds hold note 
	notes.sort(key=lambda x: (x['note'],x['time']))
	for index, note in enumerate(notes[:-1]):
		if note['action'] == 'NoteOn' and note['val']!=HOLD_DELAY_POWER and note['note']==notes[index+1]['note']:
			if notes[index+1]['time'] - note['time'] > MIN_NOTE_DUR:
				notes.insert(index+1,{'time': note['time'] + HOLD_DELAY_POWER_START_MSEC,
									  'note': note['note'],
									  'val': HOLD_DELAY_POWER,
									  'action': 'NoteOn'})
		elif note['action'] == 'NoteOff' and note['note']==notes[index+1]['note']:
			noteOn,noteOff,nextNoteOn = notes[index-1], note, notes[index+1]
			if abs(noteOff['time'] - nextNoteOn['time']) < TAIL_GAP_MSEC:
				if nextNoteOn['time'] - TAIL_GAP_MSEC - noteOn['time'] < MIN_NOTE_DUR: 
					noteOff['time'] = noteOn['time'] + MIN_NOTE_DUR
				else: noteOff['time'] = nextNoteOn['time'] - TAIL_GAP_MSEC	

	#update timestamp to delta t
	notes.sort(key=lambda x: (x['time'],x['note']))
	for index, note in reversed(list(enumerate(notes))):
		note['time'] = note['time'] - notes[index-1]['time']
	notes[0]['time'] = 0

	#write files
	write_file = open(args.input_file[:len(args.input_file)-4] + '.py','w')
	writeHeader(write_file)
	for note in notes:
		writeKey(write_file,time=note['time'],key=note['note'],power=note['val'])
	print '\'{}.py\' has been created with {} notes'.format(args.input_file[:len(args.input_file)-4],num_of_notes)

elif (args.test):
	#TODO: to apply multiplier and offset
	#generates a 'test.py' to play the piano 
	if len(args.test) == 6:
		write_file = open('test.py', 'w')
		writeHeader(write_file)

		start_key=int(args.test[0])
		end_key=int(args.test[1])
		min_pwr=int(args.test[2])
		max_pwr=int(args.test[3])
		inc_pwr=int(args.test[4])
		delay_time=int(args.test[5])
		cur_key = start_key
		cur_pwr = min_pwr

		if(delay_time<HOLD_DELAY_POWER_START_MSEC):
			print '\nWARNING: delay_time({0}) is less than hold delay time({1})'.format(delay_time,HOLD_DELAY_POWER_START_MSEC)

		while cur_key <= end_key:
			cur_pwr = min_pwr
			while cur_pwr <= max_pwr:
				writeKey(write_file=write_file,time=0,key=cur_key,vol=adjust_vol(cur_pwr,cur_key,0 if args.target_average==None else args.target_average))
				write_file.write('print \'playing note {0} with power {1}...\\n\'\n'.format(cur_key,adjust_vol(cur_pwr,cur_key,0)))
				writeKey(delay_time,cur_key,pwr=0)
				cur_pwr = inc_pwr + cur_pwr
			cur_key = cur_key + 1

		print ('\ntest.py file has been generated to play from keys {0}'
			  '-{1} with power {2} to {3} in increments of {4}'
		 	  'delay {5}ms'
		 	  ''.format(start_key, end_key, min_pwr, max_pwr,inc_pwr,delay_time))
	elif len(args.test) == 4:
		#this will write a testing file with desired pwr from start_key to end_key
		write_file = open('test.py', 'w')
		writeHeader(write_file)

		start_key=int(args.test[0])
		end_key=int(args.test[1])
		pwr=int(args.test[2])
		delay_time=int(args.test[3])
		cur_key = start_key

		if(delay_time<HOLD_DELAY_POWER_START_MSEC):
			print '\nWARNING: delay_time({0}) is less than hold delay time({1})'.format(delay_time,HOLD_DELAY_POWER_START_MSEC)

		while cur_key <= end_key:
			writeKey(write_file=write_file,time=0,key=cur_key,vol=adjust_vol(pwr,cur_key,0 if args.target_average == None else args.target_average),hold=True)
			write_file.write('print \'playing note {0} with power {1} ... \\n\'\n'.format(cur_key,adjust_vol(pwr,cur_key,0)))
			writeKey(write_file=write_file,time=delay_time,key=cur_key,pwr=0, hold=True) 
			cur_key = cur_key + 1

		print ('\ntest.py file has been generated to play keys {0}-{1}'
			  ' with power {2} and delay {3}ms'
		 	  ''.format(start_key, end_key, pwr, delay_time))
	else:
		parser.print_help()
else:
	parser.print_help()
