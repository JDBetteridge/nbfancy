import os
import csv
import pkg_resources
import re
import traceback

import nbformat as nf
import nbconvert as nc

from urllib.parse import quote as urlquote

def isdir(path):
    '''
    Checks whether given path is a directory
    '''
    if not os.path.isdir(path):
        raise OSError('"' + path + '"' + ' is not a direcotry')
    else:
        return path

def try_config(configdir, filename):
    '''
    Tries to read specified config, else uses global config
    returns file handle to requested file
    '''
    resource_package = 'nbfancy'
    config_path = '/config'  # Do not use os.path.join()
    
    if not os.path.isdir(configdir):
        configdir = pkg_resources.resource_filename(resource_package, config_path)
    
    try:
        filepath = os.path.join(configdir, filename)
        filehandle = open(filepath, 'r')
    except FileNotFoundError:
        configdir = pkg_resources.resource_filename(resource_package, config_path)
        filepath = os.path.join(configdir, filename)
        filehandle = open(filepath, 'r')
    
    return filehandle

def read_header(configdir):
    '''
    Reads header from config directory
    '''
    # Open file and extract text in second cell
    with try_config(configdir, 'header.ipynb') as fh:
        notebook = nf.read(fh, nf.NO_CONVERT)
        box = notebook['cells'][1]
        template = box['source']
    
    return template
    
def read_footer(configdir):
    '''
    Reads footer from config directory
    '''
    # Open file and extract text in second cell
    with try_config(configdir, 'footer.ipynb') as fh:
        notebook = nf.read(fh, nf.NO_CONVERT)
        box = notebook['cells'][1]
        template = box['source']
    
    return template

def read_box_template(configdir):
    '''
    Reads box template from given file handle
    '''
    filehandle = try_config(configdir, 'box.ipynb')
    
    # File is already open
    # Open file and extract text in second cell
    notebook = nf.read(filehandle, nf.NO_CONVERT)
    box = notebook['cells'][1]
    template = box['source']
    
    # Replace known values with placeholders
    template = template.replace('pale-green', '{bg-colour}')
    template = template.replace('green', '{fg-colour}')
    template = template.replace('fa-star', '{symbol}')
    template = template.replace('TITLE', '{title}')
    template = template.replace('BODY', '{body}')
    
    return template

def colour2fgbg(colour):
    '''
    Pairs foreground colour with background colour
    '''
    colour = colour.lower()
    colour_list = ['red', 'orange', 'yellow', 'green', 'blue', 'purple'] 
    colour_list += ['brown', 'black', 'grey', 'gray', 'white']
    assert colour in colour_list
    
    fg = colour
    if fg == 'red':
        bg = 'pale-red'
    elif fg == 'orange':
        bg = 'sand'
    elif fg == 'yellow':
        bg = 'pale-yellow'
    elif fg == 'green':
        bg = 'pale-green'
    elif fg == 'blue':
        bg = 'pale-blue'
    elif fg == 'purple':
        bg = 'pale-red'
    elif fg == 'brown':
        bg = 'khaki'
    elif fg == 'black':
        bg = 'gray'
    elif (fg == 'gray') or (fg == 'grey'):
        fg = 'gray'
        bg = 'light-gray'
    elif fg == 'white':
        bg = 'white'
    
    return fg, bg

def read_box_colour_config(configdir):
    '''
    Create a dict of configurations for each keyword in filename
    Lines starting with # are ignored as are blank lines
    '''
    config = dict()
    
    def isTF(val):
        '''
        Return true or false if val is boolean
        '''
        true_words = ['true', 't', '1']
        false_words = ['false', 'f', '0']
        test_val = val.strip().lower()
        if test_val in true_words:
            test_val = True
        elif test_val in false_words:
            test_val = False
        return test_val
    
    with try_config(configdir, 'keywords.cfg') as fh:
        no_comments = filter(lambda line: len(line)>3 and line.lstrip()[0]!='#' , fh)
        reader = csv.DictReader(no_comments)
        for row in reader:
            key = row.pop('Keyword')
            row_dict = {key.strip().lower() : isTF(row[key]) for key in row}
            row_dict['fg-colour'], row_dict['bg-colour'] = colour2fgbg(row_dict['colour'])
            config[key.strip().lower()] = row_dict
    
    return config

