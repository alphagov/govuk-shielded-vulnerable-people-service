from flask import render_template

from vulnerable_people_form.form_pages.shared.session import form_answers, is_nhs_login_user

_GOVUK_NOTIFY_SMS_CHAR_LIMIT = 918


def create_spl_no_match_email_content(reference_number):
    return render_template(
        "_spl_no_match_email_template.md",
        first_name=form_answers()["name"]["first_name"],
        last_name=form_answers()["name"]["last_name"],
        reference_number=reference_number,
        has_someone_to_shop=form_answers().get("do_you_have_someone_to_go_shopping_for_you"),
        told_to_shield=form_answers()["nhs_letter"],
    )


def create_spl_no_match_sms_content(reference_number):
    context = {
        "first_name": form_answers()["name"]["first_name"],
        "last_name": form_answers()["name"]["last_name"],
        "reference_number": reference_number,
        "has_someone_to_shop": form_answers().get("do_you_have_someone_to_go_shopping_for_you"),
        "told_to_shield": form_answers()["nhs_letter"]
    }
    rendered_template = render_template(
        "_spl_no_match_sms_template.txt", **context).replace("\n", "")

    if len(rendered_template) > _GOVUK_NOTIFY_SMS_CHAR_LIMIT:
        rendered_template = render_template(
            "_spl_no_match_sms_template_succinct.txt", **context).replace("\n", "")

    return rendered_template


def create_spl_no_match_letter_content(reference_number):
    return render_template(
        "_spl_no_match_letter_template.md",
        first_name=form_answers()["name"]["first_name"],
        last_name=form_answers()["name"]["last_name"],
        reference_number=reference_number,
        has_someone_to_shop=form_answers().get("do_you_have_someone_to_go_shopping_for_you"),
        told_to_shield=form_answers()["nhs_letter"],
    )


def create_spl_match_email_content(reference_number):
    return render_template(
        "_spl_match_email_template.md",
        first_name=form_answers()["name"]["first_name"],
        last_name=form_answers()["name"]["last_name"],
        reference_number=reference_number,
        has_someone_to_shop=form_answers().get("do_you_have_someone_to_go_shopping_for_you"),
        wants_supermarket_deliveries=form_answers().get("priority_supermarket_deliveries"),
        wants_social_care=form_answers().get("basic_care_needs"),
        has_set_up_account=is_nhs_login_user(),
    )


def create_spl_match_sms_content(reference_number):
    context = {
        "first_name": form_answers()["name"]["first_name"],
        "last_name": form_answers()["name"]["last_name"],
        "reference_number": reference_number,
        "has_someone_to_shop": form_answers().get("do_you_have_someone_to_go_shopping_for_you"),
        "wants_supermarket_deliveries": form_answers().get("priority_supermarket_deliveries"),
        "wants_social_care": form_answers().get("basic_care_needs"),
        "has_set_up_account": is_nhs_login_user()
    }

    rendered_template = render_template(
        "_spl_match_sms_template.txt", **context).replace("\n", "")

    if len(rendered_template) > _GOVUK_NOTIFY_SMS_CHAR_LIMIT:
        rendered_template = render_template(
            "_spl_match_sms_template_succinct.txt", **context).replace("\n", "")

    return rendered_template


def create_spl_match_letter_content(reference_number):
    return render_template(
        "_spl_match_letter_template.md",
        first_name=form_answers()["name"]["first_name"],
        last_name=form_answers()["name"]["last_name"],
        reference_number=reference_number,
        has_someone_to_shop=form_answers().get("do_you_have_someone_to_go_shopping_for_you"),
        wants_supermarket_deliveries=form_answers().get("priority_supermarket_deliveries"),
        wants_social_care=form_answers().get("basic_care_needs"),
        has_set_up_account=is_nhs_login_user(),
    )
