from unittest.mock import patch, call

import pytest
from flask import Flask

from vulnerable_people_form.integrations.notification_content import (
    create_spl_no_match_email_content,
    create_spl_no_match_letter_content,
    create_spl_no_match_sms_content,
    create_spl_match_email_content, create_spl_match_letter_content, create_spl_match_sms_content)

_current_app = Flask(__name__)
_current_app.secret_key = 'test_secret'

_first_name = "Jon"
_last_name = "Smith"
_ref_num = "test_ref_number"
_has_someone_to_shop = 0
_told_to_shield = 1
_wants_supermarket_deliveries = 1
_wants_social_care = 1
_has_set_up_account = True

_form_answers_no_match = {
    "name": {"first_name": _first_name, "last_name": _last_name},
    "do_you_have_someone_to_go_shopping_for_you": _has_someone_to_shop,
    "nhs_letter": _told_to_shield
}
_form_answers_spl_match = {
    **_form_answers_no_match,
    "priority_supermarket_deliveries": _wants_supermarket_deliveries,
    "basic_care_needs": _wants_social_care,
    "has_set_up_account": _has_set_up_account
}


@pytest.mark.parametrize("function_ref, template_name",
                         [(create_spl_no_match_email_content, "_spl_no_match_email_template.md"),
                          (create_spl_no_match_letter_content, "_spl_no_match_letter_template.md"),
                          (create_spl_no_match_sms_content, "_spl_no_match_sms_template.txt")])
def test_create_no_match_content_functions_should_invoke_render_template_with_data_from_form_answers(
        function_ref, template_name
):
    with patch("vulnerable_people_form.integrations.notification_content.render_template",
               return_value="rendered_template") as mock_render_template, \
            _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = _form_answers_no_match
        function_ref(_ref_num)
        mock_render_template.assert_called_once_with(
            template_name,
            first_name=_first_name,
            last_name=_last_name,
            reference_number=_ref_num,
            has_someone_to_shop=_has_someone_to_shop,
            told_to_shield=_told_to_shield
        )


def test_create_spl_no_match_sms_content_should_use_concise_template_when_govuk_max_content_length_exceeded():
    very_long_content = "long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content long email content"  # noqa
    with patch("vulnerable_people_form.integrations.notification_content.render_template",
               return_value=very_long_content) as mock_render_template, \
            _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = _form_answers_no_match
        create_spl_no_match_sms_content(_ref_num)

        calls = [
            call("_spl_no_match_sms_template.txt",
                 first_name=_first_name,
                 last_name=_last_name,
                 reference_number=_ref_num,
                 has_someone_to_shop=_has_someone_to_shop,
                 told_to_shield=_told_to_shield),
            call("_spl_no_match_sms_template_succinct.txt",
                 first_name=_first_name,
                 last_name=_last_name,
                 reference_number=_ref_num,
                 has_someone_to_shop=_has_someone_to_shop,
                 told_to_shield=_told_to_shield)
        ]

        mock_render_template.assert_has_calls(calls)


def test_create_spl_no_match_sms_content_should_strip_line_feeds():
    with patch("vulnerable_people_form.integrations.notification_content.render_template",
               return_value="sms\n notification\n content"), \
            _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = _form_answers_no_match
        result = create_spl_no_match_sms_content(_ref_num)
        assert result == "sms notification content"


@pytest.mark.parametrize("function_ref, template_name",
                         [(create_spl_match_email_content, "_spl_match_email_template.md"),
                          (create_spl_match_letter_content, "_spl_match_letter_template.md"),
                          (create_spl_match_sms_content, "_spl_match_sms_template.txt")])
def test_create_spl_match_content_functions_should_invoke_render_template_with_data_from_form_answers(
        function_ref, template_name
):
    with patch("vulnerable_people_form.integrations.notification_content.render_template",
               return_value="rendered_template") as mock_render_template, \
            _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = _form_answers_spl_match
        test_request_ctx.session["nhs_sub"] = "test value"
        function_ref(_ref_num)
        mock_render_template.assert_called_once_with(
            template_name,
            first_name=_first_name,
            last_name=_last_name,
            reference_number=_ref_num,
            has_someone_to_shop=_has_someone_to_shop,
            wants_supermarket_deliveries=_wants_supermarket_deliveries,
            wants_social_care=_wants_social_care,
            has_set_up_account=_has_set_up_account
        )
