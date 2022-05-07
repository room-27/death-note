import sys
import os
import argparse


def posint(n):
    try:
        n = int(n)
        assert n > 0
    except ValueError:
        raise argparse.ArgumentTypeError('Please enter a valid integer.')
    except AssertionError:
        raise argparse.ArgumentTypeError('Please enter a positive integer.')
    return int(n)


# StackOverflow: https://stackoverflow.com/questions/5943249/python-argparse-and-controlling-overriding-the-exit-status-code
class ArgumentParser(argparse.ArgumentParser):
    def _get_action_from_name(self, name):
        '''Given a name, get the Action instance registered with this parser.
        If only it were made available in the ArgumentError object. It is 
        passed as it's first arg...
        '''
        container = self._actions
        if name is None:
            return None
        for action in container:
            if '/'.join(action.option_strings) == name:
                return action
            elif action.metavar == name:
                return action
            elif action.dest == name:
                return action

    def error(self, message):
        exc = sys.exc_info()[1]
        if exc:
            exc.argument = self._get_action_from_name(exc.argument_name)
            raise exc
        super(ArgumentParser, self).error(message)


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', dest='h', action='help',
                        default=argparse.SUPPRESS, help='Show this help message and exit')
    parser.add_argument('-p', '--pid', dest='p', type=posint,
                        required=True, help='Kill the process with the given PID')
    try:
        args = parser.parse_args(args=(None if sys.argv[1:] else ['-h']))
    except argparse.ArgumentError as exc:
        print(exc.message, '\n', exc.argument)
        sys.exit(1)

    print(f'Killing process with PID {args.p}')
    try:
        os.kill(args.p, 9)
    except ProcessLookupError:
        print('Process not found.')
    except PermissionError:
        print('Permission denied.')
    except OSError:
        print('Unknown error.')
    except Exception as e:
        print(f'Unknown error: {e}')

if __name__ == '__main__':
    main()
