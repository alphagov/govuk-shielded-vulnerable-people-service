Feature: COVID-19 Shielded vulnerable people service - partial user journey - postcode not found after change address (user lives in England)
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
        When I give the "#postcode" field the value "BB1 1TA"
        And I submit the form
        Then I am redirected to the "nhs-letter" page

    Scenario: Should be re-directed to nhs number when yes answered to told to shield
        Given I am on the "nhs-letter" page
        When I click the ".govuk-radios__item input[value='1']" element
        And I submit the form
        Then I am redirected to the "nhs-number" page

    Scenario: Should be re-directed to name entry when valid nhs number entered
        Given I am on the "nhs-number" page
        # This passes the NHS number checksum but will never be assigned to a real person
        When I give the "#nhs_number" field the value "1116432455"
        And I submit the form
        Then I am redirected to the "name" page

    Scenario: Should be re-directed to date of birth when first name and last name entered
        Given I am on the "name" page
        When I give the "#first_name" field the value "End to end"
        And I give the "#last_name" field the value "User"
        And I submit the form
        Then I am redirected to the "date-of-birth" page

    Scenario: Should be re-directed to address lookup when valid date of birth entered
        Given I am on the "date-of-birth" page
        When I give the "#date_of_birth-day" field the value "08"
        And I give the "#date_of_birth-month" field the value "05"
        And I give the "#date_of_birth-year" field the value "2006"
        And I submit the form
        Then I am redirected to the "address-lookup" page

    Scenario: Should be directed to postcode lookup when change link clicked
        Given I am on the "address-lookup" page
        When I click the "#change-postcode" element
        Then I am redirected to the "postcode-lookup" page

    Scenario: Should be directed to do you live in england when unrecognised postcode entered
        Given I am on the "postcode-lookup" page
        When I give the "#postcode" field the value "QJ5 7VC"
        And I submit the form
        Then I am redirected to the "do-you-live-in-england" page

    Scenario: Should be re-directed to address lookup if user is in England
        Given I am on the "do-you-live-in-england" page
        When I click the ".govuk-radios__item input[value='1']" element
        And I submit the form
        Then I am redirected to the "address-lookup" page