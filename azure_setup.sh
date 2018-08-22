#!/bin/bash

# Custom CSS
mkdir $HOME/.jupyter/custom
cp $HOME/library/tools/custom.css $HOME/.jupyter/custom/

# Set iPython profile
ipython profile create
cp $HOME/library/tools/pdflatex_magic.py $HOME/.ipython/extensions/
cp $HOME/library/tools/bash2_magic.py $HOME/.ipython/extensions/
cp $HOME/library/tools/ipython_config.py $HOME/.ipython/profile_default/
