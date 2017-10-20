
class Orchestrator():

    # def __init__(self, Name="there"):
    #     pass

    def read_reqs(self, file):
        f = open(file)

        try:
            for line in f:
                if not line.startswith('#'):
                    # print (line.strip('<>'))
                    line = line.strip('<>\n')
                    values = line.split(',')
                    for string in values:
                        string = string.strip(' ')
                        print string
        finally:
            f.close()
        pass

    def generate_operational_profile(self, loc, req):
        profile = [0]*48

        pass

    # Parses the orchestrator requirements from a file
    def parse_reqs(self):
        pass


# if __name__ == '__main__':
    # pass
