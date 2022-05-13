import sys
import os
import argparse
import cmd


def posint(n):
    try:
        n = int(n)
        assert n > 0
    except ValueError:
        print('Please enter a valid integer.')
    except AssertionError:
        print('Please enter a positive integer.')
    return int(n)


class DeathNote(cmd.Cmd):
    '''Interprets user input as commands.'''

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = 'Kira> '
        self.intro = '''
DEATH NOTE

Type \'help\' to see a list of commands.
'''

    def emptyline(self):
        pass

    def do_EOF(self, line):
        return True

    def do_help(self, line):
        '''Show the help message.'''
        print('''
Commands:

> help: displays this message
> exit: exits the program
> pid: writes the PID of the process to the Death Note
> time: specify the time of death
> signal: specify the signal to be sent
> status: displays the status of Death Note jobs
''')

    def do_exit(self, line):
        '''Exit the program.'''
        sys.exit(0)

    def do_pid(self, pids):
        '''Write the PID of the process(es) to the Death Note.'''
        print(pids)
        if pids == '':
            print(
                'Please enter the PID of the process(es) to be killed (space-delimited).')
            return
        pids = pids.split()
        for pid in pids:
            try:
                pid = posint(pid)
            except Exception as e:
                print('Please enter a valid positive integer.')
                return

            try:
                os.kill(pid, 9)
                print(f'The process with PID {pid} shall die.')
            except ProcessLookupError:
                print(f'The process with PID {pid} does not exist.')
            except PermissionError:
                print(f'The process with PID {pid} is under the protection of a \'Lack of permission\', and cannot be killed.')
            except OSError:
                print(f'PID {pid} - unknown error.')
            except Exception as e:
                print(f'PID {pid} - unknown error: {e}')

    def help_pid(self):
        print('''
pid <PID> (<PID> <PID> ...)

Writes the PID of the process(es) specified to the Death Note.
''')


def main():
    DeathNote().cmdloop()


if __name__ == '__main__':
    main()
