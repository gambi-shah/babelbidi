LaTeX Package: BabelBidi v1.0.0 (2026-11-11)
----------------------------------------

An extension to Babel’s bidirectional support.

## Description

This package extends [Babel](https://ctan.org/pkg/babel)’s bidirectional support by correcting direction-sensitive behaviour and providing text-direction and layout controls. It supports Babel languages and works with LuaTeX (recommended), XeTeX, or pdfTeX, with either an LTR or RTL main language.

## Features

- BabelBidi uses `bidi`'s native interfaces on XeTeX and provides the corresponding user-level interfaces through Babel on LuaTeX and pdfTeX.
- Direction commands, environments, directional boxes, and overlapping text.
- Directed footnotes and title notes, configurable footnote rules, and optional extra footnote layouts.
- Direction controls for lists, bibliographies, cases, margin notes, and columns.
- Font configuration, LuaTeX glyph fallback, and layout patches for commonly used packages.
- Engine logos that adapt to the surrounding language and text direction.

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

BabelBidi provides the complete user-level interfaces of `bidi` and `luabidi`.

Some additional interfaces include:

- `\lr{...}` and `\rl{...}` for language-aware text direction.
- `\Latincite` for citations using the selected Latin language.
- `\latinverb` and the `latinverbatim` environment for code and verbatim text.
- `\settextfont` and `\deflatinfont` for font configuration with Unicode engines.
- `\fontfallback` for glyph fallback with LuaTeX.

## Language Selection

Auxiliary Latin, LTR, RTL, and code languages are selected automatically and updated after each `\babelprovide` call. The `latin`, `ltr`, `rtl`, and `code` options override these choices. Declare languages before configuring fonts.

## Documentation

See the [main manual](doc/babelbidi.pdf) for configuration details and examples, including compatibility notes and engine-specific limitations.

The optional `babelbidi.cwl` provides TeXstudio completion for the package's commands and environments. Copy it to TeXstudio's user completion directory (`~/.config/texstudio/completion/user/` on Linux).

The distribution also includes `amikhteh-logo`, a companion package used in the documentation. See its [companion guide](doc/amikhteh-logo.pdf).

## License and Maintainer

- License: LPPL 1.3c or later.
- Third-party source, copyright, and license details: [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
- Maintainer: Amer Amikhteh.
- Report bugs via the [repository issue tracker](https://github.com/gambi-shah/babelbidi/issues).
