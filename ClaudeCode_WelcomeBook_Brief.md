# Casa Mañana Welcome Book — Claude Code Brief
## "Build this PDF exactly right, no shortcuts"

---

## CONTEXT

This is a 20-page print-ready guest welcome book for **Casa Mañana**, a vacation rental villa in West Bay, Roatán, Honduras. It needs to match the design system of **casamananaroatan.com** precisely.

A working Python/ReportLab script already exists (`welcome_final.py`). It generates the PDF correctly in terms of **content and color palette** — but has **critical layout bugs** that make it look unprofessional. Your job is to fix those bugs and make this thing look genuinely world-class.

---

## THE EXISTING SCRIPT

The script is at `/home/user/welcome_final.py` (or wherever it lives in your environment). It uses:
- **ReportLab** (Python PDF library)
- **Poppins** font family (PopB, Pop, PopM, PopL, PopI, PopLI) loaded from `/usr/share/fonts/truetype/google-fonts/`
- **Lora** italic for signatures
- Output goes to `/mnt/user-data/outputs/CasaManana_WelcomeBook.pdf`
- Page size: US Letter, 8.5×11 in (612×792 pts), margin `M = 0.6*inch`, content width `CW = W - 2*M`

**Run it with:** `python3 welcome_final.py`

---

## DESIGN SYSTEM (do not change these)

```
PINK        = #EC407A   → CTA buttons, pill badges, accent bars
PINK_SOFT   = #FDE8F0   → soft pill backgrounds
TEAL        = #3FB9A9   → icon colors, accent numbers, teal bands
TEAL_DARK   = #2A9082   → headings, subheads
TEAL_SOFT   = #E6F7F5   → light teal card backgrounds
TEAL_MED    = #8DD5CE   → body text on dark backgrounds
CHARCOAL    = #1d1d1f   → headings, dark bands
LIGHT_BG    = #fbfbfd   → page backgrounds
GRAY_BG     = #f5f5f7   → card / alternate section backgrounds
TEXT_GRAY   = #86868b   → body copy
BORDER      = #d2d2d7   → dividers
```

Every page has:
- A **5pt teal strip at the very top** (`y = H-5` to `y = H`)
- A **5pt pink strip at the very bottom** (`y = 0` to `y = 5`)
- A standard **footer** with a light rule, centered `"Casa Mañana · West Bay, Roatán · casamananaroatan.com"` in PopL 7pt TEXT_GRAY, and page number right-aligned

---

## THE BUGS TO FIX — CRITICAL

### BUG #1: Pill labels overlapping headings (affects pages 2, 4, 6, 8, 11, 13, 16, 18, 20)

**What's happening:** Small pill labels like "A NOTE FROM YOUR HOSTS", "YOUR HOME", "TRANSPORTATION" etc. are rendering ON TOP of or INSIDE the large heading text below them. They look like a smudgy highlight behind the heading word.

**Root cause:** The `pill_label()` helper function has broken y-coordinate math. In ReportLab, `y` passed to drawing functions is the **baseline** of text. The pill is a rectangle drawn with `roundRect(x, y-h, w, h, ...)` — meaning y is the TOP of the pill. But the function is miscalculating the gap between the pill bottom and the heading below it.

**Required fix:**
```python
def pill_label(c, x, y, label, bg=PINK_SOFT, fg=PINK):
    """
    Draws a small pill tag, then returns the y coordinate for the
    HEADING that should appear directly below it.
    
    y = the TOP of the pill (i.e., where you want the pill to start)
    The pill is 18pt tall with 8.5pt corner radius.
    There should be 8pt gap between pill bottom and heading baseline.
    """
    lw = c.stringWidth(label, "PopM", 7.5) + 22
    pill_top = y
    pill_bottom = y - 18
    # Draw pill
    c.setFillColor(bg)
    c.roundRect(x, pill_bottom, lw, 18, 9, fill=1, stroke=0)
    # Draw label text — vertically centered in pill
    c.setFont("PopM", 7.5)
    c.setFillColor(fg)
    c.drawString(x + 11, pill_bottom + 5, label)
    # Return y for heading baseline (8pt below pill bottom)
    return pill_bottom - 8
```

The calling pattern should look like:
```python
y = H - 0.68*inch        # start position
y = pill_label(c, M, y, "A NOTE FROM YOUR HOSTS")   # draws pill, returns heading y
txt(c, M, y, "Welcome.", "PopB", 36, CHARCOAL)       # heading goes here
y -= 44                   # move past the heading (36pt font needs ~44pt clearance)
```

---

### BUG #2: "Your First Day" page (page 3) — time pills and content cut off right side

**What's happening:** The teal time-badge pills ("2:00 PM", "4:00 PM" etc.) and title text are overflowing the right margin. The title appears clipped.

