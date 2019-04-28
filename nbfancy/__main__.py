#!/usr/bin/env python3
import os
import sys
import argparse
import pkg_resources

import nbformat as nf
import nbconvert as nc

from shutil import move, copy, copytree
from distutils.dir_util import copy_tree # Prefer copy_tree due to overwrite
from . import globalconf
from . import nbfancy_tools as nbftools

# Trivial function for testing functionality
hello = lambda x: print('Hello World!')

def init(args):
    '''
    Initialises a directory
    '''
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.prog += ' ' + sys.argv[1]
    parser.add_argument('dir',
                        type=str,
                        default=os.getcwd(),
                        nargs='?',
                        help='Directory to initialise')
    parser.add_argument('--extra_conf',
                        action='store_true',
                        help='Initialise additional configuration files')
    parser.add_argument('--include',
                        choices=['tutorial', 'template', 'none'],
                        default = 'template',
                        help='Fill nbplain directory with examples')
    args, unknown = parser.parse_known_args(sys.argv[2:])
    
    # Get cwd
    cwd = args.dir
    
    if not os.path.isdir(cwd):
        try:
            os.mkdir(cwd)
        except FileExistsError:
            print('Directory', cwd, 'already exists')
    
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
    if args.include != 'none': # works for template and tutorial
        template_path = '/' + args.include  # Do not use os.path.join()
        source = pkg_resources.resource_filename(resource_package, template_path)
        target = os.path.join(cwd, 'nbplain')
        copy_tree(source, target)
        
    else: # works for none
        make_dir = os.path.join(cwd, 'nbplain')
        if not os.path.isdir(make_dir):
            try:
                os.mkdir(make_dir)
            except FileExistsError:
                print('Directory', make_dir, 'already exists')
                
    
