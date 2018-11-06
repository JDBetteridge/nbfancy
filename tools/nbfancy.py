#!/usr/bin/python3

import argparse
import os
import pprint

import nbformat as nf
import nbconvert as nc

from urllib.parse import quote as urlquote

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
                    type=str,
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

def apply_template(colour, symbol, title, body, index=None):
    template = '''
<div class="w3-panel w3-leftbar w3-border-{colour} w3-pale-{colour} w3-padding-small">
    <h3 id="{index}"><i class="fa fa-{symbol}"></i> {title}</h3>
    {body}
</div>
'''
    values = {  'colour' : colour,
                'symbol' : symbol,
                'title'  : title,
                'body'   : body,
                'index'  : index }
    return template.format_map(values)

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

solnfilename = args.output.replace('.ipynb', '-soln.ipynb')
solnflag = False

print('Reading input file: ' + args.input.name)

plain = nf.read(args.input, nf.NO_CONVERT)
celllist = plain['cells']
markdownlist = [c for c in celllist if c['cell_type']=='markdown']

solnb = None

if args.headercell is not None:
    print('Reading from headercell: ' + args.headercell.name)
    header = nf.read(args.headercell, nf.NO_CONVERT)
    plain['cells'].insert(0, *header['cells'])
    args.headercell.close()

for c in markdownlist:
    line = c['source'].split('\n')
    if 'Prerequisites' in line[0]:
        colour = 'green'
        symbol = 'star'
        title = line[0].lstrip('#')
        body = '\n'.join(line[1:])
        safetitle = title.replace(' ', '-')
        safetitle = safetitle.replace('`', '')
        index = urlquote(safetitle, safe='?!$\\') + '%0A'
    elif 'Overview' in line[0]:
        colour = 'green'
        symbol = 'file-o'
        title = line[0].lstrip('#')
        body = '\n'.join(line[1:])
        safetitle = title.replace(' ', '-')
        safetitle = safetitle.replace('`', '')
        index = urlquote(safetitle, safe='?!$\\') + '%0A'
    elif 'Info' in line[0]:
        colour = 'blue'
        symbol = 'info-circle'
        subtitle = line[0].split(':')
        title = ':'.join(subtitle[1:])
        body = '\n'.join(line[1:])
        safetitle = title.replace(' ', '-')
        safetitle = safetitle.replace('`', '')
        index = urlquote(safetitle, safe='?!$\\') + '%0A'
    elif 'Exercise' in line[0]:
        colour = 'yellow'
        symbol = 'pencil-square-o'
        subtitle = line[0].split(':')
        title = ':'.join(subtitle[1:])
        body = '\n'.join(line[1:])
        safetitle = title.replace(' ', '-')
        safetitle = safetitle.replace('`', '')
        link = './' + solnfilename.split('/')[-1] + '#' + urlquote(safetitle, safe='?!$\\') + '%0A'
        #print(link)
        body += '\n\n [Solution]({link})'.format(link=link)
        safetitle = title.replace(' ', '-')
        safetitle = safetitle.replace('`', '')
        index = urlquote(safetitle, safe='?!$\\') + '%0A'
    elif 'Solution' in line[0]:
        solnflag = True
        if solnb is None:
            solnb = nf.v4.new_notebook()
            solnb['metadata'] = plain['metadata']
            solnb['cells'].append(nf.v4.new_markdown_cell(source='# Solutions'))
        
        solnb['cells'].append(nf.v4.new_markdown_cell(source=''))
        # REDEFINE c
        solnb['cells'][-1] = c.copy()
        plain['cells'].remove(c)
        c = solnb['cells'][-1]
        
        colour = 'blue'
        symbol = 'eye'
        subtitle = line[0].split(':')
        title = ':'.join(subtitle[1:])
        body = '\n'.join(line[1:])
        safetitle = title.replace(' ', '-')
        safetitle = safetitle.replace('`', '')
        index = urlquote(safetitle, safe='?!$\\') + ' '
    elif 'Key Points' in line[0]:
        colour = 'green'
        symbol = 'key'
        title = line[0].lstrip('#')
        body = '\n'.join(line[1:])
        safetitle = title.replace(' ', '-')
        safetitle = safetitle.replace('`', '')
        index = urlquote(safetitle, safe='?!$\\') + ' '
    elif 'Schedule' in line[0]:
        colour = None
        body = '\n'.join(line)
        html = nc.filters.markdown2html(body)
        html2 = html.replace('<table>', '<table class="w3-table w3-striped w3-hoverable">')
        html = html2.replace('<thead>', '<thead class="w3-black">')
        c['source'] = html
    elif 'Pen' in line[0]:
        colour = 'yellow'
        symbol = 'pencil'
        subtitle = line[0].split(':')
        title = ':'.join(subtitle[1:])
        body = '\n'.join(line[1:])
        safetitle = title.replace(' ', '-')
        safetitle = safetitle.replace('`', '')
        index = urlquote(safetitle, safe='?!$\\') + '%0A'
    elif 'Pin' in line[0]:
        colour = 'blue'
        symbol = 'thumb-tack'
        subtitle = line[0].split(':')
        title = ':'.join(subtitle[1:])
        body = '\n'.join(line[1:])
        safetitle = title.replace(' ', '-')
        safetitle = safetitle.replace('`', '')
        index = urlquote(safetitle, safe='?!$\\') + '%0A'
    else:
        colour = None
    
    if colour is not None:
        htmltitle = nc.filters.markdown2html(title)
        temp = htmltitle.replace('<p>', '')
        htmltitle = temp.replace('</p>', '')
        
        htmlbody = nc.filters.markdown2html(body)
        temp = htmlbody.replace('*', '&ast;')
        htmlbody = temp.replace('_', '&lowbar;')
        
        c['source'] = apply_template(colour, symbol, htmltitle, htmlbody, index)

