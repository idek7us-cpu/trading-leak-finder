import io
import os

import pandas as pd
import streamlit as st

st.set_page_config(page_title="หารูรั่วในพอร์ต", page_icon="📉", layout="wide")

ACCENT = "#0E7C61"
DANGER = "#A5382A"

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
        tables = pd.read_html(file)
        df = max(tables, key=len)
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


# ---------------------------------------------------------------- หน้าเว็บ

st.title("📉 หารูรั่วในพอร์ต")
st.caption(
    "เสียบประวัติการเทรดของคุณ แล้วดูว่าเงินรั่วออกไปทางไหน — "
    "เครื่องมือนี้ไม่แนะนำการลงทุนและไม่รับประกันผลตอบแทนใดๆ มันแค่คำนวณสิ่งที่คุณทำไปแล้ว"
)

up = st.file_uploader(
    "ลากไฟล์ประวัติการเทรดมาวาง  (.csv จาก MT5, รายงาน .xlsx หรือ .html)",
    type=["csv", "xlsx", "xls", "html", "htm"],
)

HERE = os.path.dirname(os.path.abspath(__file__))
# sample_trades.csv คือไฟล์ตัวอย่างที่ตัดคอลัมน์ส่วนตัวออกแล้ว ตัวที่ขึ้น GitHub
SAMPLE = next(
    (p for p in (os.path.join(HERE, "sample_trades.csv"), os.path.join(HERE, "trades_clean.csv")) if os.path.exists(p)),
    None,
)

if up is not None:
    try:
        df = load(up)
        st.success(f"อ่านไฟล์สำเร็จ — {len(df)} ไม้")
    except Exception as e:
        st.error(f"อ่านไฟล์ไม่ได้: {e}")
        st.stop()
elif SAMPLE:
    with open(SAMPLE, "rb") as f:
        buf = io.BytesIO(f.read())
    buf.name = os.path.basename(SAMPLE)
    df = load(buf)
    st.info("กำลังแสดง**ข้อมูลตัวอย่าง** (บัญชีเดโม 21 วัน) — อัปโหลดไฟล์ของคุณด้านบนเพื่อดูของตัวเอง")
else:
    st.warning("อัปโหลดไฟล์เพื่อเริ่ม")
    st.stop()

if df.empty:
    st.error("ไม่พบไม้ที่ปิดแล้วในไฟล์นี้")
    st.stop()

# ---- ตัวเลขหลัก
total = df["net"].sum()
wins = df[df["net"] > 0]["net"]
losses = df[df["net"] < 0]["net"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("กำไรสุทธิ", f"{total:,.2f}")
c2.metric("จำนวนไม้", f"{len(df):,}")
c3.metric("อัตราชนะ", f"{len(wins)/len(df)*100:.1f}%")
c4.metric("Profit Factor", f"{wins.sum()/abs(losses.sum()):.2f}" if len(losses) and losses.sum() else "-")

st.divider()

# ---- ฟีเจอร์เรือธง
st.subheader("ถ้าไม้ที่แย่ที่สุดไม่เคยเกิดขึ้น")
st.caption("ลากดูว่าการขาดทุนของคุณกระจุกอยู่ที่ไม้ไม่กี่ไม้แค่ไหน")

n = st.slider("ตัดไม้ที่แย่ที่สุดออกกี่ไม้", 0, min(30, len(df) - 1), min(5, len(df) - 1))

worst = df.nsmallest(n, "net") if n else df.iloc[0:0]
kept = df.drop(index=worst.index).reset_index(drop=True)

curve = pd.DataFrame(
    {
        "ทุกไม้": df["net"].cumsum().reset_index(drop=True),
        f"ตัด {n} ไม้ที่แย่ที่สุดออก": kept["net"].cumsum(),
    }
)
st.line_chart(curve, color=[DANGER, ACCENT], height=380)

a, b, c = st.columns(3)
a.metric("ผลจริง", f"{total:,.2f}")
b.metric(f"ถ้าตัด {n} ไม้ออก", f"{kept['net'].sum():,.2f}", delta=f"{kept['net'].sum()-total:+,.2f}")
share = (worst["net"].sum() / total * 100) if n and total else 0
c.metric(f"{n} ไม้นี้คิดเป็น", f"{share:.0f}% ของผลรวม")

if n and kept["net"].sum() > 0 >= total:
    st.success(
        f"**ไม้ {n} ไม้ จากทั้งหมด {len(df)} ไม้ ({n/len(df)*100:.1f}%) "
        f"คือตัวที่เปลี่ยนพอร์ตนี้จากกำไรเป็นขาดทุน** — ปัญหาไม่ได้อยู่ที่กลยุทธ์ แต่อยู่ที่ไม้ไม่กี่ไม้"
    )

st.divider()

# ---- แยกดู
st.subheader("แยกดูว่ารูรั่วอยู่ตรงไหน")
t1, t2, t3, t4 = st.tabs(["ตามคู่เงิน", "ตามขนาดไม้", "ตามชั่วโมง", "ตามวัน"])

with t1:
    st.dataframe(df.groupby("symbol").apply(stats, include_groups=False).sort_values("กำไรสุทธิ"), width="stretch")
with t2:
    if df["volume"].notna().any():
        st.dataframe(df.groupby("volume").apply(stats, include_groups=False).sort_values("กำไรสุทธิ"), width="stretch")
        st.caption("ถ้าขนาดไม้ใหญ่ๆ กระจุกอยู่ฝั่งขาดทุน แปลว่าปัญหาคือการคุมความเสี่ยง ไม่ใช่กลยุทธ์")
    else:
        st.info("ไฟล์นี้ไม่มีข้อมูลขนาดไม้")
with t3:
    if df["time"].notna().any():
        h = df.assign(ชั่วโมง=df["time"].dt.hour).groupby("ชั่วโมง").apply(stats, include_groups=False)
        st.dataframe(h.sort_values("กำไรสุทธิ"), width="stretch")
        st.caption("เวลาตามเซิร์ฟเวอร์โบรกเกอร์ ไม่ใช่เวลาไทย")
    else:
        st.info("ไฟล์นี้ไม่มีข้อมูลเวลา")
with t4:
    if df["time"].notna().any():
        d = df.assign(วัน=df["time"].dt.day_name()).groupby("วัน").apply(stats, include_groups=False)
        st.dataframe(d.sort_values("กำไรสุทธิ"), width="stretch")
    else:
        st.info("ไฟล์นี้ไม่มีข้อมูลเวลา")

st.divider()
st.caption(
    "ข้อมูลทั้งหมดประมวลผลในเครื่องที่รันแอปนี้ ไม่มีการส่งออกไปที่ไหน · "
    "เครื่องมือนี้วิเคราะห์สิ่งที่เกิดขึ้นไปแล้วเท่านั้น ไม่ใช่คำแนะนำการลงทุน"
)
