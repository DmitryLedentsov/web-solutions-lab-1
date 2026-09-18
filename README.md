# Web Solutions Lab 1

[![Build and deploy site](https://github.com/DmitryLedentsov/web-solutions-lab-1/actions/workflows/pages.yml/badge.svg)](https://github.com/DmitryLedentsov/web-solutions-lab-1/actions/workflows/pages.yml)

Лабораторная работа по публикации результатов исследований с помощью статического сайта.

Выбранный стек: **Python + MkDocs Material + GitHub Actions + GitHub Pages**.

В работе выполнены:
- исследовательское задание **T2** — анализ конвейера «эксперимент → артефакт → страница»;
- практическое задание **P3** — воспроизводимый конвейер «данные → результат → сайт».

## Локальный запуск

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

- `data/measurements.csv` — исходные данные эксперимента;
- `scripts/generate.py` — расчёт, кэширование, генерация таблицы и графика;
- `docs/` — страницы сайта;
- `mkdocs.yml` — конфигурация MkDocs;
- `.github/workflows/pages.yml` — CI/CD и GitHub Pages.

## Публикация

После push в `master` GitHub Actions выполняет генерацию результатов, строгую сборку MkDocs и публикует содержимое `site/` на GitHub Pages.

Сайт: <https://dmitryledentsov.github.io/web-solutions-lab-1/>

## Лицензии

- код — MIT (`LICENSE`);
- текст и изображения сайта — CC BY 4.0 (`LICENSE-CONTENT`).
