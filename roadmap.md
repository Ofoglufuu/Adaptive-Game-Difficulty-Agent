# Adaptive Game Difficulty Agent – Proje Roadmap

## Proje başlığı

**Adaptive Game Difficulty Agent – Dynamische Schwierigkeitsanpassung durch Spielersimulation**

## Ana amaç

Oyuncunun performansını analiz ederek oyunun zorluk seviyesini otomatik biçimde değiştiren bir sistem geliştirmek.

Proje sonunda iki sistem karşılaştırılacak:

* Sabit zorluk sistemi
* Adaptif zorluk sistemi

Temel araştırma sorusu:

> Kann ein adaptiver Schwierigkeitsagent eine ausgewogenere Spielerfahrung erzeugen als ein statisches Schwierigkeitssystem?

---

# 1. Aşama – Proje yapısını hazırlama

## Yapılacaklar

* GitHub reposunu oluştur
* Temel klasör yapısını oluştur
* README dosyasını hazırla
* Python ortamını ve gerekli kütüphaneleri belirle
* Projenin kapsamını kesinleştir

## Önerilen klasör yapısı

```text
adaptive-game-difficulty-agent/
├── README.md
├── requirements.txt
├── src/
│   ├── player.py
│   ├── game_simulation.py
│   ├── difficulty_agent.py
│   ├── experiment.py
│   └── visualization.py
├── results/
│   ├── figures/
│   └── data/
├── docs/
│   └── project_documentation.md
└── main.py
```

## Tamamlanma kriteri

Repo çalışır durumda olacak ve README içerisinde proje fikri, amaç ve araştırma sorusu bulunacak.

---

# 2. Aşama – Oyuncu modelini oluşturma

## Oyuncu tipleri

Üç farklı oyuncu profili oluşturulacak:

* Anfänger
* Durchschnittlicher Spieler
* Erfahrener Spieler

## Oyuncu özellikleri

Her oyuncunun şu tür özellikleri olabilir:

* `skill_level`
* `accuracy`
* `reaction_speed`
* `damage_efficiency`
* `survival_factor`

İlk sürümde sistemi basit tutmak için bu özellikler tek bir genel `skill_level` değeriyle de temsil edilebilir.

Örnek:

```text
Anfänger: 0.35
Durchschnittlicher Spieler: 0.60
Erfahrener Spieler: 0.85
```

## Tamamlanma kriteri

Farklı yetenek seviyelerine sahip oyuncular oluşturulabilecek.

---

# 3. Aşama – Oyun turu simülasyonunu geliştirme

## Bir oyun turunda kullanılacak girdiler

* Oyuncunun yetenek seviyesi
* Düşman sayısı
* Düşman hasarı
* Sağlık paketi oranı
* Mevcut zorluk seviyesi
* Rastgelelik faktörü

## Tur sonunda üretilecek sonuçlar

* Sieg veya Niederlage
* Kalan can
* Alınan hasar
* İsabet oranı
* Tur süresi
* Performans skoru

## Temel mantık

Oyuncunun kazanma ihtimali:

* oyuncunun yeteneği arttıkça yükselmeli,
* düşman sayısı arttıkça düşmeli,
* düşman hasarı arttıkça düşmeli,
* sağlık paketi oranı arttıkça yükselmeli.

Sonuçlara küçük bir rastgelelik de eklenmeli. Böylece aynı oyuncu ve aynı parametreler her zaman aynı sonucu üretmez.

## Tamamlanma kriteri

Tek bir oyun turu simüle edilecek ve anlamlı sonuçlar döndürecek.

---

# 4. Aşama – Zorluk modelini oluşturma

## Temel zorluk parametreleri

İlk sürümde yalnızca şu üç parametre kullanılacak:

* `enemy_count`
* `enemy_damage`
* `health_pack_rate`

Opsiyonel olarak daha sonra şunlar eklenebilir:

* enemy speed
* player health
* enemy accuracy
* time limit

## Zorluk seviyeleri

Örneğin 1 ile 10 arasında bir zorluk seviyesi kullanılabilir.

Her zorluk seviyesi, belirli parametre değerlerine karşılık gelir.

Örnek:

```text
Schwierigkeit 3:
enemy_count = 3
enemy_damage = 8
health_pack_rate = 0.30

Schwierigkeit 7:
enemy_count = 7
enemy_damage = 15
health_pack_rate = 0.10
```

## Tamamlanma kriteri

Bir zorluk seviyesi seçildiğinde ilgili oyun parametreleri otomatik üretilecek.

---

# 5. Aşama – Adaptif ajanı geliştirme

## Ajanın kullanacağı oyuncu verileri

Ajan son birkaç turu analiz edecek:

* Son 5 turun galibiyet oranı
* Arka arkaya kazanma veya kaybetme sayısı
* Ortalama kalan can
* Ortalama alınan hasar
* Ortalama performans skoru

