.PHONY: install generate build serve clean

install:
	python -m pip install -r requirements.txt

generate:
	python scripts/generate.py

build: generate
	mkdocs build --strict

serve: generate
	mkdocs serve

clean:
	rm -rf site .cache docs/assets/experiment.png docs/experiment.md
