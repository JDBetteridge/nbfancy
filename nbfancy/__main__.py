#!/usr/bin/env python3
import os
import sys
from shutil import move, copy, copytree
import argparse
import pkg_resources
from . import globalconf

# Trivial function for testing functionality
hello = lambda x: print('Hello World!')

def init(args):
    ''' Initialises a directory
    '''
    parser = argparse.ArgumentParser()
    parser.prog += ' ' + sys.argv[1]
    parser.add_argument('--extra_conf',
                        action='store_true',
                        help='Initialise additional configuration files')
    parser.add_argument('--include',
                        choices=['tutorial', 'template', 'none'],
                        default = 'template',
                        help='Fill nbplain directory with examples')
    args, unknown = parser.parse_known_args(sys.argv[2:])
    
    # Get cwd
    cwd = os.getcwd()
    
    # Create standard directories
    # Except nbplain, which is created at the end
    dir_list = ['config', 'images', 'code', 'data']
    for idir in dir_list:
        make_dir = os.path.join(cwd, idir)
        if not os.path.isdir(make_dir):
            os.mkdir(make_dir)
    
    # Our default configuration data
    resource_package = 'nbfancy'
    config_path = '/config'  # Do not use os.path.join()
    config_source = pkg_resources.resource_filename(resource_package, config_path)
    
    # Setup config files
    config_dir = os.path.join(cwd, 'config')
    config_files = ['header.ipynb', 'footer.ipynb']
    if args.extra_conf:
        config_files += ['box.ipynb', 'keywords.cfg']
    
    for ifile in config_files:
        source = os.path.join(config_source, ifile)
        target = os.path.join(config_dir, ifile)
        copy(source, target)
    
    # Copy template if specified
    if args.include == 'tutorial':
        template_path = '/tutorial'  # Do not use os.path.join()
        source = pkg_resources.resource_filename(resource_package, template_path)
        target = os.path.join(cwd, 'nbplain')
        copytree(source, target)
    elif args.include == 'template':
        template_path = '/template'  # Do not use os.path.join()
        source = pkg_resources.resource_filename(resource_package, template_path)
        target = os.path.join(cwd, 'nbplain')
        copytree(source, target)
    else:
        make_dir = os.path.join(cwd, 'nbplain')
        if not os.path.isdir(make_dir):
            os.mkdir(make_dir)
    
def configure(args):
    '''Sets up global config
    '''
    parser = argparse.ArgumentParser()
    parser.prog += ' ' + sys.argv[1]
    parser.add_argument('package',
                        choices=['jupyter_css', 'bash2_magic', 'pdflatex_magic', 'all_magic'],
                        default = 'template',
                        help='additional package to configure for use with nbfancy')
    parser.add_argument('-y',
                        action='store_true',
                        help='answer yes to config question (only for scripting)')
    args, unknown = parser.parse_known_args(sys.argv[2:])
    
    if not args.y:
        print('This step necessarily changes your user\'s global iPython or Jupyter config.')
        print('This will affect the system copy of these configuration files, even if you are in a virtualenv')
        user_input = input('Do you wish to proceed? [Y/N] : ')
        if 'y' in user_input.lower():
            confirmed = True
        else:
            confirmed = False
    else:
        confirmed = True
    
    if confirmed:
        if args.package == 'jupyter_css':
            globalconf.jupyter()
        elif args.package == 'all_magic':
            globalconf.ipython()
        else:
            print('You can\'t pick and choose, just install all_magic')
        print('Your global config has been updated')
    else:
        print('Your global config has not been changed, however',
                args.package,
                'is not configured to work on your system')

def render(args):
    '''
    
    '''
    parser = argparse.ArgumentParser()
    parser.prog += ' ' + sys.argv[1]
    parser.add_argument('input_dir',
                        type=str,
                        help='Plain notebook directory')
    parser.add_argument('--output_dir',
                        type=str,
                        default='nbfancy',
                        help='Name of fancy notebook to output')
    parser.add_argument('-c', '--config',
                        type=str,
                        help='Custom configuration directory')
    args, unknown = parser.parse_known_args(sys.argv[2:])
    
    if os.path.isdir(args.input_dir):
        print(args.input_dir)

def html(args):
    '''
    
    '''
    pass

def main():
    ''' Checks for the verb used with nbfancy
    
    '''
    # Parse all of the command line options
    parser = argparse.ArgumentParser()
    parser.add_argument('verb',
                        choices=['init', 'hello', 'configure', 'render', 'html'],
                        help='action to perform. Try adding --help to one of these options for more usage information')
    
    # Check that an argument was passed, if not print a more helpful message
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)          
    args = parser.parse_args(sys.argv[1:2])
    
    # Call function with given name
    
    call = globals()[args.verb]
    call(args)

if __name__ == '__main__':
    main()
