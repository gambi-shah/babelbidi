# The `babelbidi` package

An extension to babel’s bidirectional support

## Description

`babelbidi` extends Babel's bidirectional support by fixing direction-sensitive behaviour and providing interfaces for explicit text direction, language selection, and font configuration, including glyph fallback with LuaTeX. It supports languages available through Babel and works with LuaTeX (recommended), XeTeX, or pdfTeX, with either an LTR or RTL main language.

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
- `\settextfont`, `\setlatintextfont`, `\setlatinsansfont`, `\setlatinmonofont`, and `\deflatinfont` — configure fonts with Unicode engines.
- `\fontfallback` — configure font fallback with LuaLaTeX.

## Language selection

The four auxiliary languages (Latin, LTR, RTL, and code) are available upon loading. Automatic selections update after each `\babelprovide` call, based on the main and loaded languages. The `latin`, `ltr`, `rtl`, and `code` options override these selections permanently. Declare languages before setting fonts. Babel's synthetic `nil` language is ignored; without a real language, Latin, LTR, and code fall back to `english`, and RTL to `arabic`.

See the [main manual](doc/babelbidi.pdf) for configuration and examples.

## License and maintainer

- License: LPPL 1.3c or later.
- Maintainer: Amer Amikhteh.
- Report bugs via the [repository issue tracker](https://github.com/gambi-shah/babelbidi/issues).
