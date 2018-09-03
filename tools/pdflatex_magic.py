from IPython.core import magic_arguments
from IPython.display import Image
from IPython.core.magic import line_magic, cell_magic, line_cell_magic, Magics, magics_class

import tempfile
import os
import subprocess

@magics_class
class PDFLatexMagic(Magics):
    @cell_magic
    def pdflatex(self, line='', cell=None):
        '''Wrap cell text with latex: header, footer
        Run pdflatex on resultant file
        Display image'''
        
        # Get working directory and save for later
        cwd = os.getcwd()
        
        # UID
        self._id = str(id(cell))
        
        # Setup temporary directory
        self.tempdir = tempfile.TemporaryDirectory()
        os.chdir(self.tempdir.name)
        self.texname = os.path.join(self.tempdir.name, self._id + '.tex')
        self.pdfname = os.path.join(self.tempdir.name, self._id + '.pdf')
        self.pngname = os.path.join(self.tempdir.name, self._id + '.png')
        
        self.writeLatex(cell, cwd)

        if self.makeImage():
            ret_val = Image(filename=self.pngname)
        else:
            print(self.error)
            print(self.error.output.decode())
            ret_val = None
        
        os.chdir(cwd)
        
        return ret_val

    def writeLatex(self, celltext, cwd):
        '''Write cell text wrapped with latex: header, footer'''
        
        template = r'''
        \documentclass[convert, varwidth]{standalone}
        \usepackage{amsmath,amssymb,amsthm,amsxtra,graphicx}
        \graphicspath{{%(CWD)s/}{%(CWD)s/../images/}{%(CWD)s/../figures/}}
        \begin{document}
            %(CELLTEXT)s
        \end{document}
        '''
        
        with open(self.texname, 'w') as tex:
            tex.write(template%{'CELLTEXT' : celltext, 'CWD' : cwd})
        
    def makeImage(self):
        '''Make pdf with pdflatex and convert to png
        Remove current files'''
        
        # return True, unless pdflatex or convert fail
        made_pdf = False
        made_png = False
        
        try:
            # Alternative (azure???) doesn't work with figures
            #pdflatex --output-format=dvi test.tex
            #dvipng -D 300 test.dvi
            result = subprocess.run(['pdflatex', '-halt-on-error', self.texname],
                                    check=True,
                                    timeout=5,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            made_pdf = True
        except Exception as e:
            self.error = e
        
        if made_pdf:
            try:
                result2 = subprocess.run(['convert', '-density', '300', self.pdfname, '-quality', '90', self.pngname],
                                         check=True,
                                         timeout=5,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT)
                made_png = True
            except Exception as e:
                self.error = e
        
        return made_png

# Allows loading as an extension
def load_ipython_extension(ipython):
    ipython.register_magics(PDFLatexMagic)

# Useful if you have already loaded as an extension
#ip = get_ipython()
#ip.register_magics(PDFLatexMagic)
