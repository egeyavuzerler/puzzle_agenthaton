"""
arena/self_play.py -- KENDİNİZİ (ya da bir rakibi) YEREL OLARAK DENEYİN

Hakemin yaptığı işin küçük bir kopyası: generator'ınız puzzle havuzu üretir, solver'ınız
o havuzu çözer, sonuç oyun oyun yazdırılır.

  1) Kendinize karşı (varsayılan): kendi solver'ınız kendi havuzunuzu çözer.
         python3 arena/self_play.py --agent takim_adi
     (takim_adi.py repo kökündeyse; başka klasördeyse --path klasor ekleyin)

  2) Başka bir ajana karşı: iki dosya birbirinin havuzunu çözer; hakemin skor formülüyle
     iki yönlü sonuç verir.
         python3 arena/self_play.py --agent takim_adi --vs rakip_adi

  3) Hakem yük denemesi: hakem OYUN BAŞINA 100 puzzle ile test edecek.
         python3 arena/self_play.py --agent takim_adi --per-type 100

NOT: Bu araç hakemin sandbox'ını (ağ/dosya kısıtı) UYGULAMAZ; yalnızca süre sınırlarını (5 sn
yumuşak, 8 sn sert) uygular. Teslimden önce yine arena/check_submission.py çalıştırın.
Kendi havuzunuz gerçek skorda sayılmaz; buradaki "kendine karşı" sayısı yalnızca bir fikir verir.
Süre: 100 puzzle/oyun, 3 oyun için yavaş generator/solver'larda dakikalar, bazen yarım saat sürebilir.
"""

import argparse
import importlib
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from arena.run_match import run_match                      # noqa: E402
from arena.sandboxed_solver import SandboxedSolver          # noqa: E402
from bank.build_bank import build_bank                      # noqa: E402
from core.registry import _auto_register_defaults, list_games   # noqa: E402


def _load(module: str, cls: str):
    return getattr(importlib.import_module(module), cls)


def _rate(summary: dict, games: list[str]) -> float:
    """Oyunların eşit ağırlıklı ortalaması; havuzda hiç puzzle'ı olmayan oyun 0 sayılmaz, atlanır."""
    rates = []
    for g in games:
        stat = summary["per_game"].get(g)
        if stat and stat["total"]:
            rates.append(stat["solved"] / stat["total"])
    return sum(rates) / len(rates) if rates else 0.0


def _make_pool(name: str, per_type: int, games: list[str], out_dir: Path):
    path = out_dir / f"{name}_bank.jsonl"
    t0 = time.time()
    print(f"[{name}] generator havuz üretiyor ({per_type} puzzle/oyun, oyunlar: {', '.join(games)}) ...", flush=True)
    gen = _load(name, "MyGenerator")()
    build_bank(gen, per_type, str(path), games=games)
    n = sum(1 for _ in open(path)) if path.exists() else 0
    print(f"[{name}] havuz hazır: {n}/{per_type * len(games)} puzzle, {time.time() - t0:.0f} sn", flush=True)
    return path, n


def _solve(solver_name: str, pool: Path, pool_owner: str, time_limit: float, hard: float):
    solver = SandboxedSolver(f"{solver_name}:MySolver", mode="local",
                             extra_pythonpath=[os.environ.get("SELF_PLAY_PATH", str(ROOT))])
    t0 = time.time()
    try:
        summary = run_match(solver, str(pool), time_limit, hard, 1024, 60, None)
    finally:
        solver.close()
    print(f"[{solver_name}] solver, {pool_owner} havuzunu çözdü: {time.time() - t0:.0f} sn", flush=True)
    return summary


