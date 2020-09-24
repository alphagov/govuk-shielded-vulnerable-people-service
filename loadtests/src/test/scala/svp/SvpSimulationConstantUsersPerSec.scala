package svp

import io.gatling.core.Predef._
import scala.concurrent.duration._

class SvpSimulationConstantUsersPerSec extends Simulation {
  setUp(ShieldedVulnerablePeople.scnEndToEndJourney.inject(
    constantUsersPerSec(Config.injectUsersPerSecond) during (Config.injectDurationSeconds seconds)))
    .protocols(Config.httpProtocol)
    .maxDuration(Config.duration * 60)
    .assertions(
      global.responseTime
        .percentile(Config.percentageOfResponsesUnderMaxResponseTime)
        .lte(Config.responseTimeMaxMs),
      global.successfulRequests.percent.gt(Config.responseSuccessPercentage)
    )
}
