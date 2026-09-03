import pandas as pd

df = pd.read_csv("trades_clean.csv", parse_dates=["time"])
df["hour"] = df["time"].dt.hour
df["dow"] = df["time"].dt.day_name()

def block(g):
    w = g[g["net"] > 0]["net"]
    l = g[g["net"] < 0]["net"]
    return pd.Series({
        "ไม้": len(g),
        "กำไรสุทธิ": round(g["net"].sum(), 2),
        "ชนะ%": round(len(w) / len(g) * 100, 1),
        "ชนะเฉลี่ย": round(w.mean(), 2) if len(w) else 0,
        "แพ้เฉลี่ย": round(l.mean(), 2) if len(l) else 0,
        "PF": round(w.sum() / abs(l.sum()), 2) if len(l) and l.sum() != 0 else 0,
    })

pd.set_option("display.width", 200)
print("=" * 70)
print("แยกตามคู่เงิน  (เรียงจากที่เสียเงินมากที่สุด)")
print("=" * 70)
by_sym = df.groupby("symbol").apply(block, include_groups=False).sort_values("กำไรสุทธิ")
print(by_sym.to_string())

print()
print("=" * 70)
print("ถ้าตัดคู่เงินที่แย่ที่สุดออก 1 ตัว")
print("=" * 70)
total = df["net"].sum()
print(f"กำไรสุทธิตอนนี้ (ทุกคู่)      : {total:,.2f}")
for sym in by_sym.index[:3]:
    without = df[df["symbol"] != sym]["net"].sum()
    print(f"  ถ้าไม่เคยเทรด {sym:<10} : {without:,.2f}   (ต่างกัน {without - total:+,.2f})")

print()
print("=" * 70)
print("แยกตามชั่วโมง (เวลาเซิร์ฟเวอร์โบรก) - เฉพาะชั่วโมงที่เทรด >= 10 ไม้")
print("=" * 70)
by_hour = df.groupby("hour").apply(block, include_groups=False)
by_hour = by_hour[by_hour["ไม้"] >= 10].sort_values("กำไรสุทธิ")
print(by_hour.to_string())

print()
print("=" * 70)
print("แยกตามวันในสัปดาห์")
print("=" * 70)
print(df.groupby("dow").apply(block, include_groups=False).sort_values("กำไรสุทธิ").to_string())

print()
print("=" * 70)
print("ขนาดไม้ (lot)")
print("=" * 70)
print(df.groupby("volume").apply(block, include_groups=False).sort_values("กำไรสุทธิ").head(10).to_string())

print()
print("=" * 70)
print("จังหวะการเทรด")
print("=" * 70)
days = (df["time"].max() - df["time"].min()).days + 1
print(f"ช่วงเวลา            : {days} วัน")
print(f"เฉลี่ยต่อวัน         : {len(df)/days:.1f} ไม้")
print(f"ไม้ที่แพ้หนักสุด      : {df['net'].min():,.2f}")
print(f"ไม้ที่ชนะหนักสุด      : {df['net'].max():,.2f}")
print(f"5 ไม้ที่แพ้หนักสุด รวม : {df.nsmallest(5,'net')['net'].sum():,.2f}  ({df.nsmallest(5,'net')['net'].sum()/total*100:.0f}% ของผลรวม)")
