install:
	uv sync

run:
	uv run python -m src

debug:
	python -m pdb -m src

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-venv:
	rm -rf .venv

lint:
	uv run flake8 src
	uv run mypy src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: clean-venv
	python3 -m flake8 src
	python3 -m mypy src --strict  

.PHONY: venv install run debug clean clean-venv lint lint-strict