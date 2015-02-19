# hed-data-parser
Parse text files scraped from the web

#####Usage


 * Copy script inside dir containing input files (input files are assumed to have a format similar to `input (0).txt`)

```
usage: parse.py [-h] [-gp] [-gi]

Get person and institution info

optional arguments:
  -h, --help         show this help message and exit
  -gp, --get_people  Get people info. Creates `output-people.tab` in CWD
  -gi, --get_insts   Get institution info. Creates `output-institutions.tab`
                     in CWD
```

