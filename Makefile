test:
	python3 -m pytest -x --disable-warnings
	@echo "✔️ Unit tests passed!"

test_with_coverage:
	coverage run --source vulnerable_people_form/ -m pytest -qx --disable-warnings
	coverage report -m

install:
	set -e
	@echo "⏳ Installing dependencies..."
	pip3 -q install -r requirements-dev.txt
	@echo "✔️ Pip dependencies installed!"

concourse_e2e:
	@echo "Executing e2e automated tests against the staging environment..."
	# execute all scenarios except no submission and backend submissions test ( the '-' character prefix means skip)
	behave behave/features -k --stop --tags core

smoke_test:
	@echo "Executing smoke test with submission..."
	behave behave/features/1.e2e_journey_no_nhs_login.feature --stop

test_e2e_local:
	@echo "Executing e2e automated tests against the local environment..."
	docker-compose run --service-ports --rm chrome-driver bash -c "behave features -k --stop --tags core,feature_postcode_tier --stop"

concourse_e2e_with_pipeline_validation_webform_entry:
	@echo "Executing web form entry for End to End with Pipeline Validation..."
	behave behave/features/e2e_test_features/01.simple_web_submission_entry.feature --stop

concourse_e2e_with_pipeline_validation_s3_check:
	@echo "Executing s3 check for End to End with Pipeline Validation..."
	behave --stage=pipeline_validation behave/features/e2e_test_features/09.s3_outputs_check.feature --stop

