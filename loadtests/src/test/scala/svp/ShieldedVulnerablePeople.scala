package svp

import io.gatling.core.Predef._
import io.gatling.core.feeder.FeederBuilder
import io.gatling.core.structure.{ChainBuilder, ScenarioBuilder}
import io.gatling.http.Predef._

object ShieldedVulnerablePeople {

  private val jsonUserDataFeeder = jsonFile("data/svp_submission_data.json").circular.random

  private val reqStart = exec(flushHttpCache).exec(http("App start")
    .get(Constants.startPath)
    .check(status.is(302)))

  private val reqConfirmation = exec(http("Confirmation")
    .get(Constants.confirmationPath)
    .check(status.is(200)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqApplyPost = exec(http("POST - Applying on own behalf")
    .post(Constants.applyingOnBehalfPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("applying_on_own_behalf", "${applying_on_own_behalf}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqNhsLoginPost = exec(http("POST - Has NHS login")
    .post(Constants.nhsLoginPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("nhs_login", "${nhs_login}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqPostcodeEligibilityPost = exec(http("POST - Postcode")
    .post(Constants.postcodePath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("postcode", "${postcode}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqNHSLetterPost = exec(http("POST - Are you 'shielding' ")
    .post(Constants.nhsLetterPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("nhs_letter", "${nhs_letter}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqNHSNumberPost = exec(http("POST - NHS number")
    .post(Constants.nhsNumberPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("nhs_number", "${nhs_number}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqNamePost = exec(http("POST - Name")
    .post(Constants.namePath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("first_name", "${first_name}")
    .formParam("middle_name", "${middle_name}")
    .formParam("last_name", "${last_name}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqDateOfBirthPost = exec(http("POST - DoB")
    .post(Constants.dobPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("day", "${day}")
    .formParam("month", "${month}")
    .formParam("year", "${year}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqAddressLookupPost = exec(http("POST - Address lookup")
    .post(Constants.addressLookupPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("address", """{"uprn": ${uprn}, "town_city": "${town_city}", "postcode": "${postcode}", "building_and_street_line_1": "${building_and_street_line_1}", "building_and_street_line_2": "${building_and_street_line_2}"}""")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqShoppingSupportPost = exec(http("POST - Shopping support")
    .post(Constants.shoppingSupportPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("priority_supermarket_deliveries", "${priority_supermarket_deliveries}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqSupermarketDeliveriesPost = exec(http("POST - Priority supermarket deliveries")
    .post(Constants.priorityDeliveriesPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("do_you_have_someone_to_go_shopping_for_you", "${do_you_have_someone_to_go_shopping_for_you}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqCareNeedsPost = exec(http("POST - Basic care needs")
    .post(Constants.basicCareNeedsPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("basic_care_needs", "${basic_care_needs}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqContactDetailsPost = exec(http("POST - Contact details")
    .post(Constants.contactDetailsPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("phone_number_calls", "${phone_number_calls}")
    .formParam("phone_number_texts", "${phone_number_texts}")
    .formParam("email", "${email}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqCheckContactDetailsPost = exec(http("POST - Check contact details")
    .post(Constants.checkContactDetailsPath)
    .formParam("csrf_token", "${csrfToken}")
    .formParam("email", "${email}")
    .check(status.is(302)))
    .pause(Config.pauseMin, Config.pauseMax)

  private val reqCheckAnswersPost = exec(http("POST - Check your answers and submit")
    .post(Constants.checkAnswersPath)
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
    buildGetRequest("Applying on own behalf", Constants.applyingOnBehalfPath),
    reqApplyPost,
    buildGetRequest("Has NHS login", Constants.nhsLoginPath),
    reqNhsLoginPost,
    buildGetRequest("Postcode", Constants.postcodePath),
    reqPostcodeEligibilityPost,
    buildGetRequest("Are you 'shielding' ", Constants.nhsLetterPath),
    reqNHSLetterPost,
    buildGetRequest("NHS Number", Constants.nhsNumberPath),
    reqNHSNumberPost,
    buildGetRequest("Name", Constants.namePath),
    reqNamePost,
    buildGetRequest("DoB", Constants.dobPath),
    reqDateOfBirthPost,
    buildGetRequest("Address lookup", Constants.addressLookupPath),
    reqAddressLookupPost,
    buildGetRequest("Shopping support", Constants.shoppingSupportPath),
    reqShoppingSupportPost,
    buildGetRequest("Priority supermarket deliveries", Constants.priorityDeliveriesPath),
    reqSupermarketDeliveriesPost,
    buildGetRequest("Basic care needs", Constants.basicCareNeedsPath),
    reqCareNeedsPost,
    buildGetRequest("Contact details", Constants.contactDetailsPath),
    reqContactDetailsPost,
    buildGetRequest("Check contact details", Constants.checkContactDetailsPath),
    reqCheckContactDetailsPost,
    buildGetRequest("Check answers and submit", Constants.checkAnswersPath),
    reqCheckAnswersPost,
    reqConfirmation
  )
}
