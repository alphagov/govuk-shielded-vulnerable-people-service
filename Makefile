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
	behave behave/features/1.e2e_journey_no_nhs_login.feature --stop

smoke_test:
	@echo "Executing smoke test without submission..."
	behave behave/features/2.e2e_journey_no_nhs_login_and_no_submission.feature --stop

test_e2e_local:
	@echo "Executing e2e automated tests against the local environment..."
	docker-compose run --service-ports --rm chrome-driver bash -c "behave features/ --stop"
