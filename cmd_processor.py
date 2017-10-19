import cmd
import os
import sys
import getopt
import Solar_Multitenancy


class CommandInterpreter(cmd.Cmd):
    # Command line processor for setting up and running the simulator.

    # Cmd class variables from cmd package
    prompt = '>>> '

    dir_path = os.path.dirname(os.path.realpath(__file__))
    orch_data_loc = dir_path + '/requirements.dat'
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

    def preloop(self):
        self.intro = self.intro_art
        self.intro += (('\nOrchestrator requirements file: '
                        '{0}').format(self.orch_data_loc))
        self.intro += (('\nEnergy harvesting data:         '
                       '{0}').format(self.harveting_data_loc))
        self.intro += (('\nSimulation results:             '
                       '{0}').format(self.output_loc))
        self.intro += ('\n')

    # def postloop(self):
    #     print "This is the name of the script: ", sys.argv[0]
    #     print "Number of arguments: ", len(sys.argv)
    #     print "The arguments are: ", str(sys.argv)
    #     print "\n"

    def do_run(self, line):
        Solar_Multitenancy.main()
    #
    # def do_print(self, line):
    #
    #
    # def do_profile(self, line):

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
                pass
            elif opt == '-o':
                self.output_loc = arg

    def set_file_paths(self):
        pass

    def emptyline(self):
        pass


if __name__ == '__main__':
    # print "This is the name of the script: ", sys.argv[0]
    # print "Number of arguments: ", len(sys.argv)
    # print "The arguments are: ", str(sys.argv)
    # print "\n"

    interpreter = CommandInterpreter()
    interpreter.parse_args(sys.argv[1:])
    CommandInterpreter().cmdloop()
