import pytest

from unittest.mock import patch

from flask import Flask

from vulnerable_people_form.form_pages.shared.render import render_template_with_title

_current_app = Flask(__name__)
_current_app.secret_key = 'test_secret'


@pytest.mark.parametrize("session_variables, expected_nhs_user_value, expected_button_text",
                         [({"nhs_sub": "value"}, True, "Continue"),
                          ({"accessing_saved_answers": True}, False, "Save and continue")])
def test_render_template_with_title_invokes_render_template_with_correct_arguments(
        session_variables, expected_nhs_user_value, expected_button_text):
    with patch("vulnerable_people_form.form_pages.shared.render.render_template") as mock_render_template, \
         _current_app.test_request_context() as test_request_ctx:
        for k, v in session_variables.items():
            test_request_ctx.session[k] = v

        render_template_with_title(
            "postcode-lookup.html",
            previous_path="/date-of-birth",
            values={"postcode": "LS1 1BA"})

        mock_render_template.assert_called_with("postcode-lookup.html",
                                                title_text="What is the postcode where you need support?",
                                                **{
                                                    "nhs_user": expected_nhs_user_value,
                                                    "button_text": expected_button_text,
                                                    "previous_path": "/date-of-birth",
                                                    "values": {"postcode": "LS1 1BA"}
                                                })


def test_render_template_with_title_raises_error_when_invalid_template_name_supplied():
    with pytest.raises(ValueError) as error_info:
        render_template_with_title("invalid-template-name")
        assert error_info.value == "Template names must end with '.html' for a title to be assigned"
