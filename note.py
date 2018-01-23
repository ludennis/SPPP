class Note(object):
	def __init__(self,note_on,note_off,key,power):
		self.note_on = note_on
		self.note_off = note_off
		self.key = key
		self.power = power

	def __str__(self):
		return '<note_on {}, note_off {}, key {}, power {}, duration {}>'.format(self.note_on,self.note_off,self.key,self.power,self.get_dur())

	def get_dur(self):
		return self.note_off - self.note_on
	
	def set_dur(self,dur):
		self.note_off = self.note_on + dur

	def get_gap(self,other):
		return other.note_on - self.note_off

	def set_gap(self,other,gap):
		self.note_off = other.note_on - gap

first_note = Note(note_on=10102,note_off=10229,key=74,power=110)
second_note = Note(note_on=10255,note_off=10918,key=74,power=110)
print first_note
print second_note
print 'the gap between note 1 and note 2 is {}'.format(first_note.get_gap(second_note))

first_note.set_gap(second_note,50)

print first_note
print second_note
print 'the gap between note 1 and note 2 is {}'.format(first_note.get_gap(second_note))
