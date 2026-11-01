LaTeX Package: BabelBidi v0.5.0 2026-11-01
----------------------------------------

An extension to Babel’s bidirectional support.

## Description

`babelbidi` extends Babel with bidirectional typesetting, direction-sensitive layout fixes, language selection, and font configuration. It supports LuaTeX (recommended), XeTeX, and pdfTeX.

## Features

- Luabidi-compatible public API across all three engines.
- Direction commands, inline text, environments, and directional boxes.
- Explicitly directed footnotes and configurable footnote rules.
- Automatic auxiliary-language selection.
- Font configuration and LuaTeX glyph fallback.
- Layout patches for common packages.

## Installation

**CTAN:** `tlmgr install babelbidi` — [Package page](https://ctan.org/pkg/babelbidi)

**GitHub:** `git clone https://github.com/gambi-shah/babelbidi.git`

Copy the files into a TeX-searchable directory or keep them beside your document.

## Usage

~~~latex
\documentclass{article}
\usepackage{babelbidi}

\begin{document}
Hey world!
\end{document}
~~~

Compile with LuaLaTeX (recommended), XeLaTeX, or pdfTeX. Babel language options are supported; see the Babel manual.

## Interfaces

BabelBidi provides LuaBidi’s public `luabidi` interfaces across LuaTeX, XeTeX, and pdfTeX: direction commands and environments, `\LRE`, `\RLE`, `\LR`, `\RL`, directional boxes, and directed footnotes with configurable rules.

Additional interfaces include `\lr{...}` and `\rl{...}` for language-aware inline text; `\latinverb` and `latinverbatim` (including starred forms); font commands such as `\settextfont` and `\deflatinfont`; and LuaTeX’s `\fontfallback`.

Code layout patches apply to non-Latin main scripts. Related packages may be loaded before or after BabelBidi.

## Language Selection

Auxiliary Latin, LTR, RTL, and code languages are selected automatically and updated after each `\babelprovide` call. The `latin`, `ltr`, `rtl`, and `code` options override these choices. Declare languages before setting fonts. Babel’s `nil` is ignored; defaults are `english` for Latin, LTR, and code, and `arabic` for RTL.

## Documentation

See the [main manual](doc/babelbidi.pdf) for configuration and examples.

## License and maintainer

- License: LPPL 1.3c or later.
- Maintainer: Amer Amikhteh.
- Report bugs via the [repository issue tracker](https://github.com/gambi-shah/babelbidi/issues).
