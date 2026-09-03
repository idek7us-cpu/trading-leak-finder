# วันที่ 1 - ไฟล์ Python ไฟล์แรกในชีวิต
print("=" * 40)
print("วันที่ 1 เริ่มแล้ว")
print("=" * 40)

# ลองสมมติผลการเทรด 5 ไม้ (หน่วยเป็นดอลลาร์)
profits = [120, -80, 45, -200, 310]

wins = [p for p in profits if p > 0]
losses = [p for p in profits if p < 0]

print("จำนวนไม้ทั้งหมด :", len(profits))
print("ไม้ที่ชนะ        :", len(wins))
print("ไม้ที่แพ้         :", len(losses))
print("กำไรรวม         :", sum(profits))
print("อัตราชนะ        :", round(len(wins) / len(profits) * 100, 1), "%")
print("กำไรเฉลี่ยต่อไม้ที่ชนะ :", round(sum(wins) / len(wins), 2))
print("ขาดทุนเฉลี่ยต่อไม้ที่แพ้ :", round(sum(losses) / len(losses), 2))
print()
print("ถ้าคุณเห็นข้อความนี้ แปลว่าคุณเขียนโค้ดเป็นแล้ว")
