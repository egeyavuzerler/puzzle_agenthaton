# Puzzle Agents Hackathon

Bu hackathon'da yapay zekâ ajanları yazıyorsunuz: bulmaca **üreten** bir
**generator** ve bulmaca **çözen** bir **solver**. Generator'ınız rakiplerin
zorlanacağı puzzle'lar üretir, solver'ınız rakiplerin puzzle'larını çözmeye çalışır.
Kazananı jüri değil, **ölçülen skor** belirler.

| | |
| --- | --- |
| **Tarih** | 27 Kasım 2026 |
| **Yer** | ÖzüX |
| **Kodlama** | 11:30 – 17:30 |
| **Sonuçlar** | 18:30 |
| **Takım** | En fazla 3 kişi |

## Program

| Saat | Ne olur |
| --- | --- |
| 11:30 | Açılış, **Queens (kolay)** verilir |
| 12:30 | **Tango (orta)** verilir |
| 14:30 | **Slitherlink (zor)** verilir |
| 17:30 | Kodların teslimi biter |
| 18:30 | Sonuçların açıklanması |

> **Yeni oyunlar bu depoya eklenir.** Programdaki saatlerde `git pull` ile (ya da depoyu yeniden
> indirerek) güncelleyin. `core/`, `games/`, `agents_examples/` ve `starter/` içindeki dosyaları
> düzenlemeyin; kopyalayıp kendi dosyanızda çalışın, böylece güncellemeler çakışmaz.

Şu an açık olan oyun(lar): **Queens**.

---

## 1. Nasıl yarışılır?

1. **Yazın.** Takımınız bir `MyGenerator` ve bir `MySolver` sınıfı yazar (Bölüm 4).
2. **Üretin.** Hakem her takımın generator'ından her oyun için puzzle ister. Her
   puzzle **çözümüyle birlikte** verilir; çözüm doğrulanamazsa puzzle havuza girmez.
3. **Çözün.** Her takımın solver'ı, diğer takımların havuzlarındaki puzzle'ları
   sınırlı sürede çözmeye çalışır. Hakem her cevabı kendisi kontrol eder.
