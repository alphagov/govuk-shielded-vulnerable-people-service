 # Load testing of SVP front end application #
This project provides a base set of load tests for the SVP web application using Gatling.
 
By default, the load tests use the injection type of `atOnceUsers`. To modify this refer to the following guide.
 
[https://gatling.io/docs/current/general/simulation_setup/](https://gatling.io/docs/current/general/simulation_setup/)
 
 ##	Prerequisites
   - Java 8
   - Maven
   - Scala
   
 ## Run ##
 
### Config variables
The following variables can be optionally supplied as command line arguments or setup as environment variables.
 
 - numberOfUsers (default:500)
 - durationMinutes (default:120 minutes) 
 - pauseBetweenRequestsInSecondsMin (default:3 seconds)
 - pauseBetweenRequestsInSecondsMax (default:6 seconds)
 - numberOfRepetitions (default:10 times)
 - responseTimeMs (default:800 milliseconds)
 - url (default:staging environment)
 
To execute the tests (default values) via the console run the following command:
 
`mvn clean package gatling:test -Dgatling.simulationClass=svp.SvpSimulation`
 
To execute the tests and override the default config values run the following command:
  
`mvn clean package gatling:test -Dgatling.simulationClass=svp.SvpSimulation -DnumberOfUsers=1000`
  