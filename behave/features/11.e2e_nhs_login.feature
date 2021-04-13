@core
Feature: COVID-19 Shielded vulnerable people service - nhs login and submission with returning user
    Scenario: can load homepage
        When I navigate to "/start"
        Then the content of element with selector ".govuk-fieldset__heading" equals "Are you using this service for yourself or for someone else?"

    Scenario: Should be re-directed to nhs-login when yes answered to applying on own behalf
        Given I am on the "applying-on-own-behalf" page
        When I click the ".govuk-radios__item input[value='0']" element
        And I submit the form
        Then I am redirected to the "nhs-login" page

    Scenario: Should be re-directed to nhs-login-link when no answered to nhs login
        Given I am on the "nhs-login" page
        When I click the ".govuk-radios__item input[value='1']" element
        And I submit the form
        Then I am redirected to the "nhs-login-link" page

    Scenario: Should be re-directed to enter-email when clicking on 
        Given I am on the "nhs-login-link" page
	When I click the "#nhs-login-anchor" element
	Then I am redirected to the "enter-email" nhs page

    Scenario: Should be re-directed to log-in-password when email entered
	Given I am on the "enter-email" nhs page
	When I give the "#user-email" field the nhs email value
	And I submit the form
	Then I am redirected to the "log-in-password" nhs page

    Scenario: Should be redirected to log-in-otp when password entered
        Given I am on the "log-in-password" nhs page
	When I give the "#password-input" field the nhs password value
	And I submit the form
	Then I am redirected to the "log-in-otp" nhs page

    Scenario: Should be redirected to postcode-eligibility when otp entered
        Given I am on the "log-in-otp" nhs page	
	When I give the "#otp-input" field the nhs otp value
	And I submit the form
	Then I am redirected to the "authcode" nhs page

   Scenario: Should be redirected to view-answers when waiting on the authcode
        Given I am on the "authcode" nhs page	
        Then I am redirected to the "view-answers" page

   Scenario: Should be redirected to name when clicking the first change link
        Given I am on the "view-answers" page 
        When I click the ".govuk-link.change-link" element
	Then I am redirected to the "name?ca=1" page
	
   Scenario: Should be redirected to view-answer when submitting a change
	Given I am on the "name?ca=1" page 
        When I submit the form
        Then I am redirected to the "view-answers?ca=1" page
 
