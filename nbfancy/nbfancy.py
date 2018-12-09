#!/usr/bin/python3

import argparse
import os

import nbformat as nf
import nbconvert as nc

from urllib.parse import quote as urlquote

from nbfancy_tools import *

# Parse all of the command line options
parser = argparse.ArgumentParser()
parser.add_argument('input',
                    type=argparse.FileType('r'),
                    help='Plain input notebook')
                    
parser.add_argument('output',
                    type=str,
                    help='Name of fancy notebook to output')
                    
parser.add_argument('--headercell',
                    type=argparse.FileType('r'),
                    help='Notebook containing header for all notebooks')

parser.add_argument('--footercell',
                    type=argparse.FileType('r'),
                    help='Notebook containing footer for all notebooks')

parser.add_argument('--boxconfig',
                    type=argparse.FileType('r'),
                    help='Keyword configuration file')

parser.add_argument('--boxcell',
                    type=argparse.FileType('r'),
                    help='Notebook containing "box" template')
                    
parser.add_argument('--sourcedir',
                    type=isdir,
                    help='Directory with existing notebook structure')
args = parser.parse_args()


# Name the solution file
solnfilename = args.output.replace('.ipynb', '-soln.ipynb')
solnflag = False
solnb = None

print('Reading input file: ' + args.input.name)

# Open notebook and list all the markdown cells
plain = nf.read(args.input, nf.NO_CONVERT)
celllist = plain['cells']
markdownlist = [c for c in celllist if c['cell_type']=='markdown']

# Read in the header file
if args.headercell is not None:
    print('Reading from headercell: ' + args.headercell.name)
    header = nf.read(args.headercell, nf.NO_CONVERT)
    plain['cells'].insert(0, *header['cells'][1:])
    args.headercell.close()
    
# Read in the box config file
if args.boxconfig is not None:
    print('Reading from config file: ' + args.boxconfig.name)
    config = read_box_colour_config(args.boxconfig)
    args.boxconfig.close()
else:
    config = {}

# Read in the box cell template
if args.boxcell is not None:
    print('Reading from box template: ' + args.boxcell.name)
    template = read_box_template(args.boxcell)
    args.boxcell.close()
else:
    template = '''
<div class="w3-panel w3-leftbar w3-border-{fg-colour} w3-pale-{bg-colour} w3-padding-small">
    <h3 id="{index}"><i class="fa {symbol}"></i> {title}</h3>
    {body}
</div>
'''

# For each markdown cell check for keywords and format according to
# the cell template and config files
for c in markdownlist:
    line = c['source'].split('\n')
    if any(keyword in line[0].lower() for keyword in config.keys()):
        htmltitle, index, key = box_title(line[0], config)
        # Recover paramters from keyword
        fg = config[key][0]
        bg = config[key][1]
        symbol = config[key][2]
        hidden = config[key][4]
        
        # If hidden move cell to new notebook
        if hidden:
            solnflag = True
            
            # Make a new notebook if it doesn't exist already
            if solnb is None:
                solnb = nf.v4.new_notebook()
                solnb['metadata'] = plain['metadata']
                solnb['cells'].append(nf.v4.new_markdown_cell(source='# Solutions'))
            
            solnb['cells'].append(nf.v4.new_markdown_cell(source=''))
            # REDEFINE c
            solnb['cells'][-1] = c.copy()
            plain['cells'].remove(c)
            c = solnb['cells'][-1]
            htmlbody = box_body(line[1:])
        else:
            link = './' + solnfilename.split('/')[-1] + '#' + index
            htmlbody = box_body(line[1:], link)
        
        values = {  'fg-colour' : fg,
                    'bg-colour' : bg,
                    'index'     : index,
                    'symbol'    : symbol,
                    'title'     : htmltitle,
                    'body'      : htmlbody
                    }
        c['source'] = template.format_map(values)
    
# Read in the footer file and add navigation
if args.footercell is not None:
    print('Reading from footercell: ' + args.footercell.name)
    footer = nf.read(args.footercell, nf.NO_CONVERT)
    
    triple = {'index' : './00_schedule.ipynb'} # Prevent error
    if args.sourcedir is not None:
        triple = navigation_triple(args.sourcedir, args.input.name)
        for cell in footer['cells'][1:]:
            cell['source'] = cell['source'].format_map(triple)
    
    inputname = './' + args.input.name.split('/')[-1]
    if triple['index'] != inputname:
        plain['cells'].append(*footer['cells'][1:])
    args.footercell.close()
    
# Write the new notebook to disk
outfp = open(args.output, 'w')
print('Writing output file: ' + args.output)
plain['metadata']['celltoolbar'] = 'None'
plain['metadata']['livereveal'] =  {'scroll' : True}
nf.write(plain, outfp)
args.input.close()
outfp.close()

# If needed also write the solutions notebook
if solnflag:
    solfp = open(solnfilename, 'w')
    print('and also solution outputfile')
    solnb['metadata']['celltoolbar'] = 'None'
    #solnb['metadata']['livereveal'] =  {"scroll" : True}
    nf.write(solnb, solfp)
    solfp.close()
    
    
