@feature_postcode_tier
Feature: COVID-19 Shielded vulnerable people service - partial user journey - postcode not eligible (not valid postcode)
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
   
    Scenario: Should be redirected to address lookup
	Given I am on the "postcode-eligibility" page
        When I give the postcode field a tier 3 postcode
        And I submit the form
	Then I am redirected to the "address-lookup" page

    Scenario: Should be re-directed support address when address cannot be found entered
        Given I am on the "address-lookup" page
        When I click the "#my-address-is-not-listed-or-wrong" element
	Then I am redirected to the "support-address" page

    Scenario: Should be  to do you live in england when unrecognised postcode entered
        Given I am on the "support-address" page
        When I give the "#building_and_street_line_1" field the value "12 Test Address Ave"
        And I give the "#building_and_street_line_2" field the value "address line 2"
        And I give the "#town_city" field the value "Harrow"
        When I give the "#postcode" field the value "QJ5 7VC"
        And I submit the form
	Then I am redirected to the "not-eligible-postcode" page
	And the content of element with selector ".govuk-heading-l" equals "Sorry, we could not find your postcode in our system"
