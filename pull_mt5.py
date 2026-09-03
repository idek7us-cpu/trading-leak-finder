import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

if not mt5.initialize():
    print("!! ต่อกับ MT5 ไม่ได้ :", mt5.last_error())
    print("   ให้เปิด MT5 แล้วล็อกอินบัญชีค้างไว้ แล้วรันใหม่")
    raise SystemExit

acc = mt5.account_info()
print("=" * 60)
print("ต่อกับ MT5 สำเร็จ")
print("=" * 60)
if acc:
    kind = "บัญชีเดโม" if acc.trade_mode == 0 else "บัญชีจริง"
    print("โบรกเกอร์ :", acc.company)
    print("เซิร์ฟเวอร์:", acc.server, "(" + kind + ")")
    print("สกุลเงิน   :", acc.currency)
print()

deals = mt5.history_deals_get(datetime(2018, 1, 1), datetime.now())
mt5.shutdown()

if deals is None or len(deals) == 0:
    print("!! ไม่พบประวัติการเทรดในบัญชีนี้")
    raise SystemExit

df = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())
df["time"] = pd.to_datetime(df["time"], unit="s")

df.to_csv("deals_raw.csv", index=False, encoding="utf-8-sig")
print("ดึงข้อมูลดิบทั้งหมด :", len(df), "รายการ  -> บันทึกไว้ที่ deals_raw.csv")
print()

# type 2 = ฝาก/ถอนเงิน ไม่ใช่การเทรด | entry 1 = ไม้ที่ปิดแล้ว (ตัวที่มีกำไรขาดทุนจริง)
closed = df[(df["type"] != 2) & (df["entry"] == 1)].copy()
closed["net"] = closed["profit"] + closed["commission"] + closed["swap"]

print("=" * 60)
print("ภาพรวมการเทรดของคุณ")
print("=" * 60)
print("จำนวนไม้ที่ปิดแล้ว :", len(closed))
if len(closed):
    print("ช่วงเวลา          :", closed["time"].min().date(), "ถึง", closed["time"].max().date())
    print("คู่เงินที่เทรด      :", ", ".join(sorted(closed["symbol"].unique())[:12]))
    wins = closed[closed["net"] > 0]
    losses = closed[closed["net"] < 0]
    print()
    print("กำไรสุทธิรวม      :", round(closed["net"].sum(), 2))
    print("อัตราชนะ          :", round(len(wins) / len(closed) * 100, 1), "%")
    print("กำไรเฉลี่ยไม้ที่ชนะ :", round(wins["net"].mean(), 2) if len(wins) else "-")
    print("ขาดทุนเฉลี่ยไม้ที่แพ้:", round(losses["net"].mean(), 2) if len(losses) else "-")
    pf = wins["net"].sum() / abs(losses["net"].sum()) if len(losses) and losses["net"].sum() != 0 else None
    print("Profit Factor     :", round(pf, 2) if pf else "-")
    closed.to_csv("trades_clean.csv", index=False, encoding="utf-8-sig")
    print()
    print("ข้อมูลที่จัดระเบียบแล้ว -> trades_clean.csv")
