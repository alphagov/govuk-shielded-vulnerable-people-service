clean:
	rm -rf __pycache__ .coverage *.zip *.egg-info .tox venv .pytest_cache htmlcov **/__pycache__ **/*.pyc .target setup.cfg
	echo "✔️ Cleanup of files completed!"

checks: clean
	echo "⏳ running pipeline..."
	set -e
	flake8 vulnerable_people_form
	echo "✔️ Checks pipeline passed!"

test:
	pytest -c pytest.ini -sqx --disable-warnings
	echo "✔️ Tests passed!"

install:
	set -e
	echo "⏳ installing..."
	pip3 -q install flake8 mypy watchdog pyyaml argh pytest isort requests_mock pytest-env
	pip3 -q install -r requirements.txt
	echo "✔️ Pip dependencies installed!"

concourse_e2e:
	echo "TODO implement and run behave tests"
