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

### Два способа публикации GitHub Pages

| Способ | Суть |
|---|---|
| Push в `gh-pages` | workflow складывает готовый HTML в отдельную ветку, из которой Pages публикует сайт |
| `upload-pages-artifact` + `deploy-pages` | готовый каталог сайта передаётся как Pages-артефакт и публикуется официальным механизмом GitHub |

В работе выбран второй вариант: он не создаёт служебную ветку с результатом сборки и напрямую поддерживается GitHub Pages.

## Кэширование P3

Ключ результата вычисляется из трёх частей:

- `data/measurements.csv`;
- `scripts/generate.py`;
- `requirements.txt`.

Если эти файлы не изменились, агрегированные значения и PNG берутся из `.cache/experiment`. В GitHub Actions каталог `.cache/experiment` сохраняется между запусками с помощью `actions/cache`.

Это позволяет не пересчитывать неизменившийся эксперимент, но метаданные страницы (commit и дата сборки) всё равно обновляются.
