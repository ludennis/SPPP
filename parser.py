import argparse
import re

#TODO: Hold power after each NoteOn (for cooling off)
#TODO: Each key on piano to tweak:
#      - multiplier
#      - offset

#CONSTANTS to tweak
TAIL_GAP_MSEC = 250
MIN_DURATION = 140
HOLD_DELAY_POWER_START_MSEC = 170
HOLD_DELAY_POWER = 50
COM_SERIAL = 'COM11'

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

def writeKey(write_file,time,key,pwr,hold=False):
	write_file.write('ser.write(\'<{0},{1},{2}>\')\n'.format(time,key,pwr))
	if(hold==True and pwr > 3):
		write_file.write('ser.write(\'<{0},{1},{2}>\')\n'.format(HOLD_DELAY_POWER_START_MSEC,key,HOLD_DELAY_POWER))
	write_file.write('ser.readline()\n')

def adjust_vol(vol,note,avg):
	return int((vol-avg) * KEY_SCALE[note] + KEY_OFFSET[note] + avg)

#TODO: add an argument that can take "test" to make a testing .py file for arduino
parser = argparse.ArgumentParser(description='Parses Midi Text file into Python commands for Arduino')
parser.add_argument('-test', nargs='*', action='store', help='-test [start_key] [end_key] [pwr] [delay_time] or -test [start_key] [end_key] [min_pwr] [max_pwr] [inc_pwr] [delay_time]')
parser.add_argument('input_file', metavar='input', type=str, nargs='?', help='the name of the input midi text file')
parser.add_argument('--target-average', type=int, help='--target-average=[target_average_power]')
args = parser.parse_args()
#print(args)

if(args.input_file) :

	read_file = open(args.input_file, 'r')
	num_of_notes = 0
	sum_vol = 0
	l = []

	#match and add into list l[timestamp,note,vol]
	for line in read_file:
		match = re.match(r'[0-9]+,Min:Sec:Msec=(?P<min>[0-9]+):(?P<sec>[0-9]+):(?P<msec>[0-9]+),(?P<action>[a-zA-Z]+) chan: 1(?P<params>( [a-zA-Z]+: [0-9]+)+)', line)
		if match:
			time_in_msec = int(match.group('min')) * 60000 + int(match.group('sec')) * 1000 + int(match.group('msec'))
			if match.group('action') == 'NoteOn':
				match = re.match(r' [a-zA-Z]+: (?P<note>[0-9]+) [a-zA-Z]+: (?P<vol>[0-9]+) [a-zA-Z]+: (?P<dur>[0-9]+)',match.group('params'))
				if match:
					num_of_notes = num_of_notes + 1
					sum_vol = sum_vol + int(match.group('vol'))
					l.append([time_in_msec,int(match.group('note')),int(int(match.group('vol')))])
			elif match.group('action') == 'NoteOff':
				match = re.match(r' [a-zA-Z]+: (?P<note>[0-9]+)',match.group('params'))
				if match:
					l.append([time_in_msec,int(match.group('note')),int(0)])
			elif match.group('action') == 'Sustain':
				match = re.match(r' [a-zA-Z]+: (?P<val>[0-9]+)',match.group('params'))
				l.append([time_in_msec,int(150),int(match.group('val'))])
	
	if args.target_average == None:
		avg_vol = sum_vol/num_of_notes
	else:
		avg_vol = args.target_average
	print 'num of notes {0} with sum volume {1} and average vol {2}'.format(num_of_notes,sum_vol,avg_vol)

	#sort the list according to note and then timestamp
	l.sort(key=lambda x: (x[1],x[0]))

	#l[[timestamp,note,vol],[timestamp,note,vol], ...]
	#cut tail of note when it is immediately played again by 50ms
	#if diff(timestamp(NoteOff) - timestamp(NoteOn) < 50) then timestamp(NoteOff) - 50ms
	#also change vol according to average vol
	i = 0

	while i < len(l) - 1:
		if l[i][1] != 150 and l[i][2] == 0 and l[i][1] == l[i+1][1] and l[i+1][0] - l[i][0] < TAIL_GAP_MSEC:
			# print 'checking: NoteOn{0} , NoteOff{1} , next NoteOn{2}'.format(l[i-1],l[i],l[i+1])
			if l[i+1][0] - TAIL_GAP_MSEC - l[i-1][0] < MIN_DURATION:
				l[i][0] = l[i-1][0] + MIN_DURATION
			else:
				l[i][0] = l[i+1][0] - TAIL_GAP_MSEC
			# print 'changed {0}\n'.format(l[i])
		elif l[i][1] != 150 and l[i][2] != 0 and l[i][2] != HOLD_DELAY_POWER and l[i+1][0] - l[i][0] > MIN_DURATION:
			# print 'checking to add power hold: {0} next action {1}'.format(l[i],l[i+1])
			l.insert(i+1,[l[i][0] + HOLD_DELAY_POWER_START_MSEC,l[i][1],HOLD_DELAY_POWER])
			# print 'added {0}\n'.format(l[i+1])
		if l[i][2] > HOLD_DELAY_POWER and l[i][1] != 150:
			l[i][2] = adjust_vol(vol=l[i][2],note=l[i][1],avg=avg_vol)
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
		writeKey(write_file,i[0],i[1],i[2])
	print '\'' + args.input_file[:len(args.input_file)-4] + '.py\' has been created'
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
