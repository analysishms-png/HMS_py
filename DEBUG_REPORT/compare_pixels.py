# -*- coding: utf-8 -*-
"""VB6 vs Python(HMS_py) side-by-side pixel comparison report generator.

Pairs VB6 screenshots (HMS_Manuals) with Python offscreen widget grabs,
computes region-level color metrics + perceptual diff, builds composite
images and a Markdown report. No external deps beyond Pillow + stdlib.
"""
from __future__ import annotations

import os
import sys
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

VB_ROOT = r"C:/Users/PC/Documents/New folder (2)/HMS_Manuals"
PY_ROOT = r"C:/Users/PC/Desktop/New folder (3)/MODULE_FIX_PLANS/FODER/PYTHONE"
OUT_DIR = os.path.join(PY_ROOT, "DEBUG_REPORT", "PIXEL_COMPARE")
SHOTS = os.path.join(PY_ROOT, "DEBUG_REPORT", "shots")

# VB6 classic palette anchors (from moondata/frm evidence)
VB_ANCHORS = {
    "dialog_gray":   (212, 208, 200),   # &HD4D0C8
    "navy":          (0, 0, 128),       # &H800000& on-title / accent
    "green":         (0, 128, 0),       # #008000
    "maroon":        (128, 0, 0),       # #800000
    "mint":          (194, 224, 206),   # &HCEE0C2 login dialog
    "bevel_light":   (255, 255, 255),
    "bevel_dark":    (128, 128, 128),
}

def _load_rgb(path):
    return Image.open(path).convert("RGB")

def _resize_to(im, size):
    return im.resize(size, Image.LANCZOS)

def _count_near(img_rgb, target, tol=18):
    """Fraction of pixels within tol of target RGB."""
    w, h = img_rgb.size
    px = img_rgb.load()
    tr, tg, tb = target
    hit = 0
    total = w * h
    step = 1
    # sample grid for speed on big images
    if total > 400_000:
        step = 2
    hits = 0
    counted = 0
    for y in range(0, h, step):
        for x in range(0, w, step):
            r, g, b = px[x, y]
            counted += 1
            if abs(r - tr) <= tol and abs(g - tg) <= tol and abs(b - tb) <= tol:
                hits += 1
    return hits / max(counted, 1)

def _dominant_colors(img_rgb, k=6):
    im = img_rgb.copy()
    im.thumbnail((160, 160))
    cnt = Counter(im.getdata())
    return cnt.most_common(k)

def _hexc(rgb):
    return "#%02x%02x%02x" % rgb

def _mean_rgb(img):
    im = img.copy()
    im.thumbnail((200, 200))
    px = list(im.getdata())
    n = len(px)
    r = sum(p[0] for p in px) / n
    g = sum(p[1] for p in px) / n
    b = sum(p[2] for p in px) / n
    return (r, g, b)

def _aabb_diff(a, b, size=(320, 240)):
    """Mean abs per-channel diff on normalized thumbnails (0..255)."""
    a2 = _resize_to(_load_rgb(a), size)
    b2 = _resize_to(_load_rgb(b), size)
    pa, pb = list(a2.getdata()), list(b2.getdata())
    n = min(len(pa), len(pb))
    tot = 0
    for i in range(0, n, 3):  # sample every 3rd pixel
        ra, ga, ba = pa[i]
        rb, gb, bb = pb[i]
        tot += abs(ra - rb) + abs(ga - gb) + abs(ba - bb)
    return tot / (n * 3) if n else 255.0

def _sample_region(img, fx, fy, fw, fh):
    w, h = img.size
    box = (int(w * fx), int(h * fy),
           int(w * (fx + fw)), int(h * (fy + fh)))
    return img.crop(box)

def _nearest_anchor_dist(rgb):
    best = None
    for name, t in VB_ANCHORS.items():
        d = sum(abs(a - b) for a, b in zip(rgb, t)) / 3
        if best is None or d < best[1]:
            best = (name, d)
    return best

