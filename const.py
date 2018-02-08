#CONSTANTS to tweak
# TAIL_GAP_MSEC => The time span of the gap to exist in between 2 consecutive notes
# MIN_NOTE_DUR => min time for a note to be playable
# COM_SERIAL => serial number when connecting to Arduino
# SUSTAIN_NOTE => the note that a sustain will be used 
# NOTE_SCALE => will multiply the value set to the corresponding note
# NUM_PERCENT => number of percentage of notes to be outside of the TARGET_MAX and TARGET_MIN

# COM_SERIAL = 'COM11'
# SUSTAIN_NOTE = 150
# TARGET_MAX = 152
# TARGET_MIN = 135

HIGH_POWER_DUR = 5
HIGH_POWER = 195
RATIO_CUT_NORMAL_POWER_DUR = .4 #the larger it is, the smaller normal_power_dur will be
PERCENT_LOW_POWER_IGNORE = .2 #the percentage if low power to be not affected
BASE_NORMAL_POWER_DUR = 85
LOW_POWER = 65


MIN_GAP_DUR = 40 #absolute smallest tailgap

MULTIPLIER_DESIRED_MIN_NOTE_DUR = 2.4
MULTIPLIER_DESIRED_GAP_DUR = 4
MULTIPLIER_SPLIT_RELEASE_TIME_RATIO = .62

DESIRED_GAP_DUR = MIN_GAP_DUR * MULTIPLIER_DESIRED_GAP_DUR
DESIRED_NOTE_DUR = BASE_NORMAL_POWER_DUR * MULTIPLIER_DESIRED_MIN_NOTE_DUR

COM_SERIAL = 'COM3'
SUSTAIN_NOTE = 150
TARGET_MAX = 155
TARGET_MIN = 146
NUM_PERCENT = 5

TARGET_RANGE = TARGET_MAX - TARGET_MIN
LOW_POWER_IGNORE = TARGET_RANGE * PERCENT_LOW_POWER_IGNORE


NOTE_SCALE = [0, 
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,					  #ignore
			 
			 
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 1 notes 24-35
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 2 notes 36-47
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 3 notes 48-59
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 4 notes 60-71
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 5 notes 72-83
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 6 notes 84-95
			 1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00, #Octave 7 notes 96-107
			 
			 0,0,0,0,         #ignore, this is up to 100
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0]     #ignore this is up to 150

NOTE_OFFSET = [0, 
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,				      #ignore
			 
			 
			  -5, -5, -5, -5, -5, -5, -5, -5, -5, -5, -5, -5, #Octave 1 notes 24-35
			  -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, #Octave 2 notes 36-47
			  -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, #Octave 3 notes 48-59
			   0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, #Octave 4 notes 60-71
			   3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3, #Octave 5 notes 72-83
			   7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7, #Octave 6 notes 84-96
			   9,  9,  9,  9,  9,  9,  9,  9,  9,  9,  9,  9, #Octave 6 notes 84-96
			 
			 
			 0,0,0,0,                 #ignore, this is up to 100
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0,     #ignore
			 0,0,0,0,0,0,0,0,0,0]     #ignore this is up to 150

