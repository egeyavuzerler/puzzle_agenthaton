"""
arena/check_submission.py

GONDERMEDEN ONCE kendi generator ve solver'inizi, organizatorun kullanacagi
AYNI izole hatla deneyin. Sorunlari yarisma gunu degil simdi gorun.

Kontrol ettikleri:
  1. Yukleme: modul import ediliyor mu, sinif var mi, olusturulabiliyor mu.
     Ayrica dosyaniz STATIK taranir: dosya adi gecerli mi, yalnizca izinli
     import'lar var mi (standart kutuphane + core/games/agents_examples),
     sinif adlari MyGenerator/MySolver mi. (Ag/dosya kisitlari bu yerel
     kontrolde UYGULANMAZ; yalnizca hakem ortaminda uygulanir.)
  2. GENERATOR: her oyundan birkac puzzle uretir; sekil + witness solution
     kontrolunden gecen kac tanesi havuza girerdi (organizatorle ayni kural,
     ayni sure/bellek siniri, generate() ayri process'te calisir)
  3. SOLVER: iki havuza karsi calisir -- (a) referans generator'un (garanti
     gecerli) puzzle'lari, (b) kendi generator'unuzun puzzle'lari. Solver ayri
     process'te, cevabi JSON olarak dondurulerek calistirilir (yarisma gunuyle
     ayni protokol): cevabiniz JSON'a cevrilemiyorsa (ornegin numpy dizisi,
     set) burada hata olarak gorursunuz.

Kullanim:
    python3 arena/check_submission.py \
        --generator takim_x.agent:MyGenerator --solver takim_x.agent:MySolver

    # sadece bazi oyunlar, daha cok puzzle:
    python3 arena/check_submission.py --generator takim_x.agent:MyGenerator \
        --games queens --per-type 5

    # kodunuz proje kokunun disindaki bir klasordeyse:
    python3 arena/check_submission.py --solver agent:MySolver --path /yol/klasor

Cikis kodu: [HATA] varsa 1, yoksa 0. [UYARI]'lar gonderimi engellemez ama bakmaya deger.
"""

import argparse
import ast
import importlib
import importlib.util
import os
import re
import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents_examples.baseline import BaselineGenerator
from arena.run_match import run_match
from arena.sandboxed_solver import SandboxedSolver
from bank.build_bank import build_bank
from core.base import BaseGeneratorAgent, BaseSolverAgent
from core.registry import _auto_register_defaults, list_games

OK, WARN, ERR = "[OK]    ", "[UYARI] ", "[HATA]  "

# Hakem degerleri (README "Hakem degerleri" tablosu ile ayni olmali)
_REFEREE_PER_TYPE = 10
_REFEREE_GAME_BUDGET_S = 600.0


def _load_class(spec: str):
    module_path, class_name = spec.split(":")
    return getattr(importlib.import_module(module_path), class_name)


def _short_tb() -> str:
    return traceback.format_exc(limit=3).strip().splitlines()[-1]


# Hakem ortaminda (Docker imaji) bulunan repo paketleri: bunlar import edilebilir.
_REPO_PACKAGES = {"core", "games", "agents_examples"}
# Bu klasorlerdeki modüller "organizator kodu"dur; teslim kurallari (dosya adi, sinif adi) onlara uygulanmaz.
_REPO_INTERNAL_DIRS = {"core", "games", "agents_examples", "arena", "bank", "tests"}
_FILENAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*\.py$")
# Standart kutuphanede olup hakem ortaminda ise yaramayacak / sorun cikaracak modüller
_RISKY_MODULES = {"socket", "ssl", "urllib", "http", "ftplib", "smtplib", "poplib", "imaplib",
                  "telnetlib", "subprocess", "ctypes"}


def _module_file(module_path: str):
    try:
        spec = importlib.util.find_spec(module_path)
    except (ImportError, ValueError, AttributeError):
        return None
    origin = getattr(spec, "origin", None)
    if not origin or not str(origin).endswith(".py"):
        return None
    return Path(origin).resolve()


