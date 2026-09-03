import io
import os

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="หารูรั่วในพอร์ต",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

INK = "#111815"
MUTED = "#4B5853"
FAINT = "#7B8880"
LINE = "#D5DED8"
ACCENT = "#0E7C61"
DANGER = "#A5382A"
GROUND = "#F3F6F4"

# ---------------------------------------------------------------- หน้าตา

st.markdown(
    """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bai+Jamjuree:wght@500;600;700&family=IBM+Plex+Sans+Thai:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap">

<style>
/* ---- ซ่อนของที่ Streamlit แถมมา ---- */
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
footer, #MainMenu { visibility: hidden; height: 0; }
[data-testid="stAppViewContainer"] > .main { padding-top: 0; }
.block-container { padding: 2.2rem 3rem 4rem !important; max-width: 1180px; }

/* ---- พื้นฐาน ---- */
html, body, [class*="css"] { font-family: "IBM Plex Sans Thai", "Segoe UI", system-ui, sans-serif; }
[data-testid="stAppViewContainer"] { background: #F3F6F4; }
h1, h2, h3 { font-family: "Bai Jamjuree", "IBM Plex Sans Thai", sans-serif !important; letter-spacing: -.01em; }

/* ---- หัวเว็บ ---- */
.eyebrow {
  font-family: "IBM Plex Mono", monospace; font-size: 11px; letter-spacing: .16em;
  text-transform: uppercase; color: #7B8880; margin-bottom: 6px;
}
.hero-title {
  font-family: "Bai Jamjuree", sans-serif; font-weight: 700;
  font-size: clamp(30px, 4vw, 44px); line-height: 1.1; color: #111815; margin: 0 0 10px;
}
.hero-sub { color: #4B5853; font-size: 16px; line-height: 1.65; max-width: 62ch; margin: 0; }
.rule { height: 1px; background: #D5DED8; margin: 26px 0; border: 0; }

/* ---- แถวตัวเลขหลัก ---- */
.tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: #D5DED8;
         border: 1px solid #D5DED8; border-radius: 10px; overflow: hidden; }
@media (max-width: 760px) { .tiles { grid-template-columns: repeat(2, 1fr); } }
.tile { background: #FFFFFF; padding: 16px 20px 18px; }
.tile .k { font-size: 12.5px; color: #7B8880; letter-spacing: .02em; }
.tile .v { font-family: "IBM Plex Mono", monospace; font-variant-numeric: tabular-nums;
           font-size: 27px; font-weight: 600; line-height: 1.25; margin-top: 3px; color: #111815; }
.tile .v.pos { color: #0E7C61; }
.tile .v.neg { color: #A5382A; }
.tile .n { font-size: 11.5px; color: #7B8880; margin-top: 2px; }

/* ---- กล่องสรุปผล ---- */
.finding { border-left: 3px solid #0E7C61; background: #DBEDE6; padding: 15px 20px;
           border-radius: 0 8px 8px 0; margin: 6px 0 4px; font-size: 15px; line-height: 1.7; color: #111815; }
.finding.warn { border-left-color: #A5382A; background: #F7E4E0; }
.finding b { font-weight: 600; }

/* ---- ตัวอัปโหลด ---- */
[data-testid="stFileUploader"] section { border: 1.5px dashed #B9C6BE; background: #FFFFFF; border-radius: 10px; }
[data-testid="stFileUploader"] section:hover { border-color: #0E7C61; }

/* ---- สไลเดอร์ + แท็บ ---- */
[data-testid="stSlider"] [role="slider"] { border-color: #0E7C61 !important; }
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #D5DED8; }
.stTabs [data-baseweb="tab"] { font-size: 14.5px; padding: 8px 16px; }
.stTabs [aria-selected="true"] { color: #0E7C61 !important; font-weight: 600; }

/* ---- ตาราง ---- */
[data-testid="stDataFrame"] { border: 1px solid #D5DED8; border-radius: 8px; }

.foot { color: #7B8880; font-size: 12.5px; line-height: 1.7; max-width: 76ch; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- อ่านไฟล์

TIME_KEYS = ["time", "close time", "open time", "closetime", "เวลา"]
PROFIT_KEYS = ["net", "profit", "p/l", "pnl", "กำไร"]
SYMBOL_KEYS = ["symbol", "item", "instrument", "คู่เงิน"]
VOLUME_KEYS = ["volume", "size", "lots", "lot", "ปริมาณ"]


def _find(cols, keys):
    low = {str(c).strip().lower(): c for c in cols}
    for k in keys:
        if k in low:
            return low[k]
    for k in keys:
        for lc, orig in low.items():
            if k in lc:
                return orig
    return None


def load(file):
    """อ่านไฟล์แล้วปรับให้เป็นรูปแบบมาตรฐาน: time / symbol / volume / net"""
    name = file.name.lower()
    if name.endswith(".csv"):
        df = pd.read_csv(file)
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file)
    elif name.endswith((".html", ".htm")):
        df = max(pd.read_html(file), key=len)
    else:
        raise ValueError("รองรับเฉพาะไฟล์ .csv .xlsx .html")

    # รายงานจาก MT5 มักมีหัวกระดาษปนมา หาแถวที่เป็นหัวตารางจริง
    if _find(df.columns, PROFIT_KEYS) is None:
        for i in range(min(len(df), 15)):
            row = df.iloc[i].astype(str).tolist()
            if _find(row, PROFIT_KEYS) and _find(row, SYMBOL_KEYS):
                df.columns = row
                df = df.iloc[i + 1 :].reset_index(drop=True)
                break

    c_time = _find(df.columns, TIME_KEYS)
    c_prof = _find(df.columns, PROFIT_KEYS)
    c_sym = _find(df.columns, SYMBOL_KEYS)
    c_vol = _find(df.columns, VOLUME_KEYS)

    if c_prof is None:
        raise ValueError(
            "หาคอลัมน์กำไร/ขาดทุนไม่เจอ — คอลัมน์ที่มีในไฟล์: "
            + ", ".join(str(c) for c in df.columns[:15])
        )

    out = pd.DataFrame()
    out["net"] = pd.to_numeric(df[c_prof], errors="coerce")

    # ถ้ามีค่าคอมกับ swap แยกอยู่ ให้บวกรวมเป็นกำไรสุทธิ
    if str(c_prof).strip().lower() != "net":
        for extra in ("commission", "swap", "fee"):
            col = _find(df.columns, [extra])
            if col is not None:
                out["net"] = out["net"] + pd.to_numeric(df[col], errors="coerce").fillna(0)

    out["time"] = pd.to_datetime(df[c_time], errors="coerce") if c_time else pd.NaT
    out["symbol"] = df[c_sym].astype(str) if c_sym else "-"
    out["volume"] = pd.to_numeric(df[c_vol], errors="coerce") if c_vol else float("nan")

    out = out.dropna(subset=["net"])
    out = out[out["net"] != 0]
    if out["time"].notna().any():
        out = out.sort_values("time")
    return out.reset_index(drop=True)


def stats(g):
    w, l = g[g["net"] > 0]["net"], g[g["net"] < 0]["net"]
    return pd.Series(
        {
            "ไม้": len(g),
            "กำไรสุทธิ": round(g["net"].sum(), 2),
            "ชนะ %": round(len(w) / len(g) * 100, 1) if len(g) else 0,
            "ชนะเฉลี่ย": round(w.mean(), 2) if len(w) else 0,
            "แพ้เฉลี่ย": round(l.mean(), 2) if len(l) else 0,
            "PF": round(w.sum() / abs(l.sum()), 2) if len(l) and l.sum() else 0,
        }
    )


def tile(label, value, note="", tone=""):
    return f'<div class="tile"><div class="k">{label}</div><div class="v {tone}">{value}</div><div class="n">{note}</div></div>'


# ---------------------------------------------------------------- หน้าเว็บ

st.markdown(
    '<div class="eyebrow">เครื่องมือวิเคราะห์การเทรด</div>'
    '<h1 class="hero-title">หารูรั่วในพอร์ต</h1>'
    '<p class="hero-sub">เทรดเดอร์ส่วนใหญ่ไม่ได้เสียเงินจากทุกไม้เท่าๆ กัน '
    'แต่เสียจากไม้ไม่กี่ไม้ที่ซ้ำรูปแบบเดิม — เสียบประวัติการเทรดของคุณ แล้วดูว่ามันอยู่ตรงไหน</p>',
    unsafe_allow_html=True,
)
st.markdown('<hr class="rule">', unsafe_allow_html=True)

up = st.file_uploader(
    "ลากไฟล์ประวัติการเทรดมาวาง — รายงานจาก MT4/MT5 (.csv .xlsx .html)",
    type=["csv", "xlsx", "xls", "html", "htm"],
)

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = next(
    (p for p in (os.path.join(HERE, "sample_trades.csv"), os.path.join(HERE, "trades_clean.csv")) if os.path.exists(p)),
    None,
)

if up is not None:
    try:
        df = load(up)
        st.success(f"อ่านไฟล์สำเร็จ — {len(df):,} ไม้")
    except Exception as e:
        st.error(f"อ่านไฟล์ไม่ได้: {e}")
        st.stop()
elif SAMPLE:
    with open(SAMPLE, "rb") as f:
        buf = io.BytesIO(f.read())
    buf.name = os.path.basename(SAMPLE)
    df = load(buf)
    st.caption("กำลังแสดง **ข้อมูลตัวอย่าง** จากบัญชีเดโม 21 วัน — อัปโหลดไฟล์ด้านบนเพื่อดูของคุณเอง")
else:
    st.warning("อัปโหลดไฟล์เพื่อเริ่ม")
    st.stop()

if df.empty:
    st.error("ไม่พบไม้ที่ปิดแล้วในไฟล์นี้")
    st.stop()

total = df["net"].sum()
wins, losses = df[df["net"] > 0]["net"], df[df["net"] < 0]["net"]
pf = wins.sum() / abs(losses.sum()) if len(losses) and losses.sum() else 0
span = ""
if df["time"].notna().any():
    span = f'{df["time"].min():%d %b %Y} – {df["time"].max():%d %b %Y}'

st.markdown(
    '<div class="tiles">'
    + tile("กำไรสุทธิ", f"{total:,.2f}", span, "pos" if total > 0 else "neg")
    + tile("จำนวนไม้", f"{len(df):,}", f'{df["symbol"].nunique()} สินทรัพย์')
    + tile("อัตราชนะ", f"{len(wins)/len(df)*100:.1f}%", f"ชนะ {len(wins):,} · แพ้ {len(losses):,}")
    + tile("Profit Factor", f"{pf:.2f}" if pf else "—", "ต่ำกว่า 1.00 คือขาดทุน", "pos" if pf >= 1 else "neg")
    + "</div>",
    unsafe_allow_html=True,
)

st.markdown('<hr class="rule">', unsafe_allow_html=True)

# ---- ฟีเจอร์เรือธง
st.subheader("ถ้าไม้ที่แย่ที่สุดไม่เคยเกิดขึ้น")
st.caption("ลากสไลเดอร์ดูว่าการขาดทุนของคุณกระจุกอยู่ที่ไม้ไม่กี่ไม้แค่ไหน")

n = st.slider("ตัดไม้ที่แย่ที่สุดออกกี่ไม้", 0, min(30, len(df) - 1), min(5, len(df) - 1), label_visibility="collapsed")
st.caption(f"กำลังตัดออก **{n}** ไม้ จากทั้งหมด {len(df):,} ไม้")

worst = df.nsmallest(n, "net") if n else df.iloc[0:0]
kept = df.drop(index=worst.index).reset_index(drop=True)

curve = pd.concat(
    [
        pd.DataFrame({"ไม้ที่": range(1, len(df) + 1), "ทุน": df["net"].cumsum().values, "เส้น": "ผลจริง"}),
        pd.DataFrame({"ไม้ที่": range(1, len(kept) + 1), "ทุน": kept["net"].cumsum().values, "เส้น": f"ตัด {n} ไม้ที่แย่ที่สุดออก"}),
    ]
)

order = ["ผลจริง", f"ตัด {n} ไม้ที่แย่ที่สุดออก"]
chart = (
    alt.Chart(curve)
    .mark_line(strokeWidth=2.2)
    .encode(
        x=alt.X("ไม้ที่:Q", title="ลำดับไม้ (เรียงตามเวลา)", axis=alt.Axis(grid=False)),
        y=alt.Y("ทุน:Q", title="กำไรสะสม", axis=alt.Axis(gridColor="#E4EAE6", format=",.0f")),
        color=alt.Color(
            "เส้น:N",
            scale=alt.Scale(domain=order, range=[DANGER, ACCENT]),
            legend=alt.Legend(title=None, orient="bottom", labelFontSize=13),
        ),
        tooltip=[alt.Tooltip("เส้น:N"), alt.Tooltip("ไม้ที่:Q"), alt.Tooltip("ทุน:Q", format=",.2f")],
    )
    .properties(height=390)
    .configure_view(strokeWidth=0)
    .configure_axis(labelColor=MUTED, titleColor=FAINT, labelFontSize=11, titleFontSize=11,
                    domainColor=LINE, tickColor=LINE, labelFont="IBM Plex Mono", titleFont="IBM Plex Sans Thai")
    .configure_legend(labelFont="IBM Plex Sans Thai", labelColor=MUTED)
)
st.altair_chart(chart, use_container_width=True)

kept_total = kept["net"].sum()
share = (worst["net"].sum() / total * 100) if n and total else 0
st.markdown(
    '<div class="tiles">'
    + tile("ผลจริง", f"{total:,.2f}", f"{len(df):,} ไม้", "pos" if total > 0 else "neg")
    + tile(f"ถ้าตัด {n} ไม้ออก", f"{kept_total:,.2f}", f"{len(kept):,} ไม้", "pos" if kept_total > 0 else "neg")
    + tile("ส่วนต่าง", f"{kept_total - total:+,.2f}", "จากไม้เพียงไม่กี่ไม้", "pos")
    + tile(f"{n} ไม้นี้คิดเป็น", f"{share:.0f}%", "ของผลรวมทั้งพอร์ต")
    + "</div>",
    unsafe_allow_html=True,
)

if n and kept_total > 0 >= total:
    st.markdown(
        f'<div class="finding"><b>ไม้ {n} ไม้ จากทั้งหมด {len(df):,} ไม้ ({n/len(df)*100:.1f}%) '
        f"คือตัวที่พลิกพอร์ตนี้จากกำไรเป็นขาดทุน</b> — เมื่อการขาดทุนกระจุกตัวขนาดนี้ "
        "ปัญหามักไม่ได้อยู่ที่กลยุทธ์ แต่อยู่ที่การคุมขนาดไม้และการหยุดตัวเอง ลองดูแท็บ "
        "“ตามขนาดไม้” ข้างล่าง</div>",
        unsafe_allow_html=True,
    )

st.markdown('<hr class="rule">', unsafe_allow_html=True)

# ---- แยกดู
st.subheader("แยกดูว่ารูรั่วอยู่ตรงไหน")
st.caption("เรียงจากที่เสียเงินมากที่สุดไปน้อยที่สุด")

t1, t2, t3, t4 = st.tabs(["ตามสินทรัพย์", "ตามขนาดไม้", "ตามชั่วโมง", "ตามวัน"])
CFG = {"use_container_width": True}

with t1:
    st.dataframe(df.groupby("symbol").apply(stats, include_groups=False).sort_values("กำไรสุทธิ"), **CFG)
with t2:
    if df["volume"].notna().any():
        st.dataframe(df.groupby("volume").apply(stats, include_groups=False).sort_values("กำไรสุทธิ"), **CFG)
        st.caption("ถ้าไม้ขนาดใหญ่กระจุกอยู่ฝั่งขาดทุน แปลว่าปัญหาคือการคุมความเสี่ยง ไม่ใช่กลยุทธ์")
    else:
        st.info("ไฟล์นี้ไม่มีข้อมูลขนาดไม้")
with t3:
    if df["time"].notna().any():
        st.dataframe(df.assign(ชั่วโมง=df["time"].dt.hour).groupby("ชั่วโมง").apply(stats, include_groups=False).sort_values("กำไรสุทธิ"), **CFG)
        st.caption("เวลาตามเซิร์ฟเวอร์โบรกเกอร์ ไม่ใช่เวลาประเทศไทย")
    else:
        st.info("ไฟล์นี้ไม่มีข้อมูลเวลา")
with t4:
    if df["time"].notna().any():
        st.dataframe(df.assign(วัน=df["time"].dt.day_name()).groupby("วัน").apply(stats, include_groups=False).sort_values("กำไรสุทธิ"), **CFG)
    else:
        st.info("ไฟล์นี้ไม่มีข้อมูลเวลา")

st.markdown('<hr class="rule">', unsafe_allow_html=True)
st.markdown(
    '<div class="foot">ไฟล์ที่คุณอัปโหลดถูกประมวลผลในหน่วยความจำเท่านั้น ไม่มีการบันทึกหรือส่งต่อไปที่ใด<br>'
    "เครื่องมือนี้วิเคราะห์เฉพาะการเทรดที่เกิดขึ้นไปแล้ว <b>ไม่ใช่คำแนะนำการลงทุน ไม่ให้สัญญาณ "
    "และไม่รับประกันผลตอบแทนใดๆ</b></div>",
    unsafe_allow_html=True,
)