def configure(args):
    '''
    Sets up global config
    '''
    parser = argparse.ArgumentParser()
    parser.prog += ' ' + sys.argv[1]
    parser.add_argument('package',
                        choices=['jupyter_css', 'bash2_magic', 'pdflatex_magic', 'all_magic'],
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

def rerun(args):
    '''
    Re evaulate all cells in notebook
    '''
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.prog += ' ' + sys.argv[1]
    parser.add_argument('input_dir',
                        type=str,
                        default='nbplain',
                        nargs='?',
                        help='Plain notebook directory')
    parser.add_argument('--output_dir',
                        type=str,
                        default='nbplain',
                        help='Name of directory for re-evaluated notebooks')
    parser.add_argument('--clear_only',
                        action='store_true',
                        help='Clear the cells, but do not re-evaluate')
    parser.add_argument('--allow_errors',
                        action='store_true',
                        help='Continue running notebook even if errors occur')
    parser.add_argument('--timeout',
                        type=int,
                        default=60,
                        help='Number of seconds to allow each cell to run for')
    args, unknown = parser.parse_known_args(sys.argv[2:])
    
    # Get directory contents
    if os.path.isdir(args.input_dir):
        contents, solution_contents = nbftools.directory_contents(args.input_dir)
        contents += solution_contents
        
        # Create output directory
        if not os.path.isdir(args.output_dir):
            try:
                os.mkdir(args.output_dir)
            except FileExistsError:
                print('Directory', args.output_dir, 'already exists')
    else:
        raise FileNotFoundError(2, 'No such directory', args.input_dir)
    
    # Create preprocessors 
    clear_pre = nc.preprocessors.ClearOutputPreprocessor()
    exec_pre = nc.preprocessors.ExecutePreprocessor(timeout=args.timeout,
                                                    allow_errors=args.allow_errors)
    if args.allow_errors:
        print('Warning: Notebooks are being run with --allow_errors flag')
        print('\tYou will not be notified of any errors and it is your')
        print('\tresponsibility to verify the output is correct.')
    
    # Loop over contents of directory
    for infile in contents:
        # Read in notebook
        print('Reading input file:', infile)
        notebook = nf.read(os.path.join(args.input_dir, infile), nf.NO_CONVERT)
        
        # Clear or clear and reexecute
        if args.clear_only:
            clear_pre.preprocess(notebook, {'metadata': {'path': args.output_dir}})
        else:
            try:
                # Needs to be output dir NOT input dir
                exec_pre.preprocess(notebook, {'metadata': {'path': args.output_dir}})
            except nc.preprocessors.CellExecutionError as e:
                print('Error: While executing the notebook', infile)
                print(e)
                print('Warning: notebook will be written, but some cells may not have executed')
                print('\tIf you want to continue running beyond this error try the --allow-_errors flag')
            
        # Write out notebook
        print('Writing output file:', infile)
        nf.write(notebook, os.path.join(args.output_dir, infile))

def render(args):
    '''
    Render plain notebooks as fancy notebooks
    '''
    from urllib.parse import quote as urlquote
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.prog += ' ' + sys.argv[1]
    parser.add_argument('input_dir',
                        type=str,
                        default='nbplain',
                        nargs='?',
                        help='Plain notebook directory')
    parser.add_argument('--output_dir',
                        type=str,
                        default='nbfancy',
                        help='Directory to output rendered notebooks to')
    parser.add_argument('-c', '--config',
                        type=str,
                        default='config',
                        help='Custom configuration directory')
    args, unknown = parser.parse_known_args(sys.argv[2:])
    
    if os.path.isdir(args.input_dir):
        contents, solution_contents = nbftools.directory_contents(args.input_dir)
        
        # Use config if specified, both fallback to global if error
        if args.config:
            configdir = args.config
        else:
            configdir = os.path.join(args.inputdir, 'config')
        
        # Read in the header, box config, box template and footer file
        header = nbftools.read_header(configdir)
        template = nbftools.read_box_template(configdir)
        config = nbftools.read_box_colour_config(configdir)
        footer = nbftools.read_footer(configdir)
        
        # Create output directory
        if not os.path.isdir(args.output_dir):
            try:
                os.mkdir(args.output_dir)
            except FileExistsError:
                print('Directory', args.output_dir, 'already exists')
    else:
        raise FileNotFoundError(2, 'No such directory', args.input_dir)
    
    # Loop over contents of directory (excluding solution files)
    for infile in contents:
        # Read input file
        print('Reading input file:', infile)
        plain = nf.read(os.path.join(args.input_dir, infile), nf.NO_CONVERT)
        solnfilename = infile.replace('.ipynb', '-soln.ipynb')
        
        # Render
        rendered, soln = nbftools.notebook2rendered(plain,
                                                    config,
                                                    template,
                                                    solnfilename,
                                                    header=header,
                                                    footer=footer)
        
        # Add header
        rendered['cells'].insert(0, nf.v4.new_markdown_cell(source=header))
        
        # Add navigation to footer
        triple = {'index' : './00_schedule.ipynb'} # Prevent error
        triple = nbftools.navigation_triple(args.input_dir, infile)
        
        tmp_footer = footer.format_map(triple)
        if triple['index'] != ('./' + infile):
            rendered['cells'].append(nf.v4.new_markdown_cell(source=tmp_footer))
            
        # Remove cell toolbars and add scroll to slides
        rendered['metadata']['celltoolbar'] = 'None'
        rendered['metadata']['livereveal'] =  {'scroll' : True}
        
        # Write the new notebook
        print('Writing output file:', infile)
        nf.write(plain, os.path.join(args.output_dir, infile))

        # If needed also write the solutions notebook
        if soln is not None:
            # Add header
            soln['cells'].insert(0, nf.v4.new_markdown_cell(source=header))
            soln['metadata']['celltoolbar'] = 'None'
            
            print('Writing output file:', solnfilename)
            nf.write(soln, os.path.join(args.output_dir, solnfilename))
    

def html(args):
    '''
    Publish fancy (or even plain) notebooks as html
    '''
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.prog += ' ' + sys.argv[1]
    parser.add_argument('input_dir',
                        type=str,
                        default='nbfancy',
                        nargs='?',
                        help='Fancy notebook directory')
    parser.add_argument('--output_dir',
                        type=str,
                        default='html',
                        help='Directory to output html pages to')
    args, unknown = parser.parse_known_args(sys.argv[2:])
    
    if not os.path.isdir(args.output_dir):
        try:
            os.mkdir(args.output_dir)
        except FileExistsError:
            print('Directory', args.output_dir, 'already exists')
    
    # Collect all input files
    if os.path.isdir(args.input_dir):
        contents, solution_contents = nbftools.directory_contents(args.input_dir)
        contents += solution_contents
    else:
        raise FileNotFoundError(2, 'No such directory', args.input_dir)
    
    # Create output directory if not already present
    cwd = os.getcwd()
    make_dir = os.path.join(cwd, args.output_dir)
    if not os.path.isdir(make_dir):
        try:
            os.mkdir(make_dir)
        except FileExistsError:
            print('Directory', make_dir, 'already exists')
    
    # Copy all resources to output directory
    resource_package = 'nbfancy'
    config_path = '/tools'  # Do not use os.path.join()
    css_dir = pkg_resources.resource_filename(resource_package, config_path)
    
    # Copy our custom CSS directory to output directory
    copy_tree(css_dir, args.output_dir)
    
    # Copy local resource directories
    dir_list = ['images', 'code', 'data']
    for idir in dir_list:
        copy_tree(idir, os.path.join(args.output_dir, idir))
    
    # Convert all collected input files
    for infile in contents:
        # Read input file
        print('Reading input file:', infile)
        html = nbftools.notebook2HTML(os.path.join(args.input_dir, infile))
        
        # Name the output file
        outfilename = infile.replace('.ipynb', '.html')
        outpath = os.path.join(args.output_dir, outfilename)
        
        print('Writing output file:', outfilename)
        with open(outpath, 'w') as fh:
            fh.write(html)

def main():
    '''
    Checks for the verb used with nbfancy command
    '''
    # Parse all of the command line options
    parser = argparse.ArgumentParser()
    parser.add_argument('verb',
                        choices=['init', 'hello', 'configure', 'rerun', 'render', 'html'],
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
