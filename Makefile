test:
	pytest -c pytest.ini -sqx --disable-warnings
	echo "✔️ Tests passed!"

install:
	set -e
	echo "⏳ installing..."
	pip3 -q install pytest
	pip3 -q install -r requirements.txt
	echo "✔️ Pip dependencies installed!"

concourse_e2e:
	echo "TODO implement and run behave tests"
