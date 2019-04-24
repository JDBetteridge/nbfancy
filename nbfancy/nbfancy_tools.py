import os
import csv
import pkg_resources
import re

import nbformat as nf
import nbconvert as nc

from urllib.parse import quote as urlquote

def isdir(path):
    '''Checks whether given path is a directory
    
    '''
    if not os.path.isdir(path):
        raise OSError('"' + path + '"' + ' is not a direcotry')
    else:
        return path

def try_config(configdir, filename):
    ''' Tries to read specified config, else uses global config
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
    '''Reads header from config directory
    
    '''
    # Open file and extract text in second cell
    with try_config(configdir, 'header.ipynb') as fh:
        notebook = nf.read(fh, nf.NO_CONVERT)
        box = notebook['cells'][1]
        template = box['source']
    
    return template
    
def read_footer(configdir):
    '''Reads footer from config directory
    
    '''
    # Open file and extract text in second cell
    with try_config(configdir, 'footer.ipynb') as fh:
        notebook = nf.read(fh, nf.NO_CONVERT)
        box = notebook['cells'][1]
        template = box['source']
    
    return template

def read_box_template(configdir):
    '''Reads box template from given file handle
    
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
    '''Pairs foreground colour with background colour
    
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
    ''' Create a dict of configurations for each keyword in filename
    Lines starting with # are ignored as are blank lines
    
    '''
    config = dict()
    
    def isTF(val):
        ''' Return true or false if val is boolean
        
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
    '''Creates title for box.
    Returns html formattted title, index and which keyword was found
    
    '''
    keywords = config.keys()
    
    # Search for keyword (lowercase) in first line and set that as the key
    for word in keywords:
        if word in line.lower():
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
    
def box_body(body, config, link=None, multicell=None):
    '''Creates body of the box
    
    '''
    # If an empty link to a solution is found, populate it with link
    # that was generated by the title
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
        html_exp = nc.HTMLExporter()
        html_exp.template_file = 'basic'
        temphtml, resources = html_exp.from_notebook_node(multicell)
        # Remove multiple newlines
        temphtml = re.sub(r'(\n\s*)+\n', '\n', temphtml)
        # Add boxy thing
        temphtml = temphtml.replace('class="input_area"',
                        'class="output_area" style="background-color:#F7F7F7;border:1px solid #CFCFCF"')
        htmlbody += temphtml
        
        #lang = multicell['metadata']['kernelspec']['language']
    
    # ~ for c in multicell:
        # ~ if c['cell_type'] == 'markdown':
            # ~ htmlbody += nc.filters.markdown2html(c['source'])
        # ~ elif c['cell_type'] == 'code':
            # ~ htmlbody += code2html(c)
        # ~ elif c['cell_type'] == 'raw':
            # ~ htmlbody += raw2html(c)
        # ~ else:
            # ~ pass ## Not sure how we'd end up here
    
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

# ~ def code2html(cell):
    # ~ '''Takes code cell and returns an approximation of the HTML that would
    # ~ be rendered by nbconvert
    # ~ '''
    # ~ assert cell['cell_type'] == 'code'
    
    # ~ # Define some HTML templates
    # ~ input_template = \
# ~ '''<div class="input">
    # ~ <div class="prompt_container">
        # ~ <div class="prompt input_prompt"><bdi>In</bdi>&nbsp;[{execution_count}]:</div>
    # ~ </div>
    # ~ <code style="background-color:#F7F7F7;border:1px solid #CFCFCF;width:100%">{source}</code>
# ~ </div>'''
    
    # ~ output_template = \
# ~ '''<div class="output">
    # ~ <div class="output_area">
        # ~ <div class="prompt output_prompt"><bdi>Out[{execution_count}]:</bdi></div>
        # ~ {outputs}
    # ~ </div>
# ~ </div>'''
    
    # ~ execute = '''<div class="output_subarea output_text output_result" style="width:100%"><pre>{out}</pre></div>'''
    # ~ image = '''<div class="output_subarea output_png output_result" style="width:100%"><img src="data:image/png;base64,{out}"></div>'''
    # ~ stream = '''<div class="output_subarea output_text output_stream output_{name}" style="width:100%"><pre>{text}</pre></div>'''
    
    # ~ # Input cells
    # ~ html = input_template.format_map(cell)
    
    # ~ # Output cells
    # ~ outputs_block = ''
    # ~ if len(cell['outputs']) != 0:
        # ~ for output in cell['outputs']:
            # ~ if output['output_type'] == 'execute_result':
                # ~ outputs_block += execute.format(out=output['data']['text/plain'])
            # ~ elif output['output_type'] == 'stream':
                # ~ outputs_block += stream.format_map(output)
            # ~ elif output['output_type'] == 'display_data':
                # ~ outputs_block += image.format(out=output['data']['image/png'])
            # ~ else:
                # ~ pass ## There are probably a lot of cases we aren't covering!
        # ~ html += '\n'
        # ~ html += output_template.format(execution_count=cell['execution_count'], outputs=outputs_block)
    
    # ~ print(html)
    # ~ return html
    
# ~ def raw2html(cell):
    # ~ assert cell['cell_type'] == 'raw'
    # ~ raw_template = \
# ~ '''<div class="input">
    # ~ <div class="prompt_container">
        # ~ <div class="prompt input_prompt"></div>
    # ~ </div>
    # ~ <code style="background-color:#F7F7F7;border:1px solid #CFCFCF;width:100%">{source}</code>
# ~ </div>'''
    # ~ html = raw_template.format_map(cell)
    # ~ return html

def notebook2HTML(filename):
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
    
    # Print directory information
    # ~ print('Directory: ', directory)
    # ~ print('contains notebooks: ')
    # ~ for afile in contents:
        # ~ print('          ', afile)
    
    return contents, soln_contents

def navigation_triple2(contents, filename):
    '''Given a contents list and filename determines which file is
    - previous lesson
    - schedule
    - next lesson
    and returns these files as a dict
    '''
    # Make list loop, incase this is the last file
    contents.append(contents[0])
    
    current = inputfile.split('/')[-1]
    # Exceptional case if you're making custom solutions documents
    if '-soln' in current:
        current = current.replace('-soln','')
    
    index = contents.index(current)
    
    outdir = './'
    print('Navigation triple is: ', outdir+contents[index-1], outdir+contents[0], outdir+contents[index+1])
    triple = {  'previous' : outdir+contents[index-1],
                'index'    : outdir+contents[0],
                'next'     : outdir+contents[index+1] }
    return triple

def navigation_triple(directory, inputfile):
    '''Given a directory and file determines which file is
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
    # ~ print('Navigation triple is: ', outdir+contents[index-1], outdir+contents[0], outdir+contents[index+1])
    triple = {  'previous' : outdir+contents[index-1],
                'index'    : outdir+contents[0],
                'next'     : outdir+contents[index+1] }
    return triple

