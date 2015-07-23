#
# this make file builds the docmanager man page
#

DB := /usr/share/xml/docbook/stylesheet/nwalsh/current
BUILDDIR := build
XMLFILE := docmanager.xml
OUTFILE := docmanager.1

.PHONY: all clean

all: clean $(BUILDDIR)
	xmllint --noout --valid xml/$(XMLFILE)
	xsltproc --nonet $(DB)/manpages/docbook.xsl xml/$(XMLFILE)
	mv $(OUTFILE) $(BUILDDIR)

clean:
	-rm -r $(BUILDDIR)

$(BUILDDIR):
	mkdir $(BUILDDIR)
