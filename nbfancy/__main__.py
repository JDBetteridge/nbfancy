#!/usr/bin/env python3
import os
import sys
import argparse
import pkg_resources

from shutil import move, copy, copytree
from . import globalconf
from . import nbfancy_tools as nbftools

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
        try:
            copytree(source, target)
        except FileExistsError:
            print('Directory', target, 'already exists')
    elif args.include == 'template':
        template_path = '/template'  # Do not use os.path.join()
        source = pkg_resources.resource_filename(resource_package, template_path)
        target = os.path.join(cwd, 'nbplain')
        try:
            copytree(source, target)
        except FileExistsError:
            print('Directory', target, 'already exists')
    else:
        make_dir = os.path.join(cwd, 'nbplain')
        if not os.path.isdir(make_dir):
            try:
                os.mkdir(make_dir)
            except FileExistsError:
                print('Directory', target, 'already exists')
                
    
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
    ''' Render plain notebooks as fancy notebooks
    '''
    import nbformat as nf
    import nbconvert as nc

    from urllib.parse import quote as urlquote
    
    parser = argparse.ArgumentParser()
    parser.prog += ' ' + sys.argv[1]
    parser.add_argument('input_dir',
                        type=str,
                        default='nbplain',
                        help='Plain notebook directory')
    parser.add_argument('--output_dir',
                        type=str,
                        default='nbfancy',
                        help='Name of fancy notebook to output')
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
        print(config)
        footer = nbftools.read_footer(configdir)
        
        #~ # Read in the header file
        #~ if args.headercell is not None:
            #~ print('Reading from headercell: ' + args.headercell.name)
            #~ header = nf.read(args.headercell, nf.NO_CONVERT)
            #~ plain['cells'].insert(0, *header['cells'][1:])
            #~ args.headercell.close()
            
        #~ # Read in the box config file
        #~ if args.boxconfig is not None:
            #~ print('Reading from config file: ' + args.boxconfig.name)
            #~ config = read_box_colour_config(args.boxconfig)
            #~ args.boxconfig.close()
        #~ else:
            #~ config = {}

        #~ # Read in the box cell template
        #~ if args.boxcell is not None:
            #~ print('Reading from box template: ' + args.boxcell.name)
            #~ template = read_box_template(args.boxcell)
            #~ args.boxcell.close()
        #~ else:
            #~ template = '''
        #~ <div class="w3-panel w3-leftbar w3-border-{fg-colour} w3-pale-{bg-colour} w3-padding-small">
            #~ <h3 id="{index}"><i class="fa {symbol}"></i> {title}</h3>
            #~ {body}
        #~ </div>
        #~ '''
    
    # Loop over contents of directory (excluding solution files)
    for infile in contents:
        # Name the solution file
        solnfilename = infile.replace('.ipynb', '-soln.ipynb')
        solnflag = False
        solnb = None

        print('Reading input file: ' + infile)

        # Open notebook and list all the markdown cells
        plain = nf.read(os.path.join(args.input_dir, infile), nf.NO_CONVERT)
        celllist = plain['cells']
        markdownlist = [c for c in celllist if c['cell_type']=='markdown']
        
        # For each markdown cell check for keywords and format according to
        # the cell template and config files
        for c in markdownlist:
            line = c['source'].split('\n')
            #~ if any(keyword in line[0].lower() for keyword in config.keys()):
                #~ htmltitle, index, key = box_title(line[0], config)
                #~ # Recover paramters from keyword
                #~ fg = config[key][0]
                #~ bg = config[key][1]
                #~ symbol = config[key][2]
                #~ hidden = config[key][4]
                
                #~ # If hidden move cell to new notebook
                #~ if hidden:
                    #~ solnflag = True
                    
                    #~ # Make a new notebook if it doesn't exist already
                    #~ if solnb is None:
                        #~ solnb = nf.v4.new_notebook()
                        #~ solnb['metadata'] = plain['metadata']
                        #~ solnb['cells'].append(nf.v4.new_markdown_cell(source='# Solutions'))
                    
                    #~ solnb['cells'].append(nf.v4.new_markdown_cell(source=''))
                    #~ # REDEFINE c
                    #~ solnb['cells'][-1] = c.copy()
                    #~ plain['cells'].remove(c)
                    #~ c = solnb['cells'][-1]
                    #~ htmlbody = box_body(line[1:])
                #~ else:
                    #~ link = './' + solnfilename.split('/')[-1] + '#' + index
                    #~ htmlbody = box_body(line[1:], link)
                
                #~ values = {  'fg-colour' : fg,
                            #~ 'bg-colour' : bg,
                            #~ 'index'     : index,
                            #~ 'symbol'    : symbol,
                            #~ 'title'     : htmltitle,
                            #~ 'body'      : htmlbody
                            #~ }
                #~ c['source'] = template.format_map(values)
            
        #~ # Read in the footer file and add navigation
        #~ if args.footercell is not None:
            #~ print('Reading from footercell: ' + args.footercell.name)
            #~ footer = nf.read(args.footercell, nf.NO_CONVERT)
            
            #~ triple = {'index' : './00_schedule.ipynb'} # Prevent error
            #~ if args.sourcedir is not None:
                #~ triple = navigation_triple(args.sourcedir, args.input.name)
                #~ for cell in footer['cells'][1:]:
                    #~ cell['source'] = cell['source'].format_map(triple)
            
            #~ inputname = './' + args.input.name.split('/')[-1]
            #~ if triple['index'] != inputname:
                #~ plain['cells'].append(*footer['cells'][1:])
            #~ args.footercell.close()
            
        #~ # Write the new notebook to disk
        #~ outfp = open(args.output, 'w')
        #~ print('Writing output file: ' + args.output)
        #~ plain['metadata']['celltoolbar'] = 'None'
        #~ plain['metadata']['livereveal'] =  {'scroll' : True}
        #~ nf.write(plain, outfp)
        #~ args.input.close()
        #~ outfp.close()

        #~ # If needed also write the solutions notebook
        #~ if solnflag:
            #~ solfp = open(solnfilename, 'w')
            #~ print('and also solution outputfile')
            #~ solnb['metadata']['celltoolbar'] = 'None'
            #~ #solnb['metadata']['livereveal'] =  {"scroll" : True}
            #~ nf.write(solnb, solfp)
            #~ solfp.close()
    

def html(args):
    ''' Publish fancy (or even plain) notebooks as html
    '''
    parser = argparse.ArgumentParser()
    parser.prog += ' ' + sys.argv[1]
    parser.add_argument('input_dir',
                        type=str,
                        default='nbfancy',
                        help='Fancy notebook directory')
    parser.add_argument('--output_dir',
                        type=str,
                        default='html',
                        help='Name of html directory to output')
    parser.add_argument('-c', '--config',
                        type=str,
                        default='config',
                        help='Custom configuration directory')
    args, unknown = parser.parse_known_args(sys.argv[2:])
    
    if os.path.isdir(args.input_dir):
        print(args.input_dir)

def main():
    ''' Checks for the verb used with nbfancy command
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
