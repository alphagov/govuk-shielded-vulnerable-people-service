# COVID-19 -
@s3_outputs_check
Feature: COVID-19 Shielded vulnerable people service - validate data from previous day
    Scenario: Pipeline should be executed and data validated for previous day run
        Given the data is available for yesterday
        When the pipeline is processed
        Then nhs_number "9999999999" is available in LA feed for "blackburn-with-darwen" for yesterday
        AND nhs_number "9999999999" is available in supermarket feed for yesterday
