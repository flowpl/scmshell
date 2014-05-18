scmshell
========

see git and mercurial stats right at prompt


INSTALL
-------

1. Clone this repo somewhere
2. Add the following line to you .bashrc file to activate it:

	PROMPT_COMMAND="/absolute/path/to/scmshell/scmshell.py"

3. Adding only PROMPT_COMMAND will leave you with duplicated user and path output, so remove the standard path by editing the line that starts with PS1 to
	
	PS1="> "


DEPENDENCIES
------------

only python stdlibs