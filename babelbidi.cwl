# TeXstudio completion list for babelbidi
# Public interfaces; availability may depend on the engine and package options.
#include:babel

# Package options; other options are passed to Babel.
#keyvals:\usepackage/babelbidi#c
latin=
ltr=
rtl=
code=
fontcache=#true,false
autofootnoterule
textwidthfootnoterule
arabmaths
extrafootnotefeatures=#on,off
logostyle=#auto,simple
bidi=
layout=
#endkeyvals

# Language and font selection
\lr{text}
\rl{text}
\latintoday
\latinfont
\latinttfamily
\settextfont{font}
\settextfont[font features]{font}
\setlatintextfont{font}
\setlatintextfont[font features]{font}
\setlatinsansfont{font}
\setlatinsansfont[font features]{font}
\setlatinmonofont{font}
\setlatinmonofont[font features]{font}
\deflatinfont{command}{font}#d
\deflatinfont{command}[font features]{font}#d
\fontfallback{source language}{candidate languages}
\latinverb|%<text%>|
\latinverb*|%<text%>|
\begin{latin}
\end{latin}
\begin{latin*}
\end{latin*}
\begin{latinverbatim}#V
\end{latinverbatim}
\begin{latinverbatim*}#V
\end{latinverbatim*}

# Language aliases
\eqcommand{alias}{original}
\eqenvironment{alias}{original}
\EqEnvironment{alias}{original}
\makezwnjletter

# Text direction
\TeXXeTOn
\TeXXeTOff
\beginL
\endL
\beginR
\endR
\LR{text}
\LRE{text}
\RL{text}
\RLE{text}
\setLTR
\setLR
\unsetRTL
\unsetRL
\setRTL
\setRL
\unsetLTR
\unsetLR
\setRTLmain
\begin{LTR}
\end{LTR}
\begin{RTL}
\end{RTL}
\begin{LTR*}
\end{LTR*}
\begin{RTL*}
\end{RTL*}

# Directional boxes and overlaps
\hboxL{contents}
\hboxR{contents}
\vboxL{contents}
\vboxR{contents}
\vtopL{contents}
\vtopR{contents}
\bidillap{text}
\bidirlap{text}

# Footnotes
\LTRfootnote{text}
\LTRfootnote[number]{text}
\RTLfootnote{text}
\RTLfootnote[number]{text}
\LTRfootnotetext{text}
\LTRfootnotetext[number]{text}
\RTLfootnotetext{text}
\RTLfootnotetext[number]{text}
\LTRthanks{text}
\RTLthanks{text}
\setfootnoteLR
\unsetfootnoteRL
\setfootnoteRL
\unsetfootnoteLR
\leftfootnoterule
\LRfootnoterule
\rightfootnoterule
\RLfootnoterule
\textwidthfootnoterule
\autofootnoterule
\footnoterulewidth#L
\SplitFootnoteRule
\debugfootnotedirection
\normalfootnotes
\normalfootnotes*
\paragraphfootnotes
\paragraphfootnotes*
\twocolumnfootnotes
\twocolumnfootnotes*
\threecolumnfootnotes
\threecolumnfootnotes*
\fourcolumnfootnotes
\fourcolumnfootnotes*
\fivecolumnfootnotes
\fivecolumnfootnotes*
\sixcolumnfootnotes
\sixcolumnfootnotes*
\sevencolumnfootnotes
\sevencolumnfootnotes*
\eightcolumnfootnotes
\eightcolumnfootnotes*
\ninecolumnfootnotes
\ninecolumnfootnotes*
\tencolumnfootnotes
\tencolumnfootnotes*

# Citations, lists and counters
\Latincite{keylist}#c
\Latincite[note]{keylist}#c
\begin{latinitems}
\end{latinitems}
\begin{LTRitems}
\end{LTRitems}
\begin{RTLitems}
\end{RTLitems}
\begin{LTRbibitems}
\end{LTRbibitems}
\begin{RTLbibitems}
\end{RTLbibitems}
\setLTRbibitems
\setRTLbibitems
\setdefaultbibitems
\RTLcases{cases}
\begin{RTLcases}
\end{RTLcases}
\SepMark{separator}

# Margins and columns
\LTRmarginpar{text}
\LTRmarginpar[left text]{right text}
\RTLmarginpar{text}
\RTLmarginpar[left text]{right text}
\setLTRmarginpar
\setRTLmarginpar
\setdefaultmarginpar
\LTRdblcol
\RTLdblcol
\LTRmulticolcolumns
\RTLmulticolcolumns
\LTRdfnmakecol
\RTLdfnmakecol
\twocolumnstableofcontents
