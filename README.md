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

Şu an açık olan oyun(lar): **Queens**, **Tango**, **Slitherlink**.

---

## 1. Nasıl yarışılır?

1. **Yazın.** Takımınız bir `MyGenerator` ve bir `MySolver` sınıfı yazar (Bölüm 4).
2. **Üretin.** Hakem her takımın generator'ından her oyun için puzzle ister. Her
   puzzle **çözümüyle birlikte** verilir; çözüm doğrulanamazsa puzzle havuza girmez.
3. **Çözün.** Her takımın solver'ı, diğer takımların havuzlarındaki puzzle'ları
   sınırlı sürede çözmeye çalışır. Hakem her cevabı kendisi kontrol eder.
4. **Skor.** Solver skoru: rakip puzzle'larından doğru çözdüğünüz oran. Generator
   skoru: puzzle'larınızın rakipleri ne kadar zorladığı.

## 2. Puanlama ve kurallar

- Generator'ınız **açık olan her oyun için** puzzle üretebilmeli, solver'ınız
  hepsini çözmeyi denemeli. Bir oyunu atlamak size avantaj sağlamaz.
- Her generator çağrısı `(puzzle, solution)` döndürmek **zorundadır**. `solution`,
  puzzle'ın çözülebilir olduğunun kanıtıdır. Kanıt doğrulanamazsa puzzle havuza **girmez**.
  Çözülemez puzzle üretmek size puan kazandırmaz.
- **Havuzu eksiksiz doldurun.** Generator skorunuzda, havuzunuzda eksik kalan kısım
  (üretilemeyen, reddedilen, tekrar eden puzzle'lar; hiç puzzle'ı olmayan oyunlar dahil)
  rakipler tarafından çözülmüş sayılır.
- Havuzdaki puzzle'lar birbirinden **farklı** olmalıdır; birebir aynı puzzle ikinci kez girmez.
  Puzzle'ların tek çözümlü olması gerekmez: kuralları sağlayan **her** geçerli çözüm kabul edilir.
- Kodlarınız **izole** çalışır: ağ erişimi yoktur, dosya sistemi salt-okunurdur, bellek ve süre
  sınırı vardır. Her `generate()` çağrısı için varsayılan süre sınırı 20 sn'dir. Sınırı aşan ya da
  hata veren çağrı sadece o deneme için başarısız sayılır, sizi elemez.
- Skorlar eşitse sıralamayı hakemin ölçtüğü süre belirler: solver'larda daha hızlı olan,
  generator'larda puzzle'ları rakiplere daha uzun sürede çözdüren öndedir.
- Yalnızca Python standart kütüphanesi ve bu depodaki modüller kullanılabilir
  (örneğin numpy yoktur).

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

**Çözüm formatı:** kraliçe konumlarının listesi, `[[satır, sütun], ...]`.

```python
puzzle = {"game": "queens", "size": [4, 4],
          "regions": [[0, 0, 1, 1],
                      [0, 0, 1, 1],
                      [2, 2, 3, 3],
                      [2, 2, 3, 3]]}
solution = [[0, 1], [1, 3], [2, 0], [3, 2]]
```

### Tango (orta)

**Amaç:** Izgaradaki boş hücreleri güneş (`"sun"`) ya da ay (`"moon"`) ile doldurun.

**Kurallar**
1. Her satırda ve her sütunda **eşit sayıda** güneş ve ay olur (bloklu hücreler sayılmaz).
2. Yan yana ya da alt alta **3 aynı sembol** gelemez.
3. Bazı komşu hücre çiftleri arasında işaret vardır: `"equal"` (aynı sembol) ya da
   `"opposite"` (zıt sembol).
4. `prefilled` hücreler baştan verilmiştir, değişmez.
5. `blocked_cells` dokunulmaz hücrelerdir: sembol konmaz. Bu yüzden her satır ve
   sütundaki **serbest hücre sayısı çift** olmalıdır; aksi halde puzzle geçersizdir.

**Puzzle formatı:** `prefilled` ve `constraints` listeleri boş olabilir.

**Çözüm formatı:** `size` boyutunda 2B liste. Her hücre `"sun"` ya da `"moon"`;
bloklu hücreler `"blocked"` yazılır.

```python
puzzle = {"game": "tango", "size": [4, 4], "blocked_cells": [],
          "prefilled": [{"pos": [0, 0], "value": "sun"},
                        {"pos": [3, 3], "value": "moon"}],
          "constraints": [{"cell1": [0, 1], "cell2": [0, 2], "type": "equal"},
                          {"cell1": [0, 0], "cell2": [1, 0], "type": "opposite"},
                          {"cell1": [1, 1], "cell2": [1, 2], "type": "equal"}]}
solution = [["sun",  "moon", "moon", "sun"],
            ["moon", "sun",  "sun",  "moon"],
            ["moon", "sun",  "moon", "sun"],
            ["sun",  "moon", "sun",  "moon"]]
```

### Slitherlink (zor)

**Amaç:** Nokta ızgarası üzerinde **tek bir kapalı döngü** çizin.

**Kurallar**
1. Döngü, komşu noktaları yatay ya da dikey kenarlarla birleştirerek oluşur.
2. Her noktaya **0 ya da 2** kenar bağlanır (dallanma ve uç yok).
3. Döngü **tek parça**dır (birden fazla ayrı döngü olamaz).
4. Sayı olan her hücrenin çevresindeki döngü kenarı sayısı o sayıya eşit olur.
   Boş (`None`) hücrelerde kısıt yoktur.

