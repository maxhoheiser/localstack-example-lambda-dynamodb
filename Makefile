test:
	python -m unittest discover -s tests/unit -v

test-integraton:
	python -m pytest tests/integration

test-coverage:
	python -m coverage run -m unittest discover tests

format:
	pre-commit run --all-files

format-staged:
	pre-commit run

lint:
	flake8 --ignore=E203,E302 src tests; mypy src tests lambdas

lint-pylint:
	pylint --fail-under=6 --rcfile=.pylintrc --disable=C0114,C0115,C0116,R0801,C0103,W0201 src tests lambdas

lint-types:
	mypy src tests lambdas
