test:
	python3 -m pytest -sqx --disable-warnings
	@echo "✔️ Unit tests passed!"

install:
	set -e
	@echo "⏳ Installing dependencies..."
	pip3 -q install -r requirements-dev.txt
	@echo "✔️ Pip dependencies installed!"

concourse_e2e:
	@echo "Executing e2e automated tests against the staging environment..."
	# execute all scenarios except no submission ( the '-' character prefix means skip)
	behave behave/features --stop --tags=-e2e_happy_path_no_nhs_login_no_submission

smoke_test:
	@echo "Executing smoke test without submission..."
	behave behave/features/5.not_eligible_postcode.feature --stop

test_e2e_local:
	@echo "Executing e2e automated tests against the local environment..."
	docker-compose run --service-ports --rm chrome-driver bash -c "behave features/ --stop"