4. **Skor.** Solver skoru: **rakip** takımların puzzle'larından doğru çözdüğünüz oran.
   Generator skoru: puzzle'larınızın **rakip** solver'ları ne kadar zorladığı
   (formüller Bölüm 2'de).

## 2. Puanlama ve kurallar

### Skor nasıl hesaplanır

- **Solver skoru:** rakip takımların havuzlarındaki puzzle'lardan doğru çözdüğünüz
  oran. **Kendi havuzunuz sayılmaz.** Her oyunun oranı ayrı hesaplanır ve oyunlar
  **eşit ağırlıkla** ortalanır (hiçbir oyun diğerinden fazla puan vermez). Hiç puzzle'ı
  olmayan bir havuz solver'ları cezalandırmaz.
- **Generator skoru:** `1 − (rakip solver'larının havuzunuzdaki ortalama çözme oranı)`.
  **Kendi solver'ınız sayılmaz.** Rakipler ne kadar az çözerse skorunuz o kadar yüksek.
  Havuzunuzda eksik kalan kısım (üretilemeyen, reddedilen, tekrar eden puzzle'lar; hiç
  puzzle'ı olmayan oyunlar dahil) rakipler tarafından **çözülmüş** sayılır. Oyunlar
  burada da eşit ağırlıklıdır.
- **Eşitlik:** skorlar eşitse sıralamayı hakemin ölçtüğü çözüm süresi belirler.
  Solver'larda ortalama çözüm süresi **kısa** olan, generator'larda rakiplerin çözmesi
  **uzun** süren öndedir. Süre, hakem makinesinde ölçülen ortalama duvar-saati süresidir.

### Hakem değerleri

| Ne | Değer |
| --- | --- |
| Havuz büyüklüğü | **oyun başına 100 puzzle** (3 oyun → takım başına 300 puzzle) |
| `difficulty` | puzzle sırasına göre 1, 2, … 10, 1, 2, … şeklinde **döngüsel**; hakem verir |
| `seed` | her puzzle için hakem verir (`None` gelmez), puzzle'lar arasında farklıdır |
| `generate()` süresi | çağrı başına **20 sn**; bir puzzle için en çok 20 deneme (farklı seed'lerle) |
| Üretimden vazgeçme | bir oyunda art arda 10 puzzle üretilemezse ya da oyun başına toplam **600 sn** dolarsa o oyundan vazgeçilir (kalan kısım eksik sayılır) |
| Generator süre payı | 100 puzzle için oyun başına 600 sn: **puzzle başına ortalama 6 sn'nin altında** kalın, yoksa havuz eksik kalır |
| Çözme bütçesi | solver'ınız **bir rakibin havuzu için en çok 250 sn** harcayabilir; dolunca o havuzun kalan puzzle'ları çözülmemiş sayılır. Ayrıca bir oyunda **art arda 30** hata/sert zaman aşımı olursa o oyunun kalanı çözülmemiş sayılır (sayaç oyun başına sıfırlanır) |
| `solve()` süresi | puzzle başına **5 sn** (`time_limit_s` olarak size verilir); **8 sn**'de süreç zorla durdurulur |
| Bellek / CPU | **1024 MB**; çağrı başına 60 sn CPU süresi |
| Python | 3.12; **yalnızca standart kütüphane** |

### Puzzle sınırları

| Oyun | Boyut | Ek kurallar |
| --- | --- | --- |
| Queens | N×N, **4 ≤ N ≤ 16** | bölge numaraları 0..N-1 arası tam sayı, N bölgenin hepsi kullanılır |

- Puzzle **yalnızca** oyunun şemasındaki anahtarları içerebilir; ekstra anahtar içeren
  puzzle reddedilir. Puzzle ve çözümün JSON boyutu en çok **100 KB** olabilir.
- Hakem, havuza yazmadan önce puzzle'ı **kanonik forma** çevirir (liste sırası, bölge
  numaralandırması ve kenar yönü normalize edilir). Bu yüzden böyle farklar bir puzzle'ı
  "farklı" yapmaz. Dönmüş ya da yansıtılmış bir puzzle ise **farklı** sayılır.

### Kurallar

- Generator'ınız **açık olan her oyun için** puzzle üretebilmeli, solver'ınız
  hepsini çözmeyi denemeli. Bir oyunu atlamak size avantaj sağlamaz.
- Her generator çağrısı `(puzzle, solution)` döndürmek **zorundadır**. `solution`,
  puzzle'ın çözülebilir olduğunun kanıtıdır. Kanıt doğrulanamazsa puzzle havuza **girmez**.
  Çözülemez puzzle üretmek size puan kazandırmaz.
- **Havuzu eksiksiz doldurun.** Eksik kalan kısım rakiplerce çözülmüş sayılır (yukarıya bakın).
- Havuzdaki puzzle'lar birbirinden **farklı** olmalıdır (kanonik forma göre); aynı puzzle
  ikinci kez girmez. Puzzle'ların tek çözümlü olması gerekmez: kuralları sağlayan **her**
  geçerli çözüm kabul edilir.
- **Takımlar arası gizli anlaşma yasaktır.** Puzzle'a bilgi gömerek (liste sırası, numaralandırma,
  ekstra veri ile) başka bir takımın solver'ına ipucu vermek ya da kod/strateji paylaşmak kural
  ihlalidir. Puzzle'a ekstra anahtar eklemek zaten reddedilir.
- **İzole çalışma:** kodlarınız hakem ortamında izole çalışır: ağ erişimi yoktur, dosya sistemi
  salt-okunurdur, bellek ve süre sınırlıdır. **Bu kısıtlar yalnızca hakem ortamında uygulanır;
  bu depodaki araçlar (`check_submission`, `run_match`, `build_bank`) bilgisayarınızda sandbox
  uygulamaz.** Yerelde çalışan ama ağ, dosya yazma ya da standart olmayan paket kullanan bir
  kod hakemde hata verir. `check_submission` bunları statik olarak tarayıp uyarır (Bölüm 5).
  Sınırı aşan ya da hata veren her `generate()` çağrısı yalnızca o deneme için başarısız,
  her `solve()` çağrısı yalnızca o puzzle için "çözülemedi" sayılır; sizi elemez.
- **Kullanılabilir modüller:** Python standart kütüphanesi ile bu depodaki `core/`, `games/`
  ve `agents_examples/` paketleri (hakem ortamında bunlar bulunur). `arena/` ve `bank/`
  import edilemez. numpy gibi paketler **yoktur**. Teslim **tek dosyadır**.
- **Referans ajanlar** (`games/<oyun>/reference_agent.py`, `agents_examples/baseline.py`) bir
  **alt sınırdır**. Starter şablonunu hiç değiştirmeden göndermek serbesttir ama referans
  seviyesinde skor getirir; referans çözücüler zor puzzle'larda zaman aşımına ya da kendi
  adım sınırlarına takılabilir. Onları geçmek sizin işiniz.

---

## 3. Oyunlar

### Queens (kolay)

**Amaç:** N×N ızgaraya N tane kraliçe yerleştirin.

**Kurallar**
1. Her **satırda** tam 1 kraliçe olur.
2. Her **sütunda** tam 1 kraliçe olur.
3. Her **renkli bölgede** tam 1 kraliçe olur.
4. Hiçbir iki kraliçe birbirine **komşu olamaz** (çapraz komşuluk dahil).

**Puzzle formatı:** `regions[r][c]`, o hücrenin bölge numarasıdır. Koordinatlar
(satır, sütun) olarak 0'dan başlar.

**Sınırlar:** N × N ızgara, 4 ≤ N ≤ 16. Bölge numaraları 0..N-1 arası tam sayıdır ve N
bölgenin hepsi kullanılmalıdır. Bölgelerin bitişik olması ya da puzzle'ın tek çözümlü
olması gerekmez.

**Çözüm formatı:** kraliçe konumlarının listesi, `[[satır, sütun], ...]`.

```python
puzzle = {"game": "queens", "size": [4, 4],
          "regions": [[0, 0, 1, 1],
                      [0, 0, 1, 1],
                      [2, 2, 3, 3],
                      [2, 2, 3, 3]]}
solution = [[0, 1], [1, 3], [2, 0], [3, 2]]
```

Her oyunun tam kuralları ve format kontrolleri `games/<oyun>/validator.py` dosyasında yazıyor.

---

## 4. Generator ve Solver yazmak

```python
from core.base import BaseGeneratorAgent, BaseSolverAgent, SolveResult

class MyGenerator(BaseGeneratorAgent):
    name = "takim_adi_generator"

    def generate(self, game: str, difficulty: int, seed: int | None = None):
        ...  # game: "queens"
        return puzzle, solution          # ZORUNLU: ikili dönüş

class MySolver(BaseSolverAgent):
    name = "takim_adi_solver"

    def solve(self, puzzle: dict, time_limit_s: float = 30.0) -> SolveResult:
        ...
        return SolveResult(solved=True, solution=solution)
```

- `difficulty`: 1 (kolay) – 10 (zor). Hakem 1–10 arasında döngüsel verir; nasıl
  yorumlayacağınız size kalmış.
- `seed`: hakem her puzzle için farklı bir seed verir (`None` gelmez). Aynı seed her zaman aynı
  puzzle'ı üretmelidir; farklı seed'ler farklı puzzle vermelidir (aynı puzzle'ı tekrar tekrar
  üretmek havuzu eksik bırakır).
- Puzzle ve solution **JSON'a çevrilebilir** olmalı: `dict`, `list`, `int`, `str`, `bool`, `None`.
  numpy dizisi ya da `set` döndürmeyin.
- Sınıf adlarını **`MyGenerator` ve `MySolver`** olarak bırakın (teslim bunlara göre çalıştırılır).

**Başlangıç:** `starter/my_agent.py` dosyasını kopyalayıp `takim_adi.py` olarak adlandırın.
Şablon `core` ve `agents_examples` modüllerini import eder; bunlar hakem ortamında bulunur, yani
dosyayı olduğu gibi teslim edebilirsiniz. Şablon olduğu haliyle **hemen çalışır**: açık olan oyunların hepsi için referans ajanlara
yönlenir. Oyunları tek tek kendi kodunuzla değiştirerek ilerleyin.

---

## 5. Kendi bilgisayarınızda deneyin

**Kurulum** (Python 3.10 ya da üstü):
```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install matplotlib          # sadece canlı izleme (run_live.py) için gerekli
```
`matplotlib` numpy'yi de kurar; bu yalnızca yerel araçlar içindir. Hakem ortamında numpy
**yoktur**, kodunuz numpy kullanmamalıdır (`check_submission` bunu `[HATA]` olarak gösterir).

**Göndermeden önce kontrol edin (önemli):**
```bash
python3 arena/check_submission.py --generator takim_adi:MyGenerator --solver takim_adi:MySolver
```
Hakemle aynı izole hat ile dener: generator'ınızın puzzle'larının kaçı havuza girerdi,
solver'ınız hata veriyor mu. Her sorun hangi oyunda ve neden olduğuyla yazdırılır.
`[HATA]` varsa düzeltin. `[UYARI]`lar teslimi engellemez ama bakmaya değer.
Dosyanız başka klasördeyse `--path klasor` ekleyin.

**Not:** bu kontrol sandbox'ı yerelde **uygulamaz** (ağ ve dosya yazma kısıtı yalnızca hakem
ortamındadır). Bunun yerine dosyanızı statik olarak tarar: dosya adı geçerli mi, yalnızca izinli
import'lar var mı (standart olmayan paketler `[HATA]`), sınıf adları `MyGenerator` ve `MySolver`
mı, dosyaya yazma ya da ağ kullanımı var mı (`[UYARI]`). Çözüm süresi sınırı hakemle aynıdır (5 sn).

