![scmshell in action](/scmshell.gif?raw=true "scmshell in action")

scmshell
========

see git and mercurial stats right at prompt


INSTALL
-------

Clone this repo somewhere

Add the following line to you .bashrc file to activate it:

	PROMPT_COMMAND="/absolute/path/to/scmshell/scmshell.py"

Adding only PROMPT_COMMAND will leave you with duplicated user and path output, so remove the standard path by editing the line that starts with PS1 to
	
	PS1="> "

This way the actual prompt from your shell is just > 


DEPENDENCIES 
------------ 
 
only python stdlibs  