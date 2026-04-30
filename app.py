import streamlit as st
import pandas as pd
import math
import io
from copy import deepcopy

st.set_page_config(
    page_title="Steel QTO Calculator",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

.stApp {
    background: #0d1117;
    color: #e6edf3;
}

/* hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem; max-width: 1600px; }

/* ── Top header ── */
.app-header {
    border-bottom: 1px solid #21262d;
    padding-bottom: 1.25rem;
    margin-bottom: 0;
}
.app-title {
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #e6edf3;
    margin: 0;
    line-height: 1.2;
}
.app-sub {
    color: #7d8590;
    font-size: 0.82rem;
    margin-top: 4px;
    font-family: 'IBM Plex Mono', monospace;
}

/* ── KPI cards ── */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 1.25rem 0;
}
.kpi-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 16px 18px;
}
.kpi-card.highlight {
    border-color: #d29922;
    background: #1a1610;
}
.kpi-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #7d8590;
    font-family: 'IBM Plex Mono', monospace;
}
.kpi-value {
    font-size: 1.55rem;
    font-weight: 700;
    color: #e6edf3;
    margin-top: 6px;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: -0.02em;
}
.kpi-card.highlight .kpi-value { color: #d29922; }

/* ── Section headings ── */
.section-label {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #7d8590;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid #21262d;
}

/* ── Rate panel ── */
.rate-panel {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 16px 18px;
    margin-bottom: 1rem;
}

/* ── Streamlit input overrides ── */
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox select {
    background: #0d1117 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #388bfd !important;
    box-shadow: 0 0 0 3px rgba(56,139,253,0.15) !important;
}
.stTextInput label, .stNumberInput label, .stTextArea label, .stSelectbox label {
    color: #7d8590 !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-family: 'IBM Plex Mono', monospace !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #1f6feb !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.82rem !important;
    padding: 0.45rem 1rem !important;
    transition: background 0.15s ease !important;
    width: 100%;
}
.stButton > button:hover {
    background: #388bfd !important;
}

/* ── DataFrame table ── */
.stDataFrame {
    border: 1px solid #21262d !important;
    border-radius: 8px !important;
    overflow: hidden;
}
[data-testid="stDataFrame"] table {
    background: #161b22 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
}
[data-testid="stDataFrame"] th {
    background: #0d1117 !important;
    color: #7d8590 !important;
    font-size: 0.65rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    border-bottom: 1px solid #30363d !important;
    padding: 8px 10px !important;
}
[data-testid="stDataFrame"] td {
    color: #e6edf3 !important;
    border-bottom: 1px solid #1c2128 !important;
    padding: 6px 10px !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #161b22 !important;
    border: 1px solid #21262d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #21262d !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #7d8590 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    padding: 8px 20px !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
    color: #1f6feb !important;
    border-bottom: 2px solid #1f6feb !important;
    background: transparent !important;
}

/* ── Data editor ── */
[data-testid="stDataEditor"] {
    border: 1px solid #21262d !important;
    border-radius: 8px !important;
}

/* ── Info/success boxes ── */
.stAlert {
    background: #161b22 !important;
    border: 1px solid #21262d !important;
    color: #e6edf3 !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
}

/* ── Divider ── */
hr { border-color: #21262d !important; }

/* ── Calculation basis box ── */
.basis-box {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 0.78rem;
    color: #7d8590;
    line-height: 1.7;
    font-family: 'IBM Plex Mono', monospace;
}
.basis-box strong { color: #c9d1d9; }

/* Delete button styling */
button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid #30363d !important;
    color: #f85149 !important;
}
button[kind="secondary"]:hover {
    background: #1a0a0a !important;
    border-color: #f85149 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── STEEL DATABASE ────────────────────────────────────────────────────────────
STEEL_TABLE = """H1,H 100x50x5x7
H2,H 125x60x6x8
H3,H 150x75x5x7
H4,H 100x100x6x8
H5,H 175x90x5x8
H6,H 200x100x4.5x7
H7,H 150x100x6x9
H8,H 200x100x5.5x8
H9,H 125x125x6.5x9
H10,H 250x125x5x8
H11,H 250x125x6x9
H12,H 200x150x6x9
H13,H 150x150x7x10
H14,H 300x150x5.5x8
H15,H 300x150x6.5x9
H16,H 175x175x7.5x11
H17,H 350x175x6x9
H18,H 250x175x7x11
H19,H 350x175x7x11
H20,H 200x200x8x12
H21,H 200x200x12x12
H22,H 400x200x7x11
H23,H 300x200x8x12
H24,H 400x200x8x13
H25,H 450x200x8x12
H26,H 250x250x9x14
H27,H 450x200x9x14
H28,H 500x200x9x14
H29,H 350x250x9x14
H30,H 250x250x14x14
H31,H 300x300x12x12
H32,H 500x200x10x16
H33,H 300x300x10x15
H34,H 600x200x10x15
H35,H 500x200x11x19
H36,H 600x200x11x17
H37,H 300x300x15x15
H38,H 400x300x10x16
H39,H 500x300x11x15
H40,H 350x350x10x16
H41,H 600x200x12x20
H42,H 450x300x11x18
H43,H 500x300x11x18
H44,H 350x350x12x19
H45,H 600x300x12x17
H46,H 400x400x15x15
H47,H 400x400x11x18
H48,H 600x300x12x20
H49,H 700x300x13x20
H50,H 400x400x13x21
H51,H 600x300x14x23
H52,H 700x300x13x24
H53,H 800x300x14x22
H54,H 400x400x21x21
H55,H 800x300x14x26
H56,H 900x300x15x23
H57,H 400x400x18x28
H58,H 900x300x16x28
H59,H 400x400x20x35
H60,H 900x300x18x34
T1,T 50x50x5x7
T2,T 62.5x60x6x8
T3,T 75x75x5x7
T4,T 50x100x6x8
T5,T 87.5x90x5x8
T6,T 100x100x4.5x7
T7,T 75x100x6x9
T8,T 100x100x5.5x8
T9,T 62.5x125x6.5x9
T10,T 125x125x5x8
T11,T 125x125x6x9
T12,T 100x150x6x9
T13,T 75x150x7x10
T14,T 150x150x5.5x8
T15,T 150x150x6.5x9
T16,T 125x175x7x11
T17,T 175x175x6x9
T18,T 125x175x7x11
T19,T 175x175x7x11
T20,T 100x200x8x12
T21,T 100x200x12x12
T22,T 200x200x7x11
T23,T 150x200x8x12
T24,T 200x200x8x13
T25,T 225x200x8x12
T26,T 125x250x9x14
T27,T 225x200x9x14
T28,T 250x200x9x14
T29,T 175x250x9x14
T30,T 125x250x14x14
T31,T 150x300x12x12
T32,T 250x200x10x16
T33,T 150x300x10x15
T34,T 300x200x10x15
T35,T 250x200x11x19
T36,T 300x200x11x17
T37,T 150x300x15x15
T38,T 200x300x10x16
T39,T 250x300x11x15
T40,T 175x350x10x16
T41,T 300x200x12x20
T42,T 225x300x11x18
T43,T 250x300x11x18
T44,T 175x350x12x19
T45,T 300x300x12x17
T46,T 200x400x15x15
T47,T 200x400x11x18
T48,T 300x300x12x20
T49,T 350x300x13x20
T50,T 200x400x13x21
T51,T 300x300x14x23
T52,T 350x300x13x24
T53,T 400x300x14x22
T54,T 200x400x21x21
T55,T 400x300x14x26
T56,T 450x300x15x23
T57,T 200x400x18x28
T58,T 450x300x16x28
T59,T 200x400x20x35
T60,T 450x300x18x34
C1,CH 75x40x5x7
C2,CH 100x50x5x7.5
C3,CH 125x65x6x8
C4,CH 150x75x6.5x10
C5,CH 180x75x7x10.5
C6,CH 150x75x9x12.5
C7,CH 200x80x7.5x11
C8,CH 200x90x8x13.5
C9,CH 250x90x9x13
C10,CH 300x90x9x13
C11,CH 250x90x11x14.5
C12,CH 300x90x10x15.5
C13,CH 300x90x12x16
C14,CH 380x100x10.5x16
C15,CH 380x100x13x16.5
C16,CH 380x100x13x20
L1,L 25x25x3
L2,L 30x30x3
L3,L 40x40x3
L4,L 45x45x4
L5,L 40x40x4
L6,L 50x50x4
L7,L 45x45x5
L8,L 60x60x4
L9,L 50x50x5
L10,L 50x50x6
L11,L 60x60x5
L12,L 65x65x5
L13,L 65x65x6
L14,L 70x70x6
L15,L 75x75x6
L16,L 80x80x6
L17,L 65x65x8
L18,L 90x90x6
L19,L 90x90x7
L20,L 75x75x9
L21,L 100x100x7
L22,L 75x75x12
L23,L 90x90x10
L24,L 120x120x8
L25,L 100x100x10
L26,L 90x90x13
L27,L 130x130x9
L28,L 100x100x13
L29,L 130x130x12
L30,L 150x150x12
L31,L 130x130x15
L32,L 175x175x12
L33,L 150x150x15
L34,L 175x175x15
L35,L 150x150x19
L36,L 200x200x15
L37,L 200x200x20
L38,L 200x200x25
L39,L 250x250x25
L40,L 250x250x35
D1,2L 25x25x3
D2,2L 30x30x3
D3,2L 40x40x3
D4,2L 45x45x4
D5,2L 40x40x4
D6,2L 50x50x4
D7,2L 45x45x5
D8,2L 60x60x4
D9,2L 50x50x5
D10,2L 50x50x6
D11,2L 60x60x5
D12,2L 65x65x5
D13,2L 65x65x6
D14,2L 70x70x6
D15,2L 75x75x6
D16,2L 80x80x6
D17,2L 65x65x8
D18,2L 90x90x6
D19,2L 90x90x7
D20,2L 75x75x9
D21,2L 100x100x7
D22,2L 75x75x12
D23,2L 90x90x10
D24,2L 120x120x8
D25,2L 100x100x10
D26,2L 90x90x13
D27,2L 130x130x9
D28,2L 100x100x13
D29,2L 130x130x12
D30,2L 150x150x12
D31,2L 130x130x15
D32,2L 175x175x12
D33,2L 150x150x15
D34,2L 175x175x15
D35,2L 150x150x19
D36,2L 200x200x15
D37,2L 200x200x20
D38,2L 200x200x25
D39,2L 250x250x25
D40,2L 250x250x35
BS1,BOX 50x50x2.3
BS2,BOX 75x45x2.3
BS3,BOX 60x60x2.3
BS4,BOX 50x50x3.2
BS5,BOX 90x45x2.3
BS6,BOX 75x45x3.2
BS7,BOX 60x60x3.2
BS8,BOX 90x45x3.2
BS9,BOX 60x60x4
BS10,BOX 100x50x3.2
BS11,BOX 75x75x3.2
BS12,BOX 80x80x3.2
BS13,BOX 125x50x3.2
BS14,BOX 90x90x3.2
BS15,BOX 100x50x4
BS16,BOX 75x75x4
BS17,BOX 125x75x3.2
BS18,BOX 100x100x3.2
BS19,BOX 100x50x4.5
BS20,BOX 125x50x4
BS21,BOX 80x80x4.5
BS22,BOX 90x90x4
BS23,BOX 150x75x3.2
BS24,BOX 125x50x4.5
BS25,BOX 90x90x4.5
BS26,BOX 125x75x4
BS27,BOX 100x100x4
BS28,BOX 125x125x3.2
BS29,BOX 125x75x4.5
BS30,BOX 100x100x4.5
BS31,BOX 150x80x4.5
BS32,BOX 125x125x4.5
BS33,BOX 150x100x4.5
BS34,BOX 150x80x6
BS35,BOX 200x100x4.5
BS36,BOX 150x150x4.5
BS37,BOX 150x100x6
BS38,BOX 175x175x4.5
BS39,BOX 200x150x4.5
BS40,BOX 200x100x6
BS41,BOX 150x150x6
BS42,BOX 175x175x6
BS43,BOX 200x150x6
BS44,BOX 200x200x6
BS45,BOX 250x150x6
BS46,BOX 250x250x6
BS47,BOX 200x200x8
BS48,BOX 200x200x9
BS49,BOX 250x150x9
BS50,BOX 300x300x6
BS51,BOX 250x250x8
BS52,BOX 250x250x9
BS53,BOX 300x300x9
BS54,BOX 350x350x9
BS55,BOX 300x300x12
BS56,BOX 350x350x12
PS1,PIPE 60.5x3.2
PS2,PIPE 60.5x4.0
PS3,PIPE 76.3x3.2
PS4,PIPE 89.1x3.2
PS5,PIPE 101.6x3.2
PS6,PIPE 89.1x4.0
PS7,PIPE 114.3x3.2
PS8,PIPE 101.6x4.0
PS9,PIPE 114.3x4.5
PS10,PIPE 139.8x4.5
PS11,PIPE 165.2x4.5
PS12,PIPE 139.8x6.0
PS13,PIPE 190.7x4.5
PS14,PIPE 216.3x4.5
PS15,PIPE 165.2x6.0
PS16,PIPE 190.7x6.0
PS17,PIPE 216.3x6.0
PS18,PIPE 216.3x8.0"""

DENSITY = 7850.0

@st.cache_data
def build_db():
    db = {}
    for line in STEEL_TABLE.strip().split("\n"):
        parts = line.split(",", 1)
        if len(parts) == 2:
            db[parts[0].strip().upper()] = parts[1].strip()
    return db

SECTION_DB = build_db()


def get_nums(s):
    import re
    return [float(x) for x in re.findall(r'\d+(?:\.\d+)?', s)]


def calc_properties(section_raw: str):
    s = str(section_raw or "").upper().strip()
    n = get_nums(s)
    area_mm2 = 0.0
    perim_mm = 0.0
    stype = "UNKNOWN"

    if s.startswith("H ") and len(n) >= 4:
        stype = "H"
        D, B, tw, tf = n[0], n[1], n[2], n[3]
        area_mm2 = 2 * B * tf + (D - 2 * tf) * tw
        perim_mm = 4 * B + 2 * D - 2 * tw
    elif s.startswith("T ") and len(n) >= 4:
        stype = "T"
        D, B, tw, tf = n[0], n[1], n[2], n[3]
        area_mm2 = B * tf + (D - tf) * tw
        perim_mm = 2 * B + 2 * D
    elif s.startswith("2L") and len(n) >= 3:
        stype = "2L"
        a, b, t = n[0], n[1], n[2]
        area_mm2 = 2 * (a * t + b * t - t * t)
        perim_mm = 2 * (2 * (a + b))
    elif s.startswith("L ") and len(n) >= 3:
        stype = "L"
        a, b, t = n[0], n[1], n[2]
        area_mm2 = a * t + b * t - t * t
        perim_mm = 2 * (a + b)
    elif (s.startswith("BOX") or s.startswith("BS")) and len(n) >= 3:
        stype = "BOX"
        h, b, t = n[0], n[1], n[2]
        area_mm2 = h * b - (h - 2 * t) * (b - 2 * t)
        perim_mm = 2 * (h + b)
    elif (s.startswith("PIPE") or s.startswith("PS")) and len(n) >= 2:
        stype = "PIPE"
        D, t = n[0], n[1]
        area_mm2 = math.pi / 4 * (D * D - (D - 2 * t) ** 2)
        perim_mm = math.pi * D
    elif s.startswith("CH") and len(n) >= 4:
        stype = "CH"
        D, B, tw, tf = n[0], n[1], n[2], n[3]
        area_mm2 = 2 * B * tf + (D - 2 * tf) * tw
        perim_mm = 4 * B + 2 * D - 2 * tw

    kg_per_m = area_mm2 * 1e-6 * DENSITY
    paint_m2_per_m = perim_mm / 1000.0
    return stype, kg_per_m, paint_m2_per_m


def compute_row(row: dict) -> dict:
    mark = str(row.get("mark", "")).upper()
    section = row.get("section", "") or SECTION_DB.get(mark, "")
    stype, kg_per_m, paint_m2_per_m = calc_properties(section)
    qty = float(row.get("qty", 0) or 0)
    length = float(row.get("length", 0) or 0)
    total_len = qty * length
    weight = total_len * kg_per_m
    paint_area = total_len * paint_m2_per_m
    steel_rate = float(row.get("steel_rate", 0) or 0)
    paint_rate = float(row.get("paint_rate", 0) or 0)
    steel_cost = weight * steel_rate
    paint_cost = paint_area * paint_rate
    total_cost = steel_cost + paint_cost
    return {
        **row,
        "mark": mark,
        "section": section,
        "type": stype,
        "kg_per_m": kg_per_m,
        "total_length": total_len,
        "weight": weight,
        "paint_m2_per_m": paint_m2_per_m,
        "paint_area": paint_area,
        "steel_cost": steel_cost,
        "paint_cost": paint_cost,
        "total_cost": total_cost,
    }


def parse_csv_text(text: str, default_steel_rate=42.0, default_paint_rate=160.0):
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    if not lines:
        return []
    header = [h.strip().lower() for h in lines[0].split(",")]

    def idx(*names):
        for name in names:
            if name in header:
                return header.index(name)
        return -1

    mi = idx("mark", "member", "member mark")
    si = idx("section", "size")
    qi = idx("qty", "quantity", "no")
    li = idx("length_m", "length", "l")
    sri = idx("steel_rate", "steel rate", "baht/kg")
    pri = idx("paint_rate", "paint rate", "baht/m2")

    rows_out = []
    for line in lines[1:]:
        cols = [c.strip() for c in line.split(",")]
        def col(i, default=""):
            return cols[i] if 0 <= i < len(cols) else default
        mark = col(mi)
        rows_out.append({
            "mark": mark,
            "section": col(si) if si >= 0 else SECTION_DB.get(mark.upper(), ""),
            "qty": float(col(qi, "1") or 1),
            "length": float(col(li, "0") or 0),
            "steel_rate": float(col(sri, str(default_steel_rate)) or default_steel_rate),
            "paint_rate": float(col(pri, str(default_paint_rate)) or default_paint_rate),
        })
    return rows_out


# ─── SESSION STATE ─────────────────────────────────────────────────────────────
DEFAULT_ROWS = [
    {"mark": "H27",  "section": SECTION_DB.get("H27",  ""), "qty": 4,  "length": 6.0,  "steel_rate": 42.0, "paint_rate": 160.0},
    {"mark": "L15",  "section": SECTION_DB.get("L15",  ""), "qty": 10, "length": 3.0,  "steel_rate": 42.0, "paint_rate": 160.0},
    {"mark": "BS18", "section": SECTION_DB.get("BS18", ""), "qty": 8,  "length": 4.5,  "steel_rate": 48.0, "paint_rate": 160.0},
    {"mark": "PS9",  "section": SECTION_DB.get("PS9",  ""), "qty": 6,  "length": 5.0,  "steel_rate": 55.0, "paint_rate": 160.0},
]

if "rows" not in st.session_state:
    st.session_state.rows = deepcopy(DEFAULT_ROWS)


# ─── COMPUTE ───────────────────────────────────────────────────────────────────
computed = [compute_row(r) for r in st.session_state.rows]

total_length = sum(r["total_length"] for r in computed)
total_weight = sum(r["weight"] for r in computed)
total_paint  = sum(r["paint_area"] for r in computed)
total_cost   = sum(r["total_cost"] for r in computed)


# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-title">🏗️ Steel QTO + Unit Rate Calculator</div>
  <div class="app-sub">Structural steel quantity take-off · Thai Baht unit rates · Weight & painting area</div>
</div>
""", unsafe_allow_html=True)

# ─── KPI CARDS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-label">Total Length</div>
    <div class="kpi-value">{total_length:,.3f} m</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Steel Weight</div>
    <div class="kpi-value">{total_weight:,.2f} kg</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Painting Area</div>
    <div class="kpi-value">{total_paint:,.2f} m²</div>
  </div>
  <div class="kpi-card highlight">
    <div class="kpi-label">Total Amount</div>
    <div class="kpi-value">฿{total_cost:,.2f}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab_editor, tab_import, tab_results = st.tabs(["✏️  Member Table", "📥  CSV Import", "📊  Results View"])

# ════════════════════════════════════════════════════════════════
# TAB 1 — EDITOR
# ════════════════════════════════════════════════════════════════
with tab_editor:
    # Rate controls
    st.markdown('<div class="section-label">Default Rates</div>', unsafe_allow_html=True)
    rc1, rc2, rc3, rc4 = st.columns([2, 2, 1.5, 1.5])
    with rc1:
        default_steel = st.number_input("Steel supply/fab rate (THB/kg)", value=42.0, step=1.0, key="def_steel")
    with rc2:
        default_paint = st.number_input("Painting rate (THB/m²)", value=160.0, step=1.0, key="def_paint")
    with rc3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("Apply to all rows", key="apply_rates"):
            for r in st.session_state.rows:
                r["steel_rate"] = default_steel
                r["paint_rate"] = default_paint
            st.rerun()
    with rc4:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("＋ Add row", key="add_row"):
            st.session_state.rows.append({
                "mark": "", "section": "",
                "qty": 1, "length": 0.0,
                "steel_rate": default_steel, "paint_rate": default_paint
            })
            st.rerun()

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Member Schedule</div>', unsafe_allow_html=True)

    # Column headers
    hcols = st.columns([1.2, 2.2, 0.7, 0.9, 0.9, 0.9, 1.1, 1.1, 1.1, 1.1, 0.5])
    for col, label in zip(hcols, [
        "Mark", "Section", "Qty", "Length (m)", "kg/m",
        "Weight (kg)", "Paint (m²/m)", "Paint area (m²)",
        "Steel ฿/kg", "Paint ฿/m²", ""
    ]):
        col.markdown(f"<span style='font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#7d8590;font-family:IBM Plex Mono,monospace'>{label}</span>", unsafe_allow_html=True)

    rows_to_delete = []
    mark_changed = []

    for i, row in enumerate(st.session_state.rows):
        c = st.columns([1.2, 2.2, 0.7, 0.9, 0.9, 0.9, 1.1, 1.1, 1.1, 1.1, 0.5])
        mark_val = c[0].text_input("", value=row.get("mark", ""), key=f"mark_{i}", label_visibility="collapsed")
        # auto-fill section on mark change
        if mark_val.upper() != str(row.get("mark", "")).upper():
            row["mark"] = mark_val
            auto = SECTION_DB.get(mark_val.upper(), "")
            if auto:
                row["section"] = auto

        row["section"] = c[1].text_input("", value=row.get("section", ""), key=f"section_{i}", label_visibility="collapsed")
        row["qty"]    = c[2].number_input("", value=float(row.get("qty", 1)), min_value=0.0, step=1.0, key=f"qty_{i}", label_visibility="collapsed", format="%g")
        row["length"] = c[3].number_input("", value=float(row.get("length", 0)), min_value=0.0, step=0.001, key=f"len_{i}", label_visibility="collapsed", format="%.3f")

        cr = compute_row(row)
        c[4].markdown(f"<div style='padding:8px 0;font-family:IBM Plex Mono,monospace;font-size:0.78rem;color:#7d8590'>{cr['kg_per_m']:.3f}</div>", unsafe_allow_html=True)
        c[5].markdown(f"<div style='padding:8px 0;font-family:IBM Plex Mono,monospace;font-size:0.78rem;color:#c9d1d9'>{cr['weight']:.2f}</div>", unsafe_allow_html=True)
        c[6].markdown(f"<div style='padding:8px 0;font-family:IBM Plex Mono,monospace;font-size:0.78rem;color:#7d8590'>{cr['paint_m2_per_m']:.3f}</div>", unsafe_allow_html=True)
        c[7].markdown(f"<div style='padding:8px 0;font-family:IBM Plex Mono,monospace;font-size:0.78rem;color:#c9d1d9'>{cr['paint_area']:.2f}</div>", unsafe_allow_html=True)

        row["steel_rate"] = c[8].number_input("", value=float(row.get("steel_rate", 42)), min_value=0.0, step=1.0, key=f"sr_{i}", label_visibility="collapsed", format="%g")
        row["paint_rate"] = c[9].number_input("", value=float(row.get("paint_rate", 160)), min_value=0.0, step=1.0, key=f"pr_{i}", label_visibility="collapsed", format="%g")
        c[10].markdown(f"<div style='padding:8px 0;font-family:IBM Plex Mono,monospace;font-size:0.78rem;font-weight:700;color:#d29922'>฿{cr['total_cost']:,.0f}</div>", unsafe_allow_html=True)

        if c[10].button("✕", key=f"del_{i}", help="Remove row"):
            rows_to_delete.append(i)

    if rows_to_delete:
        st.session_state.rows = [r for i, r in enumerate(st.session_state.rows) if i not in rows_to_delete]
        st.rerun()

    # Footer totals row
    st.markdown("<hr style='border-color:#21262d;margin:4px 0'>", unsafe_allow_html=True)
    fc = st.columns([1.2, 2.2, 0.7, 0.9, 0.9, 0.9, 1.1, 1.1, 1.1, 1.1, 0.5])
    def ftot(col, val, bold=False, gold=False):
        color = "#d29922" if gold else "#c9d1d9"
        w = "800" if bold else "600"
        col.markdown(f"<div style='padding:6px 0;font-family:IBM Plex Mono,monospace;font-size:0.8rem;font-weight:{w};color:{color}'>{val}</div>", unsafe_allow_html=True)

    ftot(fc[0], "TOTAL", bold=True)
    ftot(fc[3], f"{total_length:.3f}")
    ftot(fc[5], f"{total_weight:.2f}")
    ftot(fc[7], f"{total_paint:.2f}")
    ftot(fc[10], f"฿{total_cost:,.2f}", bold=True, gold=True)

    # Export
    st.markdown("<div style='margin-top:1.2rem'></div>", unsafe_allow_html=True)
    exp_cols = st.columns([2, 1])
    with exp_cols[1]:
        df_export = pd.DataFrame(computed)
        cols_export = ["mark","section","type","qty","length","total_length","kg_per_m","weight","paint_m2_per_m","paint_area","steel_rate","paint_rate","steel_cost","paint_cost","total_cost"]
        df_export = df_export[[c for c in cols_export if c in df_export.columns]]
        csv_bytes = df_export.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("⬇ Export CSV", data=csv_bytes, file_name="steel_qto.csv", mime="text/csv; charset=utf-8")


# ════════════════════════════════════════════════════════════════
# TAB 2 — CSV IMPORT
# ════════════════════════════════════════════════════════════════
with tab_import:
    st.markdown('<div class="section-label">Paste CSV Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="basis-box">Supported columns: <strong>mark</strong>, section, <strong>qty</strong>, <strong>length_m</strong>, steel_rate, paint_rate. Section is auto-filled from mark if found in database.</div>', unsafe_allow_html=True)
    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)

    csv_default = "mark,qty,length_m,steel_rate,paint_rate\nH27,4,6,42,160\nL15,10,3,42,160\nBS18,8,4.5,48,160"
    csv_text = st.text_area("CSV data", value=csv_default, height=200, label_visibility="collapsed")

    ic1, ic2 = st.columns([1, 4])
    with ic1:
        if st.button("Import table", key="import_btn"):
            imported = parse_csv_text(csv_text,
                                      default_steel_rate=st.session_state.get("def_steel", 42),
                                      default_paint_rate=st.session_state.get("def_paint", 160))
            if imported:
                st.session_state.rows = imported
                st.success(f"Imported {len(imported)} rows.")
                st.rerun()
            else:
                st.error("Could not parse CSV. Check format.")

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Section Reference Table</div>', unsafe_allow_html=True)
    ref_search = st.text_input("Filter by mark or section", placeholder="e.g. H27 or BOX", key="ref_search")
    ref_data = [{"Mark": k, "Section": v} for k, v in SECTION_DB.items()]
    ref_df = pd.DataFrame(ref_data)
    if ref_search:
        mask = ref_df["Mark"].str.contains(ref_search.upper(), na=False) | ref_df["Section"].str.contains(ref_search.upper(), na=False, case=False)
        ref_df = ref_df[mask]
    st.dataframe(ref_df, height=300, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════
# TAB 3 — RESULTS VIEW
# ════════════════════════════════════════════════════════════════
with tab_results:
    if not computed:
        st.info("No rows to display.")
    else:
        st.markdown('<div class="section-label">Calculated Schedule</div>', unsafe_allow_html=True)
        display_df = pd.DataFrame([{
            "Mark":              r["mark"],
            "Section":           r["section"],
            "Type":              r["type"],
            "Qty":               int(r["qty"]),
            "Length (m)":        round(r["length"], 3),
            "Total L (m)":       round(r["total_length"], 3),
            "kg/m":              round(r["kg_per_m"], 3),
            "Weight (kg)":       round(r["weight"], 2),
            "Paint (m2/m)":      round(r["paint_m2_per_m"], 3),
            "Paint area (m2)":   round(r["paint_area"], 2),
            "Steel rate (THB/kg)":  r["steel_rate"],
            "Paint rate (THB/m2)":  r["paint_rate"],
            "Steel cost (THB)":  round(r["steel_cost"], 2),
            "Paint cost (THB)":  round(r["paint_cost"], 2),
            "Total (THB)":       round(r["total_cost"], 2),
        } for r in computed])

        # Export row — sits right above the table
        ex1, ex2, ex3 = st.columns([3, 1, 1])
        with ex2:
            # utf-8-sig writes the BOM that makes Excel open non-ASCII correctly
            csv_full = display_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                "⬇ Full CSV",
                data=csv_full,
                file_name="steel_qto_results.csv",
                mime="text/csv; charset=utf-8",
                key="export_results_full",
                use_container_width=True,
            )
        with ex3:
            summary_df = display_df[[
                "Mark", "Section", "Type", "Qty",
                "Total L (m)", "Weight (kg)", "Paint area (m2)",
                "Steel cost (THB)", "Paint cost (THB)", "Total (THB)"
            ]].copy()
            totals_row = {c: "" for c in summary_df.columns}
            totals_row["Mark"]             = "TOTAL"
            totals_row["Weight (kg)"]      = round(summary_df["Weight (kg)"].sum(), 2)
            totals_row["Paint area (m2)"]  = round(summary_df["Paint area (m2)"].sum(), 2)
            totals_row["Steel cost (THB)"] = round(summary_df["Steel cost (THB)"].sum(), 2)
            totals_row["Paint cost (THB)"] = round(summary_df["Paint cost (THB)"].sum(), 2)
            totals_row["Total (THB)"]      = round(summary_df["Total (THB)"].sum(), 2)
            summary_df = pd.concat([summary_df, pd.DataFrame([totals_row])], ignore_index=True)
            csv_summary = summary_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                "⬇ Summary CSV",
                data=csv_summary,
                file_name="steel_qto_summary.csv",
                mime="text/csv; charset=utf-8",
                key="export_results_summary",
                use_container_width=True,
            )

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Cost breakdown chart
        st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Cost Breakdown by Member</div>', unsafe_allow_html=True)
        chart_df = pd.DataFrame([{
            "Member": r["mark"] or f"Row {i+1}",
            "Steel cost (THB)": round(r["steel_cost"], 2),
            "Paint cost (THB)": round(r["paint_cost"], 2),
        } for i, r in enumerate(computed)])
        chart_df = chart_df.set_index("Member")
        st.bar_chart(chart_df, height=280)

        # Weight breakdown
        st.markdown('<div class="section-label">Weight by Member (kg)</div>', unsafe_allow_html=True)
        wt_df = pd.DataFrame({
            "Member": [r["mark"] or f"Row {i+1}" for i, r in enumerate(computed)],
            "Weight (kg)": [round(r["weight"], 2) for r in computed],
        }).set_index("Member")
        st.bar_chart(wt_df, height=240)

# ─── CALCULATION BASIS ─────────────────────────────────────────────────────────
with st.expander("ℹ️ Calculation Basis & Notes"):
    st.markdown("""
<div class="basis-box">
<strong>Weight</strong> = section area (mm²) × 7850 kg/m³ × total length (m)<br>
<strong>Painting area</strong> = external perimeter (mm) ÷ 1000 × total length (m)<br><br>
<strong>Supported profiles:</strong> H, T, CH (channel), L (angle), 2L (double angle), BOX/BS (hollow section), PIPE/PS (circular hollow)<br><br>
<strong>Database:</strong> H1–H60, T1–T60, C1–C16, L1–L40, D1–D40 (2L), BS1–BS56, PS1–PS18<br><br>
⚠️ For final purchase add allowance for: end plates, stiffeners, connection plates, bolts, welds, cutting loss, splices, galvanizing holes, and project-specific wastage.
</div>
""", unsafe_allow_html=True)