def box_title(line, config):
    '''
    Creates title for box.
    Returns html formattted title, index and which keyword was found
    '''
    keywords = config.keys()
    
    # Search for keyword (lowercase) in first line and set that as the key
    for word in keywords:
        if word in line.lower().split(':')[0]:
            key = word
    
    # Recover paramters from keyword
    keep_keyword = config[key]['keep_keyword']
    hidden = config[key]['hide']
    
    # Whether to print keyword in title
    if keep_keyword:
        title = line.lstrip('#')
    else:
        subtitle = line.split(':')
        title = ':'.join(subtitle[1:])
    
    # Safe version of title for links
    safetitle = title.replace(' ', '-')
    safetitle = safetitle.replace('`', '')
    index = urlquote(safetitle, safe='?!$\\') + '%0A'
    
    # Mark up title, incase markdown syntax is used
    htmltitle = nc.filters.markdown2html(title)
    htmltitle = htmltitle.replace('<p>', '')
    htmltitle = htmltitle.replace('</p>', '')
    
    #link = './' + solnfilename.split('/')[-1] + '#' + index
    
    return htmltitle, index, key
    

def recursion_detector(f):
    '''
    Detects whether a given function is calling itself
    '''
    def decorated_f(*args, **kwargs):
        stack = traceback.extract_stack()
        if len([1 for line in stack if line[2] == f.__name__]) > 0:
            print('Warning: Nested environments detected, this is actively discouraged!')
        return f(*args, **kwargs)
    return decorated_f

@recursion_detector
def box_body(body, config, template, solnfilename, link=None, multicell=None):
    '''
    Creates body of the box
    '''
    # If an empty link to a solution is found, populate it with link
    # that was generated by the title (for single cell)
    if len(body) > 0 and '[solution]()' in body[-1].lower():
        k = body[-1].lower().find('[solution]()')
        solution_phrase = body[-1][k:k+13]
        new_solution_phrase = '\n\n' + solution_phrase.replace('()','({link})')
        new_solution_phrase = new_solution_phrase.format(link=link)
        body[-1] = body[-1].replace(solution_phrase, new_solution_phrase)
        
    body = '\n'.join(body)
    
    # Apply markup
    htmlbody = nc.filters.markdown2html(body)
    
    if multicell is not None:
        # Bit of recursion
        #print('Warning nested cell environments')
        rendered, soln = notebook2rendered(multicell, config, template, solnfilename)
        
        # Export to html to include in cell
        html_exp = nc.HTMLExporter()
        html_exp.template_file = 'basic'
        temphtml, resources = html_exp.from_notebook_node(rendered)
        # Remove multiple newlines
        temphtml = re.sub(r'(\n\s*)+\n', '\n', temphtml)
        # Add boxy thing
        temphtml = temphtml.replace('class="input_area"',
                        'class="output_area" style="background-color:#F7F7F7;border:1px solid #CFCFCF"')
        # If an empty link to a solution is found, populate it with link
        # that was generated by the title (for multicell)
        if '<a href="">solution</a>' in temphtml.lower():
            k = temphtml.lower().find('<a href="">solution</a>')
            solution_phrase = temphtml[k:k+24]
            new_solution_phrase = solution_phrase.replace('href=""','href="{link}"')
            new_solution_phrase = new_solution_phrase.format(link=link)
            temphtml = temphtml.replace(solution_phrase, new_solution_phrase)
        
        htmlbody += temphtml
    
    # Escape symbols
    htmlbody = htmlbody.replace('*', '&ast;')
    #htmlbody = htmlbody.replace('_', '&lowbar;')
    
    # Format tables
    htmlbody = htmlbody.replace('<table>', '<table class="w3-table w3-striped w3-hoverable">')
    htmlbody = htmlbody.replace('<thead>', '<thead class="w3-black">')
    
    # Be sure to remove final newline
    if htmlbody[-1] == '\n':
        htmlbody = htmlbody[:-1]
    
    return htmlbody

