########################################
# Makefile                             #
########################################

# Compilers
NBCC = jupyter nbconvert
PDFCC = wkhtmltopdf

# Compiler flags
HFLAGS =
PFLAGS =

# Folders
SRC_DIR = ../notebooks
HTML_DIR = ../html
PDF_DIR = ../pdf

# Files
SRC_FILES = $(wildcard $(SRC_DIR)/*.ipynb)
HTML_FILES = $(patsubst $(SRC_DIR)/%.ipynb,%.html,$(SRC_FILES))
PDF_FILES = $(patsubst $(SRC_DIR)/%.ipynb,%.pdf,$(SRC_FILES))

# Default (we don't actually want to do anything)
default:
	@echo "This make file is only used to generate static webpages."
	@echo "There should be no reason for the end user to run make."
	@echo "Proceed at your own peril!"

# Build everything
all: html pdf

# Build all HTML pages
html: $(HTML_DIR) $(HTML_FILES) $(HTML_DIR)/css.chk

# Build all pdf files
pdf: $(PDF_DIR) $(PDF_FILES)

# Make directories for htm and pdf output
$(HTML_DIR):
	mkdir $(HTML_DIR)

$(PDF_DIR):
	mkdir $(PDF_DIR)

# CSS dependency magic
$(HTML_DIR)/css.chk:
	cp -R ./css $(HTML_DIR)/
	cp ./custom.css $(HTML_DIR)/custom.css
	touch $(HTML_DIR)/css.chk

# HTML recipe
.PRECIOUS: %.html
%.html: $(SRC_DIR)/%.ipynb $(HTML_DIR)/css.chk
	$(NBCC) $(HFLAGS) --to=html --output-dir=$(HTML_DIR) $<
	# Replace '.ipynb' in links with '.html'
	sed -i 's/.ipynb/.html/g' $(HTML_DIR)/$@

# LaTeX (pdf) recipe
%.pdf: $(HTML_DIR)/%.html
	-$(PDFCC) $(PFLAGS) $< $(PDF_DIR)/$@

# Purge all files
clean:
	-rm $(HTML_DIR)/*.html $(PDF_DIR)/*.pdf
