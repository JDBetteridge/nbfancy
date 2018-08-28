#!/bin/bash

# Custom CSS
mkdir $HOME/.jupyter/custom
cp $HOME/library/tools/css/w3.css $HOME/.jupyter/custom/custom.css

# Set iPython profile
ipython profile create
cp $HOME/library/tools/pdflatex_magic.py $HOME/.ipython/extensions/
cp $HOME/library/tools/bash2_magic.py $HOME/.ipython/extensions/
cp $HOME/library/tools/ipython_config.py $HOME/.ipython/profile_default/
