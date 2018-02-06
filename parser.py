import argparse
import re
import const
import math
from note import Note
import logging

def write_header(write_file):
	write_file.write('import serial\n')
	write_file.write('import time\n')
	write_file.write('ser = serial.Serial(\'{0}\', 115200, timeout=5)\n'.format(const.COM_SERIAL))
	write_file.write('time.sleep(1)\n\n')
	write_file.write('#<Timestamp, track number, MIDI channel, type, key, value>\n')
	write_file.write('ser.write(\'<0,0,0,8,0,0>\')\n')


def write_footer(write_file):
	write_file.write('ser.write(\'<0,0,0,7,0,0>\')\n')


def write_note(write_file,timestamp,track,channel,event,note,power,hold=False):
	write_file.write('ser.write(\'<{},{},{},{},{},{}>\')\n'.format(int(timestamp),track,channel,event,note,power))
	write_file.write('ser.readline()\n')
	if(hold==True and event == 1):
		write_file.write('ser.write(\'<{},{},{},{},{},{}>\')\n'.format(int(timestamp + const.NORMAL_POWER_START_DUR),track,channel,event,note,const.NORMAL_POWER_START_POWER))
		write_file.write('ser.readline()\n')
	

def write_notes(write_file,notes):
	notes_copy = implode_notes(notes)
	notes_copy.sort(key=lambda x: (x['timestamp']))

	for note in notes_copy:
		write_note(write_file,timestamp=note['timestamp'],
							  track=note['track'],
							  channel=note['channel'],
							  event=note['event'],
							  note=note['note'],
							  power=note['power'])


def adjust_note_vol(note,avg):
	note['power'] = int((note['power']-avg) * const.NOTE_SCALE[note['note']] + const.NOTE_OFFSET[note['note']] + avg)
	return note


def compress_note(note,tmax,tmin):
	note['power'] = tmax if note['power'] > tmax else tmin
	return note


def implode_notes(notes):
	imploded_list = []
	for note in notes:
		#add high power first
		imploded_list.append({'timestamp':int(note.note_on),
							  'track':int(note.track),
							  'channel':(note.channel),
							  'event':int(1),
							  'note':int(note.key),
							  'power':int(const.HIGH_POWER_START_POWER)})
		#then add normal power
		if note.get_dur() >= const.HIGH_POWER_START_DUR:
			imploded_list.append({'timestamp':int(const.HIGH_POWER_START_DUR + note.note_on),
								  'track':int(note.track),
								  'channel':(note.channel),
								  'event':int(1),
								  'note':int(note.key),
								  'power':int(note.power)})
		#then add low power
		if note.get_dur() >= const.HIGH_POWER_START_DUR + const.NORMAL_POWER_START_DUR:
			imploded_list.append({'timestamp':int(const.HIGH_POWER_START_DUR + const.NORMAL_POWER_START_DUR + note.note_on),
								  'track':int(note.track),
								  'channel':(note.channel),
								  'event':int(1),
								  'note':int(note.key),
								  'power':int(const.LOW_POWER)})
		imploded_list.append({'timestamp':int(note.note_off),
							  'track':int(note.track),
							  'channel':(note.channel),
							  'event':int(0),
							  'note':int(note.key),
							  'power':int(note.power)})
		
	return imploded_list


def normalize(notes):
	tmax, tmin = (const.TARGET_MAX-const.TARGET_MIN)/2.0, (const.TARGET_MIN-const.TARGET_MAX)/2.0
	num_of_notes = sum(1 for note in notes if note['event']==1)
	sum_vol = sum(note['power'] for note in notes if note['event']==1)
	avg_vol = sum_vol / num_of_notes
	num_percent = num_of_notes / const.NUM_PERCENT

	for note in notes:
		if note['event']==1: note['power'] -= avg_vol
	notes.sort(key=lambda x: (x['event'],x['power']))
	NORMAL_linear_power, high_linear_power = 0.0, 0.0
	for index, note in enumerate(filter(lambda x:x['event']==1 and x['power'] < 0,notes)):
		if index<num_percent: note['power'] = tmin;
		elif index==num_percent: 
			NORMAL_exp_power = tmin/note['power'] if note['power']!=0 else 1
		else: note['power'] = note['power'] * NORMAL_linear_power
	for index, note in enumerate(filter(lambda x:x['event']==1 and x['power'] >= 0, reversed(notes))):
		if index<num_percent: note['power'] = tmax;
		elif index==num_percent: 
			high_exp_power=tmax/note['power'] if note['power']!=0 else 1
		else: note['power'] = note['power'] * high_linear_power
	for index, note in enumerate(filter(lambda x:x['event']==1, notes)):
		note['power'] = int(note['power'] + const.TARGET_MAX - tmax)
		note=adjust_note_vol(note=note,avg=avg_vol)
	return notes


