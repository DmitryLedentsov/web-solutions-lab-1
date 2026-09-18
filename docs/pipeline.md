# Конвейер и CI/CD

## Локальная сборка

После создания виртуального окружения достаточно выполнить:

```bash
pip install -r requirements.txt
make build
```

Команда `make build` сначала запускает `scripts/generate.py`, затем выполняет `mkdocs build --strict`.

Для локального просмотра:

```bash
make serve
```

## GitHub Actions

Workflow запускается при push в `master`, при pull request и вручную.

```text
checkout
  ↓
Python + зависимости
  ↓
восстановление кэша эксперимента
  ↓
generate.py
  ↓
mkdocs build --strict
  ↓
Pages artifact
  ↓
deploy (только master)
```

Для pull request выполняется только проверка и сборка. Публикация выполняется только из основной ветки `master`.

## Кэширование P3

Ключ результата вычисляется из трёх частей:

- `data/measurements.csv`;
- `scripts/generate.py`;
- `requirements.txt`.

Если эти файлы не изменились, агрегированные значения и PNG берутся из `.cache/experiment`. В GitHub Actions каталог `.cache/experiment` сохраняется между запусками с помощью `actions/cache`.

Это позволяет не пересчитывать неизменившийся эксперимент, но метаданные страницы (commit и дата сборки) всё равно обновляются.
