import argparse
import re
import const
import math

def write_header(write_file):
	write_file.write('import serial\n')
	write_file.write('import time\n')
	write_file.write('ser = serial.Serial(\'{0}\', 115200, timeout=5)\n'.format(const.COM_SERIAL))
	write_file.write('time.sleep(1)\n\n')
	write_file.write('#<timestamp,event,note,midipower>\n')
	write_file.write('ser.write(\'<0,0,0,8,0,0>\')\n')

def write_footer(write_file):
	write_file.write('ser.write(\'<0,0,0,7,0,0>\')\n')

def write_note(write_file,timestamp,track,channel,event,note,midipower,hold=False):
	write_file.write('ser.write(\'<{},{},{},{},{},{}>\')\n'.format(int(timestamp),track,channel,event,note,midipower))
	write_file.write('ser.readline()\n')
	if(hold==True and event == 1):
		write_file.write('ser.write(\'<{},{},{},{},{},{}>\')\n'.format(int(timestamp + const.HLD_DLY),track,channel,event,note,const.HLD_DLY_PWR))
		write_file.write('ser.readline()\n')
	

def adjust_note_vol(note,avg):
	note['midipower'] = int((note['midipower']-avg) * const.NOTE_SCALE[note['note']] + const.NOTE_OFFSET[note['note']] + avg)
	return note

def compress_note(note,tmax,tmin):
	note['midipower'] = tmax if note['midipower'] > tmax else tmin
	return note

parser = argparse.ArgumentParser(description='Parses Midi Text file into Python commands for Arduino')
parser.add_argument('-test', nargs='*', action='store', help='-test [start_note] [end_note] [delay_time] [pwr]  or -test [start_note] [end_note] [delay_time] [min_pwr] [max_pwr] [inc_pwr] ')
parser.add_argument('input_file', metavar='input', type=str, nargs='?', help='the name of the input midi text file')
args = parser.parse_args()

if(args.input_file):

	read_file = open(args.input_file, 'r')

	notes = []
	num_of_notes = 0
	sum_vol = 0

	# read from txt and store into lists of <timestamp,event,note,midipower>
	for line in read_file:		
		timestamp,track,channel,event,note,midipower=line.strip().split(',')
		notes.append({'timestamp':int(timestamp),'track':int(track),'channel':(channel),'event':int(event),'note':int(note),'midipower':int(midipower)})
		if int(event) == 1:
			num_of_notes+=1
			sum_vol+=int(midipower)

	avg_vol = sum_vol/num_of_notes

	# normalize all notes
	tmax, tmin = (const.TARGET_MAX-const.TARGET_MIN)/2.0, (const.TARGET_MIN-const.TARGET_MAX)/2.0
	for note in notes:
		if note['event']==1: note['midipower'] -= avg_vol
	notes.sort(key=lambda x: (x['event'],x['midipower']))
	num_percent = num_of_notes / const.NUM_PERCENT
	low_linear_power, high_linear_power = 0.0, 0.0
	for index, note in enumerate(filter(lambda x:x['event']==1 and x['midipower'] < 0,notes)):
		if index<num_percent: note['midipower'] = tmin;
		elif index==num_percent: 
			low_exp_power = tmin/note['midipower'] if note['midipower']!=0 else 1
		else: note['midipower'] = note['midipower'] * low_linear_power
	for index, note in enumerate(filter(lambda x:x['event']==1 and x['midipower'] >= 0, reversed(notes))):
		if index<num_percent: note['midipower'] = tmax;
		elif index==num_percent: 
			high_exp_power=tmax/note['midipower'] if note['midipower']!=0 else 1
		else: note['midipower'] = note['midipower'] * high_linear_power
	for index, note in enumerate(filter(lambda x:x['event']==1, notes)):
		note['midipower'] = int(note['midipower'] + const.TARGET_MAX - tmax)
		note=adjust_note_vol(note=note,avg=avg_vol)

	# cut tail & min note dur
	notes.sort(key=lambda x: (x['note'],x['timestamp'],x['track'],x['channel']))
	for index,note in enumerate(notes):
		if index<len(notes)-1:
			if note['event'] == 0 and note['note']==notes[index+1]['note']:
				note_on,note_off,next_note_on = notes[index-1], note, notes[index+1]
				gap_dur,note_dur = next_note_on['timestamp']-note_off['timestamp'],note_off['timestamp']-note_on['timestamp']
				if note_dur < const.SUGGESTED_DUR:
					note_off['timestamp'] = note_on['timestamp'] + const.SUGGESTED_DUR
					#if overlap, reduce increase until there is a 1 ms gap. run this for the entire song first
					if note_off['timestamp'] > next_note_on['timestamp']: note_off['timestamp'] = next_note_on['timestamp'] - 1
				if gap_dur < const.SUGGESTED_RELEASE_TIME:
					if note_dur > const.SUGGESTED_DUR + gap_dur:
						note_off['timestamp'] = note_off['timestamp'] - gap_dur
					else:
						note_off['timestamp'] = (gap_dur + note_dur) * (1. - const.MULTIPLIER_SPLIT_RELEASE_TIME)
						small_release_time = (gap_dur + note_dur) * const.MULTIPLIER_SPLIT_RELEASE_TIME
						if small_release_time < const.MIN_RELEASE_TIME:
							# -set gap = small_release_time
							note_off['timestamp'] = next_note_on['timestamp'] - small_release_time
						# -check if there is any overcut, if there is overcut, reduce until 1ms apart.
						if note_off['timestamp'] > next_note_on['timestamp']:
							note_off['timestamp'] = next_note_on['timestamp'] - 1
				#add hold delay if note is long enough
				if note_dur > const.HLD_DLY and note_on['midipower'] != const.HLD_DLY_PWR and note_on['event']==1:
					notes.append({'timestamp':note_on['timestamp']+const.HLD_DLY,
								  'track':note_on['track'],
								  'channel':note_on['channel'],
								  'event':1,
								  'note':note_on['note'],
								  'midipower':const.HLD_DLY_PWR})

	#write files
	notes.sort(key=lambda x: (x['timestamp']))
	write_file = open(args.input_file[:len(args.input_file)-4] + '.py','w')
	write_header(write_file)
	for note in notes:
		write_note(write_file,timestamp=note['timestamp'],
							  track=note['track'],
							  channel=note['channel'],
							  event=note['event'],
							  note=note['note'],
							  midipower=note['midipower'])
	write_footer(write_file)
	print '\'{}.py\' has been created with {} notes'.format(args.input_file[:len(args.input_file)-4],num_of_notes)

