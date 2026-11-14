# BabelBidi tests and examples

- `examples/` contains documents for exploring package features and visually
  checking their output. They are standalone examples unless their comments
  state otherwise.
- `checks/` contains focused compatibility and automatic checks. Some are
  intentionally minimal and test engine or package internals.
- `expected-failures/` contains tests that must report an error. Do not treat
  these as ordinary successful compilations.

The documents in `examples/` can also be used for visual checks:

| File | Purpose |
| --- | --- |
| `direction.tex` | Direction switches, environments, and inline text |
| `layout.tex` | Directional footnotes, lists, boxes, and columns |
| `extra-footnotes.tex` | Paragraph and multi-column footnote layouts |
| `footnote-rule.tex` | Compare directional footnote rules |
| `footnotes.tex` | Multilingual, math, and verbatim footnotes |
| `hyperref.tex` | Hyperlinked directional footnotes across pages |
| `labels.tex` | Dynamic label keys and references in a list |
| `langs.tex` | Language roles, `\lr`, `\rl`, and `latin` |
| `fonts.tex` | Main and Latin fonts, including `\deflatinfont` |
| `fontcache.tex` | Font cache interaction with a font-selection hook |
| `code.tex` | Multilingual `listings` and `minted` output |
| `latin-verbatim.tex` | Latin verbatim interfaces and code-language selection |
| `minted.tex` | Code direction, language, and character-direction options |
| `cite.tex` | Persian citation examples and moving arguments via UniPersian |
| `layout-luatex.tex` | LuaLaTeX RTL lists, pictures, tables, and footnotes |
| `logos.tex` | Engine logos and optional graphics support |
| `amikhteh-logo.tex` | Companion logo package dimensions and direction isolation |
| `manual-layout.tex` | Preview the companion package's manual page layout |

The documents in `checks/` cover cases that need focused inspection:

| File | Purpose |
| --- | --- |
| `compat.tex` | Combined cases, lists, columns, footnotes, and package compatibility |
| `aliases.tex` | Existing definitions of direction aliases and engine-specific behavior |
| `columns.tex` | Column direction, grouping, and package load order |
| `check-columns.py` | Check column order and load-order variants with both engines |
| `multicol-partial.tex` | Preserve one predefined column switch while defining the other |
| `nested-items.tex` | Compare nested ordinary, Latin, and LTR list geometry |
| `tufte-late.tex` | Load `bidituftesidenote` after BabelBidi |
| `tufte-notes.tex` | Directional Tufte notes and PDF reference targets |
| `check-tufte.py` | Compile and check the Tufte document with both Unicode engines |
| `font-fallback.tex` | Check glyph fallback, cache, and language/font state |
| `cite-engines.tex` | Citation packages and variants across TeX engines |
| `cite-natbib.tex` | Natbib and Persian citation-note language |

For example, from the project root, build an example in `/tmp`:

```sh
project_dir="$PWD"
output_dir="$(mktemp -d /tmp/babelbidi-example-XXXXXX)"
cd "$output_dir"
TEXINPUTS=".:$project_dir:" lualatex -interaction=nonstopmode -halt-on-error \
  "$project_dir/test/examples/direction.tex"
```

Use `xelatex` where appropriate, run a second time for references, and add
`-shell-escape` for examples that use `minted`. Before compiling a `minted`
example, run `mkdir -p _minted` in the output directory; this avoids a
`latexminted` cache-directory issue when TeX finds an unrelated cached style
elsewhere on its search path. Some examples require specific
fonts or optional packages; see the comments in each file. `font-fallback.tex`
is a LuaLaTeX check; `minted.tex` also exercises the LuaTeX-only `chardir`
option. `cite-natbib.tex` and `examples/cite.tex` additionally require
`unipersian` for their default configuration.

Run the column and Tufte checks from the project root with Python 3:

```sh
python3 test/checks/check-columns.py
python3 test/checks/check-tufte.py
```

The Tufte check compiles `tufte-notes.tex` twice for each of `biditufte-handout`
and `biditufte-book`, with XeLaTeX and LuaLaTeX in a temporary
folder and checks RTL paragraph alignment and note targets using Poppler's
`pdftotext` and `pdfinfo`. Installing `pypdf` also enables checks of the actual
PDF link annotations; without it the script reports that those checks were
skipped. The Tufte example defaults to `biditufte-handout`; its source describes
how to select `biditufte-book`. The column check uses Poppler `pdftotext` to
compare physical positions across load orders and scoped direction changes.

Write generated PDFs and auxiliary files to a temporary directory.

Compile `test/checks/aliases.tex` with both XeLaTeX and LuaLaTeX. It checks the handling
of pre-existing direction aliases.

## Expected failures

`expected-failures/dblfnote-patch.tex` is a XeLaTeX-only negative test.
It deliberately makes both `dblfnote` compatibility patches fail.

The expected result is a nonzero exit status and exactly two
`Package babelbidi Error` diagnostics:

- `Could not patch \RTLdfnmakecol`
- `Could not patch \LTRdfnmakecol`

A successful compilation, a missing expected diagnostic, or an unrelated
additional error indicates a failed test. Do not treat its nonzero exit
status as an ordinary compilation failure.
