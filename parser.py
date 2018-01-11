import argparse
import re
import const
import math

def write_header(write_file):
	write_file.write('import serial\n')
	write_file.write('import time\n')
	write_file.write('ser = serial.Serial(\'{0}\', 115200, timeout=5)\n'.format(const.COM_SERIAL))
	write_file.write('time.sleep(1)\n\n')
	write_file.write('#<time,note,power>\n')

def write_note(write_file,time,note,power,hold=False):
	write_file.write('ser.write(\'<{0},{1},{2}>\')\n'.format(time,note,power))
	if(hold==True and power > 3):
		write_file.write('ser.write(\'<{0},{1},{2}>\')\n'.format(const.HOLD_DELAY_POWER_START_MSEC,note,const.HOLD_DELAY_POWER))
	write_file.write('ser.readline()\n')

def adjust_note_vol(note,avg):
	note['val'] = int((note['val']-avg) * const.NOTE_SCALE[note['note']] + const.NOTE_OFFSET[note['note']] + avg)
	return note

def compress_note(note,tmax,tmin):
	note['val'] = tmax if note['val'] > tmax else tmin
	return note

parser = argparse.ArgumentParser(description='Parses Midi Text file into Python commands for Arduino')
parser.add_argument('-test', nargs='*', action='store', help='-test [start_note] [end_note] [pwr] [delay_time] or -test [start_note] [end_note] [min_pwr] [max_pwr] [inc_pwr] [delay_time]')
parser.add_argument('input_file', metavar='input', type=str, nargs='?', help='the name of the input midi text file')
args = parser.parse_args()

if(args.input_file):

	read_file = open(args.input_file, 'r')

	notes = []
	num_of_notes = 0
	sum_vol = 0

	for line in read_file:
		
		# <timestamp,event,note,midipower>
		timestamp,event,note,midipower=line.strip().split(',')
		print '<{},{},{},{}>'.format(timestamp,event,note,midipower)

		match = sorted([NoteOn,NoteOff,Sustain],reverse=True)[0]
		if match:
			d = match.groupdict()
			timestamp = int(d['min']) * 60000 + int(d['sec']) * 1000 + int(d['msec'])
			notes.append({'time':timestamp,
						  'note':int(d['note']) if 'note' in d else const.SUSTAIN_NOTE,
						  'val':int(d['val']) if 'val' in d else int(0),
						  'action':d['action']})
			if d['action'] == 'NoteOn': 
				num_of_notes+=1 
				sum_vol+=int(d['val']) 
		else:
			continue

	avg_vol = sum_vol/num_of_notes
	notes=filter(lambda x:x['action']=='NoteOn' or x['action']=='NoteOff' or x['action']=='Sustain',notes)

	tmax, tmin = (const.TARGET_MAX-const.TARGET_MIN)/2.0, (const.TARGET_MIN-const.TARGET_MAX)/2.0
	for note in notes:
		if note['action']=='NoteOn': note['val'] -= avg_vol

	notes.sort(key=lambda x: (x['action'],x['val']))

	num_percent = num_of_notes / const.NUM_PERCENT
	low_exp_power, high_exp_power = 0.0, 0.0
	for index, note in enumerate(filter(lambda x:x['action']=='NoteOn' and x['val'] < 0,notes)):
		if index<num_percent: note['val'] = tmin;
		elif index==num_percent: 
			low_exp_power = math.log(tmin/note['val']) if note['val']!=0 else 1
		else: note['val'] = note['val'] * math.exp(low_exp_power)

	for index, note in enumerate(filter(lambda x:x['action']=='NoteOn' and x['val'] >= 0, reversed(notes))):
		if index<num_percent: note['val'] = tmax;
		elif index==num_percent: 
			high_exp_power=math.log(tmax/note['val']) if note['val']!=0 else 1
		else: note['val'] = note['val'] * math.exp(high_exp_power)

	for index, note in enumerate(filter(lambda x:x['action']=='NoteOn', notes)):
		note['val'] = int(note['val'] + const.TARGET_MAX - tmax)
		note=adjust_note_vol(note=note,avg=avg_vol)

	# 1. cut the tail(end) of a note when it's immediately played again in 50ms 
	#	 if diff(timestamp(NoteOff) - timestamp(NoteOn) < 50ms) then timestamp(NoteOff) - 50ms
	# 2. adds hold note 
	notes.sort(key=lambda x: (x['note'],x['time']))
	for index,note in enumerate(notes):
		if index<len(notes)-1:
			if note['action'] == 'NoteOff' and note['note']==notes[index+1]['note']:
				noteOn,noteOff,nextNoteOn = notes[index-1], note, notes[index+1]
				if nextNoteOn['time'] - noteOff['time'] < const.TAIL_GAP_MSEC:
					if nextNoteOn['time'] - const.TAIL_GAP_MSEC - noteOn['time'] < const.MIN_NOTE_DUR: 
						noteOff['time'] = noteOn['time'] + const.MIN_NOTE_DUR
					else: noteOff['time'] = nextNoteOn['time'] - const.TAIL_GAP_MSEC
				if noteOff['time'] - noteOn['time'] < const.MIN_NOTE_DUR:
					noteOff['time']=noteOn['time']+const.MIN_NOTE_DUR
				if noteOff['time'] > nextNoteOn['time']:
					noteOff['time']=nextNoteOn['time']

	for index, note in enumerate(notes):
		if index<len(notes)-1:
			if note['action'] == 'NoteOn' and note['val']!=const.HOLD_DELAY_POWER and note['note']==notes[index+1]['note']:
				if notes[index+1]['time'] - note['time'] > const.MIN_NOTE_DUR:
					notes.insert(index+1,{'time': note['time'] + const.HOLD_DELAY_POWER_START_MSEC,
										  'note': note['note'],
										  'val': const.HOLD_DELAY_POWER,
										  'action': 'NoteOn'})

	#write files
	write_file = open(args.input_file[:len(args.input_file)-4] + '.py','w')
	write_header(write_file)
	for note in notes:
		write_note(write_file,time=note['time'],note=note['note'],power=note['val'])
	print '\'{}.py\' has been created with {} notes'.format(args.input_file[:len(args.input_file)-4],num_of_notes)

