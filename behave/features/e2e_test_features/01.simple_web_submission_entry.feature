@simple_web_submission_entry
Feature: COVID-19 Shielded vulnerable people service - basic e2e user journey - no NHS login- Enter data for tomorrows pipeline run
    Scenario: can load homepage
        When I navigate to "/start"
        Then the content of element with selector ".govuk-fieldset__heading" equals "Are you using this service for yourself or for someone else?"

    Scenario: Should be re-directed to nhs-login when yes answered to applying on own behalf
        Given I am on the "applying-on-own-behalf" page
        When I click the ".govuk-radios__item input[value='0']" element
        And I submit the form
        Then I am redirected to the "nhs-login" page

    Scenario: Should be re-directed to postcode eligibility when no answered to nhs login
        Given I am on the "nhs-login" page
        When I click the ".govuk-radios__item input[value='0']" element
        And I submit the form
        Then I am redirected to the "postcode-eligibility" page

    Scenario: Should be re-directed to shielding because vulnerable when eligible postcode entered
        Given I am on the "postcode-eligibility" page
        When I give the "#postcode" field the value "LU11AA"
        And I submit the form
        Then I am redirected to the "address-lookup" page

    Scenario: Should be redirected to shopping assistance when an address is selected
        Given I am on the "address-lookup" page
        When I submit the form
        Then I am redirected to the "nhs-letter" page

    Scenario: Should be re-directed to nhs number when yes answered to told to shield
        Given I am on the "nhs-letter" page
        When I click the ".govuk-radios__item input[value='1']" element
        And I submit the form
        Then I am redirected to the "nhs-number" page

    Scenario: Should be re-directed to name entry when valid nhs number entered
        Given I am on the "nhs-number" page
        # This passes the NHS number checksum but will never be assigned to a real person
        When I give the "#nhs_number" field the value "9999999999"
        And I submit the form
        Then I am redirected to the "name" page

    Scenario: Should be re-directed to date of birth when first name and last name entered
        Given I am on the "name" page
        When I give the "#first_name" field the value "End to end" appended with todays date
        And I give the "#last_name" field the value "User"
        And I submit the form
        Then I am redirected to the "date-of-birth" page

    Scenario: Should be re-directed to address lookup when valid date of birth entered
        Given I am on the "date-of-birth" page
        When I give the "#date_of_birth-day" field the value "08"
        And I give the "#date_of_birth-month" field the value "05"
        And I give the "#date_of_birth-year" field the value "2006"
        And I submit the form
        Then I am redirected to the "do-you-have-someone-to-go-shopping-for-you" page

    Scenario: Should be redirected to priority supermarket deliveries when no answered to shopping help
        Given I am on the "do-you-have-someone-to-go-shopping-for-you" page
        When I click the ".govuk-radios__item input[value='0']" element
        And I submit the form
        Then I am redirected to the "priority-supermarket-deliveries" page

    Scenario: Should be redirected to basic care needs when yes answered to priority shopping deliveries
        Given I am on the "priority-supermarket-deliveries" page
        When I click the ".govuk-radios__item input[value='1']" element
        And I submit the form
        Then I am redirected to the "basic-care-needs" page

    Scenario: Should be redirected to contact details when no answered to basic care needs help
        Given I am on the "basic-care-needs" page
        When I click the ".govuk-radios__item input[value='0']" element
        And I submit the form
        Then I am redirected to the "contact-details" page

    Scenario: Should be redirected to check contact details when email entered
        Given I am on the "contact-details" page
        When I give the "#email" field the value "coronavirus-services-smoke-tests+E2E@digital.cabinet-office.gov.uk"
        And I submit the form
        Then I am redirected to the "check-contact-details" page

    Scenario: Should be redirected to check-your-answers when form submitted
        Given I am on the "check-contact-details" page
        When I submit the form
        Then I am redirected to the "check-your-answers" page

    Scenario: Should be redirected to confirmation when no answered to basic care needs help
        Given I am on the "check-your-answers" page
        When I submit the form
        Then I am redirected to the "confirmation" page
