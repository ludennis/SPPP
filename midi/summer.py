import serial
import time
ser = serial.Serial('COM3', 115200, timeout=5)
time.sleep(1)

#SRT = MRT * MSRT = 40 * 4 = 160ms
#SD = HD * MSD = 85 * 1.6 = 136ms
#HDP = 65 power
#HD = 85 ms

#<timestamp,event,note,midipower>
ser.write('<0,0,0,8,0,0>')
ser.write('<58,1,0,0,74,64>')
ser.readline()
ser.write('<9795,1,0,1,76,151>') 
ser.readline()
ser.write('<9795,2,1,1,47,153>')
ser.readline()
ser.write('<10051,1,0,0,76,64>') #note_dur of #76 => 10051-9795=256
ser.readline()
ser.write('<10102,1,0,1,74,151>') #74 note_on
ser.readline()
ser.write('<10102,2,1,0,47,64>')
ser.readline()
ser.write('<10102,2,1,1,54,149>')
ser.readline()
ser.write('<10187,1,0,1,74,65>') #74 note_on hold delay 85ms
ser.readline()
ser.write('<10187,2,1,1,54,65>')
ser.readline()
ser.write('<10238,2,1,0,54,64>')
ser.readline()
ser.write('<10255,1,0,1,74,151>')
ser.readline()
ser.write('<10408,2,1,1,59,149>')
ser.readline()
ser.write('<10510,2,1,0,59,64>')
ser.readline()
ser.write('<10714,2,1,1,54,149>')
ser.readline()
ser.write('<10816,2,1,0,54,64>')
ser.readline()
ser.write('<10918,1,0,0,74,64>')
ser.readline()
ser.write('<0,0,0,7,0,0>')
