import os

from IPython import start_ipython
from IPython.paths import locate_profile
from IPython.core.profiledir import ProfileDirError

from jupyter_core.paths import jupyter_config_dir
from shutil import copy, copytree

def ipython():
    '''Configuration for IPython
    '''
    # Line which must be appended to IPython config
    config_line = '''
c.InteractiveShellApp.extensions = ['pdflatex_magic', 'bash2_magic']
'''
    
    # Location of IPython default profile
    try:
        profile = locate_profile()
    except (ProfileDirError, OSError):
        start_ipython(argv=['profile', 'create', 'default'])
        profile = locate_profile()
    
    # Append extensions line to end of profile config
    config_file = os.path.join(profile, 'ipython_config.py')
    
    # TODO: Change to if line in file
    #       AND magic not there, add it
    with open(config_file, 'a') as fh:
        fh.write(config_line)
    
    
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
    
    # Get our current working directory
    cwd = os.getcwd()
    css_file = os.path.join(cwd, 'nbfancy', 'tools', 'custom.css')
    css_dir = os.path.join(cwd, 'nbfancy', 'tools', 'css')
    
    # Copy our custom CSS file to the path
    copy(css_file, custom_css_path)
    # TODO: Add try catch block here
    copytree(css_dir, os.path.join(custom_dir, 'css'))
