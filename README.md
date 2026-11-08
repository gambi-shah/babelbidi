# LaTeX Package: BabelBidi v0.6.0 (2026-11-08)

An extension to Babel’s bidirectional support.

## Description

This package extends [Babel](https://ctan.org/pkg/babel)’s bidirectional support by correcting direction-sensitive behaviour, providing text-direction and layout controls, and adding interfaces for language selection and font configuration, including glyph fallback with LuaTeX. It supports Babel languages and works with LuaTeX (recommended), XeTeX, or pdfTeX, with either an LTR or RTL main language.

## Features

- BabelBidi uses `bidi`'s native interfaces on XeTeX and provides the corresponding user-level interfaces through Babel on LuaTeX and pdfTeX.
- Direction commands, environments, directional boxes, and overlapping text.
- Directed footnotes and title notes, configurable footnote rules, and optional extra footnote layouts.
- Direction controls for lists, bibliographies, cases, margin notes, and columns.
- Automatic auxiliary-language selection.
- Font configuration, LuaTeX glyph fallback, and layout patches for commonly used packages.

## Installation

**CTAN:** `tlmgr install babelbidi` — [Package page](https://ctan.org/pkg/babelbidi)

**GitHub:** `git clone https://github.com/gambi-shah/babelbidi.git`

## Usage

~~~latex
\documentclass{article}
\usepackage{babelbidi}

\begin{document}
Hey world!
\end{document}
~~~

Compile with LuaLaTeX (recommended), XeLaTeX, or pdfLaTeX. Babel language options are supported.

## Interfaces

BabelBidi provides the complete user-level interfaces of `bidi` and `luabidi`, including direction commands and environments, directional boxes, footnote controls, list and bibliography direction, the `RTLcases` environment, counter separators, margin notes, and column-order controls.

The optional `extrafootnotefeatures` package option enables paragraph and two- to ten-column footnote layouts.

Additional interfaces include language-aware `\lr{...}` and `\rl{...}`, `\latinverb` and `\latinverbatim`, font commands such as `\settextfont` and `\deflatinfont`, and LuaTeX's `\fontfallback`.

Layout patches apply to non-Latin main scripts. Related packages may be loaded before or after BabelBidi.

## Language Selection

Auxiliary Latin, LTR, RTL, and code languages are selected automatically and updated after each `\babelprovide` call. The `latin`, `ltr`, `rtl`, and `code` options override these choices. Declare languages before configuring fonts.

## Documentation

See the [main manual](doc/babelbidi.pdf) for configuration details and examples.

## License and Maintainer

- License: LPPL 1.3c or later.
- Maintainer: Amer Amikhteh.
- Report bugs via the [repository issue tracker](https://github.com/gambi-shah/babelbidi/issues).