def make_pair_report(vb_path, py_path, title, vb_crop=None, py_crop=None):
    vb = _load_rgb(vb_path)
    py = _load_rgb(py_path)
    if vb_crop:
        vb = _sample_region(vb, *vb_crop)
    if py_crop:
        py = _sample_region(py, *py_crop)

    # ---- metrics
    rows = []
    rows.append(("Canvas size (orig)", "%dx%d" % vb.size, "%dx%d" % py.size))
    rows.append(("Mean RGB", _hexc(tuple(int(v) for v in _mean_rgb(vb))),
                 _hexc(tuple(int(v) for v in _mean_rgb(py)))))
    vb_m = _mean_rgb(vb)
    py_m = _mean_rgb(py)
    rows.append(("Nearest VB6 anchor",
                 "%s (%.0f)" % _nearest_anchor_dist(vb_m),
                 "%s (%.0f)" % _nearest_anchor_dist(py_m)))
    for name in ("dialog_gray", "mint", "navy", "green", "maroon"):
        rows.append(("Anchor %%: %s" % name,
                     "%.2f%%" % (100 * _count_near(vb, VB_ANCHORS[name])),
                     "%.2f%%" % (100 * _count_near(py, VB_ANCHORS[name]))))
    d = _aabb_diff(vb_path, py_path)
    verdict = "MATCH" if d < 40 else ("CLOSE" if d < 90 else "DIFFERENT")
    rows.append(("Perceptual diff (0-255)", "%.1f" % d, verdict))

    # ---- composite side-by-side (equal height 400)
    H = 400
    vb2 = _resize_to(vb, (int(vb.width * H / vb.height), H))
    py2 = _resize_to(py, (int(py.width * H / py.height), H))
    gap = 14
    canvas = Image.new("RGB", (vb2.width + py2.width + gap * 3, H + 90),
                       (240, 240, 240))
    dr = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
        fonts = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
        fonts = font
    dr.text((gap, 8), "VB6  |  %s" % title, fill=(20, 20, 20), font=font)
    dr.text((vb2.width + gap * 2, 8), "Python (HMS_py)",
            fill=(20, 20, 20), font=font)
    canvas.paste(vb2, (gap, 40))
    canvas.paste(py2, (vb2.width + gap * 2, 40))
    dr.rectangle([gap, 40, gap + vb2.width - 1, 40 + H - 1],
                 outline=(120, 120, 120))
    dr.rectangle([vb2.width + gap * 2, 40,
                  vb2.width + gap * 2 + py2.width - 1, 40 + H - 1],
                 outline=(120, 120, 120))
    dr.text((gap, H + 52), "diff=%.1f  [%s]" % (d, verdict),
            fill=(180, 30, 30) if verdict == "DIFFERENT" else (30, 140, 30),
            font=fonts)
    out_png = os.path.join(OUT_DIR, title.replace(" ", "_") + "_side_by_side.png")
    canvas.save(out_png)

    # ---- markdown fragment
    md = []
    md.append("### %s" % title)
    md.append("")
    md.append("![side-by-side](%s)" % os.path.basename(out_png))
    md.append("")
    md.append("| Metric | VB6 | Python |")
    md.append("|---|---|---|")
    for name, a, b in rows:
        md.append("| %s | %s | %s |" % (name, a, b))
    md.append("")
    dom_v = ", ".join("%s x%d" % (_hexc(c), n) for c, n in _dominant_colors(vb, 5))
    dom_p = ", ".join("%s x%d" % (_hexc(c), n) for c, n in _dominant_colors(py, 5))
    md.append("- VB6 dominant: %s" % dom_v)
    md.append("- Python dominant: %s" % dom_p)
    md.append("")
    return "\n".join(md), d

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    pairs = [
        # (vb_path_rel, py_path_abs, title, vb_crop, py_crop)
        ("FrontOffice/screenshots/00_Login/01_Login_Page.png",
         os.path.join(SHOTS, "01_login.png"),
         "Login Dialog", (0.25, 0.05, 0.5, 0.9), None),
        ("FrontOffice/screenshots/01_Master/03_Guest_Status.png",
         os.path.join(SHOTS, "04_py_city_master.png"),
         "Master Form (VB6 Guest Status vs PY City)", None, None),
        ("Finance/screenshots/03_Master/01_Group_Accounts.png",
         os.path.join(SHOTS, "05_py_acgroup_master.png"),
         "Group Accounts Master", None, None),
        ("FrontOffice/screenshots/00_Login/01_Login_Page.png",
         os.path.join(SHOTS, "03_mainwindow.png"),
         "App Shell (VB6 MDI vs PY MainWindow)", (0.0, 0.0, 1.0, 0.14), (0.0, 0.0, 1.0, 0.30)),
    ]
    all_md = []
    all_md.append("# VB6 vs Python — Pixel Comparison Report")
    all_md.append("")
    all_md.append("**Date:** 2026-09-24  ")
    all_md.append("**Method:** VB6 screenshots (`HMS_Manuals/*/screenshots`) vs "
                  "Python offscreen widget grabs (`DEBUG_REPORT/shots`). "
                  "Metrics: mean RGB, VB6-palette anchor %, dominant colors, "
                  "perceptual mean-abs diff on normalized thumbnails.")
    all_md.append("")
    verdicts = []
    for vb_rel, py_path, title, vbc, pyc in pairs:
        vb_path = os.path.join(VB_ROOT, vb_rel)
        if not os.path.exists(vb_path):
            all_md.append("### %s\n\nMISSING VB6 shot: %s\n" % (title, vb_rel))
            continue
        if not os.path.exists(py_path):
            all_md.append("### %s\n\nMISSING PY shot: %s\n" % (title, py_path))
            continue
        md, d = make_pair_report(vb_path, py_path, title, vbc, pyc)
        all_md.append(md)
        verdicts.append((title, d))
    all_md.append("## Summary")
    all_md.append("")
    all_md.append("| Pair | Diff | Verdict |")
    all_md.append("|---|---|---|")
    for t, d in verdicts:
        v = "MATCH" if d < 40 else ("CLOSE" if d < 90 else "DIFFERENT")
        all_md.append("| %s | %.1f | %s |" % (t, d, v))
    out_md = os.path.join(OUT_DIR, "PIXEL_COMPARE_REPORT.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(all_md))
    print("report:", out_md)
    for t, d in verdicts:
        print("  %-42s diff=%6.1f" % (t, d))

if __name__ == "__main__":
    main()
