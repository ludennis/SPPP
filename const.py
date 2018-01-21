#CONSTANTS to tweak
# TAIL_GAP_MSEC => The time span of the gap to exist in between 2 consecutive notes
# MIN_NOTE_DUR => min time for a note to be playable
# HOLD_DELAY_POWER_START_MSEC => time when solarnoid will start holding
# HLD_DLY => power when the solarnoid is holding
# COM_SERIAL => serial number when connecting to Arduino
# SUSTAIN_NOTE => the note that a sustain will be used 
# NOTE_SCALE => will multiply the value set to the corresponding note
# NUM_PERCENT => number of percentage of notes to be outside of the TARGET_MAX and TARGET_MIN

# MIN_NOTE_DUR = 35
# HOLD_DELAY_POWER_START_MSEC = 90
# HOLD_DELAY_POWER = 75
# COM_SERIAL = 'COM11'
# SUSTAIN_NOTE = 150
# TARGET_MAX = 152
# TARGET_MIN = 135

HLD_DLY = 85 #replaces HOLD_DELAY_POWER_START_MSEC
HLD_DLY_PWR = 65
MIN_RELEASE_TIME = 40 #absolute smallest tailgap

MULTIPLIER_SUGGESTED_DUR = 1.6
MULTIPLIER_SUGGESTED_RELEASE_TIME = 4
MULTIPLIER_SPLIT_RELEASE_TIME = .62

SUGGESTED_RELEASE_TIME = MIN_RELEASE_TIME * MULTIPLIER_SUGGESTED_RELEASE_TIME
SUGGESTED_DUR = HLD_DLY * MULTIPLIER_SUGGESTED_DUR

COM_SERIAL = 'COM3'
SUSTAIN_NOTE = 150
TARGET_MAX = 155
TARGET_MIN = 146
NUM_PERCENT = 5


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
