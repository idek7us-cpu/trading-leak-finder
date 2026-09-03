# ขั้นที่ 5 - ให้ Python อ่านประวัติเทรดจริงของเรา
import os
import pandas as pd

FILE = "history.xlsx"
here = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(here, FILE)

if not os.path.exists(path):
    print("!! ยังไม่เจอไฟล์:", FILE)
    print("   เอารายงานจาก MT5 มาวางในโฟลเดอร์นี้ แล้วตั้งชื่อว่า history.xlsx")
    print("   โฟลเดอร์นี้คือ:", here)
    print()
    print("   ไฟล์ที่มีอยู่ตอนนี้:")
    for f in os.listdir(here):
        print("    -", f)
    raise SystemExit

df = pd.read_excel(path, header=None)

print("=" * 60)
print("อ่านไฟล์สำเร็จ")
print("=" * 60)
print("จำนวนแถว    :", len(df))
print("จำนวนคอลัมน์ :", len(df.columns))
print()
print("--- 40 แถวแรก (ยังไม่จัดระเบียบ) ---")
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 250)
print(df.head(40).to_string())
