import argparse
import re

#TODO: Hold power after each NoteOn (for cooling off)
#TODO: Each key on piano to tweak:
#      - multiplier
#      - offset

#CONSTANTS to tweak
TAIL_GAP_MSEC = 250
MIN_DURATION = 80
HOLD_DELAY_POWER_START_MSEC = 90
HOLD_DELAY_POWER = 3
COM_SERIAL = 'COM11'

#KEY_SCALE will multiply the value set to the corresponding key
KEY_SCALE = [0, 
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,					  #ignore
			 
			 
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 1 keys 24-35
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 2 keys 36-47
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 3 keys 48-59
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,0.95,0.95,0.94,0.94,0.93, #Octave 4 keys 60-71
			 0.93,0.92,0.92,0.91,0.91,0.90,0.90,0.89,0.89,0.88,0.88,0.87, #Octave 5 keys 72-83
			 0.88,0.87,0.86,0.85,0.84,0.83,0.82,0.81,0.80,0.79,0.78,0.77, #Octave 6 keys 84-96
			 
			 
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
			   3,  2,  2,  2,  1,  1,  1,  0,  0, -1, -1, -2, #Octave 3 keys 48-59
			  -2, -3, -3, -4, -4, -5, -5, -6, -6, -7, -7, -8, #Octave 4 keys 60-71
			  -8, -9, -9,-10,-10,-11,-11,-12,-12,-13,-13,-14, #Octave 5 keys 72-83
			 -14,-15,-15,-16,-16,-17,-17,-18,-18,-19,-19,-20, #Octave 6 keys 84-96
			 
			 
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

def writeKeyWithHold(write_file,t,key,pwr):
	write_file.write('ser.write(\'<{0},{1},{2}>\')\n'.format(t,key,pwr))
	write_file.write('ser.readline()\n')
	if(pwr > 3):
		write_file.write('ser.write(\'<{0},{1},{2}>\')\n'.format(HOLD_DELAY_POWER_START_MSEC,key,HOLD_DELAY_POWER))
		write_file.write('ser.readline()\n')

#TODO: add an argument that can take "test" to make a testing .py file for arduino
parser = argparse.ArgumentParser(description='Parses Midi Text file into Python commands for Arduino')
parser.add_argument('-test', nargs='*', action='store', help='-test [start_key] [end_key] [pwr] or -test [start_key] [end_key] [min_pwr] [max_pwr] [inc_pwr]')
parser.add_argument('input_file', metavar='input', type=str, nargs='?', help='the name of the input midi text file')

args = parser.parse_args()

#print(args)

if(args.input_file) :
	read_file = open(args.input_file, 'r')
	l = []

	for line in read_file:
		match = re.match(r'[0-9]+,Min:Sec:Msec=(?P<min>[0-9]+):(?P<sec>[0-9]+):(?P<msec>[0-9]+),(?P<action>[a-zA-Z]+) chan: 1(?P<params>( [a-zA-Z]+: [0-9]+)+)', line)
		if match:
			time_in_msec = int(match.group('min')) * 60000 + int(match.group('sec')) * 1000 + int(match.group('msec'))
			if match.group('action') == 'NoteOn':
				match = re.match(r' [a-zA-Z]+: (?P<note>[0-9]+) [a-zA-Z]+: (?P<vol>[0-9]+) [a-zA-Z]+: (?P<dur>[0-9]+)',match.group('params'))
				if match:
					l.append([time_in_msec,int(match.group('note')),int(int(match.group('vol'))*KEY_SCALE[int(match.group('note'))] + KEY_OFFSET[int(match.group('note'))] )])
			elif match.group('action') == 'NoteOff':
				match = re.match(r' [a-zA-Z]+: (?P<note>[0-9]+)',match.group('params'))
				if match:
					l.append([time_in_msec,int(match.group('note')),int(0)])
			elif match.group('action') == 'Sustain':
				match = re.match(r' [a-zA-Z]+: (?P<val>[0-9]+)',match.group('params'))
				l.append([time_in_msec,int(150),int(match.group('val'))])


	#sort the list according to note and then timestamp
	l.sort(key=lambda x: (x[1],x[0]))

	#cut tail of note when it is immediately played again by 50ms
	#if diff(timestamp(NoteOff) - timestamp(NoteOn) < 50) then timestamp(NoteOff) - 50ms
	i = 0
	while i < len(l) - 1:
		if l[i][1] != 150 and l[i][2] == 0 and l[i][1] == l[i+1][1] and l[i+1][0] - l[i][0] < TAIL_GAP_MSEC:
			print 'checking: NoteOn{0} , NoteOff{1} , next NoteOn{2}'.format(l[i-1],l[i],l[i+1])
			if l[i+1][0] - TAIL_GAP_MSEC - l[i-1][0] < MIN_DURATION:
				l[i][0] = l[i-1][0] + MIN_DURATION
			else:
				l[i][0] = l[i+1][0] - TAIL_GAP_MSEC
			print 'changed {0}\n'.format(l[i])
		elif l[i][1] != 150 and l[i][2] != 0 and l[i][2] != HOLD_DELAY_POWER and l[i+1][0] - l[i][0] > MIN_DURATION:
			print 'checking to add power hold: {0} next action {1}'.format(l[i],l[i+1])
			l.insert(i+1,[l[i][0] + HOLD_DELAY_POWER_START_MSEC,l[i][1],HOLD_DELAY_POWER])
			print 'added {0}\n'.format(l[i+1])
		i+=1


	#sort according to timestamp and change to delta t
	l.sort()
	i = len(l) - 1
	while i > 1:
		l[i][0] = l[i][0] - l[i-1][0]
		i-=1
	#quickfix to make sure the first two notes are with zero t
	l[0][0] = 0
	l[1][0] = 0

	#write files
	write_file = open(args.input_file[:len(args.input_file)-4] + '.py', 'w')
	writeHeader(write_file)

	for i in l:
		write_file.write('ser.write(\'<{0},{1},{2}>\')\n'.format(i[0],i[1],i[2]))
		write_file.write('ser.readline()\n')

	print '\'' + args.input_file[:len(args.input_file)-4] + '.py\' has been created'
elif (args.test):
	if len(args.test) == 5:
		#This will write a testing file to play the piano 
		#'test.py' will be generated
		write_file = open('test.py', 'w')
		writeHeader(write_file)

		#test keys 24-96
		start_key=int(args.test[0])
		end_key=int(args.test[1])
		min_pwr=int(args.test[2])
		max_pwr=int(args.test[3])
		inc_pwr=int(args.test[4])
		cur_key = start_key
		cur_pwr = min_pwr

		while cur_key <= end_key:
			cur_pwr = min_pwr
			while cur_pwr <= max_pwr:
				write_file.write('ser.write(\'<0,{0},{1}>\')\n'.format(cur_key,cur_pwr))
				write_file.write('ser.readline()\n')
				write_file.write('print \'playing note {0} with power {1}...\\n\'\n'.format(cur_key,cur_pwr))
				write_file.write('ser.write(\'<1000,{0},0>\')\n'.format(cur_key))
				write_file.write('ser.readline()\n')
				cur_pwr = inc_pwr + cur_pwr
			cur_key = cur_key + 1

		print ('\ntest.py file has been generated to play from key {0}'
			  ' to key {1} with the power from {2} to {3} in the '
		 	  'increment of {4} in every second'
		 	  ''.format(start_key, end_key, min_pwr, max_pwr,inc_pwr))
	elif len(args.test) == 3:
		#this will write a testing file with desired pwr from start_key to end_key
		write_file = open('test.py', 'w')
		writeHeader(write_file)

		start_key=int(args.test[0])
		end_key=int(args.test[1])
		pwr=int(args.test[2])
		cur_key = start_key
		while cur_key <= end_key:
			writeKeyWithHold(write_file,0,cur_key,pwr)
			write_file.write('print \'playing note {0} with power {1} ... \\n\'\n'.format(cur_key,pwr))
			writeKeyWithHold(write_file,1000,cur_key,0) 
			cur_key = cur_key + 1

		print ('\ntest.py file has been generated to play from key {0}'
			  ' to key {1} with the power of {2}'
		 	  ''.format(start_key, end_key, pwr))
