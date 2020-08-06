import os


def check_postcode(postcode):
    # TODO: add implementation
    return os.environ.get("FAIL_POSTCODE_VERIFICATION") is None
