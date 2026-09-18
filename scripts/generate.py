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
BENCHMARK_META = ROOT / "data" / "benchmark_metadata.json"
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
    digest.update(BENCHMARK_META.read_bytes())
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
    required = {"input_size", "run", "duration_ms", "checksum"}
    if not required.issubset(df.columns):
        missing = ", ".join(sorted(required - set(df.columns)))
        raise ValueError(f"В CSV отсутствуют столбцы: {missing}")

    checksum_counts = df.groupby("input_size")["checksum"].nunique()
    if (checksum_counts != 1).any():
        raise ValueError("Контрольная сумма различается между повторами бенчмарка")

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
    ax.set_title("Время выполнения CPU-бенчмарка")
    ax.set_xlabel("Число итераций")
    ax.set_ylabel("Среднее время, мс")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUTPUT_PNG, dpi=140)
    plt.close(fig)

    return grouped.round(3).to_dict(orient="records")


def table_markdown(rows: list[dict[str, float]]) -> str:
    lines = [
        "| Число итераций | Среднее время, мс | Стандартное отклонение, мс |",
        "|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {int(row['input_size'])} | {row['mean_ms']:.3f} | {row['std_ms']:.3f} |"
        )
    return "\n".join(lines)


def write_page(rows: list[dict[str, float]], used_cache: bool, elapsed: float) -> None:
    meta = json.loads(BENCHMARK_META.read_text(encoding="utf-8"))
    data_sha = dataset_hash()
    built_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    cache_text = "использован кэш" if used_cache else "результаты пересчитаны"
    sizes = ", ".join(f"{value:,}".replace(",", " ") for value in meta["sizes"])

    page = f"""# Практическое задание P3

## Воспроизводимый конвейер «данные → результат → сайт»

### Как получены исходные данные

Исходные измерения **не заданы вручную**. Их формирует `scripts/benchmark.py`: скрипт выполняет детерминированную CPU-нагрузку

```python
total += (i * i + 3 * i) % 97
```

в обычном Python-цикле для нескольких размеров входа. Для каждого размера выполняется один прогревочный запуск, после чего время измеряется {meta['repeats']} раз с помощью `{meta['timer']}`. Результат вычисления дополнительно записывается в CSV как `checksum`, чтобы убедиться, что во всех повторах выполнялась одна и та же работа.

Размеры входа: **{sizes} итераций**.

Сырые измерения находятся в `data/measurements.csv`, параметры запуска — в `data/benchmark_metadata.json`. Их можно воспроизвести командой:

```bash
python scripts/benchmark.py
```

После получения исходных данных `scripts/generate.py` вычисляет среднее время и стандартное отклонение, затем формирует таблицу и график для сайта.

### Окружение исходного замера

| Параметр | Значение |
|---|---|
| Дата измерения | `{meta['generated_at_utc']}` |
| Python | `{meta['python_implementation']} {meta['python_version']}` |
| Платформа | `{meta['platform']}` |
| Архитектура | `{meta['machine']}` |
| Повторов для каждого размера | {meta['repeats']} |
| Прогревочных запусков | {meta['warmups_per_size']} |
| Таймер | `{meta['timer']}` |

### Результаты

{table_markdown(rows)}

![График результатов эксперимента](assets/experiment.png)

Линейный характер графика ожидаем: выбранная нагрузка выполняет постоянный объём арифметики на каждой итерации, то есть имеет сложность O(n). Разброс между повторами отражается стандартным отклонением и связан с реальным временем выполнения процесса в операционной системе.

### Метаданные сборки сайта

| Параметр | Значение |
|---|---|
| Git commit | `{commit_hash()}` |
| Дата сборки | `{built_at}` |
| SHA-256 набора данных | `{data_sha}` |
| Кэш | {cache_text} |
| Время шага генерации | {elapsed:.4f} с |

### Как обеспечена воспроизводимость

1. Скрипт `scripts/benchmark.py` хранит точный алгоритм получения исходных измерений.
2. Сырые результаты и метаданные окружения сохранены в `data/`.
3. Версии зависимостей этапа анализа зафиксированы в `requirements.txt`.
4. При каждой сборке вычисляется SHA-256 исходного CSV.
5. Ключ кэша зависит от данных, метаданных бенчмарка, скрипта анализа и `requirements.txt`.
6. Если исходные данные не изменились, агрегированные значения и PNG берутся из кэша; Markdown-страница всё равно создаётся заново, чтобы обновить commit и дату сборки.

Если повторно запустить `python scripts/benchmark.py`, измерения немного изменятся из-за состояния машины. После commit и push новый CSV изменит ключ кэша, и CI автоматически пересчитает таблицу и график.
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
