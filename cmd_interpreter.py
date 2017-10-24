import cmd
import os
import sys
import getopt
import less_simulator
from orchestrator import Orchestrator


class CommandInterpreter(cmd.Cmd):
    # Command line processor for setting up and running the simulator.
    # Cmd class variables from cmd package

    app_req_list = []

    prompt = '>>> '
    dir_path = os.path.dirname(os.path.realpath(__file__))
    orch_data_loc = dir_path + '/requirements.txt'
    harveting_data_loc = dir_path + '/datasets/env_data'
    output_loc = dir_path + '/datasets/results'
    intro_art = """
             __   ____________     __              _ __  __       (2017, 2018)
            / /  / __/ __/ __/__ _/ /__ ____  ____(_) /_/ /  __ _
           / /__/ _/_\ \_\ \/ _ `/ / _ `/ _ \/ __/ / __/ _ \/  ' \\
          /____/___/___/___/\_,_/_/\_, /\___/_/ /_/\__/_//_/_/_/_/
                 _            __  /___/
            ___ (_)_ _  __ __/ /__ _/ /____  ____
           (_-</ /  ' \/ // / / _ `/ __/ _ \/ __/
          /___/_/_/_/_/\_,_/_/\_,_/\__/\___/_/

                                https://github.com/lessalgorithm/LESSAlgorithm
                             """

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.orchestrator = Orchestrator()

    def preloop(self):
        self.intro = self.intro_art
        self.intro += (('\nOrchestrator requirements file: '
                        '{0}').format(self.orch_data_loc))
        self.intro += (('\nEnergy harvesting data:         '
                       '{0}').format(self.harveting_data_loc))
        self.intro += (('\nSimulation results:             '
                       '{0}').format(self.output_loc))
        self.intro += ('\n')

    def do_run(self, line):
        sen_req_dict = self.orchestrator.read_sensor_reqs(self.orch_data_loc)
        app_req_dict = self.orchestrator.read_app_reqs(self.orch_data_loc)

        print ('\n=========================== '
               'Operational profile for applications'
               ' ===========================\n')
        for app_reqs in app_req_dict.items():
            print app_reqs[0], '\t:', self.orchestrator.parse_reqs(app_reqs)

        print ('\n=========================== '
               'Operational profile for individual'
               'sensors ===========================\n')
        for loc_reqs in sen_req_dict.items():
            # print '----------', loc_reqs[0], '-----------'
            print loc_reqs[0], '\t:', self.orchestrator.parse_reqs(loc_reqs)

        print less_simulator.main(
            self.orchestrator.parse_reqs(app_req_dict.items()[2]))

        # for app_reqs in app_req_dict.items():
        #     less_simulator.main(self.orchestrator.parse_reqs(app_reqs))

    def do_quit(self, line):
        """quit
        Quit the simulator"""
        return True

    def do_EOF(self, line):
        return True

    def parse_args(self, argv):
        try:
            opts, args = getopt.getopt(argv, "r:e:o")
        except getopt.GetoptError:
            print (('cmd_processor.py -r <requirements file> '
                    '-e <energy harvesting data file> -o <output file>'))
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-r':
                self.orch_data_loc = arg
            elif opt == '-e':
                self.harveting_data_loc = arg
            elif opt == '-o':
                self.output_loc = arg

    def set_file_paths(self):
        pass

    def emptyline(self):
        pass


def main():
    interpreter = CommandInterpreter()
    interpreter.parse_args(sys.argv[1:])
    interpreter.cmdloop()
    # CommandInterpreter().cmdloop()


if __name__ == '__main__':
    # print "This is the name of the script: ", sys.argv[0]
    # print "Number of arguments: ", len(sys.argv)
    # print "The arguments are: ", str(sys.argv)
    # print "\n"

    main()