def _is_internal(path: Path) -> bool:
    try:
        return path.relative_to(ROOT).parts[0] in _REPO_INTERNAL_DIRS
    except ValueError:
        return False


def _static_report(spec: str, expected_class: str, say, scan_file: bool = True) -> None:
    """Teslim dosyasini calistirmadan tarar: dosya adi, import'lar, sinif adi, dosya yazma/ag uyarilari."""
    module_path, _, class_name = spec.partition(":")
    path = _module_file(module_path)
    if path is None or _is_internal(path):
        return
    if class_name != expected_class:
        say(ERR, f"sinif adi '{class_name}': teslimde '{expected_class}' adli sinif aranir, adi degistirin")
    if not scan_file:
        return
    if not _FILENAME_RE.match(path.name):
        say(ERR, f"dosya adi '{path.name}' gecersiz: yalnizca harf, rakam ve alt cizgi (A-Z a-z 0-9 _) "
                 "kullanin ve harfle baslayin (ornek: takim_adi.py)")
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return  # asil hata yukleme adiminda gorunur
    stdlib = getattr(sys, "stdlib_module_names", None)
    seen: set[str] = set()
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                if "relative" not in seen:
                    seen.add("relative")
                    say(ERR, "goreli import (from . import ...) kullanilamaz: teslim TEK dosyadir")
                continue
            names = [node.module or ""]
        for full in names:
            top = full.split(".")[0]
            if not top or top in seen:
                continue
            seen.add(top)
            if top in _REPO_PACKAGES:
                continue
            if stdlib is not None and top in stdlib:
                if top in _RISKY_MODULES:
                    say(WARN, f"'{top}' import ediliyor: hakem ortaminda ag yoktur ve alt surec/yerel kutuphane "
                              "kullanimi kisitlidir, kodunuz buna dayanmamali")
                continue
            if stdlib is not None:
                say(ERR, f"'{full}' standart kutuphane degil ve hakem ortaminda KURULU DEGIL (numpy dahil): "
                         "import hatasi alirsiniz. Kodunuzu yalnizca standart kutuphane ile yazin")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name) and fn.id == "open":
                mode = None
                if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                    mode = node.args[1].value
                for kw in node.keywords:
                    if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                        mode = kw.value.value
                if isinstance(mode, str) and any(ch in mode for ch in "wax+"):
                    say(WARN, f"satir {node.lineno}: dosyaya yazma (open(..., '{mode}')): hakem ortaminda dosya "
                              "sistemi salt-okunurdur, yazma hata verir")
            elif isinstance(fn, ast.Attribute) and fn.attr in ("write_text", "write_bytes"):
                say(WARN, f"satir {node.lineno}: dosyaya yazma ({fn.attr}): hakem ortaminda dosya sistemi "
                          "salt-okunurdur, yazma hata verir")


