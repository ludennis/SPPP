
#CONSTANTS to tweak
# TAIL_GAP_MSEC => Something to do with notes being played closed to each
# MIN_NOTE_DUR => min time for a note to be playable
# HOLD_DELAY_POWER_START_MSEC => time when solarnoid will start holding
# HOLD_DELAY_POWER => power when the solarnoid is holding
# COM_SERIAL => serial number when connecting to Arduino
# SUSTAIN_NOTE => the note that a sustain will be used 
# NOTE_SCALE => will multiply the value set to the corresponding note
# NUM_PERCENT => number of percentage of notes to be outside of the TARGET_MAX and TARGET_MIN

# TAIL_GAP_MSEC = 30
# MIN_NOTE_DUR = 35
# HOLD_DELAY_POWER_START_MSEC = 90
# HOLD_DELAY_POWER = 75
# COM_SERIAL = 'COM11'
# SUSTAIN_NOTE = 150
# TARGET_MAX = 152
# TARGET_MIN = 135


TAIL_GAP_MSEC = 50
MIN_NOTE_DUR = 30
HOLD_DELAY_POWER_START_MSEC = 90
HOLD_DELAY_POWER = 75
COM_SERIAL = 'COM11'
SUSTAIN_NOTE = 150
TARGET_MAX = 155
TARGET_MIN = 138
NUM_PERCENT = 10

NOTE_SCALE = [0, 
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,					  #ignore
			 
			 
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 1 notes 24-35
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 2 notes 36-47
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 3 notes 48-59
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 4 notes 60-71
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 5 notes 72-83
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 6 notes 84-96
			 
			 
			 0,0,0,0,         #ignore, this is up to 100
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0]     #ignore this is up to 150

NOTE_OFFSET = [0, 
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,				      #ignore
			 
			 
			   0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, #Octave 1 notes 24-35
			  -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, #Octave 2 notes 36-47
			  -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, #Octave 3 notes 48-59
			   0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, #Octave 4 notes 60-71
			   1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, #Octave 5 notes 72-83
			   5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5, #Octave 6 notes 84-96
			 
			 
			 0,0,0,0,                 #ignore, this is up to 100
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0]     #ignore this is up to 150