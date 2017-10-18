import cmd
import os
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
            ___ (_)_ _  __ __/ /__ _/ /____  ____              Greg Jackson
           (_-</ /  ' \/ // / / _ `/ __/ _ \/ __/               Milan Kabac
          /___/_/_/_/_/\_,_/_/\_,_/\__/\___/_/

                             https://github.com/lessalgorithm/LESSAlgorithm
                             """

    def preloop(self):
        self.intro = self.intro_art
        self.intro += ('\nOrchestrator requirements file: ' + self.orch_data_loc)
        self.intro += ('\nEnergy harvesting data:         ' + self.harveting_data_loc)
        self.intro += ('\nSimulation results:             ' + self.output_loc)
        self.intro += ('\n')

    def do_run(self, line):
        Solar_Multitenancy.main()

    def do_quit(self, line):
        """quit
        Quit the simulator"""
        return True

    def do_EOF(self, line):
        return True

    def emptyline(self):
        pass


if __name__ == '__main__':
    interpreter = CommandInterpreter()
    CommandInterpreter().cmdloop()
