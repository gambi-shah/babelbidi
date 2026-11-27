#!/usr/bin/env python3
"""Check tabulary layout and package load order with both Unicode engines."""
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[2]
source = root / "test/checks/tabulary.tex"
env = os.environ.copy()
env["TEXINPUTS"] = ".:" + str(root) + ":" + env.get("TEXINPUTS", "")
namespace = "{http://www.w3.org/1999/xhtml}"

with tempfile.TemporaryDirectory(prefix="babelbidi-tabulary-", dir="/tmp") as tmp:
    for engine in ("xelatex", "lualatex"):
        for order in ("first", "after"):
            directory = Path(tmp) / (engine + "-" + order)
            directory.mkdir()
            flags = r"\def\PackagesFirst{}" if order == "first" else ""
            document = flags + r"\input{" + str(source) + "}"
            subprocess.run([engine, "-interaction=nonstopmode", "-halt-on-error",
                            document], cwd=directory, env=env, check=True,
                           stdout=subprocess.DEVNULL)
            log = (directory / "tabulary.log").read_text(errors="replace")
            assert "No suitable columns" not in log, (engine, order)
            assert "Could not patch tabulary" not in log, (engine, order)
            if engine == "xelatex":
                assert "TABULARY PATCH VERIFIED" in log, (engine, order)
            bbox = subprocess.check_output(
                ["pdftotext", "-bbox", str(directory / "tabulary.pdf"), "-"], text=True)
            words = {}
            for word in ET.fromstring(bbox).iter(namespace + "word"):
                text = "".join(word.itertext())
                if text in {"RFIRST", "RSECOND", "TFIRST", "TSECOND", "LFIRST", "LSECOND"}:
                    assert text not in words, (engine, order, text)
                    words[text] = (float(word.attrib["xMin"]), float(word.attrib["yMin"]))
            for left, right in (("RSECOND", "RFIRST"), ("TSECOND", "TFIRST"),
                                ("LFIRST", "LSECOND")):
                assert left in words and right in words, (engine, order, words)
                assert words[left][0] < words[right][0], (engine, order, words)
                assert abs(words[left][1] - words[right][1]) < 1, (engine, order, words)
            print(engine, order + ": RTL, LTR and ordinary tables OK")
