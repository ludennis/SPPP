import argparse
import re

#TODO: Hold power after each NoteOn (for cooling off)
#TODO: Each key on piano to tweak:
#      - multiplier
#      - offset

#CONSTANTS to tweak
TAIL_GAP_MSEC = 250
MIN_DURATION = 80
HOLD_POWER_START_MSEC = 50
HOLD_POWER = 35
COM_SERIAL = 'COM3'

#KEY_SCALE will multiply the value set to the corresponding key
KEY_SCALE = [0, 
			 1,1,1,1,1,1,1,1,1,1, #keys 1-10
			 1,1,1,1,1,1,1,1,1,1, #keys 11-20
			 1,1,1,1,1,1,1,1,1,1, #keys 21-30
			 1,1,1,1,1,1,1,1,1,1, #keys 31-40
			 1,1,1,1,1,1,1,1,1,1, #keys 41-50
			 1,1,1,1,1,1,1,1,1,1, #keys 51-60
			 1,1,1,1,1,1,1,1,1,1, #keys 61-70
			 1,1,1,1]             #keys 71-74

parser = argparse.ArgumentParser(description='Parses Midi Text file into Arduino Commands')
parser.add_argument('input_file', metavar='input', type=str, nargs='?', help='the name of the input midi text file')
args = parser.parse_args()

read_file = open(args.input_file, 'r')
l = []

for line in read_file:
	match = re.match(r'[0-9]+,Min:Sec:Msec=(?P<min>[0-9]+):(?P<sec>[0-9]+):(?P<msec>[0-9]+),(?P<action>[a-zA-Z]+) chan: 1(?P<params>( [a-zA-Z]+: [0-9]+)+)', line)
	if match:
		time_in_msec = int(match.group('min')) * 60000 + int(match.group('sec')) * 1000 + int(match.group('msec'))
		if match.group('action') == 'NoteOn':
			match = re.match(r' [a-zA-Z]+: (?P<note>[0-9]+) [a-zA-Z]+: (?P<vol>[0-9]+) [a-zA-Z]+: (?P<dur>[0-9]+)',match.group('params'))
			if match:
				l.append([time_in_msec,int(match.group('note')),int(match.group('vol')*KEY_SCALE[int(match.group('note'))])])
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
		print 'checking: NoteOn' + str(l[i-1]) + ' , NoteOff' + str(l[i]) + ' , next NoteOn' + str(l[i+1])
		if l[i+1][0] - TAIL_GAP_MSEC - l[i-1][0] < MIN_DURATION:
			l[i][0] = l[i-1][0] + MIN_DURATION
		else:
			l[i][0] = l[i+1][0] - TAIL_GAP_MSEC
		print 'changed ' + str(l[i]) + '\n'
	elif l[i][1] != 150 and l[i][2] != 0 and l[i][2] != HOLD_POWER and l[i+1][0] - l[i][0] > MIN_DURATION:
		print 'checking to add power hold: ' + str(l[i]) + ' next action ' + str(l[i+1]) 
		l.insert(i+1,[l[i][0] + HOLD_POWER_START_MSEC,l[i][1],HOLD_POWER])
		print 'added ' + str(l[i+1]) + '\n'
	i+=1


#sort according to timestamp and change to delta t
l.sort()
i = len(l) - 1
while i > 1:
	l[i][0] = l[i][0] - l[i-1][0]
	i-=1

#write files
write_file = open(args.input_file[:len(args.input_file)-4] + '.py', 'w')
write_file.write('import serial\n')
write_file.write('import time\n')
write_file.write('ser = serial.Serial(\'' + COM_SERIAL + '\', 115200, timeout=5)\n')
write_file.write('time.sleep(1)\n\n')

for i in l:
	write_file.write('ser.write(\'<' + str(i[0]) + ',' + str(i[1]) + ',' + str(i[2]) + '>\')\n')
	write_file.write('ser.readline()\n')

print '\'' + args.input_file[:len(args.input_file)-4] + '.py\' has been created'