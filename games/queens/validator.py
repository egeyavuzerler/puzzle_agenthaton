"""
games/queens/validator.py

QUEENS oyunu:
  - size = [N, N]  (KARE izgara; N, bölge sayısıyla aynı)
  - regions: N x N boyutunda 2D dizi, her hücrenin hangi renk bölgesine ait
    olduğunu gösteren tam sayı id'ler. Id'ler 0..N-1 aralığında olmalı ve
    N bölgenin hepsi kullanılmalı. (Bölgelerin bitişik olması ya da
    puzzle'ın tek çözümlü olması ZORUNLU DEĞİLDİR.)

Amaç: her satırda, her sütunda ve her renk bölgesinde TAM 1 kraliçe
olacak şekilde kraliçeleri yerleştir. İki kraliçe köşegen dahil
birbirine bitişik OLAMAZ.

Boyut sınırı: QUEENS_MIN_N <= N <= QUEENS_MAX_N. Sınırın amacı, "dev boyutlu
puzzle ile hakemi ve rakipleri boğmak"ı engellemektir.

Bilinmeyen anahtar yasaktır: puzzle yalnızca "game", "size", "regions"
anahtarlarını içerebilir (puzzle'a ekstra veri gömerek takımlar arası gizli
haberleşmeyi engellemek için).

Puzzle şeması:
{
  "game": "queens",
  "size": [8, 8],
  "regions": [[0,0,1,1,1,2,2,2], [0,0,1,1,3,3,2,2], ...]   # 8 satır, her biri 8 eleman
}

Solution şeması:
  solution = [[r0, c0], [r1, c1], ..., [r7, c7]]   # her satırdan tam 1 kraliçe pozisyonu
"""

from core.validator import BasePuzzleValidator, is_int

QUEENS_MIN_N = 4
QUEENS_MAX_N = 16
_ALLOWED_KEYS = {"game", "size", "regions"}


class QueensValidator(BasePuzzleValidator):
    game_name = "queens"

    # ---------- PUZZLE ŞEKLİ KONTROLÜ ----------
    def validate_puzzle_shape(self, puzzle: dict) -> tuple[bool, str | None]:
        if puzzle.get("game") != "queens":
            return False, "game alanı 'queens' değil"

        extra = set(puzzle) - _ALLOWED_KEYS
        if extra:
            return False, f"bilinmeyen anahtar(lar): {sorted(map(str, extra))} (izinli: game, size, regions)"

        size = puzzle.get("size")
        if not (isinstance(size, (list, tuple)) and len(size) == 2):
            return False, "size [rows, cols] formatında olmalı"
        rows, cols = size
        if not (is_int(rows) and is_int(cols)):
            return False, "size değerleri tam sayı olmalı"
        if rows != cols:
            return False, f"Queens ızgarası kare olmalı (size={[rows, cols]})"
        if not (QUEENS_MIN_N <= rows <= QUEENS_MAX_N):
            return False, f"size {rows}x{cols} sınır dışı (izinli: {QUEENS_MIN_N}..{QUEENS_MAX_N})"

        regions = puzzle.get("regions")
        if not isinstance(regions, list) or len(regions) != rows:
            return False, "regions satır sayısı size ile uyuşmuyor"
        for row in regions:
            if not isinstance(row, list) or len(row) != cols:
                return False, "regions sütun sayısı size ile uyuşmuyor"
            for rid in row:
                if not is_int(rid) or not (0 <= rid < rows):
                    return False, f"bölge id'si {rid!r} geçersiz (0..{rows - 1} arası tam sayı olmalı)"

        distinct_regions = {rid for row in regions for rid in row}
        if len(distinct_regions) != rows:
            return False, (
                f"bölge sayısı ({len(distinct_regions)}) satır sayısına ({rows}) eşit olmalı "
                "(her satır/sütun/bölgede tam 1 kraliçe olabilmesi için)"
            )

        return True, None

    # ---------- KANONİK FORM ----------
    def canonicalize(self, puzzle: dict) -> dict:
        """Bölge id'lerini ilk görülme sırasına (satır satır) göre 0..N-1 yeniden numaralar.
        Aynı puzzle'ın farklı numaralandırmaları tekrar sayılır ve id sırası bilgi taşıyamaz."""
        mapping: dict[int, int] = {}
        regions = []
        for row in puzzle["regions"]:
            new_row = []
            for rid in row:
                if rid not in mapping:
                    mapping[rid] = len(mapping)
                new_row.append(mapping[rid])
            regions.append(new_row)
        return {"game": "queens", "size": [puzzle["size"][0], puzzle["size"][1]], "regions": regions}

    # ---------- ÇÖZÜM KONTROLÜ ----------
    def validate_solution(self, puzzle: dict, solution) -> tuple[bool, str | None]:
        if not solution or not isinstance(solution, list):
            return False, "solution boş ya da liste değil"

        rows, cols = puzzle["size"]
        regions = puzzle["regions"]

        if len(solution) != rows:
            return False, f"kraliçe sayısı {len(solution)}, beklenen {rows}"

        positions = []
        for p in solution:
            if not (isinstance(p, (list, tuple)) and len(p) == 2 and is_int(p[0]) and is_int(p[1])):
                return False, f"geçersiz konum: {p!r} ([satır, sütun] tam sayıları olmalı)"
            positions.append((p[0], p[1]))

        seen_rows, seen_cols, seen_regions = set(), set(), set()
        for (r, c) in positions:
            if not (0 <= r < rows and 0 <= c < cols):
                return False, f"{(r, c)} grid dışında"
            if r in seen_rows:
                return False, f"satır {r} içinde birden fazla kraliçe"
            if c in seen_cols:
                return False, f"sütun {c} içinde birden fazla kraliçe"
            region_id = regions[r][c]
            if region_id in seen_regions:
                return False, f"bölge {region_id} içinde birden fazla kraliçe"
            seen_rows.add(r)
            seen_cols.add(c)
            seen_regions.add(region_id)

        # komşuluk kontrolü (köşegen dahil)
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                r1, c1 = positions[i]
                r2, c2 = positions[j]
                if abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1:
                    return False, f"{(r1, c1)} ve {(r2, c2)} birbirine bitişik (köşegen dahil)"

        return True, None