elif (args.test):
	
	write_file = open('test.py', 'w')
	write_header(write_file)
	start_note=int(args.test[0])
	end_note=int(args.test[1])
	delay_time=int(args.test[2])
	cur_note = start_note
	
	# -test [start_note] [end_note] [delay_time] [min_pwr] [max_pwr] [inc_pwr] 
	if len(args.test) == 6:
		min_pwr=int(args.test[3])
		max_pwr=int(args.test[4])
		inc_pwr=int(args.test[5])
		cur_pwr = min_pwr

		if(delay_time<const.HLD_DLY):
			print '\nWARNING: delay_time({0}) is less than hold delay time({1})'.format(delay_time,const.HLD_DLY)

		while cur_note <= end_note:
			cur_pwr = min_pwr
			while cur_pwr <= max_pwr:
				write_note(write_file=write_file,timestamp=0,
												 track=0,
												 channel=1,
												 event=1,
												 note=cur_note,
												 midipower=cur_pwr)
				write_file.write('print \'playing note {0} with power {1}...\\n\'\n'.format(cur_note,cur_pwr))
				write_note(write_file=write_file,timestamp=delay_time,
												 track=0,
												 channel=1,
												 event=0,
												 note=cur_note,
												 midipower=0)
				cur_pwr = inc_pwr + cur_pwr
			cur_note = cur_note + 1

		print ('\ntest.py file has been generated to play from notes {0}'
			  '-{1} with power {2} to {3} in increments of {4} '
		 	  'delay {5}ms'
		 	  ''.format(start_note, end_note, min_pwr, max_pwr,inc_pwr,delay_time))

	# -test [start_note] [end_note] [delay_time] [pwr] 
	elif len(args.test) == 4:
		pwr=int(args.test[3])

		if(delay_time<const.HLD_DLY):
			print '\nWARNING: delay_time({0}) is less than hold delay time({1})'.format(delay_time,const.HLD_DLY)

		while cur_note <= end_note:
			write_note(write_file=write_file,timestamp=0,
											 track=0,
											 channel=1,
											 event=1,
											 note=cur_note,
											 midipower=pwr,
											 hold=True)
			write_file.write('print \'playing note {0} with power {1} ... \\n\'\n'.format(cur_note,pwr))
			write_note(write_file=write_file,timestamp=delay_time,
											 track=0,
											 channel=1,
											 event=0,
											 note=cur_note,
											 midipower=0,
											 hold=True)
			cur_note = cur_note + 1

		print ('\ntest.py file has been generated to play notes {0}-{1}'
			  ' with power {2} and delay {3}ms'
		 	  ''.format(start_note, end_note, pwr, delay_time))
	else:
		parser.print_help()

	write_footer(write_file)

else:
	parser.print_help()
