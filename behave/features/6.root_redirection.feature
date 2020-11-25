@core
Feature: COVID-19 Shielded vulnerable people service - gov.uk journey start page redirection
  Scenario: Should be redirected to gov.uk journey start page
      When I navigate to "/"
      Then I am redirected to the external page with URL "https://www.gov.uk/coronavirus-shielding-support"
