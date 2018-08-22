from IPython.core import magic_arguments
from IPython.display import Image
from IPython.core.magic import line_magic, cell_magic, line_cell_magic, Magics, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from IPython.core.magics import script

import tempfile
import os
import subprocess

@magics_class
class bash2Magic(Magics):
    @magic_arguments()
    @argument('--dir', help='Set the working directory')
    @cell_magic
    def bash2(self, line='', cell=None):
        '''
        Wrapper for bash magic
        '''
        
        # Parse args
        args = parse_argstring(self.bash2, line)
        #print(args)
        
        # Change to new working directory
        try:
            if args.dir is not None:
                os.chdir(args.dir)
        except Exception as e:
            print(e)
        else:
            # Instantiate original bash magic
            newscript = script.ScriptMagics
            newscript.shell = self.shell
            
            # Add oneliner to end of cell
            pwdcmd = '\necho :pwd:`pwd` >&2'
            newcell = cell + pwdcmd
            
            # Call script magic for bash
            newscript.shebang(newscript, line='bash --err reterr', cell=newcell)
            
            # Extract new directory
            err = newscript.shell.user_ns['reterr']
            newdir = err.split(':pwd:')[-1].strip()
            
            # Change into new directory
            try:
                os.chdir(newdir)
            except Exception as e:
                print(e)
        
        return

# Allows loading as an extension
def load_ipython_extension(ipython):
    ipython.register_magics(bash2Magic)

# Useful if you have already loaded as an extension
#ip = get_ipython()
#ip.register_magics(bash2Magic)