**Puzzle formatı:** `size = [satır, sütun]` **hücre** sayısıdır; nokta ızgarası
(satır+1) × (sütun+1) boyutundadır. `clues[r][c]` 0–4 arası bir sayı ya da `None`'dur.

**Çözüm formatı:** döngünün kenarları, `[[[r1, c1], [r2, c2]], ...]`. Koordinatlar
**nokta** koordinatlarıdır ve komşu iki noktayı birleştirir.

**Zorunlu/yasak kenar (opsiyonel kural):** Generator'ınız isterseniz puzzle'a
`required_edges` (döngüde **kesinlikle olmalı**) ve `forbidden_edges` (döngüde
**kesinlikle olamaz**) ekleyebilir. Format çözümdeki kenar formatıyla aynıdır.
Zorunlu değildir; kullanırsanız witness çözümünüzün bunlarla tutarlı olduğundan
emin olun. Aynı kenar iki listede birden olamaz.

```python
# 2x2 hücre, tüm dış çerçeve bir döngü: her hücrenin 2 kenarı döngüde
puzzle = {"game": "slitherlink", "size": [2, 2],
          "clues": [[2, 2],
                    [2, 2]]}
solution = [[[0, 0], [0, 1]], [[0, 1], [0, 2]], [[0, 2], [1, 2]], [[1, 2], [2, 2]],
            [[2, 2], [2, 1]], [[2, 1], [2, 0]], [[2, 0], [1, 0]], [[1, 0], [0, 0]]]
```

Her oyunun tam kuralları ve format kontrolleri `games/<oyun>/validator.py` dosyasında yazıyor.

---

## 4. Generator ve Solver yazmak

```python
from core.base import BaseGeneratorAgent, BaseSolverAgent, SolveResult

class MyGenerator(BaseGeneratorAgent):
    name = "takim_adi_generator"

    def generate(self, game: str, difficulty: int, seed: int | None = None):
        ...  # game: "queens", "tango", "slitherlink"
        return puzzle, solution          # ZORUNLU: ikili dönüş

class MySolver(BaseSolverAgent):
    name = "takim_adi_solver"

    def solve(self, puzzle: dict, time_limit_s: float = 30.0) -> SolveResult:
        ...
        return SolveResult(solved=True, solution=solution)
```

- `difficulty`: 1 (kolay) – 10 (zor). Nasıl yorumlayacağınız size kalmış.
- `seed`: verilirse üretim deterministik olmalı (aynı seed, aynı puzzle).
- Puzzle ve solution **JSON'a çevrilebilir** olmalı: `dict`, `list`, `int`, `str`, `bool`, `None`.
  numpy dizisi ya da `set` döndürmeyin.
- Sınıf adlarını **`MyGenerator` ve `MySolver`** olarak bırakın (teslim bunlara göre çalıştırılır).

**Başlangıç:** `starter/my_agent.py` dosyasını kopyalayıp `takim_adi.py` olarak adlandırın.
Şablon olduğu haliyle **hemen çalışır**: açık olan oyunların hepsi için referans ajanlara
yönlenir. Oyunları tek tek kendi kodunuzla değiştirerek ilerleyin.

---

## 5. Kendi bilgisayarınızda deneyin

**Kurulum** (Python 3.10 ya da üstü):
```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install matplotlib          # sadece canlı izleme (run_live.py) için gerekli
```

**Göndermeden önce kontrol edin (önemli):**
```bash
python3 arena/check_submission.py --generator takim_adi:MyGenerator --solver takim_adi:MySolver
```
Hakemle aynı izole hat ile dener: generator'ınızın puzzle'larının kaçı havuza girerdi,
solver'ınız hata veriyor mu. Her sorun hangi oyunda ve neden olduğuyla yazdırılır.
`[HATA]` varsa düzeltin. `[UYARI]`lar teslimi engellemez ama bakmaya değer.
Dosyanız başka klasördeyse `--path klasor` ekleyin.

**Kendi puzzle havuzunuzu üretin:**
```bash
python3 bank/build_bank.py --generator takim_adi:MyGenerator --out bank/havuz.jsonl --per-type 50
```
Çıktıdaki `failed_solution` yüksekse generator'ınız çözülemez puzzle üretiyor demektir.

**Solver'ınızı havuza karşı çalıştırın:**
```bash
python3 arena/run_match.py --solver takim_adi:MySolver --bank bank/havuz.jsonl --time-limit 10
```

**Referans çözücüyü canlı izleyin:**
```bash
python3 arena/run_live.py --game queens --size 8
python3 arena/run_live.py --game tango --difficulty 5
python3 arena/run_live.py --game slitherlink --difficulty 4
```

---

## 6. Teslim

Kodunuzu **e-posta ile** gönderin.

| | |
| --- | --- |
| **Adres** | `[TESLİM E-POSTA ADRESİ]` |
| **Son saat** | 27 Kasım 2026, 17:30 |
| **Konu** | `Puzzle Agents - <takım adı>` |
| **Ek** | Tek bir `takim_adi.py` dosyası (adı takımınızın adı, boşluksuz ve Türkçe karakter içermeyen) |

**E-postanın içine yazın:** takım adı ve üyelerin adları.

**Teslimden önce kontrol listesi**
- [ ] `check_submission.py` **`[HATA]`sız** geçiyor.
- [ ] Dosyanızda `MyGenerator` ve `MySolver` sınıfları var.
- [ ] Dosya yalnızca Python standart kütüphanesi ve bu depodaki modülleri kullanıyor.
- [ ] Tek dosya yeterli. Başka yerel dosyalara bağımlı değil.

Birden fazla e-posta gönderirseniz **son e-posta** geçerli sayılır.
