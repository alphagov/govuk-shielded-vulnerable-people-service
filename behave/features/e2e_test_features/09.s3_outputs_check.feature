@s3_outputs_check
Feature: COVID-19 Shielded vulnerable people service - validate data from previous day
    Scenario: Pipeline should be executed and data validated for previous day run
        Given there was a new web submission yesterday
        When the pipeline has completed successfully
        Then nhs_number "9999999999" is available in LA feed for "unknown" with yesterday date in field "submission_datetime"
        AND nhs_number "9999999999" is available in supermarket feed with yesterday date in field "FirstName"