elif (args.test):
	#TODO: to apply multiplier and offset
	#generates a 'test.py' to play the piano 
	if len(args.test) == 6:
		write_file = open('test.py', 'w')
		write_header(write_file)

		start_note=int(args.test[0])
		end_note=int(args.test[1])
		min_pwr=int(args.test[2])
		max_pwr=int(args.test[3])
		inc_pwr=int(args.test[4])
		delay_time=int(args.test[5])
		cur_note = start_note
		cur_pwr = min_pwr

		if(delay_time<const.HOLD_DELAY_POWER_START_MSEC):
			print '\nWARNING: delay_time({0}) is less than hold delay time({1})'.format(delay_time,const.HOLD_DELAY_POWER_START_MSEC)

		while cur_note <= end_note:
			cur_pwr = min_pwr
			while cur_pwr <= max_pwr:
				write_note(write_file=write_file,time=0,note=cur_note,vol=adjust_vol(cur_pwr,cur_note,0 if args.target_average==None else args.target_average))
				write_file.write('print \'playing note {0} with power {1}...\\n\'\n'.format(cur_note,adjust_vol(cur_pwr,cur_note,0)))
				write_note(delay_time,cur_note,pwr=0)
				cur_pwr = inc_pwr + cur_pwr
			cur_note = cur_note + 1

		print ('\ntest.py file has been generated to play from notes {0}'
			  '-{1} with power {2} to {3} in increments of {4}'
		 	  'delay {5}ms'
		 	  ''.format(start_note, end_note, min_pwr, max_pwr,inc_pwr,delay_time))
	elif len(args.test) == 4:
		#this will write a testing file with desired pwr from start_note to end_note
		write_file = open('test.py', 'w')
		write_header(write_file)

		start_note=int(args.test[0])
		end_note=int(args.test[1])
		pwr=int(args.test[2])
		delay_time=int(args.test[3])
		cur_note = start_note

		if(delay_time<const.HOLD_DELAY_POWER_START_MSEC):
			print '\nWARNING: delay_time({0}) is less than hold delay time({1})'.format(delay_time,const.HOLD_DELAY_POWER_START_MSEC)

		while cur_note <= end_note:
			write_note(write_file=write_file,time=0,note=cur_note,vol=adjust_vol(pwr,cur_note,0 if args.target_average == None else args.target_average),hold=True)
			write_file.write('print \'playing note {0} with power {1} ... \\n\'\n'.format(cur_note,adjust_vol(pwr,cur_note,0)))
			write_note(write_file=write_file,time=delay_time,note=cur_note,pwr=0, hold=True) 
			cur_note = cur_note + 1

		print ('\ntest.py file has been generated to play notes {0}-{1}'
			  ' with power {2} and delay {3}ms'
		 	  ''.format(start_note, end_note, pwr, delay_time))
	else:
		parser.print_help()
else:
	parser.print_help()
