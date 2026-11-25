# Küresel Sıcaklık Analizi ve Tahmini

Bu proje, Global AI Hub × Akbank Makine Öğrenmesine Giriş Bootcamp'i sırasında başladı. 125 ülkedeki 321 şehirden 1995–2020 arasında toplanmış yaklaşık 2,8 milyon günlük sıcaklık ölçümünü inceledim ve günlük ortalama sıcaklığı tahmin etmeye çalıştım.

İlk sürümde ülke, yıl ve ay bilgisiyle kurduğum bir Random Forest için R² = 0,73 raporlamıştım. Sonradan fark ettim ki eğitim ve test setini rastgele ayırdığım için model test günlerinin hem öncesini hem sonrasını görüyordu; yaptığı şey tahmin değil, enterpolasyondu. Bu sürümde değerlendirmeyi zamana göre kurdum ve modelleri basit temel modellerle kıyasladım. Sonuç beklediğimden daha alçakgönüllü çıktı, ama bence çok daha dürüst.

![Trend ve mevsimsellik](images/02_trend_ve_mevsimsellik.png)

## Veri

Veriyi Kaggle'daki [Temperature of All Countries (1995–2020)](https://www.kaggle.com/datasets/subhamjain/temperature-of-all-countries-19952020) setinden aldım. Değişkenler `Region`, `Country`, `State`, `City`, `Month`, `Day`, `Year` ve `AvgTemperature` (°F). Ham dosya repoda [`Veri Seti.zip`](Veri%20Seti.zip) olarak duruyor, notebook onu doğrudan zip içinden okuyor.

Temizlik sırasında eksik ölçümleri gösteren `-99` değerlerini, hatalı yılları (200, 201), `Day = 0` satırlarını ve tekrarlanan şehir-gün kayıtlarını ayıkladım. İlk sürümde hedef °F, grafikler °C idi; bu karışıklığı giderip her şeyi °C'ye çevirdim.

Keşifçi analizde birkaç şey dikkatimi çekti. Sıcaklığın büyük kısmı coğrafya ve mevsimle açıklanıyor: ülke × ay ortalaması varyansın %73'ünü, şehir × ay ortalaması %87'sini açıklıyor. Isınma her bölgede görülüyor ama hızı farklı; 2015–19 ortalaması 1995–2004'e göre Orta Doğu'da +1,3 °C, Kuzey Amerika'da +1,0 °C, Güney/Orta Amerika'da +0,9 °C, Asya ve Avrupa'da +0,3 °C daha yüksek. Kış ile yaz arasındaki fark Avrupa'da ~19 °C, Kuzey Amerika'da ~23 °C iken Afrika ve Güney/Orta Amerika'da yıl boyunca sıcaklık neredeyse sabit. Ortalamada en sıcak ülkeler Haiti (29,6 °C), Nijerya ve Tayland; en soğuklar Moğolistan (−0,9 °C), İzlanda ve Norveç.

## Yöntem

Eğitim dönemini 1995–2015, test dönemini 2016–2019 olarak ayırdım. 2020'de yalnızca Ocak–Mayıs verisi olduğu için onu dışarıda bıraktım. Test setini en sonda bir kez açtım; hiperparametreleri eğitim yılları içinde (1995–2011 eğitim, 2012–2015 doğrulama) seçtim.

İki ayrı soru sordum:

1. Yakın geçmiş bilinmiyorsa, sadece ülke, yıl ve aydan ne kadar iyi tahmin yapılabilir? Burada ilk sürümdeki Random Forest'ı aynı hiperparametrelerle ülke × ay ve şehir × ay klimatolojisiyle kıyasladım.
2. Son birkaç günün ölçümleri biliniyorsa ertesi gün ne kadar iyi tahmin edilir? Burada `HistGradientBoostingRegressor` kullandım. Özellikler: son 3 günün sıcaklığı, son 7 günün ortalaması, şehir ve ülke klimatolojisi, dünkü anomali, yılın günü (sin/cos), yıl ve bölge. Temel model olarak "yarın = bugün" (persistence) aldım.

Sızıntıya karşı klimatolojiyi yalnızca eğitim yıllarından hesapladım, gecikmeli değerleri de sadece gerçekten bir önceki takvim gününe aitse kullandım. Belirsizlik için şehir düzeyinde bootstrap (1.000 tekrar) yaptım. Aynı şehrin günleri birbirinden bağımsız olmadığı için satır düzeyinde bootstrap güven aralıklarını yapay olarak daraltırdı.

## Sonuçlar

Köşeli parantezler şehir düzeyinde bootstrap ile %95 güven aralığı.

| Model | Test MAE (°C) |
|---|---|
| Ülke × ay klimatolojisi | 3,97 [3,73; 4,24] |
| Random Forest (ilk sürüm kurulumu) | 4,14 [3,91; 4,39] |
| Şehir × ay klimatolojisi | 2,80 [2,67; 2,91] |
| Persistence ("yarın = bugün") | 1,92 [1,84; 2,01] |
| Gradient boosting (ertesi gün) | 1,79 [1,71; 1,87] |

Benim için en öğretici sonuç, zamana dayalı bölmede ilk sürümdeki Random Forest'ın her ülkenin aylık ortalamasını kullanmaktan biraz daha kötü kalması oldu. Yani 0,73'lük R² aslında modelin bir şey öğrendiğini değil, değerlendirmenin hatalı olduğunu gösteriyordu.

Ertesi gün tahmininde gradient boosting persistence'ı %7 kadar geçiyor. Eşleştirilmiş şehir bootstrap'ında farkın güven aralığı −0,15 ile −0,13 °C arasında, yani küçük ama tutarlı bir iyileşme. Hata kışın en yüksek; kıtasal iklimdeki büyük günlük dalgalanmalar yüzünden Kuzey Amerika en zor bölge.

![Hata analizi](images/04_hata_analizi.png)

## Çalıştırmak için

```bash
git clone https://github.com/Memreu/global-temperature-prediction.git
cd global-temperature-prediction
pip install -r requirements.txt
jupyter lab GlobalTemperaturePredictionProject.ipynb
```

Notebook yaklaşık 3 dakikada baştan sona çalışıyor. İlk iki keşifçi grafiği yeniden üretmek için önce `unzip "Veri Seti.zip"`, sonra `python scripts/readme_grafikleri.py` yeterli. Kurulum yapmadan bakmak isterseniz [nbviewer](https://nbviewer.org/github/Memreu/global-temperature-prediction/blob/main/GlobalTemperaturePredictionProject.ipynb) veya Kaggle sürümleri ([memreu](https://www.kaggle.com/code/memreu/globaltemperaturepredictionproject), [kerembey](https://www.kaggle.com/code/kerembey/globaltemperaturepredictionproject)) var.

## Sınırlılıklar

Veride yalnızca ortalama sıcaklık var; yağış, nem, rüzgâr ve basınç eklenirse ertesi gün tahmini muhtemelen belirgin şekilde iyileşir. Şehirlerin önemli kısmı ABD'de olduğu için bölge sonuçları bu dengesizliği taşıyor. Klimatoloji 1995–2015 ortalaması olduğundan ısınma nedeniyle test döneminde biraz soğuk tarafta kalabilir; modeldeki yıl değişkeni bunu kısmen telafi ediyor. Sırada şehir bazında SARIMA veya durum uzayı modellerini aynı test düzeninde denemek var.

MIT lisansı ile paylaşıyorum. [LinkedIn](https://www.linkedin.com/in/memreu) · [Kaggle](https://www.kaggle.com/memreu)
