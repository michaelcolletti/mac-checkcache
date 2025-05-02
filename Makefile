install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	python -m pytest -vvv --cov=src/main.py --cov=tests  

# test-notebook:
# 	python -m pytest --nbval notebook.ipynb

# test-web:
# 	python -m pytest -v tests/test_web.py

# test-all: test test-notebook test-web
# 	@echo "All tests completed"

debug:
	python -m pytest -vv --pdb	#Debugger is invoked

one-test:
	python -m pytest -vv tests/test_greeting.py::test_my_name4

debugthree:
	#not working the way I expect
	python -m pytest -vv --pdb --maxfail=4  # drop to PDB for first three failures

format:
	black src/*.py

lint:
	pylint --disable=R,C src/*.py

refactor: lint format

run:
	python src/main.py

all: install lint test format
