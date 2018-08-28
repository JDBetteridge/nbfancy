#!/usr/bin/python3

import argparse
import os
import pprint

import nbformat as nf
import nbconvert as nc

def isdir(path):
    if not os.path.isdir(path):
        raise OSError('"' + path + '"' + ' is not a direcotry')
    else:
        return path

parser = argparse.ArgumentParser()
parser.add_argument('input',
                    type=argparse.FileType('r'),
                    help='Plain input notebook')
                    
parser.add_argument('output',
                    type=argparse.FileType('w'),
                    help='Name of fancy notebook to output')
                    
parser.add_argument('--headercell',
                    type=argparse.FileType('r'),
                    help='Notebook containing header for all notebooks')

parser.add_argument('--footercell',
                    type=argparse.FileType('r'),
                    help='Notebook containing footer for all notebooks')
                    
parser.add_argument('--sourcedir',
                    type=isdir,
                    help='Directory with existing notebook structure')
args = parser.parse_args()

def apply_template(colour, symbol, title, body):
    template = '''
<div class="text_cell_render border-box-sizing rendered_html">
<div class="w3-panel w3-leftbar w3-border-%(COLOUR)s w3-pale-%(COLOUR)s w3-padding-small">
    <h3><i class="fa fa-%(SYMBOL)s"></i> %(TITLE)s</h3>
    %(BODY)s
</div>
</div>
'''
    return template%{   'COLOUR' : colour,
                        'SYMBOL' : symbol,
                        'TITLE'  : title,
                        'BODY'   : body}

# Colours
# ~ green
# ~ blue
# ~ yellow

# Symbols
# ~ star
# ~ file-o
# ~ info-circle
# ~ pencil-square-o
# ~ eye
# ~ key

print('Reading input file: ' + args.input.name)

plain = nf.read(args.input, nf.NO_CONVERT)
celllist = plain['cells']
markdownlist = [c for c in celllist if c['cell_type']=='markdown']

for c in markdownlist:
    line = c['source'].split('\n')
    if 'Prerequisites' in line[0]:
        colour = 'green'
        symbol = 'star'
        title = line[0].lstrip('#')
        body = '\n'.join(line[1:])
    elif 'Overview' in line[0]:
        colour = 'green'
        symbol = 'file-o'
        title = line[0].lstrip('#')
        body = '\n'.join(line[1:])
    elif 'Info' in line[0]:
        colour = 'blue'
        symbol = 'info-circle'
        subtitle = line[0].split(':')
        title = ':'.join(subtitle[1:])
        body = '\n'.join(line[1:])
    elif 'Exercise' in line[0]:
        colour = 'yellow'
        symbol = 'pencil-square-o'
        subtitle = line[0].split(':')
        title = ':'.join(subtitle[1:])
        body = '\n'.join(line[1:])
    elif 'Solution' in line[0]:
        colour = 'blue'
        symbol = 'eye'
        subtitle = line[0].split(':')
        title = ':'.join(subtitle[1:])
        body = '\n'.join(line[1:])
    elif 'Key Points' in line[0]:
        colour = 'green'
        symbol = 'key'
        title = line[0].lstrip('#')
        body = '\n'.join(line[1:])
    elif 'Schedule' in line[0]:
        colour = None
        body = '\n'.join(line)
        html = nc.filters.markdown2html(body)
        html2 = html.replace('<table>', '<table class="w3-table w3-striped w3-hoverable">')
        html = html2.replace('<thead>', '<thead class="w3-black">')
        c['source'] = html
    else:
        colour = None
    
    if colour is not None:
        c['source'] = apply_template(colour, symbol, title, nc.filters.markdown2html(body))

if args.headercell is not None:
    print('Reading from headercell: ' + args.headercell.name)
    header = nf.read(args.headercell, nf.NO_CONVERT)
    plain['cells'].insert(0, *header['cells'])
    args.headercell.close()
    
if args.footercell is not None:
    print('Reading from footercell: ' + args.footercell.name)
    footer = nf.read(args.footercell, nf.NO_CONVERT)
    plain['cells'].append(*footer['cells'])
    args.footercell.close()
    
print('Writing output file: ' + args.output.name)
#pprint.pprint(plain)
nf.write(plain, args.output)
args.input.close()
args.output.close()

if args.sourcedir is not None:
    print('Directory: ', args.sourcedir)
