"""Generate IMPK monogram logo (Interlude Media Partner Kreatif) as SVG, in the
style of the Interlude Entertainment 'IE' mark: engraved gold serif monogram
with a sweeping swash tail."""
import math, os, sys
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

FONT_DIR = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

def load(name, wght):
    f = TTFont(os.path.join(FONT_DIR, name))
    return instancer.instantiateVariableFont(f, {"wght": wght})

serif = load("playfair.ttf", 560)
sans = load("jost.ttf", 400)

def glyph(font, ch):
    gs = font.getGlyphSet()
    name = font.getBestCmap()[ord(ch)]
    g = gs[name]
    pen = SVGPathPen(gs); g.draw(pen)
    bp = BoundsPen(gs); g.draw(bp)
    return pen.getCommands(), bp.bounds, g.width

CAP = 708  # Playfair cap height (units)

def place(font, ch, x, baseline, cap_px, cap_units=CAP, sx=1.0):
    """Return (svg <path>, bbox in px) with glyph's left ink edge at x."""
    d, (x0, y0, x1, y1), adv = glyph(font, ch)
    s = cap_px / cap_units
    tx = x - x0 * s * sx
    el = f'<path transform="translate({tx:.2f} {baseline:.2f}) scale({s*sx:.5f} {-s:.5f})" d="{d}"/>'
    return el, (x, baseline - y1 * s, x + (x1 - x0) * s * sx, baseline - y0 * s)

def swash(p0, p1, p2, p3, wmax, n=80, taper_start=0.5):
    """Filled tapered stroke along a cubic bezier."""
    def pt(t):
        u = 1 - t
        return [u**3*a + 3*u*u*t*b + 3*u*t*t*c + t**3*d for a, b, c, d in zip(p0, p1, p2, p3)]
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        x, y = pt(t)
        x2, y2 = pt(min(1, t + 1e-3)); x1, y1 = pt(max(0, t - 1e-3))
        dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        # thick early, long thin tail
        w = wmax * (math.sin(math.pi * min(1, t / taper_start) / 2) if t < taper_start else (1 - (t - taper_start) / (1 - taper_start)) ** 1.4)
        w = max(w, 0.6)
        left.append((x + nx * w / 2, y + ny * w / 2)); right.append((x - nx * w / 2, y - ny * w / 2))
    pts = left + right[::-1]
    return '<path d="M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts) + ' Z"/>'

# ---------- monogram layout (px) ----------
TOP = 40
H = 1000                       # tall I cap height
ROW = 455                      # small letters cap height
GAP = H - 2 * ROW              # vertical gap between rows

parts = []
I_el, I_bb = place(serif, "I", 40, TOP + H, H, sx=0.58)
parts.append(I_el)
xL = I_bb[2] - 38              # right column starts overlapping the I
M_el, M_bb = place(serif, "M", xL, TOP + ROW, ROW)
P_el, P_bb = place(serif, "P", xL + 10, TOP + H, ROW)
K_el, K_bb = place(serif, "K", P_bb[2] - 18, TOP + H, ROW)
parts += [M_el, P_el, K_el]
# thin rule echoing the IE mark's bar, tucked between the two rows
rule_y = TOP + ROW + GAP / 2
right_edge = max(M_bb[2], K_bb[2])
parts.append(f'<rect x="{xL + 30:.1f}" y="{rule_y - 5:.1f}" width="{right_edge - xL - 30:.1f}" height="10"/>')

# swashes from the base of the I sweeping right under P and K
bx = I_bb[0] + (I_bb[2] - I_bb[0]) * 0.55
by = TOP + H + 6
end_x = right_edge + 40
parts.append(swash((bx, by - 10), (bx + 120, by + 170), (end_x - 260, by - 30), (end_x, by + 240), 62))
parts.append(swash((bx + 60, by + 50), (bx + 240, by + 210), (end_x - 200, by + 60), (end_x - 70, by + 270), 24))

W = int(end_x + 60)
HT = int(by + 290)

