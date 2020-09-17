package svp

import io.gatling.core.Predef._
import io.gatling.core.feeder.FeederBuilder
import io.gatling.core.structure.{ChainBuilder, ScenarioBuilder}
import io.gatling.http.Predef._

object ShieldedVulnerablePeople {

  private val jsonUserDataFeeder = jsonFile("data/svp_submission_data.json").circular.random

  private val reqStart = exec(flushHttpCache).exec(http("App start")
    .get(PathConstants.startPath)
    .check(status.is(302)))

  private val reqConfirmation = exec(http("Confirmation")
    .get(PathConstants.confirmationPath)
    .check(status.is(200)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqApplyPost = exec(http("POST - Applying on own behalf")
    .post(PathConstants.applyingOnBehalfPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("applying_on_own_behalf", "${applying_on_own_behalf}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqNhsLoginPost = exec(http("POST - Has NHS login")
    .post(PathConstants.nhsLoginPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("nhs_login", "${nhs_login}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqPostcodeEligibilityPost = exec(http("POST - Postcode")
    .post(PathConstants.postcodePath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("postcode", "${postcode}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqNHSLetterPost = exec(http("POST - Are you 'shielding'")
    .post(PathConstants.nhsLetterPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("nhs_letter", "${nhs_letter}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqNHSNumberPost = exec(http("POST - NHS number")
    .post(PathConstants.nhsNumberPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("nhs_number", "${nhs_number}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqNamePost = exec(http("POST - Name")
    .post(PathConstants.namePath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("first_name", "${first_name}")
    .formParam("middle_name", "${middle_name}")
    .formParam("last_name", "${last_name}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqDateOfBirthPost = exec(http("POST - DoB")
    .post(PathConstants.dobPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("day", "${day}")
    .formParam("month", "${month}")
    .formParam("year", "${year}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqAddressLookupPost = exec(http("POST - Address lookup")
    .post(PathConstants.addressLookupPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("address", """{"uprn": ${uprn}, "town_city": "${town_city}", "postcode": "${postcode}", "building_and_street_line_1": "${building_and_street_line_1}", "building_and_street_line_2": "${building_and_street_line_2}"}""")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqShoppingSupportPost = exec(http("POST - Shopping support")
    .post(PathConstants.shoppingSupportPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("priority_supermarket_deliveries", "${priority_supermarket_deliveries}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqSupermarketDeliveriesPost = exec(http("POST - Priority supermarket deliveries")
    .post(PathConstants.priorityDeliveriesPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("do_you_have_someone_to_go_shopping_for_you", "${do_you_have_someone_to_go_shopping_for_you}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqCareNeedsPost = exec(http("POST - Basic care needs")
    .post(PathConstants.basicCareNeedsPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("basic_care_needs", "${basic_care_needs}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqContactDetailsPost = exec(http("POST - Contact details")
    .post(PathConstants.contactDetailsPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("phone_number_calls", "${phone_number_calls}")
    .formParam("phone_number_texts", "${phone_number_texts}")
    .formParam("email", "${email}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqCheckContactDetailsPost = exec(http("POST - Check contact details")
    .post(PathConstants.checkContactDetailsPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("email", "${email}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqCheckAnswersPost = exec(http("POST - Check your answers and submit")
    .post(PathConstants.checkAnswersPath)
    .formParam("csrf_token", "${csrfToken}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private def createScenario(name: String, feed: FeederBuilder, chains: ChainBuilder*): ScenarioBuilder = {
    scenario(name).feed(feed).repeat(Config.repeatTimes) {
      exec(chains)
    }
  }

  private def buildGetRequest(name: String, path: String): ChainBuilder = {
    exec(http(f"GET - $name%s")
      .get(path)
      .check(
        status.is(200),
        regex("""<input type="hidden" name="csrf_token" value="(.*)"/>""").saveAs("csrfToken"))
    ).pause(Config.pauseMin, Config.pauseMax)
  }

  val scnEndToEndJourney = createScenario("End 2 End (No NHS login)", jsonUserDataFeeder,
    exec(flushHttpCache),
    exec(flushSessionCookies),
    reqStart,
    buildGetRequest("Applying on own behalf", PathConstants.applyingOnBehalfPath),
    reqApplyPost,
    buildGetRequest("Has NHS login", PathConstants.nhsLoginPath),
    reqNhsLoginPost,
    buildGetRequest("Postcode", PathConstants.postcodePath),
    reqPostcodeEligibilityPost,
    buildGetRequest("Are you 'shielding'", PathConstants.nhsLetterPath),
    reqNHSLetterPost,
    buildGetRequest("NHS Number", PathConstants.nhsNumberPath),
    reqNHSNumberPost,
    buildGetRequest("Name", PathConstants.namePath),
    reqNamePost,
    buildGetRequest("DoB", PathConstants.dobPath),
    reqDateOfBirthPost,
    buildGetRequest("Address lookup", PathConstants.addressLookupPath),
    reqAddressLookupPost,
    buildGetRequest("Shopping support", PathConstants.shoppingSupportPath),
    reqShoppingSupportPost,
    buildGetRequest("Priority supermarket deliveries", PathConstants.priorityDeliveriesPath),
    reqSupermarketDeliveriesPost,
    buildGetRequest("Basic care needs", PathConstants.basicCareNeedsPath),
    reqCareNeedsPost,
    buildGetRequest("Contact details", PathConstants.contactDetailsPath),
    reqContactDetailsPost,
    buildGetRequest("Check contact details", PathConstants.checkContactDetailsPath),
    reqCheckContactDetailsPost,
    buildGetRequest("Check answers and submit", PathConstants.checkAnswersPath),
    reqCheckAnswersPost,
    reqConfirmation
  )
}
