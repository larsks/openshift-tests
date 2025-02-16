CSS = pandoc/github.css

ifeq ($(SHOWPROPS), 1)
J2MDFLAGS += -p
endif

all: testresults.html

testresults.md: testresults.xml
	uv run junit2markdown.py $(J2MDFLAGS) -o $@ $<

testresults.html: testresults.md
	pandoc -f gfm -t html5 --css $(CSS) --standalone --lua-filter pandoc/headertotitle.lua -o $@ $<

clean:
	rm -f testresults.md testresults.html
