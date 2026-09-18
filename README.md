# Web Solutions Lab 1

[![Build and deploy site](https://github.com/DmitryLedentsov/web-solutions-lab-1/actions/workflows/pages.yml/badge.svg)](https://github.com/DmitryLedentsov/web-solutions-lab-1/actions/workflows/pages.yml)

Лабораторная работа по публикации результатов исследований с помощью статического сайта.

Выбранный стек: **Python + MkDocs Material + GitHub Actions + GitHub Pages**.

В работе выполнены:
- исследовательское задание **T2** — анализ конвейера «эксперимент → артефакт → страница»;
- практическое задание **P3** — воспроизводимый конвейер «данные → результат → сайт».

## Исходные данные эксперимента

Данные не задаются вручную. `scripts/benchmark.py` выполняет простой детерминированный CPU-бенчмарк для пяти размеров входа, по 7 измеряемых повторов на каждый размер после прогрева, и сохраняет:

- `data/measurements.csv` — сырые времена и checksum;
- `data/benchmark_metadata.json` — параметры запуска и сведения об окружении.

Повторить измерения:

```bash
python scripts/benchmark.py
```

## Локальный запуск сайта

```bash
python -m venv .venv
```

Активация окружения:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Установка и запуск:

```bash
pip install -r requirements.txt
make build
make serve
```

Если `make` недоступен:

```bash
python scripts/generate.py
mkdocs build --strict
mkdocs serve
```

## Структура

- `scripts/benchmark.py` — воспроизводимое получение исходных измерений;
- `data/measurements.csv` — сырые результаты реального бенчмарка;
- `data/benchmark_metadata.json` — окружение и параметры измерений;
- `scripts/generate.py` — расчёт статистики, кэширование, генерация таблицы и графика;
- `docs/` — страницы сайта;
- `mkdocs.yml` — конфигурация MkDocs;
- `.github/workflows/pages.yml` — CI/CD и GitHub Pages.

## Публикация

Перед первой публикацией в репозитории нужно один раз выбрать **Settings → Pages → Source: GitHub Actions**.

После push в `master` GitHub Actions выполняет генерацию результатов, строгую сборку MkDocs и публикует содержимое `site/` на GitHub Pages.

Сайт: <https://dmitryledentsov.github.io/web-solutions-lab-1/>

## Лицензии

- код — MIT (`LICENSE`);
- текст и изображения сайта — CC BY 4.0 (`LICENSE-CONTENT`).
