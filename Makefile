clean:
	rm -rf __pycache__ .coverage *.zip *.egg-info .tox venv .pytest_cache htmlcov **/__pycache__ **/*.pyc .target setup.cfg
	echo "✔️ Cleanup of files completed!"

checks: clean
	echo "⏳ running pipeline..."
	set -e
	black -q .
	flake8 . --max-line-length=91
	echo "✔️ Checks pipeline passed!"

test:
	pytest -c pytest.ini -sqx --disable-warnings
	echo "✔️ Tests passed!"

install:
	set -e
	echo "⏳ installing..."
	pip3 -q install black flake8 mypy watchdog pyyaml argh pytest isort requests_mock pytest-env
	pip3 -q install -r requirements.txt
	echo "✔️ Pip dependencies installed!"