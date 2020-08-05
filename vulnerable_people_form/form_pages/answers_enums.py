import enum


@enum.unique
class ViewOrSetupAnswers(enum.Enum):
    VIEW = (
        "I would like to access an existing account on this service using my NHS login"
    )
    SETUP = "I would like to set up an account"


@enum.unique
class ApplyingOnOwnBehalfAnswers(enum.Enum):
    YES = "Yes, I'm applying on my own behalf."
    NO = "No, I'm applying on behalf of someone else."


@enum.unique
class YesNoAnswers(enum.Enum):
    YES = "Yes"
    NO = "No"


@enum.unique
class NHSLetterAnswers(enum.Enum):
    YES = "Yes, I’ve been told to shield"
    NO = "No, I haven’t been told to shield"
    NOT_SURE = "Not sure"


@enum.unique
class MedicalConditionsAnswers(enum.Enum):
    YES = "Yes, I have one of the listed medical conditions"
    NO = "No, I do not have one of the listed medical conditions"


def get_radio_options_from_enum(target_enum, selected_value):
    return [
        {
            "value": value.value,
            "text": value.value,
            "checked": selected_value == value.value,
        }
        for value in target_enum
    ]
