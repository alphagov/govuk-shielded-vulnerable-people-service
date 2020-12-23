@feature_postcode_tier
Feature: COVID-19 Shielded vulnerable people service - basic e2e user journey - manual address
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

    Scenario: Should be redirected to support address when an address is not listed
        Given I am on the "address-lookup" page
        When I click the "#my-address-is-not-listed-or-wrong" element
        Then I am redirected to the "support-address" page

    Scenario: Should be redirected to shopping assistance when an address isn't listed or is wrong
        Given I am on the "support-address" page
        When I give the "#building_and_street_line_1" field the value "this is a really long address line one this is a really long address line one this is a really long address"
        And I give the "#building_and_street_line_2" field the value "this is a really long address line two this is a really long address line two this is a really long address line two this is a really long address line two this is a really long address line two"
        And I give the "#town_city" field the value "Bradford"
        And I give the "#postcode" field the value "LE674AY"
        And I submit the form
        Then I am redirected to the "do-you-have-someone-to-go-shopping-for-you" page

    Scenario: Should be redirected to priority supermarket deliveries when no answered to shopping help
        Given I am on the "do-you-have-someone-to-go-shopping-for-you" page
        When I click the ".govuk-radios__item input[value='0']" element
        And I submit the form
        Then I am redirected to the "priority-supermarket-deliveries" page

    Scenario: Should be redirected to contact details needs when yes answered to priority shopping deliveries
        Given I am on the "priority-supermarket-deliveries" page
        When I click the ".govuk-radios__item input[value='1']" element
        And I submit the form
        Then I am redirected to the "contact-details" page

    Scenario: Should be redirected to check contact details when email entered
        Given I am on the "contact-details" page
        When I give the "#email" field the value "coronavirus-services-smoke-tests@digital.cabinet-office.gov.uk"
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



