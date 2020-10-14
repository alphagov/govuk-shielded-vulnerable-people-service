# Load testing of SVP front end application

This project provides a base set of load tests for the SVP web application using Gatling.

By default, the load tests use the injection type of `atOnceUsers`. To modify this refer to the following guide.

[https://gatling.io/docs/current/general/simulation_setup/](https://gatling.io/docs/current/general/simulation_setup/)

## Prerequisites

- Java 8
- Maven
- Scala

## Run

### Config variables

The following variables can be optionally supplied as command line arguments or setup as environment variables.

- numberOfUsers (default:500)
- duration (default:120 minutes)
- pauseBetweenRequestsInSecondsMin (default:3 seconds)
- pauseBetweenRequestsInSecondsMax (default:6 seconds)
- numberOfRepetitions (default:10 times)
- responseTimeMs (default:800 milliseconds)
- url (default:staging environment)
- injectUsersPerSecond (for simulation SvpSimulationConstantUsersPerSec only, default: 10 users per second)
- injectDurationSeconds (for simulation SvpSimulationConstantUsersPerSec only, default: inject users for 10 seconds)

To execute the tests (default values) via the console run the following command:

`mvn clean package gatling:test -Dgatling.simulationClass={simulation to run, e.g. svp.SvpSimulation}`

To execute the tests and override the default config values run the following command:

`mvn clean package gatling:test -Dgatling.simulationClass={simulation to run, e.g. svp.SvpSimulation} {config var and value with '-D' in front of it, e.g -DnumberOfUsers=1000}`

### Simulations

# ShieldedVulnerablePeople

Details needed

# SvpSimulationConstantUsersPerSec

This simulation adds users at a constant rate for a constant period of time using the 'constantUsersPerSecond' injection method (see [here](https://gatling.io/docs/current/general/simulation_setup/)). Relevant settings:

- `injectUsersPerSecond`: how many users per second to inject (default: 10)
- `injectDurationSeconds`: how long to inject users for (i.e. the duration of the test) (default: 10)
- `pauseBetweenRequestsInSeconds`: how long an individual simulated user pauses between requests (default: randomised between 3 and 5 seconds)
- `numberOfRepetitions`: how many times to repeat the test (default: 1)

Each user makes a 28 request journey (assuming its successful). The number of concurrent users / requests per second will be determined by this, the `injectUsersPerSecond` and the `pauseBetweenRequestsInSeconds` parameters. For example, when this simulation is run nightly by concourse (see `concourse/tasks/gatling-workflow-load-test.yml` config file and the section on automated load tests, below), 36 users per second were injected with 1 second pauses, reaching a steady state of 1008 requsts per second (28 \* 36) after 28 seconds (as this is the time at which new users are added at the same rate as old users drop off.)

To determine the `injectUsersPerSecond` value needed for a target load, just calculate `target requests per second / (n requests in user journey * pause in seconds between requests)` and round up to the nearest user.

### AWS Environments and Gatling

To work, gatling tests requires a working and accessible instance of the form response front-end to be attached to the AWS environment to be tested. At the time of writing
this was only available in the Staging environment (and Prod, but its probably not a good idea to fire automated load tests at Prod). The AWS environment that the load tests point at is controlled by the (private) `url` setting in `loadtests/src/test/main/scala/svp/Config.scala`, which controls the instance of the front-end that gatling sends requests to.

### Automated gatling load tests with concourse

As mentioned above, the SvpSimulationConstantUsersPerSec test is currently run nightly using [Concourse CI](https://concourse-ci.org/). Config for this is found in the
`gatling-workflow-load-test-in-staging` job in `concourse/pipeline.yml`. The full test consists of two main tasks, run in parallel:

1. Triggering the gatling test itself, which is configured by the `concourse/tasks/gatling-workflow-load-test.yml` file. The test uses the configuration described above to run at a steady 1008 requests per second for 20 minutes.

2. Starting the `v-vulnerable-people-daily-wave-two-pipeline-staging` and the `wave2-mvp-reporting-data-daily-pipeline-staging` glue pipelines in the staging environment. These two are the heaviest pipelines that are run regularly, and combined with the gatling tests, should place the system under something close to maximum expected load. The credentials to trigger these workflows (and other AWS operations) are provided by assuming the `concourse-gatling-tester-staging` role, which is done by the task configured in the `concourse/tasks/get-gatling-tester-aws-creds.yml` file.

The gatling tests run for 20 minutes, which shold be sufficient time for both workflows to complete. After the gatling test is over, further tasks upload the html gatling
reports to a timestamped folder in s3 (`3://gds-ons-covid-19-system-test-results-staging/gatling/workflow-load-tests/{date + time of test}/`), and clean out the test data
from the staging environment (this is done by triggering the glue job `rds-clean-gatling-test-data`, which removes all submission data from staging that has the email address `coronavirus-services-smoke-tests@digital.cabinet-office.gov.uk`).
