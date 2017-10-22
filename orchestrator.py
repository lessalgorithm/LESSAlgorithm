
class Orchestrator():

    # def __init__(self, Name="there"):
    #     pass

    def read_reqs(self, file):
        req_dict = {}
        f = open(file)

        try:
            for line in f:
                if len(line) > 1 and (not line.startswith('#')):
                    line = line.strip('<>\n')
                    line = line.replace(' ', '')
                    values = line.split(',')

                    print values
                    # print values[0]
                    # print values[1]
                    # print values[2]

                    if values[1] in req_dict:
                        req_dict.get(values[1]).append(
                                values[0] + ":" + values[2])
                        print req_dict.get(values[1])
                    else:
                        req_dict[values[1]] = [values[0] + ':' + values[2]]
                        print req_dict[values[1]]

                    # for string in values:
                    #     string = string.strip(' ')
                    # print string
        finally:
            f.close()

    def generate_operational_profile(self, loc, reqs):
        profile = [0]*48

        pass

    # Parses the orchestrator requirements from a file
    def parse_reqs(self):
        pass


# if __name__ == '__main__':
    # pass