def run_checks(generator_spec: str | None, solver_spec: str | None, games: list[str] | None = None,
               per_type: int = 3, time_limit_s: float = 5.0, gen_timeout_s: float = 20.0,
               extra_paths: list[str] | None = None, out=print) -> dict:
    """Kontrolleri calistirir, raporu `out` ile yazdirir, {"errors": n, "warnings": n, ...} dondurur."""
    _auto_register_defaults()
    all_games = list_games()
    games = games or all_games
    for p in extra_paths or []:
        sys.path.insert(0, str(Path(p).resolve()))

    report = {"errors": 0, "warnings": 0, "generator": None, "solver": None}

    def say(tag, msg):
        if tag == ERR:
            report["errors"] += 1
        elif tag == WARN:
            report["warnings"] += 1
        out(f"  {tag}{msg}")

    out("=" * 64)
    out("GONDERIM KONTROLU")
    out("=" * 64)

    # ------------------------------------------------------------ 1) yukleme
    out("\n[1/3] Yukleme")
    out("  (Not: ag ve dosya kisitlari yalnizca hakem ortaminda uygulanir; bu kontrol onlari yerelde\n"
        "   uygulamaz, bu yuzden dosyaniz asagida ayrica statik olarak taranir.)")
    generator = solver = None
    if generator_spec:
        _static_report(generator_spec, "MyGenerator", say)
    if solver_spec:
        same_file = bool(generator_spec) and generator_spec.partition(":")[0] == solver_spec.partition(":")[0]
        _static_report(solver_spec, "MySolver", say, scan_file=not same_file)
    if generator_spec:
        try:
            cls = _load_class(generator_spec)
            generator = cls()
            say(OK, f"generator yuklendi: {generator_spec}")
            if not isinstance(generator, BaseGeneratorAgent):
                say(WARN, "generator BaseGeneratorAgent'tan miras almiyor (zorunlu degil ama onerilir)")
            if not callable(getattr(generator, "generate", None)):
                say(ERR, "generator sinifinda generate() metodu yok")
                generator = None
        except Exception:
            say(ERR, f"generator yuklenemedi ({generator_spec}): {_short_tb()}")
    if solver_spec:
        try:
            cls = _load_class(solver_spec)
            inst = cls()
            say(OK, f"solver yuklendi: {solver_spec}")
            if not isinstance(inst, BaseSolverAgent):
                say(WARN, "solver BaseSolverAgent'tan miras almiyor (zorunlu degil ama onerilir)")
            if not callable(getattr(inst, "solve", None)):
                say(ERR, "solver sinifinda solve() metodu yok")
            else:
                solver = True
        except Exception:
            say(ERR, f"solver yuklenemedi ({solver_spec}): {_short_tb()}")

    tmp = tempfile.mkdtemp(prefix="check_submission_")
    own_bank = None

    # ------------------------------------------------------------ 2) generator
    out(f"\n[2/3] Generator (her oyundan {per_type} puzzle; generate() basina {gen_timeout_s:g}s sinir)")
    if generator is None:
        out("  (atlandi)")
    else:
        out("  (kotu giden bir generator'da bu adim birkac dakika surebilir)")
        path = os.path.join(tmp, "own_bank.jsonl")
        res = build_bank(generator, per_type, path, max_retries_per_puzzle=2, gen_timeout_s=gen_timeout_s,
                         games=games, max_consecutive_failures=2,
                         game_time_budget_s=max(60.0, per_type * gen_timeout_s * 2))
        report["generator"] = res
        for g in games:
            st = res["per_game"][g]
            line = f"{g:12s} {st['ok']}/{per_type} havuza girdi  ({st['seconds']:.1f}s)"
            if st["ok"] == per_type:
                tag = OK
            elif st["ok"] > 0:
                tag = WARN
            else:
                tag = ERR
            if st["ok"] < per_type and st["example_error"]:
                line += f"\n{'':11s}ilk hata -> {st['example_error']}"
            if st["gave_up"]:
                line += f"\n{'':11s}(bu oyundan vazgecildi: {st['gave_up']})"
            say(tag, line)
            if st["ok"] and st["seconds"] / max(1, st["ok"]) > gen_timeout_s * 0.5:
                say(WARN, f"{g}: yavas, puzzle basina ort. {st['seconds']/st['ok']:.1f}s (sinir {gen_timeout_s:g}s)")
            if st["ok"]:
                avg = st["seconds"] / st["ok"]
                est = int(_REFEREE_GAME_BUDGET_S / max(avg, 1e-9))
                if est < _REFEREE_PER_TYPE:
                    say(WARN, f"{g}: puzzle basina ort. {avg:.1f}s; hakemin {_REFEREE_GAME_BUDGET_S:g}s oyun butcesinde "
                              f"~{est}/{_REFEREE_PER_TYPE} puzzle uretilir, havuz eksik kalir "
                              "(eksik kisim rakiplerce cozulmus sayilir)")
        if res["written"] > 0:
            own_bank = path

    # ------------------------------------------------------------ 3) solver
    out(f"\n[3/3] Solver (cozum suresi siniri {time_limit_s:g}s/puzzle)")
    if not solver:
        out("  (atlandi)")
    else:
        ref_path = os.path.join(tmp, "ref_bank.jsonl")
        build_bank(BaselineGenerator(), per_type, ref_path, games=games, isolate=False)
        banks = [("referans havuz (garanti gecerli puzzle'lar)", ref_path)]
        if own_bank:
            banks.append(("kendi generator'unuzun havuzu", own_bank))
        elif generator_spec:
            out("  (kendi havuzunuz bos oldugu icin solver sadece referans havuza karsi denenecek)")
        report["solver"] = {}
        for label, bank_path in banks:
            out(f"\n  -- {label}")
            with SandboxedSolver(solver_spec, mode="local", extra_pythonpath=extra_paths) as sv:
                summary = run_match(sv, bank_path, time_limit_s, time_limit_s + 3.0)
            report["solver"][label] = summary
            for g in games:
                st = summary["per_game"].get(g)
                if not st:
                    continue
                line = f"{g:12s} {st['solved']}/{st['total']} cozdu"
                if st["avg_solved_time_s"] is not None:
                    line += f"  (ort. {st['avg_solved_time_s']:.2f}s)"
                if st["invalid_solution"] > 0:
                    tag = ERR
                    line += f"\n{'':11s}{st['invalid_solution']} cevap GECERSIZ sayildi: {st['first_error']}"
                elif st["errors"] == st["total"]:
                    tag = ERR
                    line += f"\n{'':11s}her puzzle'da hata -> {st['first_error']}"
                elif st["errors"] > 0 or st["timeouts"] > 0:
                    tag = WARN
                    line += f"\n{'':11s}{st['errors']} hata, {st['timeouts']} zaman asimi"
                    if st["first_error"]:
                        line += f" -> {st['first_error']}"
                else:
                    tag = OK
                say(tag, line)
            out(f"  Genel: {summary['total_solved']}/{summary['total_puzzles']} puzzle cozuldu "
                f"(bilgi amacli; asil skor rakiplerin puzzle'lariyla olculur)")

    # ------------------------------------------------------------ sonuc
    out("\n" + "=" * 64)
    if report["errors"]:
        out(f"SONUC: {report['errors']} HATA, {report['warnings']} uyari -- gondermeden once duzeltin.")
    elif report["warnings"]:
        out(f"SONUC: hata yok, {report['warnings']} uyari -- gonderebilirsiniz, uyarilara bakmaniz onerilir.")
    else:
        out("SONUC: her sey yolunda -- gonderime hazir.")
    out("=" * 64)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Gonderim oncesi generator/solver kontrolu")
    parser.add_argument("--generator", help="modul.yolu:SinifAdi")
    parser.add_argument("--solver", help="modul.yolu:SinifAdi")
    parser.add_argument("--games", help="virgullu oyun listesi (varsayilan: hepsi)")
    parser.add_argument("--per-type", type=int, default=3, help="oyun basina puzzle sayisi (varsayilan 3)")
    parser.add_argument("--time-limit", type=float, default=5.0, help="solver sure siniri (sn, varsayilan 5 = hakem degeri)")
    parser.add_argument("--gen-timeout", type=float, default=20.0, help="generate() cagrisi sinirI (sn, varsayilan 20)")
    parser.add_argument("--path", action="append", default=[], help="kodunuzun bulundugu klasor (birden fazla verilebilir)")
    args = parser.parse_args()

    if not args.generator and not args.solver:
        parser.error("en az bir tane --generator ya da --solver verin")
    games = [g.strip() for g in args.games.split(",")] if args.games else None
    if games:
        _auto_register_defaults()
        unknown = [g for g in games if g not in list_games()]
        if unknown:
            parser.error(f"bilinmeyen oyun(lar): {unknown} (bilinenler: {list_games()})")

    report = run_checks(args.generator, args.solver, games, args.per_type, args.time_limit,
                        args.gen_timeout, args.path)
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
