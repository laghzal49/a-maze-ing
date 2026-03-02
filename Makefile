.PHONY: install run debug clean lint build

install:
	pip install -r requirements.txt

run:
	python3 a_maze_ing.py config.txt

debug:
	python3 -m pdb a_maze_ing.py config.txt

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	rm -rf mazegen/__pycache__ tests/__pycache__
	rm -rf *.egg-info dist build
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -delete

lint:
	python3 -m flake8 .
	python3 -m mypy .

build:
	python3 -m pip install --user --upgrade build "setuptools>=61.0" wheel
	python3 -m build --no-isolation
