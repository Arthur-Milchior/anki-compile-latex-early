Copyright: Arthur Milchior arthur@milchior.fr
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
Feel free to contribute to the code on https://github.com/Arthur-Milchior/anki-compile-latex-early/
Add-on number: 769835008

Note's latex are created as soon as possible. I.e. either on creation, or when an edit is done to a field. 
As usual, compilation occurs only when the document is not already compiled.
In case of error, a tag LaTeXError is added. Once every error deleted or repared, the tag is removed.

This addon avoids the requirement to «check media» in order to compile the card of new cards before synchronizing. 
However, it may slow done the process of adding new cards with a lot of new latex text, since compiling takes some time.


The browser does not show when the LaTeXError tag is added/removed. Do
not rely on the tag line when you edit your code to know whether
errors remain. The yellow box shows if there are error, if you do not
see messages regarding error, you can assume that there are no errors.

A message also tells you when there is at least one latex error in your note.
The first message is in a warning box. (the exact rule is: there is a warning box when there is an error and the LaTeXError tag is absent)
The successive messages are in tip box (small yellow boxes). Those tips occurs when you edit a note.



if you want to remove this warning/tip, its not complicated:
1)Tools > addons >compile-latex-early.py
2)Looks for the line showWarning("There was some LaTex compilation error.") 
  or for the line tooltip("There was some LaTex compilation error.")
3) adds a # in front of the line
4) restart anki.