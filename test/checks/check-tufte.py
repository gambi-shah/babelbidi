#!/usr/bin/env python3
"""Check Tufte notes with XeLaTeX and LuaLaTeX.

Requires Poppler's pdfinfo and pdftotext. If pypdf is installed, also check
actual PDF link annotations; otherwise report that this check was skipped.
"""
import os
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

root = Path(__file__).resolve().parent.parent.parent
source = root / "test/checks/tufte-notes.tex"
env = os.environ.copy()
env["TEXINPUTS"] = ".:" + str(root) + ":" + env.get("TEXINPUTS", "")
ns = "{http://www.w3.org/1999/xhtml}"

with tempfile.TemporaryDirectory(prefix="babelbidi-tufte-", dir="/tmp") as tmp:
    for engine in ("xelatex", "lualatex"):
        for variant in ("handout", "book"):
            directory = Path(tmp) / (engine + "-" + variant)
            directory.mkdir()
            document = str(source) if variant == "handout" else (
                r"\def\UseTufteBook{}\input{" + str(source) + "}")
            for _ in range(2):
                subprocess.run([engine, "-interaction=nonstopmode", "-halt-on-error",
                                document], cwd=directory, env=env, check=True,
                               stdout=subprocess.DEVNULL)
            base = directory / source.stem
            pdf = base.with_suffix(".pdf")
            aux = base.with_suffix(".aux").read_text()
            targets = {}
            for label in ("section:notes", "after:note", "note:rtl", "note:ltr"):
                match = re.search(r"\\newlabel\{" + label + r"\}\{.*\{(section\*\.\d+)\}\{\}\}", aux)
                assert match, (engine, label)
                targets[label] = match.group(1)
            assert targets["section:notes"] == targets["after:note"]
            assert len({targets["section:notes"], targets["note:rtl"], targets["note:ltr"]}) == 3
            dests = subprocess.check_output(["pdfinfo", "-dests", str(pdf)], text=True)
            for label in ("note:rtl", "note:ltr"):
                match = re.search(r'\[ XYZ\s+([\d.]+)\s+([\d.]+)\s+null\s+\]\s+"' + re.escape(targets[label]) + '"', dests)
                assert match and float(match.group(1)) > 350, (engine, label, dests)

            bbox = subprocess.check_output(["pdftotext", "-bbox", str(pdf), "-"], text=True)
            words = list(ET.fromstring(bbox).iter(ns + "word"))
            def text(word):
                return "".join(word.itertext())
            def coord(word, name):
                return float(word.attrib[name])

            if PdfReader is not None:
                reader = PdfReader(str(pdf))
                links = []
                for page in reader.pages:
                    height = float(page.mediabox.height)
                    for ref in page.get("/Annots", []):
                        annot = ref.get_object()
                        if annot.get("/Subtype") == "/Link":
                            action = annot.get("/A", {})
                            if action.get("/S") == "/GoTo":
                                links.append((str(action.get("/D")),
                                              [float(x) for x in annot["/Rect"]], height))
                for label, number in (("note:rtl", "8"), ("note:ltr", "9")):
                    matches = [(rect, height) for dest, rect, height in links
                               if dest == targets[label]]
                    assert len(matches) == 1, (engine, label, links)
                    rect, height = matches[0]
                    # The annotation must cover the actual reference number in the
                    # main text, not merely be another link to the same target.
                    refs = [w for w in words if text(w).startswith(number)
                            and coord(w, "xMin") < 300
                            and rect[0] - 1 <= coord(w, "xMin") <= rect[2] + 1
                            and height - rect[3] - 2 <= coord(w, "yMin") <= height - rect[1] + 2]
                    assert len(refs) == 1, (engine, label, rect, refs)
                print(engine + " " + variant + ": both PDF link annotations target their own notes")
            else:
                print(engine + " " + variant + ": PDF annotation check skipped (pypdf not installed)")

            # Unique, inline LTR markers delimit the beginning of each RTL
            # paragraph. Their positions are compared within each PDF, not between
            # engines, and the first note's mark may add a small indentation.
            markers = []
            for name in ("PARAONE", "PARATWO", "PARATHREE"):
                matches = [w for w in words if text(w) == name]
                assert len(matches) == 1, (engine, name, len(matches))
                markers.append(matches[0])
            ltr = [w for w in words if text(w) == "First" and coord(w, "xMin") > 350]
            assert len(ltr) == 1, (engine, "LTR note not found")
            ys = [coord(w, "yMin") for w in markers]
            assert ys[0] < ys[1] < ys[2] < coord(ltr[0], "yMin"), (engine, ys)
            right_edges = [coord(w, "xMax") for w in markers]
            assert min(coord(w, "xMin") for w in markers) > 400, (engine, right_edges)
            assert max(right_edges) - min(right_edges) < 9, (engine, right_edges)
            for marker in markers:
                # The Arabic text must occur on the same line, to the left of its
                # paragraph marker and inside the RTL note, excluding page text.
                same_line = [w for w in words if 400 < coord(w, "xMin")
                             and coord(w, "xMax") <= coord(marker, "xMin") + 1
                             and abs(coord(w, "yMin") - coord(marker, "yMin")) < 2
                             and any(ord(c) > 127 for c in text(w))]
                assert same_line, (engine, text(marker), "Arabic text missing or misdirected")
            print(engine + " " + variant + ": all three RTL paragraphs and independent destinations OK")
