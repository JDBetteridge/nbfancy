########################################
# Makefile                             #
########################################

# Folders
ROOT_DIR = ..
SRC_DIR = $(ROOT_DIR)/notebooks_plain
RENDERED_DIR = $(ROOT_DIR)/notebooks_rendered
HTML_DIR = $(ROOT_DIR)/html
PDF_DIR = $(ROOT_DIR)/pdf
IMAGE_DIR = $(ROOT_DIR)/images
DATA_DIR = $(ROOT_DIR)/data

# Files
SRC_FILES = $(wildcard $(SRC_DIR)/*.ipynb)
RENDERED_FILES_TARGET = $(patsubst $(SRC_DIR)/%.ipynb,$(RENDERED_DIR)/%.ipynb,$(SRC_FILES))
# Later now
# RENDERED_FILES = $(shell ls $(RENDERED_DIR)/*.ipynb)
#$(patsubst $(SRC_DIR)/%.ipynb,$(RENDERED_DIR)/%.ipynb,$(SRC_FILES))
# HTML_FILES = $(patsubst $(RENDERED_DIR)/%.ipynb,%.html,$(RENDERED_FILES))
# PDF_FILES = $(patsubst $(HTML_DIR)/%.html,%.pdf,$(HTML_FILES))

# Compilers
RENDERCC = python nbfancy.py
NBCC = jupyter nbconvert
PDFCC = wkhtmltopdf

# Compiler flags
RFLAGS = --headercell=./top.ipynb --footercell=./bottom.ipynb --sourcedir=$(SRC_DIR)
HFLAGS = --to=html --output-dir=$(HTML_DIR)
PFLAGS =

# Blue title thingy
PRINT = @/bin/echo -e "\e[1;34mBuilding $@\e[0m"

# Default (we don't actually want to do anything)
default:
	@echo "This make file is only used to generate static webpages."
	@echo "There should be no reason for the end user to run make."
	@echo "Proceed at your own peril!"

# Build everything
all: render html pdf
	$(PRINT)

# Render all notebooks
render: $(RENDERED_DIR) $(RENDERED_FILES_TARGET)
	$(PRINT)

# Build all HTML pages
html: render $(HTML_DIR) $(HTML_DIR)/css.chk $(HTML_DIR)/index.html
	$(PRINT)
	$(eval RENDERED_FILES = $(shell ls $(RENDERED_DIR)/*.ipynb))
	$(eval HTML_FILES = $(patsubst $(RENDERED_DIR)/%.ipynb,$(HTML_DIR)/%.html,$(RENDERED_FILES)))
	$(MAKE) $(HTML_FILES)

# Build all pdf files
pdf: html $(PDF_DIR)
	$(PRINT)
	$(eval RENDERED_FILES = $(shell ls $(RENDERED_DIR)/*.ipynb))
	$(eval PDF_FILES = $(patsubst $(RENDERED_DIR)/%.ipynb,$(PDF_DIR)/%.pdf,$(RENDERED_FILES)))
	$(MAKE) $(PDF_FILES)

# Make directories for rendered noterbook, html and pdf output
$(RENDERED_DIR):
	$(PRINT)
	mkdir $(RENDERED_DIR)

$(HTML_DIR):
	$(PRINT)
	mkdir $(HTML_DIR)

$(PDF_DIR):
	$(PRINT)
	mkdir $(PDF_DIR)

# Rendered Notebook recipe
.PRECIOUS: %.ipynb
$(RENDERED_DIR)/%.ipynb: $(SRC_DIR)/%.ipynb
	$(PRINT)
	$(RENDERCC) $(RFLAGS) $< $@

# CSS dependency magic
$(HTML_DIR)/css.chk:
	$(PRINT)
	cp -R ./css $(HTML_DIR)/
	cp ./custom.css $(HTML_DIR)/custom.css
	touch $(HTML_DIR)/css.chk

#Create index for html and copy image and data directory to html build
$(HTML_DIR)/index.html:
	$(PRINT)
	pandoc $(ROOT_DIR)/README.md > $(HTML_DIR)/index.html
	cat ./index_footer.html >> $(HTML_DIR)/index.html
	cp -r $(IMAGE_DIR) $(HTML_DIR)/
	if [ -e $(DATA_DIR) ]; then cp -r $(DATA_DIR) $(HTML_DIR)/; fi

# HTML recipe
.PRECIOUS: %.html
$(HTML_DIR)/%.html: $(RENDERED_DIR)/%.ipynb $(HTML_DIR)/css.chk
	$(PRINT)
	$(NBCC) $(HFLAGS) $<
	# Replace '../images' in links with './images'
	sed -i 's/..\/images/.\/images/g' $(HTML_DIR)/$@
	# Replace '../data' in links with './data'
	sed -i 's/..\/data/.\/data/g' $(HTML_DIR)/$@
	# Replace '.ipynb' in links with '.html'
	sed -i 's/.ipynb/.html/g' $(HTML_DIR)/$@
	# Horrible hack because <code> environment doesn't seem to work with CSS sheet
	sed -i 's/<code>/<code style="background-color:#F7F7F7;border:1px solid #CFCFCF">/g' $(HTML_DIR)/$@
	# Another hack since \n is converted to [space] in links
	sed -i 's/%0A"/%20"/g' $(HTML_DIR)/$@

        
	
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

# PDF recipe
$(PDF_DIR)/%.pdf: $(HTML_DIR)/%.html
	@echo $(HTML_DIR)
	$(PRINT)
	-$(PDFCC) $(PFLAGS) $< $(PDF_DIR)/$@

# Purge all files
clean:
	-rm $(RENDERED_DIR)/*.ipynb $(HTML_DIR)/*.html $(PDF_DIR)/*.pdf
