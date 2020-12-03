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
ifeq (${TIERING_LOGIC},True)
	behave behave/features -k --stop --tags core,feature_postcode_tier
else
	behave behave/features -k --stop --tags core,e2e_partial_journey_do_you_live_in_england
endif

smoke_test:
	@echo "Executing smoke test without submission..."
ifeq (${TIERING_LOGIC},True)
	behave behave/features/11.e2e_not_eligible_postcode_tier.feature --stop
else
	behave behave/features/5.e2e_not_eligible_postcode.feature --stop
endif

test_e2e_local:
	@echo "Executing e2e automated tests against the local environment..."
ifeq (${TIERING_LOGIC},True)
	docker-compose run --service-ports --rm chrome-driver bash -c "behave features -k --stop --tags core,feature_postcode_tier --stop"
else
	docker-compose run --service-ports --rm chrome-driver bash -c "behave features -k --stop --tags core,e2e_partial_journey_do_you_live_in_england --stop"
endif

concourse_e2e_with_pipeline_validation_webform_entry:
	@echo "Executing web form entry for End to End with Pipeline Validation..."
	behave behave/features/e2e_test_features/01.simple_web_submission_entry.feature --stop

concourse_e2e_with_pipeline_validation_s3_check:
	@echo "Executing s3 check for End to End with Pipeline Validation..."
	behave --stage=pipeline_validation behave/features/e2e_test_features/09.s3_outputs_check.feature --stop
