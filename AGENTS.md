# AGENTS.md: Puzzle Agents Hackathon (yapay zekâ kod asistanları için kurallar)

Bu depo bir hackathon katılımcı reposudur. Takımın teslim edeceği şey **tek bir Python dosyasıdır**
(`takim_adi.py`) ve içinde `MyGenerator` ile `MySolver` sınıfları bulunur. Oyun kuralları, puzzle
formatları, puanlama ve hakem değerleri `README.md` içinde yazılıdır; önce onu oku.

## Teslim kuralları (sert)

- **Dosya adı:** yalnızca harf, rakam ve alt çizgi; harfle başlar (`takim_adi.py`). Boşluk ve Türkçe
  karakter yok.
- **Sınıf adları:** `MyGenerator` ve `MySolver` (başka ad kullanma).
- **Import:** yalnızca Python standart kütüphanesi ve bu depodaki `core/`, `games/`, `agents_examples/`
  paketleri. numpy, scipy, ortools vb. **yoktur**. `arena/` ve `bank/` import edilemez. Göreli import ve
  başka yerel dosya yok: teslim **tek dosyadır**.
- **Ağ yok, dosya yazma yok:** hakem ortamında ağ kapalı ve dosya sistemi salt-okunurdur. Kod buna
  dayanmamalı.
- **Sözleşme:** `generate(game, difficulty, seed) -> (puzzle, solution)` ve
  `solve(puzzle, time_limit_s) -> SolveResult(solved=..., solution=...)`. Çıktılar JSON'a çevrilebilir
  olmalı (numpy dizisi / `set` yok). Aynı seed aynı puzzle'ı üretmeli.
- **Süreler:** `generate()` çağrısı başına 20 sn, `solve()` puzzle başına 5 sn (8 sn'de zorla durdurulur).
- **Puzzle şeması:** yalnızca oyunun bilinen anahtarları (ekstra anahtar reddedilir); boyut sınırları
  README'de. Puzzle'a gizli bilgi gömmek ve takımlar arası anlaşma yasaktır.

## Kontrol

Teslimden önce mutlaka çalıştır; çıktıda `[HATA]` kalmamalı:

```bash
python3 arena/check_submission.py --generator takim_adi:MyGenerator --solver takim_adi:MySolver
```

`[UYARI]` satırları teslimi engellemez ama hakemde sorun çıkarabilecek şeyleri gösterir
(dosyaya yazma, ağ vb.). Bu kontrol sandbox'ı yerelde uygulamaz; kuralları kendin gözet.

## Dokunma

`core/`, `arena/`, `bank/`, `games/*/validator.py` hakem kodudur: değiştirme (teslimde yalnızca
`takim_adi.py` alınır, bu dosyalarda yaptığın değişiklik hakemde yoktur). Referans ajanlar
(`games/<oyun>/reference_agent.py`) birer alt sınırdır: okuyup öğrenebilirsin, ama onları olduğu gibi
göndermek referans seviyesinde skor getirir.