**Kendi puzzle havuzunuzu üretin:**
```bash
python3 bank/build_bank.py --generator takim_adi:MyGenerator --out bank/havuz.jsonl --per-type 10
```
Hakem oyun başına **100** puzzle ister (yukarıdaki komutta hızlı deneme için 10 var; gerçek yükü `--per-type 100` ile deneyin). Yavaş bir generator'da büyük `--per-type` değerleri
dakikalar sürebilir. Çıktıdaki `failed_solution` yüksekse generator'ınız çözülemez puzzle üretiyor
demektir, `failed_shape` yüksekse puzzle'larınız şema/boyut kurallarına uymuyordur (ilk hata
mesajı yazdırılır).

**Solver'ınızı havuza karşı çalıştırın:**
```bash
python3 arena/run_match.py --solver takim_adi:MySolver --bank bank/havuz.jsonl --time-limit 5
```

**Kendinize karşı (ya da bir rakibe karşı) deneyin:**
```bash
python3 arena/self_play.py --agent takim_adi                 # kendi solver'ınız kendi havuzunuzu çözer
python3 arena/self_play.py --agent takim_adi --vs rakip_adi  # iki dosya birbirinin havuzunu çözer, mini skor tablosu
python3 arena/self_play.py --agent takim_adi --per-type 100  # hakemin yükü: oyun başına 100 puzzle
```
Generator + solver'ı tek komutla dener: havuzunuzun kaçı girdi, hangi oyunda kaç puzzle çözüldü, ortalama süre, zaman aşımı/hata sayısı. `--vs` ile iki ajan birbirini yarışma formülüyle ölçer (solver skoru = rakibin havuzundaki çözme oranınız, generator skoru = 1 − rakibin sizin havuzunuzdaki oranı). Dosyanız repo kökünde değilse `--path klasor` ekleyin. Süre sınırları hakemle aynıdır (5 sn / 8 sn); ağ/dosya kısıtı yerelde uygulanmaz. **Hakem her oyundan 100 puzzle ile test edecek**: `--per-type 100` yavaş ajanlarda dakikalar sürebilir, önceden bir kez deneyin.

