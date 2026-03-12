#!/usr/bin/env python3
"""
Casa Mañana Welcome Book — Final Version
Design system exactly matched to casamananaroatan.com

COLOR SYSTEM (from site CSS variables):
  --hibiscus-pink:  #EC407A
  --seafoam-green:  #3FB9A9
  --charcoal:       #1d1d1f
  --light-bg:       #fbfbfd
  --gray-bg:        #f5f5f7
  --text-gray:      #86868b
  --border-gray:    #d2d2d7

FONT: Poppins (closest available to site's SF Pro Display system-ui)
STYLE: Clean Apple-influenced minimalism — generous white space,
       bold headings, pill badges in pink, teal accent numbers/icons,
       dark charcoal footer sections
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import math, random

# ── REGISTER FONTS ──────────────────────────────────────────────────────────
FP = "/usr/share/fonts/truetype/google-fonts/"
pdfmetrics.registerFont(TTFont("Pop",   FP + "Poppins-Regular.ttf"))
pdfmetrics.registerFont(TTFont("PopB",  FP + "Poppins-Bold.ttf"))
pdfmetrics.registerFont(TTFont("PopM",  FP + "Poppins-Medium.ttf"))
pdfmetrics.registerFont(TTFont("PopL",  FP + "Poppins-Light.ttf"))
pdfmetrics.registerFont(TTFont("PopI",  FP + "Poppins-Italic.ttf"))
pdfmetrics.registerFont(TTFont("PopLI", FP + "Poppins-LightItalic.ttf"))
pdfmetrics.registerFont(TTFont("Lora",  FP + "Lora-Variable.ttf"))
pdfmetrics.registerFont(TTFont("LoraI", FP + "Lora-Italic-Variable.ttf"))

# ── SITE-EXACT PALETTE ──────────────────────────────────────────────────────
PINK        = HexColor("#EC407A")
PINK_SOFT   = HexColor("#FDE8F0")
PINK_MED    = HexColor("#F9B8CF")
TEAL        = HexColor("#3FB9A9")
TEAL_DARK   = HexColor("#2A9082")
TEAL_SOFT   = HexColor("#E6F7F5")
TEAL_MED    = HexColor("#8DD5CE")
CHARCOAL    = HexColor("#1d1d1f")
CHARCOAL2   = HexColor("#2c2c2e")
LIGHT_BG    = HexColor("#fbfbfd")
GRAY_BG     = HexColor("#f5f5f7")
TEXT_GRAY   = HexColor("#86868b")
BORDER      = HexColor("#d2d2d7")
BORDER_SOFT = HexColor("#e8e8ed")
WHITE       = white

W, H  = letter          # 612 × 792 pts  =  8.5 × 11 in
M     = 0.6 * inch      # page margin
CW    = W - 2 * M       # content width  =  7.3 in
OUT   = "/mnt/user-data/outputs/CasaManana_WelcomeBook.pdf"

# ── PRIMITIVE DRAWING ───────────────────────────────────────────────────────

def fill_page(c, col=None):
    c.setFillColor(col or LIGHT_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)

def txt(c, x, y, s, font, size, color=CHARCOAL, align="left"):
    c.setFont(font, size); c.setFillColor(color)
    {"center": c.drawCentredString, "right": c.drawRightString}.get(align, c.drawString)(x, y, s)

def wraptext(c, x, y, s, font, size, color, max_w, lh, align="left"):
    """Word-wrap string; return bottom y. For center/right, x is the anchor point."""
    c.setFont(font, size); c.setFillColor(color)
    words = s.split()
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        if c.stringWidth(test, font, size) <= max_w:
            cur.append(w)
        else:
            if cur: lines.append(" ".join(cur))
            cur = [w]
    if cur: lines.append(" ".join(cur))
    fn = {"center": c.drawCentredString, "right": c.drawRightString}.get(align, c.drawString)
    for line in lines:
        fn(x, y, line); y -= lh
    return y

def hrule(c, x, y, w, col=BORDER, thick=0.5):
    c.setStrokeColor(col); c.setLineWidth(thick); c.line(x, y, x + w, y)

def rbox(c, x, y, w, h, fill, stroke=None, r=8):
    """Rounded rectangle — y is TOP edge."""
    c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke); c.setLineWidth(0.6)
        c.roundRect(x, y - h, w, h, r, fill=1, stroke=1)
    else:
        c.roundRect(x, y - h, w, h, r, fill=1, stroke=0)

def pill(c, x, y, w, h, col=PINK):
    """Pill badge (border-radius: 980px like website)."""
    c.setFillColor(col)
    c.roundRect(x, y - h, w, h, h/2, fill=1, stroke=0)

def accent_bar(c, x, y, h, col=TEAL, w=3.5):
    """Left vertical accent bar."""
    c.setFillColor(col); c.rect(x, y - h, w, h, fill=1, stroke=0)

def teal_underline(c, x, y, text_str, font, size):
    """Draw teal underline under a heading."""
    w = c.stringWidth(text_str, font, size)
    c.setStrokeColor(TEAL); c.setLineWidth(2)
    c.line(x, y - 4, x + w, y - 4)

def footer(c, n=None):
    hrule(c, M, 0.52 * inch, CW, BORDER_SOFT)
    txt(c, W/2, 0.34*inch,
        "Casa Mañana  ·  West Bay, Roatán  ·  casamananaroatan.com",
        "PopL", 7, TEXT_GRAY, "center")
    if n:
        txt(c, W - M, 0.34*inch, str(n), "PopL", 7.5, TEXT_GRAY, "right")

def pill_label(c, x, y, label, bg=PINK_SOFT, fg=PINK):
    """Small pill section label above heading — y is TOP of pill."""
    lw = c.stringWidth(label, "PopM", 7.5) + 20
    # Draw pill: x, bottom-left y, width, height
    c.setFillColor(bg)
    c.roundRect(x, y - 17, lw, 17, 8.5, fill=1, stroke=0)
    txt(c, x + 10, y - 13, label, "PopM", 7.5, fg)
    return y - 26   # return y for next element (heading)

def dark_band(c, y, h, col=CHARCOAL):
    c.setFillColor(col); c.rect(0, y, W, h, fill=1, stroke=0)

def section_header(c, title, subtitle=None,
                   bg=CHARCOAL, title_col=WHITE, sub_col=None, h=None):
    """Full-width header band at top of page."""
    bh = h or (1.05*inch if subtitle else 0.85*inch)
    dark_band(c, H - bh, bh, bg)
    ty = H - bh/2 - 7
    txt(c, M, ty + (10 if subtitle else 0), title, "PopB", 22, title_col)
    if subtitle:
        txt(c, M, ty - 10, subtitle, "PopL", 9, sub_col or TEXT_GRAY)

def two_col(items_left, items_right):
    """Helper to zip two columns with indices."""
    return list(zip(
        [(i, t, b) for i, (t, b) in enumerate(items_left)],
        [(i, t, b) for i, (t, b) in enumerate(items_right)]
    ))

def subhead(c, x, y, label, col=CHARCOAL):
    txt(c, x, y, label, "PopB", 10.5, col)
    teal_underline(c, x, y, label, "PopB", 10.5)
    return y - 18

def dashed_price_row(c, x, y, w, label, price, label_font="Pop", price_font="PopM"):
    txt(c, x, y, label, label_font, 9.2, CHARCOAL)
    txt(c, x + w, y, price, price_font, 9.2, TEAL, "right")
    lw = c.stringWidth(label, label_font, 9.2)
    pw = c.stringWidth(price, price_font, 9.2)
    c.setStrokeColor(BORDER); c.setLineWidth(0.3); c.setDash(1, 4)
    c.line(x + lw + 4, y + 3.5, x + w - pw - 4, y + 3.5)
    c.setDash()
    return y - 15

def restaurant_entry(c, x, y, w, name, detail, lines, hours=None, accent=TEAL):
    """Restaurant listing with left accent bar."""
    total_h = 14 + (12 if detail else 0) + len(lines) * 13 + (12 if hours else 0) + 4
    accent_bar(c, x, y, total_h, accent, 3.5)
    cx = x + 12
    txt(c, cx, y, name, "PopB", 11, CHARCOAL)
    y -= 13
    if detail:
        txt(c, cx, y, detail, "PopI", 8.5, TEXT_GRAY)
        y -= 12
    for line in lines:
        txt(c, cx, y, line, "Pop", 9, CHARCOAL)
        y -= 13
    if hours:
        txt(c, cx, y, hours, "Pop", 7.8, TEXT_GRAY)
        y -= 12
    return y - 10

def check_item(c, x, y, text_str, w, col=TEAL):
    """Checkmark bullet item."""
    c.setFillColor(col)
    c.circle(x + 5.5, y - 2, 5.5, fill=1, stroke=0)
    c.setFont("PopB", 7); c.setFillColor(WHITE)
    c.drawCentredString(x + 5.5, y - 5, "✓")
    return wraptext(c, x + 16, y, text_str, "Pop", 9.5, CHARCOAL, w - 16, 14)


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE BUILDERS
# ═══════════════════════════════════════════════════════════════════════════

# ── 1. COVER ────────────────────────────────────────────────────────────────
def pg_cover(c):
    # Full charcoal background
    fill_page(c, CHARCOAL)

    # Top teal sliver
    c.setFillColor(TEAL); c.rect(0, H - 5, W, 5, fill=1, stroke=0)
    # Bottom pink sliver
    c.setFillColor(PINK); c.rect(0, 0, W, 5, fill=1, stroke=0)

    # Large decorative circles — site aesthetic, very subtle
    c.setFillColor(CHARCOAL2)
    c.circle(W + 0.2*inch, H - 0.5*inch, 3.2*inch, fill=1, stroke=0)
    c.circle(-0.5*inch, 0.8*inch, 2.2*inch, fill=1, stroke=0)

    # Inner lighter circles
    c.setFillColor(HexColor("#252528"))
    c.circle(W + 0.2*inch, H - 0.5*inch, 2.1*inch, fill=1, stroke=0)
    c.circle(-0.5*inch, 0.8*inch, 1.3*inch, fill=1, stroke=0)

    # Vertical pink accent rule — matches site's use of hibiscus pink
    c.setFillColor(PINK)
    c.rect(M - 0.05*inch, H * 0.42, 3.5, H * 0.34, fill=1, stroke=0)

    # Property name — large bold, exactly like site's bold heading style
    cx = M + 0.18*inch
    txt(c, cx, H * 0.70, "CASA", "PopB", 56, WHITE)
    txt(c, cx, H * 0.70 - 52, "MAÑANA", "PopB", 56, WHITE)

    # Teal underline under MAÑANA
    mw = c.stringWidth("MAÑANA", "PopB", 56)
    c.setStrokeColor(TEAL); c.setLineWidth(3)
    c.line(cx, H * 0.70 - 58, cx + mw, H * 0.70 - 58)

    # Location tag
    txt(c, cx, H * 0.70 - 76, "WEST BAY  ·  ROATÁN, HONDURAS", "PopL", 10.5, TEAL_MED)

    # Tagline in italic Lora — elegant contrast
    txt(c, cx, H * 0.70 - 96, "Your Home on the Caribbean", "LoraI", 13, HexColor("#aaaaac"))

    # Welcome Guide pill label
    pw = c.stringWidth("WELCOME GUIDE", "PopB", 8) + 26
    pill(c, cx, H * 0.70 - 116, pw, 20, PINK)
    txt(c, cx + 13, H * 0.70 - 128, "WELCOME GUIDE", "PopB", 8, WHITE)

    # Stats box — dark card, teal numbers (matches site's fact numbers)
    bx, by, bw, bh = M, 1.2*inch, CW, 0.92*inch
    c.setFillColor(HexColor("#252528"))
    c.roundRect(bx, by, bw, bh, 10, fill=1, stroke=0)

    stats = [("8 min", "Walk to Beach"), ("50+", "Mbps Starlink"),
             ("100%", "Private Pool"), ("5.0 ★", "Guest Rating")]
    sw = bw / 4
    for i, (num, lbl) in enumerate(stats):
        scx = bx + i * sw + sw / 2
        txt(c, scx, by + bh - 0.28*inch, num, "PopB", 16, TEAL, "center")
        txt(c, scx, by + bh - 0.5*inch, lbl, "PopL", 7.8, TEXT_GRAY, "center")
        if i < 3:
            c.setStrokeColor(HexColor("#3a3a3c"))
            c.setLineWidth(0.5)
            c.line(bx + (i+1)*sw, by + 0.12*inch, bx + (i+1)*sw, by + bh - 0.12*inch)

    txt(c, W/2, 0.82*inch, "Hosted by Josh & Pamela", "PopL", 9, TEXT_GRAY, "center")


# ── 2. WELCOME LETTER ───────────────────────────────────────────────────────
def pg_welcome(c):
    fill_page(c)
    # Top teal accent
    c.setFillColor(TEAL); c.rect(0, H - 4, W, 4, fill=1, stroke=0)

    y = H - 0.68*inch
    y = pill_label(c, M, y, "A NOTE FROM YOUR HOSTS")
    txt(c, M, y, "Welcome.", "PopB", 36, CHARCOAL)
    y -= 8
    hrule(c, M, y, 0.5*inch, PINK, 3); y -= 18

    paras = [
        ("Hey. We're really glad you're here.", "PopI", TEAL_DARK),
        ("We've been hosting guests at Casa Mañana and we genuinely love it — not in a scripted, five-star-review kind of way. We just love having people in this place. This little corner of Roatán is something we feel lucky to call home, and we hope you feel that within about five minutes of arriving.", "Pop", CHARCOAL),
        ("We live right on-site, Pamela and I. She's the one who actually has everything organized. I'm Josh — a musician, a designer, and the person who plays guitar on Sunday evenings at Sundowner's down the beach. Before settling here in April 2025, we spent seven years living in Mexico, then five years sailing the Caribbean on a catamaran. We've been away from the United States since 2017, and we've never looked back.", "Pop", CHARCOAL),
        ("This guide covers everything: the house, the neighborhood, where to eat, what to do, what not to do, and a few things you probably didn't think to ask. Flip to what you need.", "Pop", CHARCOAL),
        ("The island tends to take care of people. Let it.", "PopI", TEAL_DARK),
    ]
    for para, font, col in paras:
        y = wraptext(c, M, y, para, font, 9.8, col, CW, 15); y -= 10

    y -= 2
    txt(c, M, y, "— Josh & Pamela", "LoraI", 14, CHARCOAL); y -= 16
    txt(c, M, y, "Casa Mañana, West Bay, Roatán", "PopL", 8.5, TEXT_GRAY)

    # Charley card
    y -= 32
    card_h = 82
    rbox(c, M, y, CW, card_h, GRAY_BG, r=12)
    accent_bar(c, M, y, card_h, PINK)
    txt(c, M + 16, y - 15, "A QUICK NOTE ABOUT CHARLEY", "PopB", 8.5, CHARCOAL)
    wraptext(c, M + 16, y - 30,
        "Charley is our cat — he was here before us and he'll probably outlast us both. "
        "He lives in the garden and will almost certainly come say hello, especially if "
        "you're eating something good. He's friendly, harmless, and absolutely world-class "
        "at looking like he hasn't eaten in days. He has. Please don't feed him. "
        "He has a whole thing going on.",
        "Pop", 9, TEXT_GRAY, CW - 26, 13.5)
    footer(c, 2)


# ── 3. YOUR FIRST DAY ───────────────────────────────────────────────────────
def pg_first_day(c):
    fill_page(c)
    section_header(c, "Your First Day",
                   "If you need a plan — and most people do — here's ours.",
                   bg=TEAL, sub_col=HexColor("#C0E8E4"))
    y = H - 1.12*inch

    steps = [
        ("2:00 PM", "Arrive & Decompress",
         "Drop your bags. Change into something lighter than whatever you flew in. "
         "Do a lap around the property. Jump in the pool. "
         "Let the island catch up to you. You don't need to do anything yet."),
        ("4:00 PM", "Walk to the Beach",
         "It's 8 minutes. Gentle decline on the way, small hill back — nothing major. "
         "Take the walk slowly. When you get to the beach, "
         "you'll know you made the right call booking this trip."),
        ("4:30 PM", "Happy Hour at Beachers",
         "Pull up a chair right on the sand. Order the lobster tails and something cold. "
         "Yes, on your first afternoon. Three tails for around $20. "
         "It sets the tone properly."),
        ("6:00 PM", "Catch the Sunset",
         "Walk toward the western end of the beach. Or head to Sundowner's — "
         "best sunset view on the island. Get there by 5:30. Good seats go fast."),
        ("8:00 PM", "Call It a Night",
         "You've been traveling. Go back to the house, sit on the porch. "
         "The stars might be out. The pool lights look great at night. "
         "Tomorrow you hit the ground running. Tonight, just land."),
    ]

    for i, (time_s, title, body) in enumerate(steps):
        if i > 0:
            c.setStrokeColor(BORDER_SOFT); c.setLineWidth(0.8); c.setDash(2, 4)
            c.line(M + 28, y + 2, M + 28, y + 16); c.setDash()

        # Time pill — fixed width, stays within margin
        pw = 72  # fixed pill width
        pill(c, M, y - 16, pw, 17, TEAL)
        txt(c, M + pw/2, y - 11, time_s, "PopB", 7.5, WHITE, "center")
        # Title on same line, after pill
        txt(c, M + pw + 10, y - 4, title, "PopB", 10.5, CHARCOAL)
        y -= 20
        # Body indented to align with title
        y = wraptext(c, M + pw + 10, y, body, "Pop", 9, TEXT_GRAY, CW - pw - 10, 13.5)
        y -= 10

    y -= 6
    rbox(c, M, y, CW, 28, GRAY_BG, r=8)
    txt(c, W/2, y - 18, "Arriving late? Completely fine. The island will still be here in the morning. It's good at that.",
        "PopI", 8.8, TEXT_GRAY, "center")
    footer(c, 3)


# ── 4. THE HOUSE ────────────────────────────────────────────────────────────
def pg_house(c):
    fill_page(c)
    c.setFillColor(TEAL); c.rect(0, H - 4, W, 4, fill=1, stroke=0)
    y = H - 0.68*inch
    y = pill_label(c, M, y, "YOUR HOME")
    txt(c, M, y, "The House", "PopB", 30, CHARCOAL); y -= 10
    hrule(c, M, y, CW, BORDER_SOFT); y -= 16

    # Info strip — 4 quick facts like site's stat row
    labels = ["Check-In", "Check-Out", "Entry", "Parking"]
    vals   = ["3:00 – 9:00 PM", "Before 11:00 AM", "Smart Lock", "Free · On-Site"]
    iw = CW / 4
    for i, (lb, vl) in enumerate(zip(labels, vals)):
        ix = M + i * iw + 5
        txt(c, ix, y, lb, "Pop", 7.5, TEXT_GRAY)
        txt(c, ix, y - 14, vl, "PopM", 9.3, CHARCOAL)
        if i < 3:
            c.setStrokeColor(BORDER_SOFT); c.setLineWidth(0.5)
            c.line(M + (i+1)*iw, y - 22, M + (i+1)*iw, y + 3)
    y -= 36
    hrule(c, M, y, CW, BORDER_SOFT); y -= 12
    y = wraptext(c, M, y,
        "We use a smart lock — no key to lose, no one to wait for. "
        "Your code arrives a few days before check-in. "
        "Early check-in or late checkout? Just ask — we'll always do our best.",
        "Pop", 9.3, TEXT_GRAY, CW, 14); y -= 16

    col = (CW - 16) / 2
    lx, rx = M, M + col + 16

    def sec(x, y_cur, head, body_str, cw):
        y_cur = subhead(c, x, y_cur, head)
        y_cur = wraptext(c, x, y_cur, body_str, "Pop", 9, TEXT_GRAY, cw, 13.5)
        return y_cur - 12

    y_l = y
    y_l = sec(lx, y_l, "The Pool",
        "100% private — solar-heated, cleaned regularly. "
        "Please rinse at the outdoor shower (top of the steps, corner of the house) "
        "before getting in, and keep glass out of the pool area. "
        "Turn the pool lights on at night. Seriously — guests always wish they had.", col)

    y_l = sec(lx, y_l, "The Kitchen",
        "Fully stocked for real cooking: stove, oven, full-size fridge, coffee maker, "
        "blender, and pantry basics to get you started.", col)

    y_l = sec(lx, y_l, "Towels",
        "Black makeup towels for makeup removal. Old towels under the sink for big messes. "
        "The beautiful white towels are for drying off — we trust you with this.", col)

    y_r = y
    # WiFi — styled like site's feature list
    y_r = subhead(c, rx, y_r, "WiFi & Tech")
    wifi = [("Network", "CasaManana"),
            ("Password", "Westbaybeach123"),
            ("Speed", "50+ Mbps · Starlink"),
            ("Smart TV", "Use your own logins")]
    for lb, vl in wifi:
        txt(c, rx, y_r, lb + ":", "PopM", 8.8, CHARCOAL)
        txt(c, rx + c.stringWidth(lb + ":  ", "PopM", 8.8), y_r, vl, "Pop", 8.8, TEXT_GRAY)
        y_r -= 13
    y_r -= 8

    y_r = sec(rx, y_r, "Climate",
        "Bedroom and living area have AC. The covered porch is open-air with great airflow. "
        "Ceiling fans throughout. Light clothes, AC when you want it.", col)

    y_r = sec(rx, y_r, "Security Cameras",
        "Exterior cameras in the backyard pool area, monitored for safety only. "
        "No cameras inside the guesthouse.", col)

    footer(c, 4)


# ── 5. HOUSE RULES ──────────────────────────────────────────────────────────
def pg_rules(c):
    fill_page(c)
    section_header(c, "House Rules",
                   "Short, honest, and not gotchas — just good-neighbor stuff.",
                   bg=PINK, sub_col=HexColor("#F9C0D3"))
    y = H - 1.12*inch
    col = (CW - 16) / 2
    lx, rx = M, M + col + 16

    rules = [
        ("Maximum 2 guests.",
         "The space is designed for couples and solo travelers. "
         "Please don't bring additional guests without checking with us first."),
        ("No smoking inside.",
         "The covered porch and garden are fine. "
         "We'll leave an ashtray out if you need one."),
        ("No glass in the pool area.",
         "Plastic or canned drinks poolside only."),
        ("Rinse before swimming.",
         "Outdoor shower is at the top of the steps on the corner of the house. "
         "Keeps the water clean for everyone."),
        ("Respect the neighbors.",
         "Music and gatherings are fine — just keep it reasonable after 10 PM."),
        ("Treat it like a friend's home.",
         "We trust our guests, and that trust goes a long way."),
        ("Tell us if something breaks.",
         "We'd much rather fix it than find out at checkout."),
        ("Checkout is 11 AM.",
         "Dishes washed, trash bagged, towels in the bathroom. No need to strip the bed."),
        ("Smart TV.",
         "Plug in your own streaming accounts — Netflix, Hulu, etc. are not provided."),
    ]

    y_l = y_r = y
    for i, (bold, body) in enumerate(rules):
        tx = lx if i % 2 == 0 else rx
        ty = y_l if i % 2 == 0 else y_r

        # Teal numbered circle
        c.setFillColor(TEAL); c.circle(tx + 8, ty - 5, 8, fill=1, stroke=0)
        txt(c, tx + 8, ty - 8.5, str(i+1), "PopB", 7.5, WHITE, "center")
        txt(c, tx + 21, ty, bold, "PopB", 9.2, CHARCOAL)
        ny = wraptext(c, tx + 21, ty - 13, body, "Pop", 8.8, TEXT_GRAY, col - 21, 13)
        ny -= 10
        if i % 2 == 0: y_l = ny
        else: y_r = ny

    y = min(y_l, y_r) - 6

    # Toilet paper — pink warning card
    th = 90
    rbox(c, M, y, CW, th, HexColor("#FEF0F4"), r=10)
    accent_bar(c, M, y, th, PINK, 4)
    txt(c, M + 16, y - 15, "ONE VERY IMPORTANT ISLAND THING — PLEASE READ",
        "PopB", 9.2, PINK)
    wraptext(c, M + 16, y - 31,
        "Please do NOT flush toilet paper. We know. But the sewer system here "
        "works differently — this is true across most of Central America and island destinations. "
        "There's a lined, covered trash can in the bathroom for a reason. It gets emptied. "
        "It takes about one day to get used to. The alternative involves a plumbing situation "
        "nobody wants. You're a traveler. You've absolutely got this.",
        "Pop", 8.9, CHARCOAL, CW - 28, 13.5)
    y -= th + 8

    # Quick reassurance card
    rbox(c, M, y, CW, 32, TEAL_SOFT, r=8)
    txt(c, M + 14, y - 12, "Something not working?  ", "PopB", 9, TEAL_DARK)
    txt(c, M + 14 + c.stringWidth("Something not working?  ", "PopB", 9), y - 12,
        "We live on-site. Just tell us. We won't be upset — we'd just rather know sooner.", "Pop", 9, TEXT_GRAY)
    footer(c, 5)


# ── 6. GETTING AROUND ───────────────────────────────────────────────────────
def pg_getting_around(c):
    fill_page(c)
    c.setFillColor(PINK); c.rect(0, H - 4, W, 4, fill=1, stroke=0)
    y = H - 0.68*inch
    y = pill_label(c, M, y, "TRANSPORTATION")
    txt(c, M, y, "Getting Around", "PopB", 30, CHARCOAL); y -= 10
    txt(c, M, y - 4, "Roatán is small. You can get almost anywhere for under $25.", "Pop", 10, TEXT_GRAY)
    y -= 24; hrule(c, M, y, CW, BORDER_SOFT); y -= 16

    # Beach
    y = subhead(c, M, y, "The Beach")
    y = wraptext(c, M, y,
        "West Bay Beach is an 8-minute walk from the house. "
        "There's a gentle decline on the way — and a small hill back, nothing major. "
        "Walk slowly. The beach is consistently rated one of the best in the Caribbean. "
        "You'll understand why when you get there.",
        "Pop", 9.3, TEXT_GRAY, CW, 14); y -= 16

    col = (CW - 16) / 2
    lx, rx = M, M + col + 16
    y_l = y_r = y

    # LEFT col
    y_l = subhead(c, lx, y_l, "Taxis")
    y_l = wraptext(c, lx, y_l,
        "Always agree on price before getting in — drivers expect it. "
        "Always use an official taxi: white car, yellow number on the side. "
        "Easy to find throughout West Bay, especially near West Bay Mall.",
        "Pop", 9, TEXT_GRAY, col, 13.5); y_l -= 10
    for label, price in [("West Bay to West End", "$5–8 per person"),
                         ("West Bay to Airport", "$20–25"),
                         ("Island tour (half day)", "$75+")]:
        y_l = dashed_price_row(c, lx, y_l, col, label, price)
    y_l -= 8

    y_l = subhead(c, lx, y_l, "Water Taxis")
    y_l = wraptext(c, lx, y_l,
        "Look for the guys near Bananarama or down by Beachers and Roa Market "
        "— there are always people ready to go. "
        "About $10 solo, $15 for 3 or more people. Take it at least once.",
        "Pop", 9, TEXT_GRAY, col, 13.5)

    # RIGHT col
    y_r = subhead(c, rx, y_r, "West Bay vs. West End")
    y_r = wraptext(c, rx, y_r,
        "You're in West Bay: beach-focused and relaxed. "
        "West End is 5 minutes by taxi — more restaurants, galleries, dive shops, nightlife. "
        "The beach path between them is about 30–40 minutes on foot — a great morning walk.",
        "Pop", 9, TEXT_GRAY, col, 13.5); y_r -= 12

    y_r = subhead(c, rx, y_r, "The Airport")
    y_r = wraptext(c, rx, y_r,
        "Roatán International (RTB) is in Coxen Hole, 20–30 minutes from the house. "
        "Need a transfer? Ask us — we work with a reliable driver.",
        "Pop", 9, TEXT_GRAY, col, 13.5); y_r -= 12

    y_r = subhead(c, rx, y_r, "ATMs & Money")
    y_r = wraptext(c, rx, y_r,
        "ATM right in West Bay Mall — 5-minute walk. "
        "BAC and Banco Atlántida are the most reliable. Some dispense USD. "
        "Always pay in Lempiras. Decline dynamic currency conversion on card machines.",
        "Pop", 9, TEXT_GRAY, col, 13.5)

    footer(c, 6)


# ── 7. DON'T MAKE THESE MISTAKES ────────────────────────────────────────────
def pg_mistakes(c):
    fill_page(c, GRAY_BG)
    section_header(c, "Don't Make These Mistakes",
                   "We say this with love. We've watched a lot of guests learn these the hard way.",
                   bg=CHARCOAL)
    y = H - 1.1*inch
    col = (CW - 16) / 2
    lx, rx = M, M + col + 16

    mistakes = [
        ("Forgetting Reef-Safe Sunscreen",
         "Regular sunscreen damages coral and is banned in many reef areas. "
         "Pick some up before you arrive — local shops carry it."),
        ("Agreeing on Taxi Price After Getting In",
         "Always negotiate before you get in — drivers expect it. "
         "Most West Bay / West End rides are $5–8. "
         "Always use an official white taxi with a yellow number."),
        ("Sleeping Through the Morning Snorkel",
         "Water is calmest and clearest before 10 AM. "
         "Afternoon winds pick up. Make snorkeling a morning thing."),
        ("Skipping West End",
         "West Bay is beautiful. But West End is 5 minutes away "
         "and has a completely different energy. Give it at least one evening."),
        ("Ordering Bottled Water at Restaurants",
         "Most places charge a lot for it. Bring a reusable bottle, "
         "refill at the house, save the money for lobster."),
        ("Renting a Car",
         "You don't need one in West Bay. "
         "Everything is a short walk or a cheap taxi. "
         "The island roads have a personality of their own."),
        ("Saving Everything for the Last Night",
         "We've had guests at checkout who never made it to Sandy Buns. "
         "The island is small — start early and you'll fit in more than you'd expect."),
        ("Feeding Charley",
         "He is very good at looking like he hasn't eaten in days. "
         "He has. He has a whole thing going on."),
    ]

    y_l = y_r = y
    for i, (title, body) in enumerate(mistakes):
        tx = lx if i % 2 == 0 else rx
        ty = y_l if i % 2 == 0 else y_r

        # Pink numbered pill
        pw = c.stringWidth(str(i+1), "PopB", 8) + 16
        pill(c, tx, ty - 16, pw, 17, PINK)
        txt(c, tx + pw/2, ty - 12.5, str(i+1), "PopB", 8, WHITE, "center")
        txt(c, tx + pw + 8, ty - 4, title, "PopB", 9.2, CHARCOAL)
        ny = wraptext(c, tx + pw + 8, ty - 17, body, "Pop", 8.8, TEXT_GRAY, col - pw - 8, 13)
        ny -= 10
        if i % 2 == 0: y_l = ny
        else: y_r = ny

    footer(c, 7)


# ── 8. FOOD — WEST BAY ──────────────────────────────────────────────────────
def pg_food_wb(c):
    fill_page(c)
    c.setFillColor(TEAL); c.rect(0, H - 4, W, 4, fill=1, stroke=0)
    y = H - 0.68*inch
    y = pill_label(c, M, y, "FOOD & DRINK")
    txt(c, M, y, "Where to Eat & Drink", "PopB", 30, CHARCOAL); y -= 10
    txt(c, M, y - 4, "We've eaten our way around this island. Here's the honest list.", "Pop", 10, TEXT_GRAY)
    y -= 22; hrule(c, M, y, CW, BORDER_SOFT); y -= 12

    pw = c.stringWidth("IN WEST BAY", "PopB", 8) + 26
    c.setFillColor(CHARCOAL)
    c.roundRect(M, y - 20, pw, 18, 9, fill=1, stroke=0)
    txt(c, M + 13, y - 15, "IN WEST BAY", "PopB", 8, WHITE)
    y -= 32

    y = restaurant_entry(c, M, y, CW, "Beachers Bar & Grill",
        "Right on the beach · Locally owned, 15+ years",
        ["Three grilled lobster tails for around $20 with salad and mashed potatoes.",
         "That is not a typo. Same ocean as the resort restaurants. Better vibe.",
         "Also great: coconut shrimp, whole grilled red snapper."],
        "Happy hour 2–6 PM · Cash & cards", TEAL)

    y = restaurant_entry(c, M, y, CW, "JavaVine Cafe & Wine Bar",
        "West Bay Beach Mall",
        ["Best coffee on the island. Coffee ice cubes so drinks never water down.",
         "Pizza available anytime — don't sleep on it. The 'Rumors' pizza is exceptional.",
         "Also: breakfast sandwiches, smoothies, good WiFi."],
        "Tue–Thu 7:30–5 PM · Fri 7:30–9 PM · Sat–Sun 8–2 PM · Closed Mon", TEAL)

    y = restaurant_entry(c, M, y, CW, "Bananarama / Thirsty Turtle Bar & Grill",
        "West Bay Beach · At Bananarama Dive Resort",
        ["Most energetic spot on the beach. 2-for-1 happy hour 4–6 PM.",
         "Hermit crab races (charity), fire dancers, karaoke, live music. Great fish tacos."],
        "Open daily · Cash & cards", TEAL)

    y = restaurant_entry(c, M, y, CW, "Roa Market",
        "Next door to Beachers",
        ["Best selection in West Bay. Good for anything out of the ordinary.",
         "Prices are a bit higher — but it's right here and very convenient."],
        None, TEAL)

    footer(c, 8)


# ── 9. FOOD — WEST END ──────────────────────────────────────────────────────
def pg_food_we(c):
    fill_page(c)
    c.setFillColor(CHARCOAL); c.rect(0, H - 0.55*inch, W, 0.55*inch, fill=1, stroke=0)
    txt(c, M, H - 0.36*inch, "Where to Eat & Drink  ·  West End", "PopB", 14, WHITE)
    txt(c, W - M, H - 0.36*inch, "continued", "PopI", 9, TEXT_GRAY, "right")

    y = H - 0.73*inch
    pw = c.stringWidth("IN WEST END", "PopB", 8) + 26
    c.setFillColor(CHARCOAL)
    c.roundRect(M, y - 20, pw, 18, 9, fill=1, stroke=0)
    txt(c, M + 13, y - 15, "IN WEST END", "PopB", 8, WHITE)
    y -= 32

    y = restaurant_entry(c, M, y, CW, "Sandy Buns Bakery & Cafe",
        "Run by Tim & Shantal · Texan expats · West End",
        ["The Motherclucker — Josh's personal favorite dish on the entire island. Full stop.",
         "Also: smoked brisket, legendary cinnamon rolls, the Dirty Bird sandwich.",
         "Texas-sized portions — one entrée easily feeds two. Only 10–12 seats. Go early."],
        "Mon–Fri 8–3 PM · Sat 8–2 & 4–8 PM · Closed Sun · Cash, Venmo, PayPal", PINK)

    y = restaurant_entry(c, M, y, CW, "Ginger's Caribbean Grill",
        "Owned by Ginger & Jeff · Half Moon Bay, West End",
        ["Fresh seafood from local fishermen — sustainable catches only.",
         "The bang bang shrimp and shrimp po'boy are both exceptional.",
         "Lionfish tacos: invasive species, delicious solution, good for the reef."],
        "Beautiful waterfront setting · Cash & cards", PINK)

    y = restaurant_entry(c, M, y, CW, "Sundowner's Beach Bar",
        "Half Moon Bay · Best sunset view on Roatán",
        ["Get there by 5:30 for a good table. Taco Tuesdays, trivia Thursdays, live music all week.",
         "Full disclosure: Josh plays here Sunday evenings 6:30–8:30 PM. You should come."],
        "Daily 11 AM–10 PM · Cash, Venmo, PayPal", PINK)

    y = restaurant_entry(c, M, y, CW, "Deco Stop Bar & Grill",
        "Down by Tita's Pink Seahorse · West End Beach",
        ["Covered tables, cornhole boards, darts, outstanding food and service.",
         "The Smokehouse Burger: best burger we've had south of the United States.",
         "Get the forearm-sized Cali Burrito. Truly outstanding."],
        "Right on the beach · Casual and fun", PINK)

    y = restaurant_entry(c, M, y, CW, "Thai Blue Elephant",
        "West End Main Road · 16+ years on the island",
        ["Pad thai, yellow curry, tom yum, chicken satay. Good vegan options. Consistently excellent."],
        "Tue–Sun 11 AM–9 PM", PINK)

    y -= 4
    rbox(c, M, y, CW, 36, GRAY_BG, r=8)
    txt(c, M + 14, y - 12, "PIZZA:", "PopB", 9, CHARCOAL)
    txt(c, M + 14 + c.stringWidth("PIZZA:  ", "PopB", 9), y - 12,
        "Bigros/C-Level — 4.8 stars, great gluten-free, open until 8:30 PM", "Pop", 9, TEXT_GRAY)
    txt(c, M + 14, y - 26,
        "Junior's Patio — fresh dough, real oven, cash only, closes 8 PM sharp. Call ahead: +504 9685-5073",
        "Pop", 8.8, TEXT_GRAY)
    footer(c, 9)


# ── 10. THE PEOPLE ──────────────────────────────────────────────────────────
def pg_people(c):
    fill_page(c, GRAY_BG)
    section_header(c, "The People Behind Your Favorite Spots",
                   "Roatán's best spots are run by people who chose this place on purpose.",
                   bg=TEAL, sub_col=HexColor("#B8E6E1"))
    y = H - 1.1*inch
    col = (CW - 16) / 2
    lx, rx = M, M + col + 16

    people = [
        ("Tim & Shantal", "Sandy Buns Bakery & Cafe",
         "Left Texas and built something genuinely special in West End. Sandy Buns "
         "shouldn't work on paper — BBQ brisket and cinnamon rolls on a Caribbean island "
         "— and yet it's always packed and always worth it."),
        ("Ginger & Jeff", "Ginger's Caribbean Grill",
         "Built Ginger's on doing things right: sustainable catches, local fishermen, "
         "a setting that earns its view. Ordering the lionfish tacos here "
         "is one of the most eco-correct meals you can eat on this island."),
        ("Jay & Lavina", "Bottom Time Scuba · Two doors down",
         "Came to Roatán to dive and never left — which is exactly the profile "
         "of the best dive instructors anywhere. Obsessive, experienced, doing it "
         "because they love it. Two doors down. Can't be easier."),
        ("The Team at Beachers", "West Bay Beach · 15+ years",
         "Locally owned, family-run for over 15 years. The lobster price isn't "
         "a gimmick — it's what happens when the owner cares more about feeding "
         "people well than maximizing margin. Those places are getting rare."),
    ]

    y_l = y_r = y
    for i, (name, place, body) in enumerate(people):
        tx = lx if i % 2 == 0 else rx
        ty = y_l if i % 2 == 0 else y_r

        txt(c, tx, ty, name, "PopB", 11.5, CHARCOAL); ty -= 13
        txt(c, tx, ty, place, "Pop", 8.5, TEAL); ty -= 5
        hrule(c, tx, ty, col, BORDER_SOFT); ty -= 11
        ty = wraptext(c, tx, ty, body, "Pop", 9, TEXT_GRAY, col, 13.5)
        ty -= 16

        if i % 2 == 0: y_l = ty
        else: y_r = ty

    footer(c, 10)


# ── 11. THINGS TO DO ────────────────────────────────────────────────────────
def pg_activities(c):
    fill_page(c)
    c.setFillColor(TEAL); c.rect(0, H - 4, W, 4, fill=1, stroke=0)
    y = H - 0.68*inch
    y = pill_label(c, M, y, "ACTIVITIES")
    txt(c, M, y, "Things to Do", "PopB", 30, CHARCOAL); y -= 10
    txt(c, M, y - 4, "Start with the reef. Everything else is gravy.", "Pop", 10, TEXT_GRAY)
    y -= 22; hrule(c, M, y, CW, BORDER_SOFT); y -= 12

    # Featured snorkeling card
    rbox(c, M, y, CW, 110, TEAL_SOFT, r=10)
    accent_bar(c, M, y, 110, TEAL, 4)
    txt(c, M + 16, y - 14, "SNORKELING", "PopB", 11, TEAL_DARK)
    txt(c, M + 16 + c.stringWidth("SNORKELING  ", "PopB", 11), y - 14,
        "· Free · Gear Provided", "Pop", 9, TEAL)
    wraptext(c, M + 16, y - 30,
        "We provide snorkel gear for all guests. West Bay Beach sits on the "
        "Mesoamerican Barrier Reef — one of the largest reef systems in the world — "
        "and it starts in very shallow water right off the shore. No boat, no guide, no cost. "
        "Go between 7–9 AM when the water is glassy and fish are most active. "
        "Best spot: Black Rock, at the far western end of the beach. "
        "Keep walking past where most people stop. You'll know it when you see it.",
        "Pop", 9.2, CHARCOAL, CW - 28, 13.5)
    y -= 122

    col = (CW - 16) / 2
    lx, rx = M, M + col + 16
    y_l = y_r = y

    y_l = subhead(c, lx, y_l, "Scuba Diving")
    y_l = wraptext(c, lx, y_l,
        "Bottom Time Scuba is literally two doors down — Jay and Lavina are excellent "
        "and we recommend them without hesitation. Open Water certification and fun dives. "
        "The reef wall hits 80–100+ feet visibility in dry season.",
        "Pop", 9, TEXT_GRAY, col, 13.5); y_l -= 12

    y_l = subhead(c, lx, y_l, "Other Activities")
    for label, price in [("Zip-lining", "From $65/person"),
                         ("Island tours", "From $75 · half day"),
                         ("Deep sea fishing", "From $150"),
                         ("Kayaking / paddleboarding", "On the beach"),
                         ("Glass bottom boat", "On the beach"),
                         ("Chocolate factory tour", "Macaw Ridge · ask us"),
                         ("Rum factory tour", "Roatán Rum Co."),
                         ("Monkey & sloth park", "Great half-day")]:
        y_l = dashed_price_row(c, lx, y_l, col, label, price)

    y_r = subhead(c, rx, y_r, "Groceries & Supplies")
    for name, desc in [("Fresco Market", "Fruits & vegetables · nearby"),
                       ("Captain Van's", "Beer, wine, liquor, convenience"),
                       ("Roa Market", "Widest local selection · next to Beachers"),
                       ("Eldon's", "Main road · great for pre-arrival or after airport")]:
        txt(c, rx, y_r, name, "PopM", 9, CHARCOAL); y_r -= 12
        txt(c, rx + 8, y_r, desc, "Pop", 8.5, TEXT_GRAY); y_r -= 14
    y_r -= 6

    rbox(c, rx, y_r, col, 50, PINK_SOFT, r=8)
    accent_bar(c, rx, y_r, 50, PINK, 4)
    txt(c, rx + 12, y_r - 13, "CRUISE SHIP DAYS", "PopB", 8.5, PINK)
    wraptext(c, rx + 12, y_r - 27,
        "Beach gets busier mid-morning through mid-afternoon when ships are in. "
        "Check the schedule at casamananaroatan.com.",
        "Pop", 8.5, CHARCOAL, col - 20, 13)

    footer(c, 11)


# ── 12. REEF GUIDE ──────────────────────────────────────────────────────────
def pg_reef(c):
    fill_page(c, GRAY_BG)
    section_header(c, "What You Might See Out There",
                   "A quick guide to the reef — so you know what you're looking at.",
                   bg=TEAL, sub_col=HexColor("#B8E6E1"))
    y = H - 1.08*inch
    col = (CW - 16) / 2
    lx, rx = M, M + col + 16

    creatures = [
        ("Parrotfish",
         "Hard to miss — bright blue, green, and pink. They eat coral (you can hear it) "
         "and produce white sand from digestion. "
         "Yes, you're lying on parrotfish output. That's the Caribbean."),
        ("Sea Turtles",
         "West Bay has a healthy turtle population. Real chance of seeing one, "
         "especially in the morning. Keep distance, don't chase. "
         "They're not in a hurry — you shouldn't be either."),
        ("Blue Tangs",
         "The electric blue fish from that animated movie. "
         "Travel in schools. Stunning in person. Found at all depths."),
        ("Lionfish",
         "Beautiful and a genuine problem — invasive, no natural predators, "
         "eating native fish populations. Don't touch (venomous spines). "
         "Several restaurants serve them. Ordering one is the most eco-correct "
         "meal on the island."),
        ("Eagle Rays & Stingrays",
         "Both common around West Bay. Rays near the sandy bottom: stingrays. "
         "Ones soaring through open water: eagle rays. Both worth stopping for."),
        ("Brain Coral",
         "Giant boulder-shaped corals. Some on this reef are hundreds of years old, "
         "growing half an inch per year. Please do not stand on them."),
        ("Sergeant Majors",
         "Small black-and-white striped fish that swim directly toward you. "
         "Especially near food. Fearless little characters. Entertaining every time."),
        ("Fire Coral",
         "Pale, branching coral. Brush against it and you'll feel it — "
         "a burning sting that lingers. Not dangerous, but memorable. "
         "Look, don't touch. Especially this."),
    ]

    y_l = y_r = y
    for i, (name, body) in enumerate(creatures):
        tx = lx if i % 2 == 0 else rx
        ty = y_l if i % 2 == 0 else y_r
        txt(c, tx, ty, name, "PopB", 10.5, TEAL_DARK); ty -= 5
        hrule(c, tx, ty, col, TEAL_SOFT, 1); ty -= 11
        ty = wraptext(c, tx, ty, body, "Pop", 8.8, TEXT_GRAY, col, 13)
        ty -= 12
        if i % 2 == 0: y_l = ty
        else: y_r = ty

    y = min(y_l, y_r) - 6
    rbox(c, M, y, CW, 28, TEAL_SOFT, r=6)
    txt(c, W/2, y - 10, "The reef starts in 3–4 feet of water right off the beach.", "PopI", 9.5, TEAL_DARK, "center")
    txt(c, W/2, y - 22, "If you can float, you can snorkel here. That's the whole barrier to entry.", "PopI", 9, TEXT_GRAY, "center")
    footer(c, 12)


# ── 13. HIDDEN GEMS ─────────────────────────────────────────────────────────
def pg_gems(c):
    fill_page(c)
    c.setFillColor(PINK); c.rect(0, H - 4, W, 4, fill=1, stroke=0)
    y = H - 0.68*inch
    y = pill_label(c, M, y, "INSIDER TIPS")
    txt(c, M, y, "Hidden Gems & Local Secrets", "PopB", 28, CHARCOAL); y -= 10
    txt(c, M, y - 4, "The stuff the guidebooks don't tell you.", "Pop", 10, TEXT_GRAY)
    y -= 22; hrule(c, M, y, CW, BORDER_SOFT); y -= 14

    col = (CW - 16) / 2
    lx, rx = M, M + col + 16

    gems = [
        ("The Best Snorkel Window Is 7–9 AM",
         "Before the beach fills up, before the wind picks up, "
         "before cruise ship crowds. The water is glass. "
         "You'll have the reef almost to yourself."),
        ("The Beach Has Shade — If You Know Where",
         "The eastern end, closest to the house, has more palm shade "
         "in the afternoon. Stake out a spot there early on long beach days."),
        ("Sunday Evenings at Sundowner's",
         "Josh may have a vested interest here, but — arrive by 5:30. "
         "Good sunset tables go fast. Music starts at 6:30. "
         "The sunset usually cooperates."),
        ("The Water Taxi Is More Fun Than the Road",
         "Look for the guys near Bananarama or by Beachers. "
         "Take it at least once — a little boat ride along the coast."),
        ("Junior's Patio: Always Call Ahead",
         "Cash only, closes 8 PM sharp. "
         "Call: +504 9685-5073. Don't show up without calling. "
         "Do call ahead and expect a really excellent pizza."),
        ("The Pool Looks Great at Night",
         "Turn the pool lights on after dark. Sit on the porch with a drink. "
         "Sounds obvious. Guests always mention at checkout they never did it."),
        ("Beachers' Lobster Is the Best Deal on the Island",
         "Three tails for ~$20. People pay $50–80 at resort restaurants up the beach. "
         "Same ocean. Better vibe. Go at happy hour (2–6 PM)."),
        ("Sandy Buns: Order the Motherclucker",
         "There's a menu. You don't need it. "
         "The Motherclucker. Josh's personal favorite dish on the island. "
         "You can thank us later."),
    ]

    y_l = y_r = y
    for i, (title, body) in enumerate(gems):
        tx = lx if i % 2 == 0 else rx
        ty = y_l if i % 2 == 0 else y_r

        # Pink diamond bullet
        c.setFillColor(PINK)
        p = c.beginPath()
        p.moveTo(tx+5, ty+5); p.lineTo(tx+10, ty)
        p.lineTo(tx+5, ty-5); p.lineTo(tx, ty); p.close()
        c.drawPath(p, fill=1, stroke=0)

        txt(c, tx + 15, ty + 2, title, "PopB", 9, CHARCOAL)
        ny = wraptext(c, tx + 15, ty - 12, body, "Pop", 8.8, TEXT_GRAY, col - 15, 13)
        ny -= 10
        if i % 2 == 0: y_l = ny
        else: y_r = ny

    footer(c, 13)


# ── 14. RAINY DAY ───────────────────────────────────────────────────────────
def pg_rainy(c):
    fill_page(c, GRAY_BG)
    section_header(c, "What to Do on a Rainy Afternoon",
                   "It happens. Usually clears in an hour. Here's what we'd do.",
                   bg=CHARCOAL, sub_col=TEXT_GRAY)
    y = H - 1.1*inch
    col = (CW - 16) / 2
    lx, rx = M, M + col + 16

    items = [
        ("Cook Something Real",
         "You've got a full kitchen. Grab fresh fish or produce from Fresco Market "
         "or Roa Market, follow a recipe you've been meaning to try, "
         "and eat on the covered porch while the rain does its thing."),
        ("Wander West End",
         "West End's main road is more enjoyable in light rain than on a blazing hot day. "
         "Shops, galleries, and cafes are covered or open-air. Wander slowly."),
        ("Chocolate Factory Tour",
         "Macaw Ridge runs a cacao farm tour that's genuinely interesting. "
         "You'll learn more about cacao than you expected, and leave with chocolate."),
        ("Rum Factory Tour",
         "Roatán Rum Company does tours and tastings. "
         "You don't need a sunny day to appreciate rum. Ask us for directions."),
        ("JavaVine on a Rainy Morning",
         "Best coffee on the island. Good WiFi. Warm and comfortable. "
         "Open at 7:30 AM Tuesday through Friday. And seriously — order the Rumors pizza."),
        ("Movie Afternoon",
         "Plug in your Netflix. Bedroom has AC. "
         "This is a completely valid way to spend a rainy afternoon. We will not judge."),
        ("Plan the Rest of Your Trip",
         "Scroll this guide. Book that dive. Decide which morning you're finally "
         "getting up at 7 AM for Black Rock."),
    ]

    y_l = y_r = y
    for i, (title, body) in enumerate(items):
        tx = lx if i % 2 == 0 else rx
        ty = y_l if i % 2 == 0 else y_r
        txt(c, tx, ty, title, "PopB", 10, TEAL_DARK)
        ty -= 4
        c.setStrokeColor(TEAL); c.setLineWidth(1.5)
        c.line(tx, ty, tx + c.stringWidth(title, "PopB", 10), ty); ty -= 10
        ty = wraptext(c, tx + 6, ty, body, "Pop", 9, TEXT_GRAY, col - 6, 13.5)
        ty -= 12
        if i % 2 == 0: y_l = ty
        else: y_r = ty

    y = min(y_l, y_r) - 6
    rbox(c, M, y, CW, 28, WHITE, r=8)
    txt(c, W/2, y - 10, "Rainy season usually means a brief afternoon shower.",
        "PopI", 9, TEXT_GRAY, "center")
    txt(c, W/2, y - 22, "Give it until noon — the island usually shows up.",
        "PopI", 9, TEXT_GRAY, "center")
    footer(c, 14)


# ── 15. STARGAZING ──────────────────────────────────────────────────────────
def pg_stars(c):
    """Stargazing — dark charcoal background, fully on-brand, all content within margins."""
    fill_page(c, CHARCOAL)

    # Subtle star field — kept well inside page area
    random.seed(42)
    for _ in range(160):
        sx = random.uniform(M * 0.8, W - M * 0.8)
        sy = random.uniform(H * 0.22, H - 1.0*inch)
        sr = random.uniform(0.35, 1.5)
        br = random.randint(120, 200)
        c.setFillColor(HexColor(f"#{br:02X}{br:02X}{min(br+8,255):02X}"))
        c.circle(sx, sy, sr, fill=1, stroke=0)

    # Teal/pink strips (consistent with all pages)
    c.setFillColor(TEAL); c.rect(0, H - 5, W, 5, fill=1, stroke=0)
    c.setFillColor(PINK); c.rect(0, 0, W, 5, fill=1, stroke=0)

    # Page heading — constrained to margins
    y = H - 0.72*inch
    txt(c, W/2, y, "Look Up Tonight.", "PopB", 36, WHITE, "center")
    tw = c.stringWidth("Look Up Tonight.", "PopB", 36)
    c.setStrokeColor(TEAL); c.setLineWidth(2.5)
    c.line(W/2 - tw/2, y - 8, W/2 + tw/2, y - 8)
    y -= 28

    y = wraptext(c, M, y,
        "One thing people don't expect: the sky here at night.",
        "PopI", 11, TEAL_MED, CW, 16, "center")
    y -= 8

    y = wraptext(c, M, y,
        "We're far from any major city's light pollution. On a clear night — which is most "
        "nights outside of rainy season — the stars are genuinely stunning. "
        "The Milky Way is visible on moonless nights. "
        "You can spot satellites with the naked eye if you're patient.",
        "Pop", 10, HexColor("#9AAFBA"), CW, 15, "center")
    y -= 28

    # Three step cards — fixed width, properly positioned
    card_w = (CW - 24) / 3
    card_h = 72
    card_y = y
    for i, (num, label) in enumerate([
        ("1", "Turn off the\npool lights."),
        ("2", "Let your eyes\nadjust 5 min."),
        ("3", "Look up."),
    ]):
        bx = M + i * (card_w + 12)
        c.setFillColor(HexColor("#252527"))
        c.roundRect(bx, card_y - card_h, card_w, card_h, 10, fill=1, stroke=0)
        # Number circle
        c.setFillColor(TEAL)
        c.circle(bx + card_w/2, card_y - 16, 13, fill=1, stroke=0)
        txt(c, bx + card_w/2, card_y - 20.5, num, "PopB", 11, WHITE, "center")
        # Label (split on newline)
        lines = label.split("\n")
        ly = card_y - 42
        col = WHITE if num == "3" else TEAL_MED
        for line in lines:
            txt(c, bx + card_w/2, ly, line, "PopB", 9, col, "center")
            ly -= 14
    y = card_y - card_h - 20

    txt(c, W/2, y, "That's the whole instruction.", "PopI", 11, TEXT_GRAY, "center")
    y -= 28

    # Tips — dark card
    tip_h = 72
    c.setFillColor(HexColor("#252527"))
    c.roundRect(M, y - tip_h, CW, tip_h, 10, fill=1, stroke=0)
    accent_bar(c, M, y, tip_h, TEAL, 4)
    txt(c, M + 16, y - 14, "TIPS FOR THE BEST VIEW", "PopB", 8.5, TEAL)
    for ti, tip in enumerate([
        "Best nights: new moon nights, when the sky is at its darkest.",
        "If your stay includes a new moon night, don't waste it.",
        "Download Sky Map or Stellarium before you arrive — free apps, totally worth it.",
    ]):
        txt(c, M + 16, y - 28 - ti * 14, tip, "Pop", 8.8, HexColor("#9AAFBA"))
    y -= tip_h + 16

    # Footer
    c.setStrokeColor(HexColor("#2A2A2C")); c.setLineWidth(0.5)
    c.line(M, 0.56*inch, M + CW, 0.56*inch)
    txt(c, W/2, 0.36*inch,
        "Casa Mañana  ·  West Bay, Roatán  ·  casamananaroatan.com",
        "PopL", 7, HexColor("#3A4A50"), "center")
    txt(c, W - M, 0.36*inch, "15", "PopL", 7.5, HexColor("#3A4A50"), "right")


# ── 16. PRACTICAL INFO ──────────────────────────────────────────────────────
def pg_practical(c):
    fill_page(c)
    c.setFillColor(TEAL); c.rect(0, H - 4, W, 4, fill=1, stroke=0)
    y = H - 0.68*inch
    y = pill_label(c, M, y, "NEED TO KNOW")
    txt(c, M, y, "Practical Info", "PopB", 30, CHARCOAL); y -= 10
    txt(c, M, y - 4, "The reference page. Come back to this one mid-trip.", "Pop", 10, TEXT_GRAY)
    y -= 22; hrule(c, M, y, CW, BORDER_SOFT); y -= 14

    col = (CW - 16) / 2
    lx, rx = M, M + col + 16

    def sec(x, y0, head, body, cw):
        y0 = subhead(c, x, y0, head)
        y0 = wraptext(c, x, y0, body, "Pop", 9, TEXT_GRAY, cw, 13.5)
        return y0 - 12

    y_l = y
    y_l = sec(lx, y_l, "Money",
        "US dollars widely accepted. Local currency: Honduran Lempira (~25L = $1 USD). "
        "Pay in Lempiras when possible for a slightly better rate. "
        "Always decline dynamic currency conversion on card machines.", col)

    y_l = sec(lx, y_l, "Tipping",
        "10–15% at restaurants. Some beach spots add a 10% service charge — "
        "check your bill before adding more. "
        "For dive instructors and tour guides, $5–10 USD is customary and appreciated.", col)

    y_l = sec(lx, y_l, "If You Get Sick",
        "Emergency clinic right in West Bay Mall — just down the street. "
        "Pharmacy on the Bananarama road, about halfway down toward the beach. "
        "Hospital in Coxen Hole for anything serious.", col)

    y_l = subhead(c, lx, y_l, "Cell Service & eSIM")
    y_l = wraptext(c, lx, y_l,
        "Cell service can be spotty on the island. For reliable mobile data, "
        "get an eSIM before you arrive:", "Pop", 9, TEXT_GRAY, col, 13.5)
    y_l -= 10
    for nm, desc in [("Airalo", "Best overall"),
                     ("Holafly", "Unlimited data"),
                     ("Nomad", "Affordable, flexible plans"),
                     ("Saily", "Budget-friendly")]:
        txt(c, lx + 8, y_l, nm + " —", "PopM", 8.8, TEAL)
        txt(c, lx + 8 + c.stringWidth(nm + " — ", "PopM", 8.8), y_l, desc, "Pop", 8.8, TEXT_GRAY)
        y_l -= 13
    y_l -= 4
    txt(c, lx, y_l, "Simple to set up before you travel. Cheap. Worth it.", "PopI", 8.5, TEXT_GRAY)

    y_r = y
    y_r = subhead(c, rx, y_r, "Weather")
    for label, val in [("Air temp year-round", "82–88°F · 28–31°C"),
                       ("Best for most visitors", "February – June"),
                       ("Peak dry season", "March – May"),
                       ("Rainy season", "June – November"),
                       ("Hurricane risk", "Low, but possible Jun–Nov")]:
        y_r = dashed_price_row(c, rx, y_r, col, label, val, "Pop", "PopM")
    y_r = wraptext(c, rx, y_r - 4,
        "Rainy season usually means brief afternoon showers, not all-day rain. "
        "Travel insurance is always smart, especially during hurricane season.",
        "PopI", 8.8, TEXT_GRAY, col, 13); y_r -= 12

    y_r = sec(rx, y_r, "Safety",
        "West Bay is very safe. Quiet neighborhood, good lighting, on-site hosts. "
        "Apply normal travel sense: avoid isolated areas after dark, "
        "always use official white taxis with yellow numbers, "
        "keep valuables off the beach. Beyond that — relax. You're on vacation.", col)

    footer(c, 16)


# ── 17. FAQ ─────────────────────────────────────────────────────────────────
def pg_faq(c):
    fill_page(c, GRAY_BG)
    section_header(c, "Questions You Might Have   But Were Too Polite to Ask",
                   "We've been asked every single one of these.",
                   bg=CHARCOAL)
    y = H - 1.1*inch
    col = (CW - 16) / 2
    lx, rx = M, M + col + 16

    faqs = [
        ("Is the water safe to swim in?",
         "Yes. West Bay Beach is calm, clean, and healthy. "
         "The reef keeps the ecosystem in good shape. We swim in it regularly."),
        ("Will I get sick from the tap water?",
         "Stick to bottled water or the kitchen filter for drinking. "
         "Tap water is fine for teeth and cooking — standard practice across Honduras, "
         "not an emergency situation."),
        ("Are there jellyfish?",
         "Occasionally. Serious stings at West Bay are very uncommon. "
         "If concerned, the dive shops know current conditions — worth a quick ask."),
        ("What about mosquitoes?",
         "They exist. Most active at dusk and dawn. "
         "A little repellent in the evening goes a long way. "
         "Inside with the AC on, you won't have issues."),
        ("Is it safe to walk around at night?",
         "In West Bay, yes. Our neighborhood is quiet, well-lit, and safe. "
         "West Bay has been consistently safe for us and our guests."),
        ("Is the pool heated?",
         "Solar-heated — depends on the sun. Warm on sunny days, "
         "refreshing on overcast ones. Air temp rarely drops below 80°F "
         "so it's never cold."),
        ("Can we have friends over?",
         "The listing is for 2 guests. If you'd like a friend to join for dinner "
         "on the porch, just ask us first. We're reasonable — we just want to know "
         "what's happening at the property."),
        ("Are there dangerous animals?",
         "Nothing significant. Lionfish and fire coral will teach you not to touch them. "
         "On land: iguanas, hummingbirds, crabs. Charley is harmless."),
        ("What's the noise situation?",
         "The neighborhood is quiet. Birds in the morning (in a good way). "
         "No road noise, no club next door. Tell us if something bothers you."),
    ]

    y_l = y_r = y
    for i, (q, a) in enumerate(faqs):
        tx = lx if i % 2 == 0 else rx
        ty = y_l if i % 2 == 0 else y_r
        ny = wraptext(c, tx, ty, q, "PopB", 9.2, TEAL_DARK, col, 13)
        ny -= 3; hrule(c, tx, ny, col, BORDER_SOFT); ny -= 9
        ny = wraptext(c, tx + 6, ny, a, "Pop", 9, TEXT_GRAY, col - 6, 13)
        ny -= 14
        if i % 2 == 0: y_l = ny
        else: y_r = ny

    footer(c, 17)


# ── 18. LANGUAGE ────────────────────────────────────────────────────────────
def pg_language(c):
    fill_page(c)
    c.setFillColor(PINK); c.rect(0, H - 4, W, 4, fill=1, stroke=0)
    y = H - 0.68*inch
    y = pill_label(c, M, y, "ESPAÑOL")
    txt(c, M, y, "A Little Language Goes a Long Way", "PopB", 26, CHARCOAL); y -= 10
    y = wraptext(c, M, y - 4,
        "Roatán has a mix of mainland Honduran Spanish and Bay Island Creole English. "
        "Most people in tourist areas speak English, but a few words of Spanish "
        "will get you a noticeably warmer response almost everywhere.",
        "Pop", 9.5, TEXT_GRAY, CW, 14); y -= 16
    hrule(c, M, y, CW, BORDER_SOFT); y -= 14

    col = (CW - 16) / 2
    lx, rx = M, M + col + 16

    pl = [("Buenos días", "Good morning"),
          ("Buenas tardes", "Good afternoon / evening"),
          ("Gracias", "Thank you"),
          ("Por favor", "Please"),
          ("¿Cuánto cuesta?", "How much does it cost?"),
          ("Una cerveza, por favor", "One beer, please")]

    pr = [("La cuenta, por favor", "The check, please"),
          ("Muy rico", "Very delicious"),
          ("¿Habla inglés?", "Do you speak English?"),
          ("Está bien", "It's fine / Okay"),
          ("Para usted", "For you (when tipping)"),
          ("La propina", "The tip")]

    txt(c, lx, y, "Spanish Basics", "PopB", 10.5, CHARCOAL)
    teal_underline(c, lx, y, "Spanish Basics", "PopB", 10.5)
    y -= 18

    y_l = y_r = y
    for i, (ph, mn) in enumerate(pl):
        bg = GRAY_BG if i % 2 == 0 else LIGHT_BG
        c.setFillColor(bg); c.rect(lx, y_l - 14, col, 16, fill=1, stroke=0)
        txt(c, lx + 6, y_l - 1, ph, "PopM", 9, CHARCOAL)
        txt(c, lx + col, y_l - 1, mn, "Pop", 9, TEXT_GRAY, "right")
        y_l -= 16

    for i, (ph, mn) in enumerate(pr):
        bg = GRAY_BG if i % 2 == 0 else LIGHT_BG
        c.setFillColor(bg); c.rect(rx, y_r - 14, col, 16, fill=1, stroke=0)
        txt(c, rx + 6, y_r - 1, ph, "PopM", 9, CHARCOAL)
        txt(c, rx + col, y_r - 1, mn, "Pop", 9, TEXT_GRAY, "right")
        y_r -= 16

    y = min(y_l, y_r) - 14
    hrule(c, M, y, CW, BORDER_SOFT); y -= 16

    txt(c, M, y, "A Few Things Worth Knowing", "PopB", 10.5, CHARCOAL)
    teal_underline(c, M, y, "A Few Things Worth Knowing", "PopB", 10.5)
    y -= 18

    y = wraptext(c, M, y,
        "\"Baleada\" is a traditional Honduran dish — a thick flour tortilla with beans, "
        "cheese, and cream. You'll find them everywhere, they're delicious and cheap. "
        "Order one at least once.", "Pop", 9.3, TEXT_GRAY, CW, 14); y -= 10

    y = wraptext(c, M, y,
        "The Bay Islands have their own English Creole dialect, distinct from mainland Spanish. "
        "If you hear something that sounds almost like English but slightly different — "
        "that's probably it. It's been spoken on these islands for centuries.",
        "Pop", 9.3, TEXT_GRAY, CW, 14); y -= 16

    rbox(c, M, y, CW, 30, PINK_SOFT, r=6)
    txt(c, W/2, y - 12, "You don't need Spanish to have a great trip.",
        "PopI", 9.5, PINK, "center")
    txt(c, W/2, y - 24, "But the people who try — even badly — always get a warmer response. Give it a shot.",
        "PopI", 9, PINK, "center")
    footer(c, 18)


# ── 19. THINGS THAT SURPRISED US ───────────────────────────────────────────
def pg_surprises(c):
    fill_page(c, HexColor("#FDFAF3"))
    c.setFillColor(HexColor("#8B6C14")); c.rect(0, H - 0.95*inch, W, 0.95*inch, fill=1, stroke=0)
    txt(c, M, H - 0.54*inch, "A Few Things That Surprised Us", "PopB", 22, WHITE)
    txt(c, M, H - 0.76*inch, "We moved here in April 2025. Here's what we didn't expect.",
        "PopL", 9.5, HexColor("#D4AE60"))

    y = H - 1.12*inch
    col = (CW - 16) / 2
    lx, rx = M, M + col + 16

    items = [
        ("We thought we'd miss the city. We don't.",
         "Before Roatán, we spent seven years in Mexico, then five years sailing the Caribbean "
         "on a catamaran. We've been away from the United States since 2017. "
         "And yet this island felt like landing. Cities have energy, convenience, variety. "
         "Turns out the island has its own version — just slower and better."),
        ("We thought the sunsets would get old. They haven't.",
         "We've watched hundreds of them from this island. "
         "We still go outside for every one. If that tells you anything."),
        ("The community is smaller than you think.",
         "West Bay and West End together are a small world. You'll see the same faces. "
         "The restaurant owners know each other. The dive instructors know each other. "
         "Visitors are welcomed warmly because these businesses run on repeat guests "
         "and word of mouth. People are genuinely glad you're here."),
        ("The pace is the point.",
         "Things move more slowly here. Meals take longer. Taxis come when they come. "
         "Island time is real and it's not an insult. "
         "It took us a little while to stop fighting it. "
         "Once we did, we understood why people come here and don't leave."),
        ("The water is actually that blue.",
         "Photos don't exaggerate it. If anything, they undersell it. "
         "The first time you look out at the Caribbean from this place, "
         "you might actually stop talking for a moment. That happens to people."),
        ("The reef is fragile.",
         "Living near it changes how you think about it. "
         "It's one of the most biodiverse ecosystems on earth and it's under real pressure. "
         "The reef-safe sunscreen rule, the don't-touch-the-coral rule — "
         "these aren't bureaucratic. The reef is worth protecting. "
         "We hope you come away feeling that too."),
    ]

    y_l = y_r = y
    for i, (title, body) in enumerate(items):
        tx = lx if i % 2 == 0 else rx
        ty = y_l if i % 2 == 0 else y_r
        txt(c, tx, ty, title, "PopB", 9.5, CHARCOAL); ty -= 13
        ty = wraptext(c, tx, ty, body, "Pop", 9, TEXT_GRAY, col, 13.5)
        ty -= 10
        hrule(c, tx, ty, col * 0.35, HexColor("#C9A030"), 0.6)
        ty -= 12
        if i % 2 == 0: y_l = ty
        else: y_r = ty

    y = min(y_l, y_r) - 6
    rbox(c, M, y, CW, 38, HexColor("#F2E8CC"), r=8)
    c.setFillColor(HexColor("#8B6C14")); c.roundRect(M, y - 38, 4, 38, 2, fill=1, stroke=0)
    txt(c, M + 16, y - 13, "This place was built in 2016. We've only been here a year.", "PopB", 9.5, CHARCOAL)
    txt(c, M + 16, y - 28, "But we already can't imagine being anywhere else. We're really glad you're in it with us.",
        "Pop", 9, TEXT_GRAY)
    footer(c, 19)


# ── 20. BEFORE YOU GO ───────────────────────────────────────────────────────
def pg_final(c):
    fill_page(c)

    # Top teal accent
    c.setFillColor(TEAL); c.rect(0, H - 4, W, 4, fill=1, stroke=0)

    # Dark charcoal footer band
    c.setFillColor(CHARCOAL); c.rect(0, 0, W, 2.65*inch, fill=1, stroke=0)
    c.setFillColor(TEAL); c.rect(0, 2.65*inch, W, 3, fill=1, stroke=0)

    # Decorative teal circles — top right
    c.setFillColor(TEAL_SOFT)
    c.circle(W - 0.75*inch, H - 0.75*inch, 1.45*inch, fill=1, stroke=0)
    c.setFillColor(HexColor("#CCE9E6"))
    c.circle(W - 0.75*inch, H - 0.75*inch, 0.88*inch, fill=1, stroke=0)
    c.setFillColor(LIGHT_BG)
    c.circle(W - 0.75*inch, H - 0.75*inch, 0.42*inch, fill=1, stroke=0)

    y = H - 0.7*inch
    y = pill_label(c, M, y, "CHECKOUT")
    txt(c, M, y, "Before You Go", "PopB", 32, CHARCOAL); y -= 14
    txt(c, M, y, "Checkout is at 11 AM. Here's all you need to do:", "Pop", 10, TEXT_GRAY)
    y -= 22; hrule(c, M, y, CW, BORDER_SOFT); y -= 14

    items = [
        "Wash the dishes and leave them in the strainer — it's in the cabinet under the sink.",
        "Bag up trash and leave it on the front porch by the door. "
        "Or take it to the large pink bin near the neighborhood entrance. Very much appreciated.",
        "Leave used towels in the bathroom.",
        "No need to strip the bed.",
        "Turn off the AC and lock the door — press the lock button on the bottom right of the keypad.",
        "Sign the guestbook. We love hearing your stories.",
    ]
    for item in items:
        y = check_item(c, M, y, item, CW, TEAL)
        y -= 8

    y -= 10
    rbox(c, M, y, CW, 66, GRAY_BG, r=10)
    accent_bar(c, M, y, 66, PINK, 4)
    txt(c, M + 16, y - 14, "ONE LAST THING", "PopB", 10, PINK)
    wraptext(c, M + 16, y - 30,
        "If something wasn't right during your stay, please tell us before you go. "
        "We'd much rather hear it directly — and we'll make it right.",
        "Pop", 9.2, TEXT_GRAY, CW - 28, 13.5)
    wraptext(c, M + 16, y - 52,
        "If everything was great — a review on Airbnb takes two minutes "
        "and means the world to small hosts like us.",
        "Pop", 9.2, TEXT_GRAY, CW - 28, 13.5)

    # Closing in dark band
    txt(c, W/2, 2.2*inch,  "Thank you for choosing us.",
        "PopB", 19, WHITE, "center")
    txt(c, W/2, 1.92*inch, "We hope you truly enjoy this place as much as we do.",
        "Pop", 10, TEXT_GRAY, "center")
    c.setStrokeColor(TEAL); c.setLineWidth(1.2)
    c.line(W/2 - 72, 1.72*inch, W/2 + 72, 1.72*inch)
    txt(c, W/2, 1.48*inch, "— Josh & Pamela", "LoraI", 15, TEAL, "center")
    txt(c, W/2, 1.28*inch, "Casa Mañana  ·  West Bay, Roatán, Honduras", "PopL", 8.5, TEXT_GRAY, "center")
    txt(c, W/2, 1.1*inch,  "casamananaroatan.com", "Pop", 8.5, TEAL, "center")
    txt(c, W - M, 0.34*inch, "20", "PopL", 7.5, TEXT_GRAY, "right")


# ═══════════════════════════════════════════════════════════════════════════
#  ASSEMBLE PDF
# ═══════════════════════════════════════════════════════════════════════════

c = canvas.Canvas(OUT, pagesize=letter)
c.setTitle("Casa Mañana Welcome Guide")
c.setAuthor("Josh & Pamela · Casa Mañana · casamananaroatan.com")

pages = [
    pg_cover, pg_welcome, pg_first_day, pg_house, pg_rules,
    pg_getting_around, pg_mistakes, pg_food_wb, pg_food_we,
    pg_people, pg_activities, pg_reef, pg_gems, pg_rainy,
    pg_stars, pg_practical, pg_faq, pg_language,
    pg_surprises, pg_final,
]

for i, pg in enumerate(pages, 1):
    pg(c)
    c.showPage()
    print(f"  ✓ Page {i:2d}: {pg.__name__}")

c.save()
print(f"\n✓ Saved → {OUT}")
print(f"✓ {len(pages)} pages · 8.5 × 11 in · Ready to print")
