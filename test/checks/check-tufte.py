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
            for label in ("section:notes", "after:note", "note:rtl", "note:ltr", "note:ltr-foot", "note:rtl-foot"):
                match = re.search(r"\\newlabel\{" + label + r"\}\{.*\{(section\*\.\d+)\}\{\}\}", aux)
                assert match, (engine, label)
                targets[label] = match.group(1)
            assert targets["section:notes"] == targets["after:note"]
            assert len({targets[label] for label in ("section:notes", "note:rtl", "note:ltr", "note:ltr-foot", "note:rtl-foot")}) == 5
            dests = subprocess.check_output(["pdfinfo", "-dests", str(pdf)], text=True)
            for label in ("note:rtl", "note:ltr", "note:ltr-foot", "note:rtl-foot"):
                match = re.search(r'\[ XYZ\s+([\d.]+)\s+([\d.]+)\s+null\s+\]\s+"' + re.escape(targets[label]) + '"', dests)
                assert match, (engine, label, dests)
                x = float(match.group(1))
                if variant == "book" and label.endswith("-foot"):
                    assert x < 225, (engine, label, x)
                else:
                    assert x > 350, (engine, label, x)

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
                    annots = page.get("/Annots", [])
                    if hasattr(annots, "get_object"):
                        annots = annots.get_object()
                    for ref in annots:
                        annot = ref.get_object() if hasattr(ref, "get_object") else ref
                        if annot.get("/Subtype") == "/Link":
                            action = annot.get("/A", {})
                            if hasattr(action, "get_object"):
                                action = action.get_object()
                            if action.get("/S") == "/GoTo":
                                destination = action.get("/D")
                                if hasattr(destination, "get_object"):
                                    destination = destination.get_object()
                                rect = annot["/Rect"]
                                if hasattr(rect, "get_object"):
                                    rect = rect.get_object()
                                links.append((str(destination),
                                              [float(x) for x in rect], height))
                for label, number in (("note:rtl", "8"), ("note:ltr", "9")):
                    matches = [(rect, height) for dest, rect, height in links
                               if dest == targets[label]]
                    # The annotation must cover the actual reference number in the
                    # main text, not merely be another link to the same target.
                    refs = [(w, rect) for rect, height in matches for w in words
                            if text(w).startswith(number) and coord(w, "xMin") < 300
                            and rect[0] - 1 <= coord(w, "xMin") <= rect[2] + 1
                            and height - rect[3] - 2 <= coord(w, "yMin") <= height - rect[1] + 2]
                    assert len(refs) == 1, (engine, label, matches, refs)
                for label in ("note:ltr-foot", "note:rtl-foot"):
                    assert any(dest == targets[label] for dest, rect, _ in links), (engine, label, links)
                print(engine + " " + variant + ": PDF link annotations match note and footnote labels")
            else:
                print(engine + " " + variant + ": PDF annotation check skipped (pypdf not installed)")

            for name in ("LTRFOOTNOTE", "RTLFOOTNOTE"):
                assert any(text(w) == name and (coord(w, "xMin") < 225 if variant == "book" else coord(w, "xMin") > 400) for w in words), (engine, name)

            # Verify that complete note markers survive page clipping inside an
            # RTL environment with RTL policy, for both text directions.
            for name in ("NESTEDNOTE", "NESTEDLTR", "NESTEDRTL"):
                found = [w for w in words if text(w) == name]
                assert len(found) == 1, (engine, variant, name, len(found))
                assert 0 <= coord(found[0], "xMin") < coord(found[0], "xMax") <= 612, (engine, name)

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
            print(engine + " " + variant + ": note placement and reference targets OK")
