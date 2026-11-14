# Third-party notices

BabelBidi is a separate project maintained by Amer Amikhteh. References to
upstream works do not imply that their authors maintain or support BabelBidi.
The following identifies material retained or adapted in this distribution.
The LPPL text is included in `LICENSE`. The version numbers below identify
sources inspected for comparison; they do not assert that the exact upstream
revision used when the material was first written is known.

## Babel

- Upstream: Babel, version 26.14 (2026-10-15), `babel.dtx` and `babel.tex`;
  the LuaTeX code is also distributed as `luababel.def`.
- Copyright (C) 2012-2026 Javier Bezos and Johannes L. Braams.
  Copyright (C) 1989-2012 Johannes L. Braams and any individual authors
  listed elsewhere in the original file.
- License: LPPL version 1.3 or, at your option, any later version.
- Complete original distribution: https://ctan.org/pkg/babel
  and https://github.com/latex3/babel
- In `doc/babelbidi.tex`, the presentation helpers and layout settings
  draw on the Babel guide. They have been adapted for this manual; its
  cover and package-specific prose describe BabelBidi.
- In `babelbidi-onchar.def`, the expected font-mapper definition and part
  of the cache-miss path retain code corresponding to Babel's `\bbl@mapdir`.
  The file adds a compatibility guard and a cache for font mappings.

## bidi

- Upstream: bidi, `latex-xetex-bidi.def` and `bidituftesidenote.sty`;
  copyright (c) 2007–2026 Vafa
  Khalighi and (c) 2018–2020 bidi-tex GitHub Organization; LPPL version
  1.3c or later. Complete original distribution: https://ctan.org/pkg/bidi
- The mathematical alignment in `babelbidi-api-layout.def` is adapted from the
  `\def\RTLcases` in bidi's `latex-xetex-bidi.def` (version 26.01.08).
  It supports the single-column example in bidi's guide and the optional
  second column of that alignment. BabelBidi adds dispatch between the
  command and environment forms.
- The LuaTeX directional note builders in `babelbidi-api-layout.def` are
  adapted from the biditufte note implementation distributed with bidi,
  taking account of BabelBidi's direction and package-loading mechanisms.

## beamer-rl and beamer

- Upstream: beamer-rl, compared with version 2.1 (2026-07-22),
  `beamer-rl.cls`. Copyright (c) 2019-2026 Salim Bou; LPPL version 1.3c
  or later. Complete original distribution: https://ctan.org/pkg/beamer-rl
  and https://github.com/seloumi/beamer-rl
- `babelbidi-beamer.def` extracts the rounded-box definitions from
  beamer-rl for the BabelBidi/beamer integration. The definitions match
  the compared version apart from whitespace; file identification and
  loading wrappers have been added.
- The rounded-box implementation also shares substantial code with
  beamer's `beamerbaseboxes.sty`. That file states: Copyright 2003-2007
  Till Tantau; Copyright 2010 Vedran Miletić; Copyright 2012, 2015
  Vedran Miletić and Joseph Wright; Copyright 2020-2026 Joseph Wright and
  samcarter. It permits distribution and modification under the LPPL
  and/or the GNU Public License; this distribution uses the LPPL option.
  Complete original distribution: https://ctan.org/pkg/beamer

## LaTeX citation code

- The standard citation loop in `babelbidi-cite.def` closely matches
  `\@citex` in the LaTeX kernel (`ltbibl.dtx`, generated in `latex.ltx`).
  Copyright (C) 1993-2026 The LaTeX Project and any individual authors
  listed in the original file. License: LPPL version 1.3c or later.
  Complete original distribution: https://ctan.org/pkg/latex-base
- BabelBidi's citation processor adds Latin-language selection, local
  handling of the optional note and integration with citation packages.

Some public interfaces share names or purposes with interfaces in bidi and
XePersian, but their behavior and coverage can differ. Under XeTeX,
BabelBidi uses the bidi backend. The upstream packages retain their
respective licenses and maintainers.