def notebook2rendered(plain, config, template, solnfilename, header=None, footer=None):
    '''
    Converts notebook JSON to rendered notebook JSON for output
    '''
    # List all the markdown cells
    celllist = plain['cells']
    markdownlist = [c for c in celllist if c['cell_type']=='markdown']
    solnb = None
    
    # For each markdown cell check for keywords and format according to
    # the cell template and config files
    end = -1
    
    for c in markdownlist:
        line = c['source'].split('\n')
        
        # Check for a colon in the first line
        if line[0].find(':') < 0:
            continue
        
        # Check for a keyword if a colon is found
        temp_line = line[0].split(':')
        if any(keyword in temp_line[0].lower().strip('# ') for keyword in config.keys()):
            htmltitle, index, key = box_title(line[0], config)
            # Recover paramters from keyword
            hidden = config[key]['hide']
            
            # Multicell procedure
            if key + '+' in temp_line[0].lower().strip('# '):
                start = celllist.index(c) + 1
                end = None
                # Find end cell
                for subcell in celllist[start:]:
                    if subcell['cell_type'] == 'markdown':
                        lastline = subcell['source'].split('\n')
                        temp_lastline = lastline[-1].split(':')
                        if key in temp_lastline[-1].lower().strip():
                            end = celllist.index(subcell) + 1
                            lastline[-1] = ':'.join(temp_lastline[:-1]).strip()
                            subcell['source'] = '\n'.join(lastline)
                            break
                else:
                    # If no end cell found print warning
                    try:
                        print('Warning in file', infile, ':')
                        print('\tNo end tag found for', key + '+', 'environment in cell', start)
                    except NameError:
                        print('Warning in temporary file:')
                        print('\tNo end tag found for', key + '+', 'environment in cell', start)
                        print('\tCheck you haven\'t nested environments')
                
                # Move multicells to new notebook for processing
                multicell = celllist[start:end]
                for subcell in multicell:
                    celllist.remove(subcell)
                    
                multicellnb = nf.v4.new_notebook()
                multicellnb['metadata'] = plain['metadata']
                multicellnb['cells'] = multicell
            else:
                # If we aren't in a multicell environment
                # we don't need the additional notebook
                multicellnb = None
            
            # If hidden move cell to new notebook
            if hidden:
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
                htmlbody = box_body(line[1:], config, template, solnfilename, multicell=multicellnb)
            else:
                link = './' + solnfilename.split('/')[-1] + '#' + index
                htmlbody = box_body(line[1:], config, template, solnfilename, link=link, multicell=multicellnb)
            
            values = config[key].copy()
            values['index'] = index
            values['title'] = htmltitle
            values['body'] = htmlbody
            c['source'] = template.format_map(values)
    
    return plain, solnb

def notebook2HTML(filename):
    '''
    Converts notebook file to a html string
    '''
    html_exp = nc.HTMLExporter()
    html, resources = html_exp.from_filename(filename)
    
    # SED rules:
    # Replace '../folders' in links with './folders'
    # for folders images, data, code
    html = html.replace('../images', './images')
    html = html.replace('../data', './data')
    html = html.replace('../code', './code')
    
	# Replace '.ipynb' in links with '.html'
    html = html.replace('.ipynb', '.html')
    
	# Horrible hack because <code> environment doesn't seem to work with CSS sheet
    # For plaintext blocks
    html = html.replace('<pre><code>', '<pre><code style="">')
    # For inline highlighting
    html = html.replace('<code>', '<code style="background-color:#F7F7F7;border:1px solid #CFCFCF">')
    
	# Another hack since \n is converted to [space] in links
    html = html.replace('%0A"','%20"')
    
    return html

def directory_contents(directory):
    '''
    Returns directory notebook contents
    split into lessons and solutions
    '''
    # Store contents of directory as list
    contents = os.listdir(directory)
    contents.sort()
    try:
        # Remove checkpoints folder from list
        contents.remove('.ipynb_checkpoints')
    except ValueError:
        pass
    
    # Removes everything that isn't a notebook ending with .ipynb
    contents = [f for f in contents if '.ipynb' in f]
    
    # Remove solution files from contents and store in seperate list
    soln_contents = [f for f in contents if '-soln' in f]
    contents = [f for f in contents if '-soln' not in f]
    
    return contents, soln_contents

def navigation_triple(directory, inputfile):
    '''
    Given a directory and file determines which file is
    - previous lesson
    - schedule
    - next lesson
    and returns these files as a dict
    '''
    contents, _ = directory_contents(directory)
    
    contents.append(contents[0])
    
    current = inputfile.split('/')[-1]
    # Exceptional case if you're making a new solution document
    if '-soln' in current:
        current = current.replace('-soln','')
    
    index = contents.index(current)
    
    outdir = './'
    triple = {  'previous' : outdir+contents[index-1],
                'index'    : outdir+contents[0],
                'next'     : outdir+contents[index+1] }
    return triple