**Root cause:** The pill width is calculated dynamically from text width + padding, which is fine. But the **title text** starts immediately after the pill with only a small gap, and uses the full remaining `CW` for its column width — which pushes it past the right margin. The body text wrapping also uses the wrong column width.

**Required fix for the First Day step layout:**
```python
PILL_W = 76   # fixed width for all time pills — wide enough for "4:30 PM"
PILL_H = 18
GAP = 10      # gap between pill right edge and title start
TITLE_X = M + PILL_W + GAP
TITLE_WRAP_W = CW - PILL_W - GAP   # remaining width after pill

for i, (time_s, title, body) in enumerate(steps):
    # Dashed connector line between steps
    if i > 0:
        c.setStrokeColor(BORDER_SOFT)
        c.setLineWidth(0.8)
        c.setDash(2, 4)
        c.line(M + PILL_W/2, y + 2, M + PILL_W/2, y + 12)
        c.setDash()
    
    # Time pill — centered horizontally within PILL_W
    c.setFillColor(TEAL)
    c.roundRect(M, y - PILL_H, PILL_W, PILL_H, PILL_H/2, fill=1, stroke=0)
    c.setFont("PopB", 7.5)
    c.setFillColor(WHITE)
    c.drawCentredString(M + PILL_W/2, y - PILL_H + 5, time_s)
    
    # Title — aligned with pill top, never exceeds right margin
    c.setFont("PopB", 10.5)
    c.setFillColor(CHARCOAL)
    c.drawString(TITLE_X, y - 5, title)  # y-5 puts it near pill top
    
    y -= PILL_H + 4  # move below pill
    
    # Body text — same x as title, same wrap width
    y = wraptext(c, TITLE_X, y, body, "Pop", 9, TEXT_GRAY, TITLE_WRAP_W, 13.5)
    y -= 12
```

---

### BUG #3: "IN WEST BAY" / "IN WEST END" pill badges (pages 8 and 9) — rendering as giant black blob

**What's happening:** These section divider badges (small dark pills separating West Bay restaurants from West End restaurants) are rendering as an enormous black rounded rectangle that covers 1/4 of the page.

**Root cause:** The `pill()` helper function signature is `pill(c, x, y, w, h, col)` where `y` is the **bottom-left corner** in ReportLab's coordinate system (bottom-up). But the caller is passing `y` as if it's the top of the pill, causing `h` to be treated as an upward offset, which makes the pill enormous.

**Required fix — replace the section badge code on both food pages:**
```python
# Section badge — "IN WEST BAY" or "IN WEST END"
BADGE_H = 20
BADGE_TEXT = "IN WEST BAY"  # or "IN WEST END"
badge_w = c.stringWidth(BADGE_TEXT, "PopB", 8.5) + 28
# Draw: x=M, bottom of badge = y - BADGE_H, top of badge = y
c.setFillColor(CHARCOAL)
c.roundRect(M, y - BADGE_H, badge_w, BADGE_H, BADGE_H/2, fill=1, stroke=0)
c.setFont("PopB", 8.5)
c.setFillColor(WHITE)
c.drawString(M + 14, y - BADGE_H + 5.5, BADGE_TEXT)
y -= BADGE_H + 14  # space below badge before first restaurant entry
```

---

### BUG #4: "Look Up Tonight" page (page 15) — terrible formatting, text off page

**What's happening:** The stargazing page is not on-brand and text is running off the page or into the margins. The layout is broken.

**Required complete rebuild of `pg_stars()`:**