**Referans çözücüyü canlı izleyin:**
```bash
python3 arena/run_live.py --game queens --size 8
```
Bu araç yalnızca **referans** çözücüyü gösterir, `MySolver`'ınızı çalıştırmaz. Canlı pencere
için `tkinter` gerekir (Linux'ta `sudo apt install python3-tk`); yoksa araç yalnızca
ilerlemeyi yazdırır.

---

## 6. Teslim

Kodunuzu **e-posta ile** gönderin.

| | |
| --- | --- |
| **Adres** | `egeyavuzerler@icloud.com` |
| **Son saat** | 27 Kasım 2026, 17:30 |
| **Konu** | `Puzzle Agents - <takım adı>` |
| **Ek** | Tek bir `takim_adi.py` dosyası (adı takımınızın adı, boşluksuz ve Türkçe karakter içermeyen) |

**E-postanın içine yazın:** takım adı ve üyelerin adları.

**Ek engellenirse:** bazı posta sistemleri `.py` eklerini siler. Bu durumda aynı dosyayı `.zip`
içinde gönderin (zip'in içinde yalnızca `takim_adi.py` olsun). Son 10 dakikaya kalmayın; gönderdiğinizden
emin olmak için gönderilmiş öğelerinizi kontrol edin.

**Teslimden önce kontrol listesi**
- [ ] `check_submission.py` **`[HATA]`sız** geçiyor.
- [ ] Dosya adı yalnızca harf, rakam ve alt çizgiden oluşuyor (`takim_adi.py`).
- [ ] Dosyanızda `MyGenerator` ve `MySolver` sınıfları var.
- [ ] Dosya yalnızca Python standart kütüphanesini ve `core/`, `games/`, `agents_examples/`
      paketlerini import ediyor (numpy yok).
- [ ] Tek dosya yeterli. Başka yerel dosyalara bağımlı değil.

Birden fazla e-posta gönderirseniz **son e-posta** geçerli sayılır.

---

## 7. Sık yapılan hatalar

Önceki denemelerde en çok görülenler:

1. **Starter'ı olduğu gibi teslim etmek.** Referans seviyesinde skor getirir; asıl skor rakip havuzlarına karşı ölçülür.
2. **Dosya adında boşluk veya Türkçe karakter kullanmak.** `takim_adi.py` biçimini kullanın; `check_submission` bunu `[HATA]` olarak gösterir.
3. **Yerel kontrolden geçmeyi hakemde de geçmek sanmak.** numpy importu ve dosya yazma yerelde çalışabilir, hakem ortamında çalışmaz (Bölüm 2).
4. **Generator'da duvar saatine bağlı bütçe kullanmak.** Aynı seed farklı makinede ya da yükte farklı puzzle verir; sözleşme "aynı seed, aynı puzzle" ister. Bütçeyi düğüm ya da çağrı sayacına bağlayın, süreyi yalnızca emniyet için kullanın.
5. **`seed=None`'ı sabit bir değere çevirmek.** Yerelde her çağrı aynı puzzle'ı üretir ve testleriniz sizi yanıltır. Hakem seed'i her zaman verir.
6. **Yavaş generator yazmak.** Oyun başına 600 sn bütçe (100 puzzle → puzzle başına ortalama 6 sn) dolunca havuz eksik kalır; eksik kısım rakiplerce çözülmüş sayılır.
7. **"Çözülebilir" ile "tek çözümlü"yü karıştırmak.** Tekliğe güveniyorsanız bunu çözüm sayarak test edin; "bir çözüm buldum" testi hatayı gizler.
8. **Queens generator'ında bölge numaralarını 0..N-1 dışına ya da ızgarayı kare olmayan bir şekle çıkarmak.** Hakem bunları reddeder, puzzle havuza girmez.
9. **Uzun ömürlü solver'da sınırsız önbellek tutmak.** Bellek sınırı 1 GB; `lru_cache(maxsize=None)` gibi önbellekler sınırı aşabilir.
10. **Rastgele yeniden başlatma olmadan derin arama yapmak.** Büyük puzzle'larda bazı örnekler ağır kuyruk yüzünden zaman aşımına düşer; büyüyen bütçeli yeniden başlatma bunu çözer.
11. **Puzzle zorluğunu yalnızca referans solver'a karşı ölçmek.** Referansın çözemediği puzzle'ı propagation kullanan bir solver milisaniyede çözebilir.