## İlk sürümün karar mantığı

Örnek kurallar:

```text
Eğer son 5 turun galibiyet oranı %40'tan düşükse:
    zorluk seviyesini azalt

Eğer son 5 turun galibiyet oranı %80'den yüksekse:
    zorluk seviyesini artır

Aksi durumda:
    zorluk seviyesini koru
```

Ek kurallar:

```text
Oyuncu 3 kez arka arkaya kaybettiyse:
    zorluğu 1 azalt

Oyuncu 3 kez arka arkaya çok rahat kazandıysa:
    zorluğu 1 artır
```

## Güvenlik sınırları

* Minimum zorluk: 1
* Maksimum zorluk: 10
* Bir turda en fazla 1 seviye değişiklik
* Her tur zorluk değiştirmemek için bekleme süresi kullanılabilir

## Tamamlanma kriteri

Ajan oyuncu performansına göre zorluğu artırabilecek, azaltabilecek veya sabit tutabilecek.

---

# 6. Aşama – Sabit sistem ve adaptif sistem karşılaştırması

## Deney yapısı

Her oyuncu tipi için iki ayrı deney çalıştırılacak:

### Statisches System

Zorluk seviyesi bütün turlar boyunca aynı kalır.

### Adaptives System

Ajan performansa göre zorluk seviyesini değiştirir.

## Önerilen deney sayısı

Her oyuncu tipi için:

* 100 ila 500 tur
* Birden fazla random seed
* Aynı başlangıç zorluğu

Örnek:

```text
Anfänger:
- 300 tur statik sistem
- 300 tur adaptif sistem

Durchschnittlicher Spieler:
- 300 tur statik sistem
- 300 tur adaptif sistem

Erfahrener Spieler:
- 300 tur statik sistem
- 300 tur adaptif sistem
```

## Tamamlanma kriteri

Her iki sistem için sonuçlar CSV veya JSON dosyasına kaydedilecek.

---

# 7. Aşama – Değerlendirme ölçütleri

## Ana ölçütler

* Ortalama galibiyet oranı
* Hedef galibiyet oranından sapma
* Ortalama tur süresi
* Ortalama kalan can
* Ortalama zorluk seviyesi
* Zorluk değişikliği sayısı
* Arka arkaya mağlubiyet sayısı
* Sistemin kararlılığı

## Hedef değer

Örnek hedef galibiyet oranı:

```text
target_win_rate = 0.60
```

Ana değerlendirme:

```text
Hata = |gerçek galibiyet oranı - hedef galibiyet oranı|
```

Bu hata adaptif sistemde daha düşükse sistem başarılı kabul edilebilir.

## Tamamlanma kriteri

Statik ve adaptif sistem sayısal olarak karşılaştırılabilecek.

---

# 8. Aşama – Grafikler

## Hazırlanacak temel grafikler

1. Tur sayısına göre zorluk seviyesinin değişimi
2. Hareketli galibiyet oranının gelişimi
3. Statik ve adaptif sistemlerin galibiyet oranı karşılaştırması
4. Hedef galibiyet oranından sapma
5. Oyuncu tiplerine göre sistem performansı

## Opsiyonel grafikler

* Kalan can dağılımı
* Tur süreleri dağılımı
* Düşman hasarının zaman içerisindeki gelişimi
* Sağlık paketi oranının değişimi

## Tamamlanma kriteri

En az üç anlaşılır ve sunumda kullanılabilir grafik üretilecek.

---

# 9. Aşama – Live Demo

## Demo akışı

Canlı demoda yaklaşık 10–20 oyun turu gösterilecek.

Terminal çıktısı örneği:

```text
Runde 1
Spielertyp: Anfänger
Schwierigkeit: 6
Ergebnis: Niederlage
Restliche Gesundheit: 0
Agentenentscheidung: Schwierigkeit reduzieren

Runde 2
Spielertyp: Anfänger
Schwierigkeit: 5
Ergebnis: Niederlage
Agentenentscheidung: Schwierigkeit beibehalten

Runde 3
Spielertyp: Anfänger
Schwierigkeit: 5
Ergebnis: Sieg
Agentenentscheidung: Schwierigkeit beibehalten
```

Demo sonunda kısa bir özet gösterilecek:

```text
Zielgewinnrate: 60 %
Tatsächliche Gewinnrate: 58 %
Durchschnittliche Schwierigkeit: 4.8
```

## Tamamlanma kriteri

Tek komutla çalışan, kısa ve güvenilir bir demo hazırlanacak.

Örnek:

```bash
python main.py --demo
```

---

# 10. Aşama – Opsiyonel LLM entegrasyonu

Bu aşama yalnızca temel proje tamamen çalıştıktan sonra yapılacak.

## LLM'nin görevi

