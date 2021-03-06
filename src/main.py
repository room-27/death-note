import sys
import os
import psutil
import datetime
import dateutil.parser
import cmd
import threading
import itertools


def posint(n):
    try:
        n = int(n)
        assert n > 0
    except ValueError:
        print('\nPlease enter a valid integer.')
        raise
    except AssertionError:
        print('\nPlease enter a positive integer.')
        raise
    return int(n)


class Page():
    id_counter = itertools.count(1)

    def __init__(self):
        self.id = next(self.id_counter)
        self.modified = False
        self.details = {
            'pid': [0],
            'time': None,
            'signal': 15
        }
        self.flags = {
            'time_set': False,
            'pid_set': False,
            'signal_set': False,
            'written_at': None
        }

    # Setters for details as input is time-sensitive
    def set_time(self, time):
        self.modified = True
        dn.update_prompt()
        self.details['time'] = time
        self.flags['time_set'] = True

    def set_signal(self, signal):
        self.modified = True
        dn.update_prompt()
        self.details['signal'] = signal
        self.flags['signal_set'] = True

    def set_pid(self, pid):
        self.modified = True
        dn.update_prompt()
        self.details['pid'] = pid

    def set_written_at(self, time):
        self.flags['written_at'] = time


class DeathNote(cmd.Cmd):
    '''Interprets user input as commands.'''

    pages = []

    last = {}

    signal_map = {
        0: '',
        1: 'SIGHUP',
        2: 'SIGINT',
        3: 'SIGQUIT',
        4: 'SIGILL',
        5: 'SIGTRAP',
        6: 'SIGABRT',
        7: 'SIGBUS',
        8: 'SIGFPE',
        9: 'SIGKILL',
        10: 'SIGUSR1',
        11: 'SIGSEGV',
        12: 'SIGUSR2',
        13: 'SIGPIPE',
        14: 'SIGALRM',
        15: 'SIGTERM',
        16: 'SIGSTKFLT',
        17: 'SIGCHLD',
        18: 'SIGCONT',
        19: 'SIGSTOP',
        20: 'SIGTSTP',
        21: 'SIGTTIN',
        22: 'SIGTTOU',
        23: 'SIGURG',
        24: 'SIGXCPU',
        25: 'SIGXFSZ',
        26: 'SIGVTALRM',
        27: 'SIGPROF',
        28: 'SIGWINCH',
        29: 'SIGIO',
        30: 'SIGPWR',
        31: 'SIGSYS',
    }

    # Create the first page:
    page = Page()
    pages.append(page)
    # pages.append(Page())
    # pages.append(Page())
    # pages.append(Page())

    def kill(self, details):
        pids = details['pid']
        signal = details['signal']
        for pid in pids:
            try:
                os.kill(int(pid), signal)
                print(
                    f'The process with PID {pid} has been sent a {self.signal_map[signal]}.')
                continue
            except ProcessLookupError:
                print(f'The process with PID {pid} has already been killed.')
                continue
            except PermissionError:
                print(
                    f'The process with PID {pid} is under the protection of a Lack of permission.')
                continue
            except Exception as e:
                print(
                    f'An unknown error occurred while terminating the process with PID {pid}: {e}')
                continue

    def reset_details(self):
        # Copy details to a restorable dict
        self.last = self.page.details
        self.page.details = {
            'pid': [0],
            'time': None,
            'signal': 15
        }
        self.page.flags = {
            'time_set': False,
            'pid_set': False,
            'signal_set': False,
            'written_at': None
        }
        self.page.modified = False
        self.update_prompt()

    def __init__(self):
        cmd.Cmd.__init__(self)
        current_page = self.page.id
        self.prompt = f'\n[???? {current_page}] Kira> '
        self.intro = '''
DEATH NOTE

Type \'help\' to see a list of commands.'''

    def update_prompt(self):
        current_page = self.page.id
        modified = "????" if self.page.modified else "????"
        self.prompt = f'\n[{modified} {current_page}] Kira> '

    def emptyline(self):
        pass

    def do_help(self, line):
        '''Show the help message.'''
        if line != '':
            cmd.Cmd.do_help(self, line)
        else:
            print('''
Commands:

> help: displays this message
> exit: exits the program
> pid: writes the PID of the process to the Death Note
> time: specify the time of death
> signal: specify the signal to be sent
> status: displays the status of Death Note jobs''')

    def help_help(self):
        print('''
help

Displays a list of commands for manipulating what is written to the Death Note.''')

    def do_exit(self, line):
        '''Exit the program.'''
        sys.exit(0)

    def help_exit(self):
        print('''
exit

Exits the Death Note interpreter.''')

    do_EOF = do_exit
    help_EOF = help_exit

    def do_page(self, page):
        # switch to the specified page id:
        if page == '':
            print('\nPlease specify a page number to switch to.')
            return
        try:
            page = posint(page)
        except Exception as e:
            return
        if page > len(self.pages):
            print('\nThe specified page does not exist.')
            return
        page_found = False
        for i, p in enumerate(self.pages):
            if p.id == page:
                page_found = True
                self.page = p
                break
        if not page_found:
            print('\nThe specified page does not exist.')
            return
        self.update_prompt()
        print(f'\nSwitched to page {page}.')

    def do_pid(self, pids):
        '''Write the PID of the process(es) to the Death Note.'''
        if pids == '':
            print(
                'Please enter the PID of the process(es) to be killed (space-delimited).')
            return
        pids = pids.split()

        errors = False
        for pid in pids:
            try:
                pid = posint(pid)
            except Exception as e:
                errors = True
                continue

            # Check if the given process exists with psutil:
            if not psutil.pid_exists(pid):
                print(f'\nThe process with PID {pid} does not exist.')
                errors = True
                continue

            if psutil.Process(pid).username() == 'root':
                print(
                    f'\nWarning: the process with PID {pid} is currently possessed by a Superuser of Death.')
        if errors:
            return

        if self.page.flags['time_set']:
            # Check if time was set to before the current time
            if self.page.details['time'] < datetime.datetime.now():
                print(f'\nThe time you specified is before the current time.')
                return
        else:
            # Set default time to 40s
            self.page.set_time(datetime.datetime.now() +
                               datetime.timedelta(seconds=40))

        self.page.set_written_at(datetime.datetime.now())

        self.page.set_pid(pids)

        # Create a Timer thread

        threading.Timer(
            (self.page.details['time'] -
                datetime.datetime.now()).total_seconds(),
            self.kill,
            args=[self.page.details]).start()  # PAGE - link page number

        self.reset_details()  # For now, reset details after thread creation

        plural = len(pids) > 1
        print('\nThe process' + 'es'*plural + ' with PID' +
              's'*plural + f' {", ".join(pids)} will die.')

    def help_pid(self):
        print('''
pid <PID> (<PID> <PID> ...)

Writes the PID of the process(es) specified to the Death Note.''')

    def do_time(self, when):
        '''Specify the date and time of death.'''
        if when == '':
            print('Please enter the time of death in MM/DD/YYYY HH/MM/SS format.')
            return

        # Parse input as best as possible
        try:
            when = dateutil.parser.parse(
                when, dayfirst=True, fuzzy=True).replace(tzinfo=None)
        except (dateutil.parser.ParserError, OverflowError) as e:
            print(f'\nPlease enter a valid date and time. ({e})')
            return

        # Check if the time has already passed and date is today, if so push to tomorrow
        now = datetime.datetime.now()
        if when.date() == now.date():
            if when.time() <= now.time():
                when = when + datetime.timedelta(days=1)

        # This is not Stein's Gate
        if when <= now:
            print('\nPlease enter a date and time in the future.')
            return

        # Write to page
        self.page.set_time(when)

        pretty_when = when.strftime('%A, %B %d, %Y at %H:%M:%S')
        print(f'\nSelected time of death: {pretty_when}.')

    def help_time(self):
        print('''
time (<MM.DD.(YY)YY>) (HH.MM.SS)

Specifies the date and time of death. The format is fairly flexible, but will prefer DD/MM/(YY)YY.
Even some words can be used when describing the date given,
    e.g. "23rd day of the 12th month 2036, at midnight+20s" -> "Tuesday, December 23, 2036 at 00:00:20".
If the date is omitted, the default is today, else tomorrow if the time has already passed.
If the time is omitted, midnight will be used, on the specified day.
If time is not specified at all, the resulting time will be 40 seconds from  of completion.''')

    def do_signal(self, signal):
        '''Specify the signal used to terminate the process.'''
        if signal == '':
            print('\nPlease enter the signal to be sent to the process.')
            return

        try:
            signal = int(signal)
            # Check if between 0 and 31
            if signal < 0 or signal > 31:
                print(
                    '\nPlease enter a valid signal number between 0 and 31, or its corresponding signal code.')
                return

            self.page.set_signal(signal)
            signal_num = signal
            signal_code = self.signal_map.get(signal, 'None')

        except ValueError:
            # Assume it's a signal code, check against dictionary
            signal = signal.upper()
            signal_prefix = signal.startswith('SIG')
            signal_found = False

            # signal_num = [n for n, c in self.signal_map.items() if c == signal or c[3:] == signal][0]
            if signal_prefix:
                for n, c in self.signal_map.items():
                    if c == signal:
                        signal_num = n
                        signal_found = True
                        break
            else:
                for n, c in self.signal_map.items():
                    if c[3:] == signal:
                        signal_num = n
                        signal_found = True
                        break
            if not signal_found:
                print(
                    '\nPlease enter a valid signal code, or its corresponding number between 0 and 31.')
                return

            self.page.set_signal(signal_num)
            signal_code = (not signal_prefix) * 'SIG' + signal

        except Exception as e:
            print(f'\nAn error occured while processing the given signal: {e}')
            return

        print(f'\nSelected cause of death: {signal_code} ({signal_num}).')

    def help_signal(self):
        print('''
signal <signal>

Specifies the signal to be sent to the process.
The signal can be specified by its number, or by its name with or without the SIG prefix,
    e.g. \'signal 15\', \'signal TERM\', \'signal SIGINT\'''')

    def do_status(self, arg):
        '''Prints the current status of the Death Note.'''
        # check if no arguments were given:
        print('')
        if arg == '':
            if not self.page.flags['time_set']:
                print('No time of death has been specified yet.')
            else:
                print(
                    f'Time of death: {self.page.details["time"].strftime("%A, %B %d, %Y at %H:%M:%S")}')
            if not self.page.flags['signal_set']:
                print('No signal has been specified yet.')
            else:
                print(
                    f'Signal: {self.page.details["signal"]} ({self.signal_map[self.page.details["signal"]]})')
        elif arg == 'all':
            # List details of all running threads, with job and page IDs
            if len(threading.enumerate()) == 1:
                print('No jobs are running.')
            else:
                for thread in threading.enumerate():
                    if thread is threading.main_thread():
                        continue
                    job_details = thread.args[0]
                    pids = job_details["pid"]
                    jid = thread.native_id

                    # TODO: get page number instead of JID

                    plural = len(pids) > 1
                    print(f'({jid}) {thread.name}: PID{"s" * plural} {", ".join(pids)} \
{"are" if plural else "is"} scheduled to die on {job_details["time"].strftime("%A, %B %d, %Y at %H:%M:%S")} \
by signal {job_details["signal"]} ({self.signal_map[job_details["signal"]]}).')
                return
        else:
            try:
                # TODO: get BY page number instead of JID
                jid = int(arg)
                # Check if the thread with the given ID exists
                if not any(thread.native_id == jid for thread in threading.enumerate()):
                    print(f'No thread with ID {jid} exists.')
                    return
                # Get the thread with the given ID
                thread = [thread for thread in threading.enumerate() if (
                    thread.native_id == jid) and thread is not threading.current_thread()][0]
                # Print the thread's details
                job_details = thread.args[0]
                pids = job_details["pid"]

                plural = len(pids) > 1
                print(f'({jid}) {thread.name}: PID{"s" * plural} {", ".join(pids)} \
{"are" if plural else "is"} scheduled to die on {job_details["time"].strftime("%A, %B %d, %Y at %H:%M:%S")} \
by signal {job_details["signal"]} ({self.signal_map[job_details["signal"]]}).')
                return
            except ValueError:
                print('Please enter a valid thread ID.')
                return

    def help_status(self):
        print('''
status (<id>|all)

Prints the current status of Death Note jobs.
Without an argument, prints the status of current message being written.
With an ID, prints the status of the message with the given ID.
With \'all\', prints the status of all running jobs.
Printed output for a running job includes Job ID, PID, date, time and signal.''')

    def do_last(self, line):
        '''Re-use the last time of death and signal'''
        if not self.last == {}:
            self.page.set_time(self.last['time'])
            self.page.set_signal(self.last['signal'])
        else:
            print('\nNo previous details found.')


dn = DeathNote()
def main():
    dn.cmdloop()


if __name__ == '__main__':
    main()
