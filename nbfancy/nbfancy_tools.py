import os
import csv
import pkg_resources

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
    
def box_body(body, config, link=None):
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
    
    # Escape symbols
    htmlbody = htmlbody.replace('*', '&ast;')
    htmlbody = htmlbody.replace('_', '&lowbar;')
    
    # Format tables
    htmlbody = htmlbody.replace('<table>', '<table class="w3-table w3-striped w3-hoverable">')
    htmlbody = htmlbody.replace('<thead>', '<thead class="w3-black">')
    
    return htmlbody

def code2md():
    #~ <div class="input">
        #~ <div class="prompt_container">
            #~ <div class="prompt input_prompt"><bdi>In</bdi>&nbsp;[4]:</div>
            #~ <code style="background-color:#F7F7F7;border:1px solid #CFCFCF">nbft.colour2fgbg('red')</code>
        #~ </div>
    #~ </div>
    #~ <div class="output">
        #~ <div class="output_area">
            #~ <div class="prompt output_prompt"><bdi>Out[4]:</bdi></div>
            #~ <div class="output_subarea output_text output_result"><pre>('red', 'pale-red')</pre></div>
        #~ </div>
    #~ </div>
    pass
    
def output2md():
    # <img src="data:image/png;base64,NASTYBYTESRING">
    pass

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
    print('Directory: ', directory)
    print('contains notebooks: ')
    for afile in contents:
        print('          ', afile)
    
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
    # Store contents of directory as list
    contents = os.listdir(directory)
    contents.sort()
    try:
        # Remove checkpoints folder from list
        contents.remove('.ipynb_checkpoints')
    except ValueError:
        pass
    
    # Remove solution files from index
    contents = [f for f in contents if '-soln' not in f]
    
    # Removes everything else that isn't a notebook ending with .ipynb
    contents = [f for f in contents if '.ipynb' in f]
    
    # Print directory information
    print('Directory: ', directory)
    print('contains notebooks: ')
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

