#!/usr/bin/env python3

import argparse

# Parse all of the command line options
parser = argparse.ArgumentParser()
parser.add_argument('verb',
                    choices=['init', 'hello'],
                    help='action to perform')
                    
args = parser.parse_args()

def main():
    if args.verb == 'init':
        print('We have not yet implemented this')
    elif args.verb == 'hello':
        print('Hello World!')
    else:
        print('What did you say??')

if __name__ == '__main__':
    main()