if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='Parses Midi Text file into Python commands for Arduino')
	parser.add_argument('-test', nargs='*', action='store', help='-test [start_note] [end_note] [delay_time] [power]  or -test [start_note] [end_note] [delay_time] [min_power] [max_power] [inc_power] ')
	parser.add_argument('input_file', metavar='input', type=str, nargs='?', help='the name of the input midi text file')
	args = parser.parse_args()

	if(args.input_file):
		
		# read from txt and store into lists of <timestamp,event,note,power>
		notes = []
		with open(args.input_file,'r') as read_file:
			for line in read_file:		
				timestamp,track,channel,event,note,power=line.strip().split(',')
				notes.append({'timestamp':int(timestamp),'track':int(track),'channel':(channel),'event':int(event),'note':int(note),'power':int(power)})
		
		# normalize all notes
		notes=normalize(notes)

		#store as Note class
		notes.sort(key=lambda x: (x['note'],x['timestamp'],x['track'],x['channel']))
		notes_copy = []
		for index,note in enumerate(notes):
			if note['event'] == 1:
				note_on = note['timestamp']
				note_off = notes[index+1]['timestamp']
				key = note['note']
				power = note['power']
				track = note['track']
				channel = note['channel']
				notes_copy.append(Note(note_on=note['timestamp'],
									   note_off=notes[index+1]['timestamp'],
									   key=note['note'],
									   power=note['power'],
									   track=note['track'],
									   channel=note['channel']))

		# cut tail & min note dur
		for index,note in enumerate(notes_copy):
			# check if out of bound
			next_note = notes_copy[index+1] if index+1 < len(notes_copy) else None
			#if next note exists
			if next_note is not None:
				#set note duration to DESIRED_NOTE_DUR if less than it
				if note.get_dur() < const.DESIRED_NOTE_DUR:
					note.set_dur(const.DESIRED_NOTE_DUR)
					#change gap to 1ms if there's overlap
					if note.is_overlapped(next_note): note.set_gap(next_note,gap=1)
				# if gap is leses than DESIRED_GAP_DUR and that there is a gap
				if note.get_gap(next_note) < const.DESIRED_GAP_DUR and note.get_gap(next_note) is not None:
					# if ntoe duration is larger than DESIRED_NOTE_DUR + gap
					# print '{} ------------------> {}'.format(note,next_note)
					if note.get_dur() > const.DESIRED_NOTE_DUR + note.get_gap(next_note):
						note.set_dur(note.get_dur()-const.DESIRED_GAP_DUR)
					else:
						# if not, set note duration to math formula
						note.set_dur((note.get_gap(next_note) + note.get_dur()) * (1. - const.MULTIPLIER_SPLIT_RELEASE_TIME_RATIO))
						# update small release time 
						small_release_time = (note.get_gap(next_note) + note.get_dur()) * const.MULTIPLIER_SPLIT_RELEASE_TIME_RATIO
						if small_release_time < const.MIN_GAP_DUR:
							note.set_gap(next_note,const.MIN_GAP_DUR)
						else:
							note.set_gap(next_note,small_release_time)
						if note.is_overlapped(next_note):
							note.set_gap(next_note,const.MIN_GAP_DUR)
							# note_off['timestamp'] = next_note_on['timestamp'] - 1

		#write files
		with open(args.input_file[:len(args.input_file)-4] + '.py','w') as write_file:
			write_header(write_file)
			write_notes(write_file,notes_copy)
			write_footer(write_file)
		num_of_notes = num_notes = sum(1 for note in notes if note['event']==1)
		print '\'{}.py\' has been created with {} notes'.format(args.input_file[:len(args.input_file)-4],num_of_notes)

	elif (args.test):
		# -test [start_note] [end_note] [delay_time] [min_power] [max_power] [inc_power] 
		if len(args.test) == 6:
			start_note=int(args.test[0])
			end_note=int(args.test[1])
			delay_time=int(args.test[2])
			min_power=int(args.test[3])
			max_power=int(args.test[4])
			inc_power=int(args.test[5])
			cur_power = min_power

			if(delay_time<const.NORMAL_POWER_START_DUR):
				logging.warning('\nWARNING: delay_time({0}) is less than hold delay time({1})'.format(delay_time,const.NORMAL_POWER_START_DUR))

			notes=[]
			for cur_note in xrange(start_note,end_note):
				for cur_power in xrange(min_power, max_power,inc_power):
					notes.append(Note(note_on=len(notes)*delay_time,
									  note_off=(len(notes)+1)*delay_time,
									  key=cur_note,
									  power=cur_power,
									  track=1,
									  channel=1))

			with open('test.py','w') as write_file:
				write_header(write_file)
				write_notes(write_file,notes)
				write_footer(write_file)

			print ('\ntest.py file has been generated to play from notes {0}'
				  '-{1} with power {2} to {3} in increments of {4} '
			 	  'delay {5}ms'
			 	  ''.format(start_note, end_note, min_power, max_power,inc_power,delay_time))

		# -test [start_note] [end_note] [delay_time] [power] 
		elif len(args.test) == 4:
			start_note=int(args.test[0])
			end_note=int(args.test[1])
			delay_time=int(args.test[2])
			power=int(args.test[3])

			if(delay_time<const.NORMAL_POWER_START_DUR):
				print '\nWARNING: delay_time({0}) is less than hold delay time({1})'.format(delay_time,const.NORMAL_POWER_START_DUR)

			notes=[]
			for cur_note in xrange(start_note,end_note):
				notes.append(Note(note_on=len(notes)*delay_time,
								  note_off=(len(notes)+1)*delay_time,
								  key=cur_note,
								  power=power,
								  track=1,
								  channel=1))

			with open('test.py','w') as write_file:
				write_header(write_file)
				write_notes(write_file,notes)
				write_footer(write_file)

			print ('\ntest.py file has been generated to play notes {0}-{1}'
				  ' with power {2} and delay {3}ms'
			 	  ''.format(start_note, end_note, power, delay_time))
		else:
			parser.print_help()
	else:
		parser.print_help()
