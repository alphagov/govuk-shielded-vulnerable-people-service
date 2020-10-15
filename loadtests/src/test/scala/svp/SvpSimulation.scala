package svp

import io.gatling.core.Predef._


class SvpSimulation extends Simulation {
  setUp(ShieldedVulnerablePeople.scnEndToEndJourney.inject(atOnceUsers(Config.numberOfUsers)))
    .protocols(Config.httpProtocol)
    .maxDuration(Config.duration)
    .assertions(
      global.responseTime.max.lt(Config.responseTimeMs),
      global.successfulRequests.percent.gt(Config.responseSuccessPercentage)
    )
}
