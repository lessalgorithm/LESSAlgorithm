import cmd


class CommandInterpreter(cmd.Cmd):
    # Command line processor for setting up and running the simulator.

    prompt = '>>> '
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
