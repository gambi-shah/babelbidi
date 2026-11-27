#!/usr/bin/env python3
"""Compare rendered XeLaTeX output with the installed bidi package.

Requires XeLaTeX and Poppler's pdftoppm. Builds only in /tmp.
"""
import hashlib
import os
from pathlib import Path
import re
import subprocess
import tempfile
from PIL import Image, ImageChops

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

root = Path(__file__).resolve().parents[2]
env = os.environ.copy()
env["TEXINPUTS"] = ".:" + str(root) + ":" + env.get("TEXINPUTS", "")


def run(*args, cwd):
    subprocess.run(args, cwd=cwd, env=env, check=True, stdout=subprocess.DEVNULL)


with tempfile.TemporaryDirectory(prefix="babelbidi-native-", dir="/tmp") as tmp:
    for source, variants in (("bidi-xetex", ("article",)),
                             ("bidi-shared", ("article",)),
                             ("columns", ("first",))):
        for variant in variants:
            outputs = {}
            for mode in ("native", "babelbidi"):
                directory = Path(tmp) / (source + "-" + variant + "-" + mode)
                directory.mkdir()
                flags = (r"\def\UseNativeBidi{}" if mode == "native" else "")
                if variant == "book":
                    flags += r"\def\UseTufteBook{}"
                if variant == "first":
                    flags += r"\def\PackagesFirst{}"
                document = flags + r"\input{" + str(root / "test/checks" / (source + ".tex")) + "}"
                # Two runs are insufficient for some bidi footnote direction labels.
                for _ in range(3):
                    run("xelatex", "-interaction=nonstopmode", "-halt-on-error",
                        document, cwd=directory)
                pdf = directory / (source + ".pdf")
                run("pdftoppm", "-r", "100", "-png", str(pdf), "page", cwd=directory)
                pages = sorted(directory.glob("page-*.png"))
                assert pages, (source, variant, mode, "no rendered pages")
                hashes = [hashlib.sha256(page.read_bytes()).hexdigest() for page in pages]
                labels = {}
                links = []
                if source == "tufte-notes":
                    aux = (directory / (source + ".aux")).read_text()
                    for name in ("section:notes", "after:note", "note:rtl", "note:ltr"):
                        match = re.search(r"\\newlabel\{" + name + r"\}\{(.*)\}", aux)
                        assert match, (mode, name)
                        labels[name] = match.group(1)
                    if PdfReader is not None:
                        for page in PdfReader(str(pdf)).pages:
                            for ref in page.get("/Annots", []):
                                annotation = ref.get_object()
                                action = annotation.get("/A", {})
                                if annotation.get("/Subtype") == "/Link" and action.get("/S") == "/GoTo":
                                    links.append((str(action.get("/D")),
                                                  tuple(round(float(x), 3) for x in annotation["/Rect"])))
                outputs[mode] = (hashes, labels, sorted(links), pages)
            native, actual = outputs["native"], outputs["babelbidi"]
            assert len(native[0]) == len(actual[0]), (source, variant, "page count")
            differences = [i for i, (a, b) in enumerate(zip(native[0], actual[0]), 1) if a != b]
            expected_regions = {
                "bidi-xetex": (6, (.80, .22, .95, .30)),
                "columns": (3, (.20, .78, .82, .81)),
            }
            expected = expected_regions.get(source)
            if expected and differences == [expected[0]]:
                page_number, region = expected
                native_page = Image.open(native[3][page_number - 1]).convert("RGB")
                actual_page = Image.open(actual[3][page_number - 1]).convert("RGB")
                assert native_page.size == actual_page.size
                width, height = native_page.size
                delta = ImageChops.difference(native_page, actual_page)
                left, top, right, bottom = region
                delta.paste((0, 0, 0), (int(width * left), int(height * top),
                                         int(width * right), int(height * bottom)))
                assert delta.getbbox() is None, "unexpected difference outside improved area"
                differences = []
            assert not differences, (source, variant, "different rendered pages", differences)
            assert native[1] == actual[1], (source, variant, "different labels", native[1], actual[1])
            assert native[2] == actual[2], (source, variant, "different link annotations", native[2], actual[2])
            print(f"{source} {variant}: rendered pages, labels and checked links match bidi outside expected improvements")
    if PdfReader is None:
        print("PDF link annotation comparison skipped: pypdf is not installed")