This page should be **dark and atmospheric** but fully readable and on-brand. Use `CHARCOAL` (#1d1d1f) as the page background — NOT a custom navy. Keep the teal/pink strips at top and bottom.

```python
def pg_stars(c):
    # Background: charcoal (on-brand)
    fill_page(c, CHARCOAL)
    
    # Subtle star field — ONLY within the safe content area
    # x: between M and W-M (within margins)
    # y: between footer area (0.8*inch) and top band (H - 0.8*inch)
    import random
    random.seed(99)
    for _ in range(140):
        sx = random.uniform(M, W - M)
        sy = random.uniform(0.8*inch, H - 0.9*inch)
        sr = random.uniform(0.3, 1.4)
        br = random.randint(100, 180)
        c.setFillColor(HexColor(f"#{br:02X}{br:02X}{min(br+6,255):02X}"))
        c.circle(sx, sy, sr, fill=1, stroke=0)
    
    # Standard teal/pink strips
    c.setFillColor(TEAL); c.rect(0, H-5, W, 5, fill=1, stroke=0)
    c.setFillColor(PINK); c.rect(0, 0, W, 5, fill=1, stroke=0)
    
    # --- ALL CONTENT STRICTLY WITHIN M to M+CW horizontally ---
    
    # Heading
    y = H - 0.72*inch
    c.setFont("PopB", 34)
    c.setFillColor(WHITE)
    c.drawCentredString(W/2, y, "Look Up Tonight.")
    # Teal underline
    tw = c.stringWidth("Look Up Tonight.", "PopB", 34)
    c.setStrokeColor(TEAL); c.setLineWidth(2.5)
    c.line(W/2 - tw/2, y - 7, W/2 + tw/2, y - 7)
    y -= 30
    
    # Intro lines — use wraptext with x=W/2 for center, max_w=CW
    y = wraptext(c, W/2, y,
        "One thing people don't expect: the sky here at night.",
        "PopI", 11, TEAL_MED, CW, 16, "center")
    y -= 8
    y = wraptext(c, W/2, y,
        "We're far from any city's light pollution. On a clear night — most nights "
        "outside of rainy season — the Milky Way is visible. "
        "You can spot satellites with the naked eye.",
        "Pop", 10, HexColor("#9AAFBA"), CW, 15, "center")
    y -= 26
    
    # Three step cards — equal width, side by side, strictly within CW
    card_w = (CW - 20) / 3   # 20 = 2 gaps of 10pt each
    card_h = 78
    for i, (num, line1, line2) in enumerate([
        ("1", "Turn off the", "pool lights."),
        ("2", "Let your eyes", "adjust 5 min."),
        ("3", "Look up.", ""),
    ]):
        bx = M + i * (card_w + 10)
        # Card background
        c.setFillColor(HexColor("#252527"))
        c.roundRect(bx, y - card_h, card_w, card_h, 10, fill=1, stroke=0)
        # Circle with number
        circle_cx = bx + card_w / 2
        circle_cy = y - 18
        c.setFillColor(TEAL)
        c.circle(circle_cx, circle_cy, 12, fill=1, stroke=0)
        c.setFont("PopB", 10); c.setFillColor(WHITE)
        c.drawCentredString(circle_cx, circle_cy - 4, num)
        # Lines of text
        text_color = WHITE if i == 2 else TEAL_MED
        c.setFont("PopB", 9.5); c.setFillColor(text_color)
        c.drawCentredString(bx + card_w/2, y - 42, line1)
        if line2:
            c.drawCentredString(bx + card_w/2, y - 56, line2)
    y -= card_h + 18
    
    # Subline
    c.setFont("PopI", 10.5); c.setFillColor(TEXT_GRAY)
    c.drawCentredString(W/2, y, "That's the whole instruction.")
    y -= 26
    
    # Tips card
    tip_h = 74
    c.setFillColor(HexColor("#252527"))
    c.roundRect(M, y - tip_h, CW, tip_h, 10, fill=1, stroke=0)
    # Left teal accent bar
    c.setFillColor(TEAL)
    c.roundRect(M, y - tip_h, 4, tip_h, 2, fill=1, stroke=0)
    # Tips content — x = M+16, wrap width = CW-22
    c.setFont("PopB", 9); c.setFillColor(TEAL)
    c.drawString(M + 16, y - 15, "TIPS FOR THE BEST VIEW")
    tips = [
        "Best nights are new moon nights — the sky is darkest then.",
        "If your stay includes one, don't waste it.",
        "Download Sky Map or Stellarium before you arrive — free and worth it.",
    ]
    for ti, tip in enumerate(tips):
        c.setFont("Pop", 8.8); c.setFillColor(HexColor("#9AAFBA"))
        c.drawString(M + 16, y - 30 - ti*15, tip)
    y -= tip_h + 16
    
    # Dark footer (no standard white footer on dark pages — use dark version)
    c.setStrokeColor(HexColor("#2A2A2C")); c.setLineWidth(0.5)
    c.line(M, 0.56*inch, M + CW, 0.56*inch)
    c.setFont("PopL", 7); c.setFillColor(HexColor("#3A4A50"))
    c.drawCentredString(W/2, 0.36*inch,
        "Casa Mañana  ·  West Bay, Roatán  ·  casamananaroatan.com")
    c.setFont("PopL", 7.5)
    c.drawRightString(W - M, 0.36*inch, "15")
```

---

### BUG #5: "Rainy Afternoon" page (page 14) — off-brand header color

**What's happening:** The header band at the top of the rainy day page is a custom blue-gray (#3a5a6a) that doesn't match the brand at all. The subheading teal underlines are also that same off-brand blue.

**Required fix:** Change `section_header()` call on this page to use `CHARCOAL` background (same as several other pages), and ensure the `TEAL_DARK` color is used for subhead underlines:

```python
def pg_rainy(c):
    fill_page(c, GRAY_BG)
    section_header(c, "What to Do on a Rainy Afternoon",
                   "It happens. Usually clears in an hour. Here's what we'd do.",
                   bg=CHARCOAL, sub_col=TEXT_GRAY)   # ← CHARCOAL, not blue-gray
    y = H - 1.1*inch
    # ... rest of function ...
    
    # For item titles, use TEAL_DARK underlines:
    txt(c, tx, ty, title, "PopB", 10, TEAL_DARK)  # ← TEAL_DARK not blue-gray
    ty -= 4
    c.setStrokeColor(TEAL); c.setLineWidth(1.5)    # ← TEAL not blue-gray
    c.line(tx, ty, tx + c.stringWidth(title, "PopB", 10), ty)
```

---

## COORDINATE SYSTEM REMINDER FOR CLAUDE CODE

ReportLab uses a **bottom-up coordinate system**:
- `y=0` is the **bottom** of the page
- `y=792` (H) is the **top** of the page
- When you call `c.drawString(x, y, text)`, `y` is the **baseline** of the text
- When you call `c.roundRect(x, y_bottom, w, h, r)`, `y_bottom` is the **bottom-left corner**
- When you call `c.rect(x, y_bottom, w, h)`, same — `y_bottom` is the bottom

**The most common bug in this file is treating `y` as "top of element" when passing to `roundRect`, when ReportLab wants the bottom.** The correct pattern is:

```python
# To draw a box that STARTS at visual position y (top) and extends DOWN by h:
c.roundRect(x, y - h, w, h, r, fill=1, stroke=0)
# After drawing, advance y downward: y -= h + gap
```

---

## THE `wraptext()` FUNCTION — CRITICAL NOTE

For `align="center"`, the `x` parameter must be the **center point** (e.g., `W/2`), NOT the left edge. The word-wrap still uses `max_w` to break lines, but each line is drawn centered on `x`.

```python
# CORRECT for centered text:
wraptext(c, W/2, y, "Some long text here", "Pop", 10, TEXT_GRAY, CW, 14, "center")
# The text will wrap within CW width, centered on W/2

# WRONG — passing M (left margin) with align="center" causes text to wrap wrong:
wraptext(c, M, y, "Some long text here", "Pop", 10, TEXT_GRAY, CW, 14, "center")
```

---

## VISUAL QUALITY STANDARDS

When complete, every page should look like it could have been designed in Figma and exported professionally. Specifically:

1. **No element bleeds into another element** — every pill, every card, every heading has clean space around it
2. **All text stays within the page margins** (M=0.6in on each side) — nothing clips
3. **Consistent vertical rhythm** — headings, subheadings, and body text have consistent spacing throughout
4. **Pills are readable** — teal time pills show white text clearly, pink section pills show text clearly, dark "IN WEST BAY" badges show white text clearly
5. **The stargazing page looks atmospheric and intentional** — dark charcoal background, stars visible but subtle, three step cards clean and readable, tips card legible
6. **The rainy day page header matches the brand** — dark charcoal band, not blue-gray
7. **Footer appears on every page** in the correct position with the correct styling

---

## HOW TO VERIFY YOUR FIX

After running `python3 welcome_final.py`:

1. Open the PDF and go to **page 2 (Welcome)** — the "A NOTE FROM YOUR HOSTS" pill should float cleanly ABOVE the word "Welcome." with visible white space between pill bottom and heading
2. Go to **page 3 (Your First Day)** — the teal time pills (2:00 PM, 4:00 PM, 4:30 PM, 6:00 PM, 8:00 PM) should be on the LEFT side, with title text starting to their right, all within the page width
3. Go to **page 8 (Food — West Bay)** — the "IN WEST BAY" badge should be a small, elegant dark pill, not a massive blob
4. Go to **page 9 (Food — West End)** — same check for "IN WEST END"
5. Go to **page 14 (Rainy Day)** — header band should be dark charcoal (#1d1d1f), matching pages 7, 12, 17, 19
6. Go to **page 15 (Look Up Tonight)** — dark charcoal background, all text visible and within margins, three step cards cleanly laid out, tips card at the bottom readable

---

## WHAT NOT TO CHANGE

- **Page content** — all the text, all the restaurant names, all the property details. Do not alter any copy.
- **Color palette** — the HEX values listed above are exact matches to the website CSS and must stay.
- **Page order** — 20 pages in this exact sequence
- **Font choices** — Poppins everywhere except Lora italic for "— Josh & Pamela" signatures
- **The general structure of each page** — section headers, two-column layouts, card styles

---

## OUTPUT

The final PDF should be saved to:
```
/mnt/user-data/outputs/CasaManana_WelcomeBook.pdf
```

It should be **8.5×11 inches, 20 pages, ready to print in binder sleeves.**

When you're done, please also confirm:
- All 20 pages generated without Python errors
- File size is reasonable (100–250KB typical for this type of PDF)

---

*This guide is printed and placed in a binder at the property for every arriving guest. It needs to look world-class. Thank you.*
