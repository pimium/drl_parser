import re
import json
import argparse
import os.path

from decimal import Decimal

from drill_group import DrillGroup


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DrillParser):
            return obj.__str__()
        if isinstance(obj, DrillGroup):
            return 'CustomSomethingRepresentation'
        return json.JSONEncoder.default(self, obj)


class DrillParserEncoder(json.JSONEncoder):
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
                    ret_list.append([items[0], items[1]])
                return {'number': obj.number, 'diameter': obj.diameter, 'drill': list(ret_list)}
            # return list(iterable)

        return json.JSONEncoder.default(self, obj)


def getParmeters():
    parser = argparse.ArgumentParser(description="Script to parse drl-files")
    parser.add_argument("-V", "--verbose", action="store_true", default=False, help="verbose")

    parser.add_argument("-if", "--inputfile", action="store", default="", dest="inputfile", help="input filepath")

    parser.add_argument("-of", "--outputfile", action="store", default="", dest="outputfile", help="output filepath")

    args = parser.parse_args()

    return args


class DrillParser:
    def __init__(self, drillgroup=[], inputfile="drl_test.drl", outputfile="", config=getParmeters()):

        self.drillgroup = drillgroup
        self.outputfile = outputfile
        self.inputfile = inputfile
        self.config = config

        if config != None:
            if (config.inputfile):
                self.inputfile = config.inputfile

            if (config.outputfile):
                self.outputfile = config.outputfile

        if self.outputfile == "":
            self.outputfile = self.inputfile + ".js"

        self.header = "M48\n" \
                      "G21\n" \
                      "G90\n" \
                      "G05\n"

    def __str__(self):
        test = '{ "data": \n['
        for items in self.drillgroup:
            test = test + items.__str__()
        test = test + ']}\n'
        return test

    def print_to_DRL_file(self):
        outputfile_ = os.path.splitext(self.inputfile)[0]
        for dg in self.drillgroup:
            outputfile = outputfile_ + "_T" + str(dg.number) + ".drl"
            print(outputfile)
            try:
                with open(outputfile, 'w') as f:
                    try:
                        f.write(";Drill file for T" + str(dg.number) + ": " + str(dg.diameter))
                        f.write(self.header)
                        for drill_point in dg.drill:
                            f.write("G00Z1\n")
                            f.write("G00 X%.3fY%.3f\n" % (drill_point[0], drill_point[1]))
                            f.write("G91Z-1F100\n")
                            f.write("G91Z1F100\n")

                        f.write("G00 X0Y0Z1F100\n")
                        f.close()
                        pass
                    except Exception as e:
                        print("Could not write data to the file: %s" % outputfile)
            except IOError:
                print("Could not open file ", outputfile)

    def writeJsonToFile(self):
        try:
            with open(self.outputfile, 'w') as f:
                try:
                    json.dump(self, f, cls=DrillParserEncoder, indent=4)
                # f.write(self.results)
                except Exception as e:
                    print("Could not write data to %s" % (self.outputfile))
        except IOError:
            print("Could not open file ", self.outputfile)

    def get_small_coodinate(self):
        x = None
        y = None

        for items in self.drillgroup:
            for drill in items.drill:
                if not x != None:
                    x = drill[0]
                elif x > drill[0]:
                    x = drill[0]

                if not y != None:
                    y = (drill[1])
                elif y > (drill[1]):
                    y = (drill[1])
        return x, y

    def adjust_coordinate(self):
        x_min, y_min = self.get_small_coodinate()
        for items in self.drillgroup:
            new_dg = []
            for drill in items.drill:
                new_dg.append((drill[0] - x_min, drill[1] - y_min))
            items.drill = new_dg

def main():
    obj = DrillParser()
    with open(obj.inputfile, "r") as file:
        for line in file:
            if (re.match('^[T]\d+C\d*.\d*', line)):
                m = re.search('^[T](.+?)C', line)
                if m:
                    found = m.group(1)
                    # print("Found: " + found)
                    dg = DrillGroup(obj.inputfile, found)
                    dg.diameter = re.findall(r'C(\d*\.\d*)?', line)[0]
                    obj.drillgroup.append(dg)
    #        print(line)
    print(obj)
    for items in obj.drillgroup:
        print(len(items.drill))
        items.parse()

    obj.adjust_coordinate()
    obj.print_to_DRL_file()


# for items in obj.drillgroup:
#	print(len(items.drill))

# print(json.dumps(obj.drillgroup[0], cls=DrillParserEncoder, indent=4))
# obj.writeJsonToFile()

if __name__ == '__main__':
    main()