def _report(title: str, summary: dict, games: list[str]):
    print(f"\n  {title}")
    print(f"  {'oyun':<14}{'havuz':>7}{'çözülen':>9}{'oran':>8}{'ort.süre':>10}{'zaman aşımı':>13}{'hata':>6}")
    for g in games:
        s = summary["per_game"].get(g)
        if not s or not s["total"]:
            print(f"  {g:<14}{0:>7}   (havuzda bu oyundan puzzle yok)")
            continue
        avg = s["total_time"] / s["total"]
        print(f"  {g:<14}{s['total']:>7}{s['solved']:>9}{s['solved'] / s['total']:>8.3f}{avg:>9.2f}s"
              f"{s['timeouts']:>13}{s['errors']:>6}")
        if s.get("first_error"):
            print(f"      ilk hata: {s['first_error'][:160]}")
    print(f"  genel (oyun-eşit ağırlıklı) çözme oranı: {_rate(summary, games):.3f}")


def main():
    ap = argparse.ArgumentParser(description="Kendi ajanınızı kendinize ya da bir rakibe karşı deneyin.")
    ap.add_argument("--agent", required=True, help="takım dosyanızın modül adı (takim_adi, .py olmadan); "
                    "içinde MyGenerator ve MySolver olmalı")
    ap.add_argument("--vs", default=None, help="karşı ajanın modül adı (isteğe bağlı)")
    ap.add_argument("--path", default=None, help="dosyalar repo kökünde değilse klasörü")
    ap.add_argument("--per-type", type=int, default=10,
                    help="oyun başına puzzle (varsayılan 10; hakem 100 kullanacak)")
    ap.add_argument("--games", default=None, help="virgüllü oyun listesi (varsayılan: açık tüm oyunlar)")
    ap.add_argument("--time-limit", type=float, default=5.0)
    ap.add_argument("--hard-timeout", type=float, default=8.0)
    a = ap.parse_args()

    if a.path:
        p = str(Path(a.path).resolve())
        sys.path.insert(0, p)
        os.environ["SELF_PLAY_PATH"] = p
        os.environ["PYTHONPATH"] = p + os.pathsep + os.environ.get("PYTHONPATH", "")
    _auto_register_defaults()
    games = [g.strip() for g in a.games.split(",")] if a.games else list_games()
    print(f"Oyunlar: {', '.join(games)} | oyun başına {a.per_type} puzzle | süre sınırı {a.time_limit:g}/{a.hard_timeout:g} sn")

    names = [a.agent] + ([a.vs] if a.vs else [])
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        pools = {n: _make_pool(n, a.per_type, games, out) for n in names}
        results = {}
        for solver_name in names:
            for owner in names:
                results[(solver_name, owner)] = _solve(solver_name, pools[owner][0], owner, a.time_limit, a.hard_timeout)

    print("\n" + "=" * 70)
    if not a.vs:
        _report(f"{a.agent} solver'ı, kendi havuzunuzu çözdü", results[(a.agent, a.agent)], games)
        pool_n = pools[a.agent][1]
        print(f"\n  Havuz: {pool_n}/{a.per_type * len(games)} puzzle girdi. Eksikse generator'ınız puzzle üretemedi/çözümü"
              " doğrulanamadı: hakemde bu eksik kısım rakiplerce 'çözülmüş' sayılır, skorunuz düşer.")
        return
    A, B = names
    _report(f"{A} solver'ı  ->  {B} havuzu", results[(A, B)], games)
    _report(f"{B} solver'ı  ->  {A} havuzu", results[(B, A)], games)
    ra, rb = _rate(results[(A, B)], games), _rate(results[(B, A)], games)
    miss_a = a.per_type * len(games) - pools[A][1]
    print("\n" + "=" * 70)
    print("MİNİ SKOR TABLOSU (hakem formülü, 2 takımlık)")
    print(f"  {A:<24} solver skoru {ra:.3f}   generator skoru {1 - rb:.3f}")
    print(f"  {B:<24} solver skoru {rb:.3f}   generator skoru {1 - ra:.3f}")
    print("  (Generator skoru = 1 - rakibin sizin havuzunuzdaki çözme oranı. Hakemde eksik havuz kısmı 'çözülmüş' sayılır;"
          f" burada {A} için eksik: {miss_a} puzzle.)")


if __name__ == "__main__":
    main()