def navigation_triple(directory, inputfile):
    print('Directory: ', directory)
    print('contains: ')
    contents = os.listdir(directory)
    contents.sort()
    try:
        # Remove checkpoints folder from list
        contents.remove('.ipynb_checkpoints')
    except ValueError:
        pass
    
    # Remove solution files from index
    contents = [f for f in contents if '-soln' not in f]
    
    for afile in contents:
        print('          ', afile)
    
    contents.append(contents[0])
    
    current = inputfile.split('/')[-1]
    # Exceptional case if you're making a new solution document
    if '-soln' in current:
        current = current.replace('-soln','')
    
    index = contents.index(current)
    
    outdir = './'
    print('Navigation triple is: ', outdir+contents[index-1], outdir+contents[0], outdir+contents[index+1])
    triple = {  'previous' : outdir+contents[index-1],
                'index'    : outdir+contents[0],
                'next'     : outdir+contents[index+1] }
    return triple

if args.footercell is not None:
    print('Reading from footercell: ' + args.footercell.name)
    footer = nf.read(args.footercell, nf.NO_CONVERT)
    
    triple = {'index' : './00_schedule.ipynb'} # Prevent error
    if args.sourcedir is not None:
        triple = navigation_triple(args.sourcedir, args.input.name)
        for cell in footer['cells']:
            #print(cell['source'].format_map(triple))
            cell['source'] = cell['source'].format_map(triple)
    
    inputname = './' + args.input.name.split('/')[-1]
    if triple['index'] != inputname:
        plain['cells'].append(*footer['cells'])
    args.footercell.close()
    
outfp = open(args.output, 'w')
print('Writing output file: ' + args.output)
plain['metadata']['celltoolbar'] = 'None'
plain['metadata']['livereveal'] =  {'scroll' : True}
nf.write(plain, outfp)
args.input.close()
outfp.close()

if solnflag:
    solfp = open(solnfilename, 'w')
    print('and also solution outputfile')
    solnb['metadata']['celltoolbar'] = 'None'
    #solnb['metadata']['livereveal'] =  {"scroll" : True}
    nf.write(solnb, solfp)
    solfp.close()
    
    
