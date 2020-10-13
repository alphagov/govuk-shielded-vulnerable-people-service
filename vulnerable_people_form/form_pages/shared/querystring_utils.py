from flask import request, session

from vulnerable_people_form.form_pages.shared.constants import SESSION_KEY_QUERYSTRING_PARAMS

_QUERY_STRING_PARAMS_TO_RETAIN = ["la"]  # local authority query string param key


def append_querystring_params(initial_url):
    output_url = initial_url
    session_querystring_params_to_retain = session.get(SESSION_KEY_QUERYSTRING_PARAMS)
    for query_str_param_key in _QUERY_STRING_PARAMS_TO_RETAIN:
        if f"{query_str_param_key}=" in initial_url:
            continue
        if query_str_param_key in request.args:
            output_url = _add_querystring_param_to_url(output_url,
                                                       query_str_param_key,
                                                       request.args[query_str_param_key])
        elif session_querystring_params_to_retain and query_str_param_key in session_querystring_params_to_retain:
            output_url = _add_querystring_param_to_url(output_url,
                                                       query_str_param_key,
                                                       session_querystring_params_to_retain[query_str_param_key])

    return output_url


def get_querystring_params_to_retain():
    output = {}
    for query_str_param in _QUERY_STRING_PARAMS_TO_RETAIN:
        if query_str_param in request.args:
            output[query_str_param] = request.args[query_str_param]
    return output


def _add_querystring_param_to_url(url, key, value):
    prefix_char = "&" if ("?" in url or "&" in url) else "?"
    return f"{url}{prefix_char}{key}={value}"
