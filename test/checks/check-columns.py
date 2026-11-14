#!/usr/bin/env python3
"""Check multicol and dblfnote load order, direction, and grouping.

Requires XeLaTeX, LuaLaTeX and Poppler's pdftotext. All files go to /tmp.
"""
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[2]
source = root / "test/checks/columns.tex"
env = os.environ.copy()
env["TEXINPUTS"] = ".:" + str(root) + ":" + env.get("TEXINPUTS", "")
ns = "{http://www.w3.org/1999/xhtml}"

with tempfile.TemporaryDirectory(prefix="babelbidi-columns-", dir="/tmp") as tmp:
    for engine in ("xelatex", "lualatex"):
        for order in ("late", "first"):
            for prior in (("none", "RTL", "LTR") if engine == "lualatex" else ("none",)):
                directory = Path(tmp) / (engine + "-" + order + "-" + prior)
                directory.mkdir()
                flags = (r"\def\PackagesFirst{}" if order == "first" else "")
                if prior != "none":
                    flags += r"\def\Predefined" + prior + "{}"
                document = flags + r"\input{" + str(source) + "}"
                subprocess.run([engine, "-interaction=nonstopmode", "-halt-on-error",
                                document], cwd=directory, env=env, check=True,
                               stdout=subprocess.DEVNULL)
                bbox = subprocess.check_output(
                    ["pdftotext", "-bbox", str(directory / "columns.pdf"), "-"], text=True)
                words = {}
                for word in ET.fromstring(bbox).iter(ns + "word"):
                    text = "".join(word.itertext()).rstrip(".")
                    if text.startswith(("MLEFT", "MRIGHT", "FLEFT", "FRIGHT", "FRESTORE")):
                        assert text not in words, (engine, order, prior, text)
                        words[text] = float(word.attrib["xMin"])
                expected = [("FLEFTFIRST", "FRIGHTSECOND"),
                            ("FLEFTSECOND", "FRIGHTFIRST"),
                            ("FRESTOREFIRST", "FRESTORESECOND")]
                if prior != "RTL":
                    expected.append(("MLEFTSECOND", "MRIGHTFIRST"))
                if prior != "LTR":
                    expected.append(("MLEFTFIRST", "MRIGHTSECOND"))
                for left, right in expected:
                    assert left in words and right in words and words[left] < words[right], (
                        engine, order, prior, left, right, words)
                print(engine, order, prior + ": column order and scoped restore OK")
