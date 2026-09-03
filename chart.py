import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("trades_clean.csv", parse_dates=["time"]).sort_values("time").reset_index(drop=True)

worst5 = df.nsmallest(5, "net").index
no_blowup = df.drop(index=worst5).reset_index(drop=True)
small = df[df["volume"] <= 0.30].reset_index(drop=True)

fig, ax = plt.subplots(figsize=(11, 6.2), dpi=140)
fig.patch.set_facecolor("#F3F6F4"); ax.set_facecolor("#FFFFFF")

ax.plot(range(len(df)), df["net"].cumsum(), color="#A5382A", lw=2.2,
        label=f"All 527 trades:  ${df['net'].sum():,.0f}")
ax.plot(range(len(no_blowup)), no_blowup["net"].cumsum(), color="#0E7C61", lw=2.4,
        label=f"Without the 5 worst trades:  ${no_blowup['net'].sum():,.0f}")
ax.plot(range(len(small)), small["net"].cumsum(), color="#8A6012", lw=1.6, ls="--",
        label=f"Only trades sized 0.30 lot or less:  ${small['net'].sum():,.0f}")

ax.axhline(0, color="#B9C6BE", lw=1)
ax.set_title("Same strategy. Same 21 days. The difference is 5 trades.",
             fontsize=15, fontweight="bold", color="#111815", pad=14)
ax.set_xlabel("Trade number (chronological)", fontsize=10, color="#4B5853")
ax.set_ylabel("Cumulative P/L (USD)", fontsize=10, color="#4B5853")
ax.legend(frameon=False, fontsize=10.5, loc="lower left")
ax.grid(alpha=.18, color="#7B8880")
for s in ("top", "right"): ax.spines[s].set_visible(False)
for s in ("left", "bottom"): ax.spines[s].set_color("#D5DED8")
ax.tick_params(colors="#4B5853", labelsize=9)
plt.tight_layout()
plt.savefig("equity_curve.png", facecolor=fig.get_facecolor())
print("บันทึกกราฟแล้ว: equity_curve.png")
print()
print(f"ทุกไม้ (527)            : {df['net'].sum():>10,.2f}")
print(f"ตัด 5 ไม้ที่แย่ที่สุดออก  : {no_blowup['net'].sum():>10,.2f}   <-- กำไร")
print(f"เฉพาะไม้ที่ <= 0.30 lot : {small['net'].sum():>10,.2f}")
