import os
import pkg_resources

from tempfile import mkstemp
from shutil import move, copy, copytree

from IPython import start_ipython
from IPython.paths import locate_profile
from IPython.core.profiledir import ProfileDirError

from jupyter_core.paths import jupyter_config_dir

def replace(filename, pattern, subst):
    ''' Replaces one string with another in config file
    '''
    #Create temp file
    temp_file, abs_path = mkstemp()
    with open(temp_file, 'w') as temp:
        with open(filename) as fh:
            for line in fh:
                temp.write(line.replace(pattern, subst))
    #Remove original file
    os.remove(filename)
    #Move new file
    move(abs_path, filename)

def ipython():
    '''Configuration for IPython
    '''
    # Line which must be appended to IPython config
    config_line = '''c.InteractiveShellApp.extensions = ['pdflatex_magic', 'bash2_magic']'''

    # Location of IPython default profile
    try:
        profile = locate_profile()
    except (ProfileDirError, OSError):
        start_ipython(argv=['profile', 'create', 'default'])
        profile = locate_profile()

    # Append extensions line to end of profile config
    config_file = os.path.join(profile, 'ipython_config.py')
    
    # Open config file
    fh = open(config_file, 'r+')
    
    # Search for line to be configured
    # Ensure it isn't a comment
    line_list = []
    for line in fh.readlines():
        if 'c.InteractiveShellApp.extensions' in line:
            if not line.lstrip().startswith('#'):
                line_list.append(line)
    
    # There should be at most one, othewise config is broken
    # If config is broken, this won't break it more :-P
    if len(line_list) == 1:
        # Extract current extensions
        before = line_list[0].split('[')
        after = before[1].split(']')
        
        # If none, just put new ones straight it
        if after[0].strip() == '':
            after[0] = "'pdflatex_magic', 'bash2_magic'"
        else:
            if "'pdflatex_magic'" not in after[0]:
                after[0] += ", 'pdflatex_magic'"
            if "'bash2_magic'" not in after[0]:
                after[0] += ", 'bash2_magic'"
        config_line = before[0] + '[' + ']'.join(after)
        fh.close()
        
        # To substitute into existing file we need to create a copy
        replace(config_file, line_list[0], config_line)
    else:
        # Write config line to file (at the end)
        fh.writelines(config_line)
        fh.close()
    
    # fh should be closed before here
    
def jupyter():
    '''Configuration for Jupyter
    '''
    # Get the path to Jupyter config
    jupyter_dir = jupyter_config_dir()
    
    # Set a target path for the CSS file
    custom_dir = os.path.join(jupyter_dir, 'custom')
    custom_css_path = os.path.join(custom_dir, 'custom.css')
    
    if os.path.isfile(custom_css_path):
        # Incase the user already uses a custom CSS file, back it up
        backup_css_path = os.path.join(custom_dir, 'custom.backup')
        os.rename(custom_css_path, backup_css_path)
    else:
        # Otherwise check if the custom folder is there
        if not os.path.isdir(custom_dir):
            os.mkdir(custom_dir)
    
    resource_package = 'nbfancy'
    config_path = '/tools'  # Do not use os.path.join()
    css_dir = pkg_resources.resource_filename(resource_package, config_path)
    
    # Copy our custom CSS file to the path
    copy(os.path.join(css_dir, 'custom.css'), custom_css_path)
    try:
        copytree(os.path.join(css_dir, 'css'), os.path.join(custom_dir, 'css'))
    except FileExistsError as e:
        print('ERROR: You already have a directory named')
        print(os.path.join(custom_dir, 'css'))
        print('Remove or rename and try again.')
        print('Install will continue, on the assumption that these files are left over from a previous build.')