LLM, matematiksel kararı vermek zorunda olmayacak. Yalnızca ajanın verdiği kararı doğal dille açıklayacak.

Örnek:

```text
Die Schwierigkeit wurde reduziert, weil der Spieler drei Runden
hintereinander verloren und eine niedrige Trefferquote erreicht hat.
```

## Neden opsiyonel?

* API kotası riski
* İnternet bağlantısı riski
* Demo sırasında gecikme riski
* Projenin gereksiz karmaşıklaşması

Ana sistem LLM olmadan tamamen çalışabilir durumda olmalı.

---

# 11. Aşama – Almanca dokümantasyon

## Dokümantasyon bölümleri

1. Einleitung
2. Problemstellung
3. Forschungsfrage
4. Ziel des Projekts
5. Modellierung des Spielers
6. Modellierung des Schwierigkeitsgrades
7. Aufbau des Agenten
8. Simulationsmethode
9. Versuchsaufbau
10. Ergebnisse
11. Diskussion
12. Grenzen des Modells
13. Fazit
14. Ausblick

## Dokümantasyonda açıklanması gerekenler

* Oyuncu gerçekte değil, basitleştirilmiş bir modeldir.
* Galibiyet olasılığı matematiksel olarak hesaplanır.
* Rastgelelik, gerçek oyun davranışındaki belirsizliği temsil eder.
* Adaptif sistem hedef galibiyet oranına yaklaşmaya çalışır.
* Sistem gerçek oyuncu memnuniyetini doğrudan ölçmez.
* Galibiyet oranı, dengeli oyun deneyimi için yaklaşık bir gösterge olarak kullanılır.

## Tamamlanma kriteri

Kod, deney sonuçları ve grafiklerle uyumlu bir Almanca dokümantasyon hazırlanacak.

---

# 12. Aşama – 5 dakikalık sunum

## Önerilen sunum yapısı

### Slayt 1 – Problem

Sabit zorluk neden sorun olabilir?

### Slayt 2 – Proje fikri

Adaptif zorluk ajanı nasıl çalışıyor?

### Slayt 3 – Model

Oyuncu, zorluk ve oyun turu nasıl modelleniyor?

### Slayt 4 – Deney

Statik ve adaptif sistem nasıl karşılaştırıldı?

### Slayt 5 – Sonuçlar

Grafikler ve temel ölçümler.

### Slayt 6 – Live Demo ve sonuç

Ajanın zorluğu canlı değiştirmesi.

## Tamamlanma kriteri

Sunum 5 dakikayı aşmadan projenin problemi, yöntemi ve sonucunu anlatacak.

---

# Minimum uygulanabilir proje

Teslim için kesinlikle bulunması gerekenler:

* Üç oyuncu tipi
* Basitleştirilmiş oyun turu simülasyonu
* Sabit zorluk sistemi
* Kural tabanlı adaptif ajan
* Üç temel zorluk parametresi
* Statik ve adaptif sistem karşılaştırması
* En az üç grafik
* Almanca README ve dokümantasyon
* Çalışan live demo

---

# Opsiyonel özellikler

Temel proje bittikten sonra eklenebilir:

* Streamlit arayüzü
* Gerçek zamanlı kullanıcı girdisi
* LLM ile karar açıklaması
* Daha fazla oyuncu profili
* Öğrenen reinforcement learning ajanı
* Oyuncunun zamanla gelişmesi veya yorulması
* Farklı hedef galibiyet oranları
* Farklı oyun türleri
* Boss fight simülasyonu

Bu özellikler başlangıçta projeye eklenmemeli.

---

# Tahmini çalışma planı

## Gün 1

* Repo ve klasör yapısı
* Oyuncu modeli
* Tek tur oyun simülasyonu

## Gün 2

* Zorluk parametreleri
* Adaptif ajan
* Çok turlu simülasyon

## Gün 3

* Statik ve adaptif deneyler
* Sonuçların kaydedilmesi
* Temel testler

## Gün 4

* Grafikler
* Model ayarlamaları
* Hata düzeltmeleri

## Gün 5

* Almanca README
* Dokümantasyon
* Live demo hazırlığı

## Gün 6

* Sunum
* Demo provası
* Son kontroller

---

# Yeni sohbette ChatGPT'ye verilecek bilgi

Yeni bir sohbet açıldığında aşağıdakileri gönder:

1. Güncel README dosyası
2. Bu roadmap
3. Oluşturulan dosyaların listesi
4. Varsa çalışan kodlar
5. Alınan hatalar
6. Hocanın ek talepleri
7. Teslim tarihi

Ardından şu talimat verilebilir:

> Bu proje için daha önce hazırlanan roadmap burada. Güncel README ve mevcut dosyaları kontrol et. Roadmap'e göre hangi aşamada olduğumuzu belirle, eksikleri sırala ve bir sonraki adımı bana tek tek yaptır.
