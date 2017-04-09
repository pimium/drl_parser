import re
import json
from drill_group import DrillGroup 

class SetEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, DrillParser):
			return obj.__str__()
		if isinstance(obj, DrillGroup):
			return 'CustomSomethingRepresentation'
		return json.JSONEncoder.default(self, obj)

class ComplexEncoder(json.JSONEncoder):
	def default(self, obj):
		dict = {'DrillParser': 'DrillGroups'}
		if isinstance(obj, DrillParser):
			try:
				iterable = iter(obj.drillgroup)
			except TypeError:
				pass
			else:
				# dict['DrillParser'] = iterable
				return {'data': list(iterable)}
			# return json.JSONEncoder.default(self, obj)

		if isinstance(obj, DrillGroup):
			ret_list = []
			
			try:
				iteraable = iter(obj.drill)
			except TypeError:
				pass
			else:
				for items in iteraable:
					ret_list.append({'x': items[0], 'y': items[1]})
				return {'number':obj.number, 'diameter':obj.diameter, 'drill': list(ret_list)}
				# return list(iterable)
				
		return json.JSONEncoder.default(self, obj)



class DrillParser:
	def __init__(self, drillgroup=[], outputfile="for_znc.js"):

		self.drillgroup = drillgroup
		self.outputfile = outputfile

		
	def __str__(self):
		test = '{ "data": \n['
		for items in self.drillgroup:
			test = test + items.__str__()
		test = test + ']}\n'
		return test

	def writeJsonToFile(self):
		try:			
			with open(self.outputfile, 'w') as f:
				try:
					json.dump(self, f, cls=ComplexEncoder, indent=4)
					#f.write(self.results)
				except Exception as e:
					print "Could not write data to %s" %(self.outputfile)
		except IOError:
			print "Could not open file ", self.outputfile

def main():
	obj = DrillParser()
	with open("drl_test.drl", "r") as file:
		for line in file: 
			if (re.match('^[T]{1}\d+C\d+.\d+', line)):
				m = re.search('^[T]{1}(.+?)C', line)
				if m:
					found = m.group(1)
					# print "Found: " + found
					dg = DrillGroup("drl_test.drl", found)
					dg.diameter = re.findall(r'C(\d+\.\d+)?', line)[0]
					obj.drillgroup.append(dg)
				# print line,
	print obj
	for items in obj.drillgroup:
		print len(items.drill)
		items.parse()

	for items in obj.drillgroup:
		print len(items.drill)

	# print json.dumps(obj, separators=(',', ':'), cls=ComplexEncoder, indent=4) 
	obj.writeJsonToFile() 
	print len(obj.drillgroup[1].drill)

if __name__ == '__main__':
	main()
