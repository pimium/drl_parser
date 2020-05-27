import re

class DrillGroup:
	def __init__(self, file=None, number=None, diameter=None):

		self.file = file
		self.number = number
		self.diameter = diameter
		self.drill = []

	def __str__(self):
		test = ''
		xy = ''
		test = '{ number: ' + self.number + ', diameter: ' + self.diameter + ',\n drill: ['
		for items in self.drill:
			xy = xy + '(' + items[0] + ', ' + items[0] + '),'
			# print items
		return test + xy + ']},\n'

	def parse(self):
		start_reading = 0
		stop_reading = 0
		with open(self.file, "r") as file:
			for line in file: 
				if stop_reading:
					break
				if (start_reading == 0):
					if (re.match('T'+self.number+'\s', line)):	
						#print(line),
						start_reading = 1
				elif start_reading:
					if (re.match('T\d\s', line)):
						# print("\nEXIT\n"),
						# print(line)
						stop_reading = 1
						break
					else:
						if (re.match('[X][+-]?\d*.\d*[Y][+-]?\d*.\d*', line)):
							x = re.search('[X]([+-]?\d*.\d*)', line)
							y = re.search('[Y]([+-]?\d*.\d*)', line)
							if x:
								x = float(x.group(1))
							if y:
								y = float(y.group(1))
							self.drill.append((x, y))

