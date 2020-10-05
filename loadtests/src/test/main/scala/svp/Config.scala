package svp

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

object Config {
  val numberOfUsers: Int = getProperty("numberOfUsers", "500").toInt
  val responseTimeMs:  Int = getProperty("responseTimeMs", "800").toInt
  val repeatTimes: Int = getProperty("numberOfRepetitions", "10").toInt
  val duration: FiniteDuration = getProperty("durationMinutes", "120").toInt.minutes
  val pauseMin: FiniteDuration = getProperty("pauseBetweenRequestsInSecondsMin", "3").toInt.seconds
  val pauseMax: FiniteDuration = getProperty("pauseBetweenRequestsInSecondsMax", "6").toInt.seconds
  val responseSuccessPercentage = 99
  private val url: String = getProperty("url", "https://gds-shielded-vulnerable-people-service-staging.london.cloudapps.digital")

  val httpProtocol = http
    .baseUrl(url)
    .disableFollowRedirect
    .maxRedirects(1)
    .disableWarmUp
    .disableCaching
    .acceptHeader("text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
    .acceptEncodingHeader("gzip, deflate")
    .acceptLanguageHeader("en-GB,en;q=0.5")
    .userAgentHeader("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:80.0) Gecko/20100101 Firefox/80.0/Gatling")

  private def getProperty(propertyName: String, defaultValue: String) = {
    Option(System.getenv(propertyName))
      .orElse(Option(System.getProperty(propertyName)))
      .getOrElse(defaultValue)
  }
}
