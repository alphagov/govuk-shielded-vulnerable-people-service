@feature_postcode_tier
Feature: COVID-19 Shielded vulnerable people service - partial user journey - postcode not eligible (postcode tier 1/2)
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
      
  Scenario: Should be re-directed to do you live in England when unknown postcode entered
        Given I am on the "postcode-eligibility" page
        When I give the "#postcode" field the value "LE674AY"
        And I submit the form
        Then I am redirected to the "not-eligible-postcode" page
        And the content of element with selector ".govuk-heading-l" equals "Sorry, this service is not available in your area"

