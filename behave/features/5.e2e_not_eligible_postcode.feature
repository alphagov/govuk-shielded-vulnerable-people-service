@e2e_partial_journey_do_you_live_in_england
Feature: COVID-19 Shielded vulnerable people service - partial user journey - ineligible postcode
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
        When I give the "#postcode" field the value "QJ5 7VC"
        And I submit the form
        Then I am redirected to the "do-you-live-in-england" page

    Scenario: Should be re-directed to not eligible postcode when user is not in England
        Given I am on the "do-you-live-in-england" page
        When I click the ".govuk-radios__item input[value='0']" element
        And I submit the form
        Then I am redirected to the "not-eligible-postcode" page
