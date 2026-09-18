from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "measurements.csv"
DOCS = ROOT / "docs"
ASSETS = DOCS / "assets"
OUTPUT_MD = DOCS / "experiment.md"
OUTPUT_PNG = ASSETS / "experiment.png"
CACHE = ROOT / ".cache" / "experiment"


def dataset_hash() -> str:
    return hashlib.sha256(DATA.read_bytes()).hexdigest()


def cache_key() -> str:
    digest = hashlib.sha256()
    digest.update(DATA.read_bytes())
    digest.update(Path(__file__).read_bytes())
    digest.update((ROOT / "requirements.txt").read_bytes())
    return digest.hexdigest()


def commit_hash() -> str:
    github_sha = os.getenv("GITHUB_SHA")
    if github_sha:
        return github_sha[:12]
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "local-build"


def calculate() -> list[dict[str, float]]:
    df = pd.read_csv(DATA)
    required = {"input_size", "run", "duration_ms"}
    if not required.issubset(df.columns):
        missing = ", ".join(sorted(required - set(df.columns)))
        raise ValueError(f"В CSV отсутствуют столбцы: {missing}")

    grouped = (
        df.groupby("input_size", as_index=False)["duration_ms"]
        .agg(["mean", "std"])
        .reset_index()
        .rename(columns={"mean": "mean_ms", "std": "std_ms"})
    )

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.errorbar(
        grouped["input_size"],
        grouped["mean_ms"],
        yerr=grouped["std_ms"],
        marker="o",
        capsize=4,
    )
    ax.set_title("Зависимость времени обработки от размера входных данных")
    ax.set_xlabel("Размер входных данных")
    ax.set_ylabel("Среднее время, мс")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUTPUT_PNG, dpi=140)
    plt.close(fig)

    return grouped.round(3).to_dict(orient="records")


def table_markdown(rows: list[dict[str, float]]) -> str:
    lines = [
        "| Размер входных данных | Среднее время, мс | Стандартное отклонение, мс |",
        "|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {int(row['input_size'])} | {row['mean_ms']:.3f} | {row['std_ms']:.3f} |"
        )
    return "\n".join(lines)


def write_page(rows: list[dict[str, float]], used_cache: bool, elapsed: float) -> None:
    data_sha = dataset_hash()
    built_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    cache_text = "использован кэш" if used_cache else "результаты пересчитаны"

    page = f"""# Практическое задание P3

## Воспроизводимый конвейер «данные → результат → сайт»

Исходные измерения находятся в `data/measurements.csv`. Скрипт `scripts/generate.py` читает CSV, группирует повторные измерения по размеру входных данных, вычисляет среднее время и стандартное отклонение, затем формирует таблицу и график для этой страницы.

### Результаты

{table_markdown(rows)}

![График результатов эксперимента](assets/experiment.png)

### Метаданные сборки

| Параметр | Значение |
|---|---|
| Git commit | `{commit_hash()}` |
| Дата сборки | `{built_at}` |
| SHA-256 набора данных | `{data_sha}` |
| Кэш | {cache_text} |
| Время шага генерации | {elapsed:.4f} с |

### Как обеспечена воспроизводимость

1. Версии Python-зависимостей зафиксированы в `requirements.txt`.
2. Исходные данные хранятся в репозитории вместе с кодом расчёта.
3. При каждой сборке вычисляется SHA-256 исходного CSV.
4. Ключ кэша зависит от данных, скрипта расчёта и `requirements.txt`.
5. Если ключ не изменился, численные результаты и график берутся из кэша; Markdown-страница всё равно создаётся заново, чтобы обновить commit и дату сборки.

Чтобы продемонстрировать автоматическое обновление, достаточно изменить значение в `data/measurements.csv` и выполнить `git push`: workflow повторно запустит генератор и пересоберёт сайт.
"""
    OUTPUT_MD.write_text(page, encoding="utf-8")


def main() -> None:
    started = time.perf_counter()
    ASSETS.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)

    key = cache_key()
    cached_json = CACHE / f"{key}.json"
    cached_png = CACHE / f"{key}.png"

    used_cache = cached_json.exists() and cached_png.exists()
    if used_cache:
        rows = json.loads(cached_json.read_text(encoding="utf-8"))
        shutil.copy2(cached_png, OUTPUT_PNG)
    else:
        rows = calculate()
        cached_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        shutil.copy2(OUTPUT_PNG, cached_png)

    elapsed = time.perf_counter() - started
    write_page(rows, used_cache, elapsed)
    print(f"generation_mode={'cache' if used_cache else 'compute'}")
    print(f"generation_seconds={elapsed:.4f}")
    print(f"dataset_sha256={dataset_hash()}")


if __name__ == "__main__":
    main()
