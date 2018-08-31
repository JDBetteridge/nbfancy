########################################
# Makefile                             #
########################################

# Folders
SRC_DIR = ../notebooks_plain
RENDERED_DIR = ../notebooks_rendered
HTML_DIR = ../html
PDF_DIR = ../pdf

# Files
SRC_FILES = $(wildcard $(SRC_DIR)/*.ipynb)
RENDERED_FILES = $(patsubst $(SRC_DIR)/%.ipynb,$(RENDERED_DIR)/%.ipynb,$(SRC_FILES))
HTML_FILES = $(patsubst $(SRC_DIR)/%.ipynb,%.html,$(SRC_FILES))
PDF_FILES = $(patsubst $(SRC_DIR)/%.ipynb,%.pdf,$(SRC_FILES))

# Compilers
RENDERCC = python nbfancy.py
NBCC = jupyter nbconvert
PDFCC = wkhtmltopdf

# Compiler flags
RFLAGS = --headercell=./top.ipynb --footercell=./bottom.ipynb --sourcedir=$(SRC_DIR)
HFLAGS =
PFLAGS =

# Default (we don't actually want to do anything)
default:
	echo $(SRC_FILES)
	echo $(RENDERED_FILES)
	echo $(HTML_FILES)
	@echo "This make file is only used to generate static webpages."
	@echo "There should be no reason for the end user to run make."
	@echo "Proceed at your own peril!"

# Build everything
all: render html pdf

# Render all notebooks
render: $(RENDERED_DIR) $(RENDERED_FILES)

# Build all HTML pages
html: $(HTML_DIR) $(HTML_FILES) $(HTML_DIR)/css.chk

# Build all pdf files
pdf: $(PDF_DIR) $(PDF_FILES)

# Make directories for rendered noterbook, html and pdf output
$(RENDERED_DIR):
	mkdir $(RENDERED_DIR)

$(HTML_DIR):
	mkdir $(HTML_DIR)

$(PDF_DIR):
	mkdir $(PDF_DIR)

# Rendered Notebook recipe
.PRECIOUS: %.ipynb
$(RENDERED_DIR)/%.ipynb: $(SRC_DIR)/%.ipynb
	$(RENDERCC) $(RFLAGS) $< $@

# CSS dependency magic
$(HTML_DIR)/css.chk:
	cp -R ./css $(HTML_DIR)/
	cp ./custom.css $(HTML_DIR)/custom.css
	touch $(HTML_DIR)/css.chk

# HTML recipe
.PRECIOUS: %.html
%.html: $(RENDERED_DIR)/%.ipynb $(HTML_DIR)/css.chk
	$(NBCC) $(HFLAGS) --to=html --template=style_template.tpl --output-dir=$(HTML_DIR) $<
	# Replace '.ipynb' in links with '.html'
	sed -i 's/.ipynb/.html/g' $(HTML_DIR)/$@
	# Horrible hack because <code> environment doesn't seem to work with CSS sheet
	sed -i 's/<code>/<code style="background-color:#F7F7F7;border:1px solid #CFCFCF">/g' $(HTML_DIR)/$@

# Hopefully removable
# schedule HTML recipe (Correctly handles table)
#~ .PRECIOUS: %.html
#~ %.html: $(SRC_DIR)/%.ipynb $(HTML_DIR)/css.chk
#~ 	$(NBCC) $(HFLAGS) --to=html --template=style_template.tpl --output-dir=$(HTML_DIR) $<
#~ 	# Replace '.ipynb' in links with '.html'
#~ 	sed -i 's/.ipynb/.html/g' $(HTML_DIR)/$@
#~ 	# Horrible hack because <code> environment doesn't seem to work with CSS sheet
#~ 	sed -i 's/<code>/<code style="background-color:#F7F7F7;border:1px solid #CFCFCF">/g' $(HTML_DIR)/$@
#~ 	# Horrible hack to adjust the table
#~ 	sed -i 's/<table>/<table class="w3-table w3-striped w3-hoverable">/g' $(HTML_DIR)/$@
#~ 	sed -i 's/<thead>/<thead class="w3-black">/g' $(HTML_DIR)/$@

# LaTeX (pdf) recipe
%.pdf: $(HTML_DIR)/%.html
	-$(PDFCC) $(PFLAGS) $< $(PDF_DIR)/$@

# Purge all files
clean:
	-rm $(RENDERED_DIR)/*.ipynb $(HTML_DIR)/*.html $(PDF_DIR)/*.pdf
