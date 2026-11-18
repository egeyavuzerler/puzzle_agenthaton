"""
agents_examples/baseline.py

Bu dosya bir HAKEM ya da CEKIRDEK parcasi DEGIL -- sadece "boyle bir agent
yazacaksiniz" ornegi. Gercek generator/solver kodu games/<oyun>/reference_agent.py
icinde; bu dosya sadece "game" adina gore dogru fonksiyona yonlendiren
INCE bir dispatch katmani.
"""

import random

from core.base import BaseGeneratorAgent, BaseSolverAgent, SolveResult

from games.queens.reference_agent import generate_queens, solve_queens
from games.tango.reference_agent import generate_tango, solve_tango
from games.slitherlink.reference_agent import generate_slitherlink, solve_slitherlink

_GENERATORS = {
    "queens": generate_queens,
    "tango": generate_tango,
    "slitherlink": generate_slitherlink,
}

_SOLVERS = {
    "queens": solve_queens,
    "tango": solve_tango,
    "slitherlink": solve_slitherlink,
}


class BaselineGenerator(BaseGeneratorAgent):
    name = "baseline_generator"

    def generate(self, game: str, difficulty: int, seed: int | None = None):
        if game not in _GENERATORS:
            raise NotImplementedError(f"BaselineGenerator '{game}' uretmiyor")
        rng = random.Random(seed)
        return _GENERATORS[game](rng, difficulty)  # artik (puzzle, solution) doner


class BaselineSolver(BaseSolverAgent):
    name = "baseline_solver"

    def solve(self, puzzle: dict, time_limit_s: float = 30.0) -> SolveResult:
        game = puzzle.get("game")
        if game not in _SOLVERS:
            return SolveResult(solved=False, error=f"BaselineSolver '{game}' cozmuyor")
        return _SOLVERS[game](puzzle, time_limit_s=time_limit_s)
