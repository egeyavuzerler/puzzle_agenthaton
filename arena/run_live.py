"""
arena/run_live.py

Bir puzzle uretir (ya da bank'tan okur), solver'i CALISIRKEN ekranda
CANLI bir matplotlib penceresi acar.

Kullanim:
    python3 arena/run_live.py --game queens --size 8

    # kendi havuzunuzdan belirli bir puzzle'i izlemek icin:
    python3 arena/run_live.py --game queens --from-bank bank/takim_x_bank.jsonl --puzzle-id 0
"""

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from games.queens.reference_agent import solve_queens_backtrack, solve_n_queens_any
from core.live_view import LiveQueensView

_SIMPLE_GAMES = {
}


def build_puzzle(args) -> dict:
    if args.from_bank:
        with open(args.from_bank) as f:
            for line in f:
                record = json.loads(line)
                if record["game"] == args.game and (args.puzzle_id is None or record["id"] == args.puzzle_id):
                    return record["puzzle"]
        raise ValueError("bank icinde uygun puzzle bulunamadi")

    rng = random.Random(args.seed)

    # queens
    solution = solve_n_queens_any(args.size, rng)
    n = args.size
    regions = [[-1] * n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            best_q, best_dist = None, None
            for qi, (qr, qc) in enumerate(solution):
                d = max(abs(r - qr), abs(c - qc))
                if best_dist is None or d < best_dist:
                    best_dist, best_q = d, qi
            regions[r][c] = best_q
    return {"game": "queens", "size": [n, n], "regions": regions}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", choices=['queens'], required=True)
    parser.add_argument("--size", type=int, default=8, help="grid boyutu (NxN) -- queens icin")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--from-bank", default=None, help="bir bank.jsonl dosyasindan puzzle oku")
    parser.add_argument("--puzzle-id", type=int, default=None)
    parser.add_argument("--redraw-every", type=int, default=None, help="kac adimda bir ekrani yenile")
    parser.add_argument("--pause", type=float, default=None, help="her yenilemede bekleme suresi, saniye")
    args = parser.parse_args()

    puzzle = build_puzzle(args)

    # queens
    redraw_every = args.redraw_every if args.redraw_every is not None else 1
    pause = args.pause if args.pause is not None else 0.05
    view = LiveQueensView(puzzle, redraw_every=redraw_every, pause=pause)
    result = solve_queens_backtrack(puzzle, on_step=view.on_step)
    view.finish(result)

    print(f"\nSonuc: solved={result.solved}" + (f", error={result.error}" if result.error else ""))


if __name__ == "__main__":
    main()
