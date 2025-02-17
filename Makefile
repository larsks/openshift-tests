CSS = pandoc/github.css
PANDOC = pandoc

ifeq ($(SHOWPROPS), 1)
J2MDFLAGS += -p
endif

all: testresults.html

testresults.md: testresults.xml
	uv run junit2markdown.py $(J2MDFLAGS) -o $@ $<

testresults.html: testresults.md
	$(PANDOC) -f gfm -t html5 --css $(CSS) --standalone --lua-filter pandoc/headertotitle.lua -o $@ $<

clean:
	rm -f testresults.md testresults.html

.PHONY: view
view: testresults.html
	xdg-open $<
