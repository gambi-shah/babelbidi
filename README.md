# The `babelbidi` package

An extension to Babel’s bidirectional support, with layout fixes and direction/language interfaces.

## Description

`babelbidi` extends Babel's bidirectional support with
direction-sensitive layout fixes and complementary interfaces for text
direction and language selection. It works with LuaTeX (recommended), XeTeX (fallback), or pdfTeX (last resort), whether the main language is LTR or RTL.

## Features

- Direction commands `\LRE{...}`, `\RLE{...}`, `\lr{...}`, and `\rl{...}`.
- `RTL`, `LTR`, and `latin` environments.
- Language selection for auxiliary text with `\babelbidilangs`.
- Layout patches for direction-sensitive elements, chiefly with LuaLaTeX.

## Installation

Place `babelbidi.sty` and the accompanying `babelbidi-*.def` files in a
TeX-searchable directory or next to your document. Keep the accompanying
`babelbidi-lang` file with them.

## Usage
Minimal example:

~~~latex
\documentclass{article}
\usepackage{babelbidi}

\begin{document}
Hey world!
\end{document}
~~~

Compile with LuaLaTeX (recommended), XeLaTeX (fallback) or pdfTeX (last resort).

For further
configuration and examples, see the [main manual](doc/babelbidi.pdf).

## License and maintainer

- License: LPPL 1.3c or later.
- Maintainer: Amer Amikhteh.