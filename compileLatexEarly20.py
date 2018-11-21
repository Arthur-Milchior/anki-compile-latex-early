# -*- coding: utf-8 -*-

"""Copyright: Arthur Milchior arthur@milchior.fr
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

========Note concerning header/footer's change

If you change header and/or footer after a compilation failed, you'll
stee have the previous error message. In order to try a new
compilation, please change your latex code. You may just add a useless
{} or a space, it doesn't matter.

Indeed, in order to avoid loosing time, compilation is tried again
only when the text between [$], [$$] or [late] changed. And this text
does not contain the header/footer. 

"""

from anki.hooks import wrap
from aqt.utils import tooltip, showWarning
from anki.utils import checksum
from anki.notes import Note
import re
import unicodedata
import anki.notes
import os
from anki.latex import regexps, _latexFromHtml, build, _buildImg
from anki.consts import *

def mungeQA(html, type, fields, model, data, col):
    "Convert TEXT with embedded latex tags to image links. Returns the HTML and whether an error occurred."
    error = False
    for match in regexps['standard'].finditer(html):
        link, er = _imgLink(col, match.group(1), model)
        html = html.replace(match.group(), link)
        error = error or er
    for match in regexps['expression'].finditer(html):
        link, er = _imgLink(
            col, "$" + match.group(1) + "$", model)
        html = html.replace(match.group(), link)
        error = error or er
    for match in regexps['math'].finditer(html):
        link, er = _imgLink(
            col,
            "\\begin{displaymath}" + match.group(1) + "\\end{displaymath}", model)
        html = html.replace(match.group(), link)
        error = error or er
    return html, error

buggedLatex ={}

def _imgLink(col, latex, model):
    """A pair containing:
    An img link for LATEX, creating if necesssary. 
    Whether an error occurred."""
    txt = _latexFromHtml(col, latex)
    if txt in buggedLatex:
        return (buggedLatex[txt],True)
    if model.get("latexsvg", False):
        ext = "svg"
    else:
        ext = "png"

    # is there an existing file?
    fname = "latex-%s.%s" % (checksum(txt.encode("utf8")), ext)
    link = '<img class=latex src="%s">' % fname
    if os.path.exists(fname):
        return (link,False)

    # building disabled?
    if not build:
        return ("[latex]%s[/latex]" % latex,False)

    err = _buildImg(col, txt, fname, model)
    if err:
        buggedLatex[txt]=err
        return (err,True)
    else:
        return (link,False)

oldFlush = Note.flush
def filesInStr(self, mid, string, note, mod, includeRemote=False):
    """The list of media's path in the string
    
    Keyword arguments:
    self -- the media manager
    mid -- the id of the model of the note whose string is considered
    string -- A string, which corresponds to a field of a note
    note -- the note
    includeRemote -- whether the list should include contents which is with http, https or ftp
    """
    l = []
    model = self.col.models.get(mid)
    strings = []
    someError = False
    if model['type'] == MODEL_CLOZE and "{{c" in string:
       # if the field has clozes in it, we'll need to expand the
        # possibilities so we can render latex
        strings = self._expandClozes(string)
    else:
        strings = [string]
    for string in strings:
        # handle latex
        (string,error) = mungeQA(string, None, None, model, None, self.col)
        someError = error or someError
        # extract filenames
        for reg in self.regexps:
            for match in re.finditer(reg, string):
                fname = match.group("fname")
                isLocal = not re.match("(https?|ftp)://", fname.lower())
                if isLocal or includeRemote:
                    l.append(fname)
    return (l,someError)

def noteFlush(note, mod=None):
    someError=False
    for field in note.fields:
        (_,error)=filesInStr(note.col.media, note.mid,  field, note, mod)
        someError = someError or error
    if someError:
        if note.hasTag("LaTeXError"):
            tooltip("Some LaTex compilation error remains.")
        else:
            note.addTag("LaTeXError")
            tooltip("There was some LaTex compilation error.")
    else:
        if note.hasTag("LaTeXError"):
            note.delTag("LaTeXError")
            tooltip("There are no more LaTeX error.")
    oldFlush(note,mod=mod)
      
  
Note.flush = noteFlush