def defs(tone):
    if tone == "gold":
        stops = [("0", "#F1D9A0"), ("0.35", "#D4B06A"), ("0.7", "#C9A35C"), ("1", "#8C6A2C")]
        hatch = "#5a4012"
    else:  # dark gold for light backgrounds
        stops = [("0", "#A9823A"), ("0.4", "#8A6824"), ("0.75", "#7E5E1B"), ("1", "#5A4210")]
        hatch = "#2e2006"
    st = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'''<defs>
<linearGradient id="g" x1="0" y1="0" x2="0.35" y2="1">{st}</linearGradient>
<pattern id="h" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(35)">
<line x1="0" y1="0" x2="0" y2="5" stroke="{hatch}" stroke-width="1.4" stroke-opacity=".55"/></pattern>
<pattern id="h2" width="11" height="11" patternUnits="userSpaceOnUse" patternTransform="rotate(-50)">
<line x1="0" y1="0" x2="0" y2="11" stroke="#fff" stroke-width="1.2" stroke-opacity=".22"/></pattern>
<clipPath id="c">{''.join(parts)}</clipPath>
</defs>'''

def mark_group(tone):
    stroke = "#6e5320" if tone == "gold" else "#3d2c08"
    return f'''<g fill="url(#g)" stroke="{stroke}" stroke-width="3" stroke-opacity=".55">{''.join(parts)}</g>
<g clip-path="url(#c)"><rect width="{W}" height="{HT}" fill="url(#h)"/><rect width="{W}" height="{HT}" fill="url(#h2)"/></g>'''

def text_paths(font, s, x_center, baseline, size_px, tracking, units_per_em=1000):
    sc = size_px / units_per_em
    gs = font.getGlyphSet(); cmap = font.getBestCmap()
    items, x = [], 0
    for ch in s:
        if ch == " ":
            x += gs[cmap[32]].width * sc + tracking; continue
        g = gs[cmap[ord(ch)]]
        pen = SVGPathPen(gs); g.draw(pen)
        items.append((x, pen.getCommands())); x += g.width * sc + tracking
    total = x - tracking
    x0 = x_center - total / 2
    return "".join(f'<path transform="translate({x0 + dx:.2f} {baseline:.2f}) scale({sc:.5f} {-sc:.5f})" d="{d}"/>' for dx, d in items), total

def write(name, tone, lockup=False):
    if not lockup:
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {HT}" width="{W}" height="{HT}">{defs(tone)}{mark_group(tone)}</svg>'
    else:
        txt_col = "#C9A35C" if tone == "gold" else "#7E5E1B"
        sub_col = "#BDBDBD" if tone == "gold" else "#555555"
        cx = W / 2
        t1, w1 = text_paths(serif, "INTERLUDE MEDIA", cx, HT + 150, 120, 22)
        t2, w2 = text_paths(sans, "PARTNER KREATIF", cx, HT + 250, 54, 30)
        LW = int(max(W, w1, w2) + 120)
        off = (LW - W) / 2
        t1, _ = text_paths(serif, "INTERLUDE MEDIA", LW / 2, HT + 150, 120, 22)
        t2, _ = text_paths(sans, "PARTNER KREATIF", LW / 2, HT + 250, 54, 30)
        ln = f'<rect x="{LW/2 - w2/2 - 160:.0f}" y="{HT + 229}" width="120" height="3" fill="{txt_col}"/><rect x="{LW/2 + w2/2 + 40:.0f}" y="{HT + 229}" width="120" height="3" fill="{txt_col}"/>'
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LW} {HT + 300}" width="{LW}" height="{HT + 300}">{defs(tone)}'
               f'<g transform="translate({off:.1f} 0)">{mark_group(tone)}</g>'
               f'<g fill="{txt_col}">{t1}</g><g fill="{sub_col}">{t2}</g>{ln}</svg>')
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", name)

write("impk-gold.svg", "gold")
write("impk-dark.svg", "dark")
write("impk-lockup-gold.svg", "gold", lockup=True)
write("impk-lockup-dark.svg", "dark", lockup=True)
