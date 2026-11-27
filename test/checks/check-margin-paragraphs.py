#!/usr/bin/env python3
"""Check XeTeX directional notes over multiple paragraphs and both margins."""
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[2]
env = os.environ.copy()
env["TEXINPUTS"] = ".:" + str(root) + ":" + env.get("TEXINPUTS", "")
ns = "{http://www.w3.org/1999/xhtml}"
with tempfile.TemporaryDirectory(prefix="babelbidi-margin-", dir="/tmp") as tmp:
    result = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error",
                             str(root / "test/checks/margin-paragraphs.tex")],
                            cwd=tmp, env=env, text=True, stdout=subprocess.PIPE)
    assert result.returncode == 0, result.stdout
    for direction, primitive in (("R", r"\beginR"), ("L", r"\beginL")):
        for paragraph in range(1, 7):
            assert f"MARGIN-{direction}{paragraph}:" in result.stdout
            line = next(line for line in result.stdout.splitlines()
                        if line.startswith(f"MARGIN-{direction}{paragraph}:"))
            assert primitive in line, line
    assert "Could not adapt" not in result.stdout, result.stdout
    bbox = subprocess.check_output(["pdftotext", "-bbox", str(Path(tmp) /
                                    "margin-paragraphs.pdf"), "-"], text=True)
    pages = list(ET.fromstring(bbox).iter(ns + "page"))
    assert len(pages) == 4
    for index, page in enumerate(pages):
        words = [word for word in page.iter(ns + "word")
                 if float(word.attrib["yMin"]) < 250]
        main = next(word for word in words if "MAIN" in "".join(word.itertext()))
        main_x = float(main.attrib["xMin"])
        note = [word for word in words if (float(word.attrib["xMin"]) > main_x + 150
                if index in (0, 3) else float(word.attrib["xMax"]) < main_x - 10)]
        assert len(note) >= 9, (index, [("".join(w.itertext()), w.attrib) for w in words])
        assert len({round(float(word.attrib["yMin"])) for word in note}) >= 6
        assert all(0 <= float(word.attrib["xMin"]) < float(word.attrib["xMax"])
                   <= float(page.attrib["width"]) for word in note)
    print("XeTeX RTL/LTR notes: three paragraphs, wrapped lines and both margins OK")
