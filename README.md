LaTeX Package: BabelBidi v0.4.0 2026-10-26
----------------------------------------

An extension to babel’s bidirectional support

## Description

`babelbidi` extends Babel's bidirectional support with direction-sensitive fixes, explicit direction and language selection, and font configuration with LuaTeX glyph fallback. It supports Babel languages, LTR and RTL main languages, and LuaTeX (recommended), XeTeX, or pdfTeX.

## Features

- Explicit text-direction control.
- Language-aware inline text and block environments.
- Automatic selection of auxiliary Babel languages.
- Font configuration, including LuaTeX glyph fallback.
- Layout patches for direction-sensitive elements and common packages.

## Installation

### From CTAN

Latest release: https://ctan.org/pkg/babelbidi

~~~bash
tlmgr install babelbidi
~~~

### Manual installation from GitHub

~~~bash
git clone https://github.com/gambi-shah/babelbidi.git
~~~

Copy the files into a TeX-searchable directory (run `mktexlsr` if needed) or keep them beside your document.

## Usage

~~~latex
\documentclass{article}
\usepackage{babelbidi}

\begin{document}
Hey world!
\end{document}
~~~

Compile with LuaLaTeX (recommended), XeLaTeX (fallback), or pdfTeX (last resort). Babel language options are supported; see the Babel manual for the complete list.

## Interfaces

- `\LRE{...}` and `\RLE{...}` — typeset text with explicit direction.
- `\lr{...}` and `\rl{...}` — switch to the configured LTR and RTL languages for inline text.
- `LTR`, `RTL`, and `latin` environments — typeset longer text blocks.
- `\latinverb`, `\latinverb*`, `latinverbatim`, and `latinverbatim*` — use the code language and its monospaced font for every main script; starred forms show spaces. Base interfaces retain their behaviour.
- `\settextfont`, `\setlatintextfont`, `\setlatinsansfont`, `\setlatinmonofont`, and `\deflatinfont` — configure fonts with Unicode engines.
- `\fontfallback` — configure font fallback with LuaLaTeX.

Code layout patches apply to non-Latin main scripts. Related packages can be loaded before or after `babelbidi`.

## Language selection

Auxiliary languages (Latin, LTR, RTL, and code) are selected automatically and updated after each `\babelprovide` call. The `latin`, `ltr`, `rtl`, and `code` options fix these choices explicitly. Declare languages before setting fonts. Babel's `nil` is ignored; without a real language, Latin, LTR, and code default to `english`, and RTL to `arabic`.

## Documentation
See the [main manual](doc/babelbidi.pdf) for configuration and examples.

## License and maintainer

- License: LPPL 1.3c or later.
- Maintainer: Amer Amikhteh.
- Report bugs via the [repository issue tracker](https://github.com/gambi-shah/babelbidi/issues).
