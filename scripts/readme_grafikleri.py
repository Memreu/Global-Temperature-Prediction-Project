"""Ham veriden README'deki keşifçi analiz grafiklerini üretir. Önce 'Veri Seti.zip' açılmalıdır.

Kullanım:  python scripts/readme_grafikleri.py
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="whitegrid", font="DejaVu Sans")
plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 110, "axes.titleweight": "bold", "axes.titlesize": 13,
    "axes.labelsize": 11, "axes.spines.top": False, "axes.spines.right": False,
})
BLUE="#2E5EAA"; RED="#C0392B"; ORANGE="#E67E22"; GREEN="#29A36A"; GREY="#8C8C8C"; GOLD="#F2A900"
def save(fig, path):
    fig.tight_layout(); fig.savefig(path, bbox_inches="tight", facecolor="white"); plt.close(fig); print("kaydedildi:", path)

import pandas as pd, numpy as np, os
R=str(Path(__file__).resolve().parents[1]); os.makedirs(R+'/images',exist_ok=True)
df=pd.read_csv(R+'/GlobalLandTemperaturesByCountry.csv',low_memory=False)
print(len(df), (df.AvgTemperature==-99).sum(), df.Country.nunique(), df.City.nunique(), df.Year.min(), df.Year.max())
df=df[df.AvgTemperature!=-99.0].copy(); df["C"]=(df.AvgTemperature-32)*5/9
print("after",len(df))
ca=df.groupby("Country").C.mean().sort_values()
fig,ax=plt.subplots(1,2,figsize=(15,6))
t=ca.tail(15); ax[0].barh(t.index,t.values,color=RED); ax[0].set_title("En sıcak 15 ülke (1995–2020 ort., °C)")
b=ca.head(15)[::-1]; ax[1].barh(b.index,b.values,color=BLUE); ax[1].set_title("En soğuk 15 ülke (1995–2020 ort., °C)")
for a,v in [(ax[0],t.values),(ax[1],b.values)]:
    for i,x in enumerate(v): a.text(x+(.3 if x>=0 else -.3),i,f"{x:.1f}",va="center",ha="left" if x>=0 else "right",fontsize=9)
    a.set_xlabel("Ortalama sıcaklık (°C)")
ax[1].axvline(0,color="black",lw=.8)
save(fig,R+'/images/01_ulke_sicakliklari.png')
d=df[(df.Year>=1995)&(df.Year<=2019)]
ym=d.groupby(["Region","Year"]).C.mean().unstack(0)
an=ym-ym.loc[1995:2004].mean()
fig,ax=plt.subplots(1,2,figsize=(15,5.2))
pal=sns.color_palette("tab10",ym.shape[1])
for i,c in enumerate(an.columns): ax[0].plot(an.index,an[c].rolling(3,center=True,min_periods=1).mean(),lw=2,color=pal[i],label=c)
ax[0].axhline(0,color="black",lw=.8); ax[0].set_title("Bölgelere göre sıcaklık sapması (1995–2004 ortalamasına göre)"); ax[0].set_ylabel("Sapma (°C, 3 yıllık hareketli ort.)"); ax[0].legend(fontsize=8.5,ncol=2)
mm=d.groupby(["Region","Month"]).C.mean().unstack(1)
sns.heatmap(mm,cmap="RdYlBu_r",annot=True,fmt=".0f",cbar_kws={"label":"°C"},ax=ax[1],annot_kws={"size":8})
ax[1].set_title("Mevsimsellik: bölge × ay ortalama sıcaklık"); ax[1].set_xlabel("Ay"); ax[1].set_ylabel("")
save(fig,R+'/images/02_trend_ve_mevsimsellik.png')
g=d.groupby("Year").C.mean(); sl=np.polyfit(g.index,g.values,1)[0]; print("global slope per decade",sl*10)
print(an.loc[2015:2019].mean().round(2))
print("month share of variance: ", df.groupby(["Country","Month"]).C.transform("mean").var()/df.C.var())
