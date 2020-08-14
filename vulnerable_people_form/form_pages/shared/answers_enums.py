import enum


class EnumWithText(enum.Enum):
    __text_values__ = {}

    @property
    def value_as_text(self):
        return self.__text_values__[self.value]


@enum.unique
class ViewOrSetupAnswers(EnumWithText):
    VIEW = 0
    SETUP = 1

    __text_values__ = {
        VIEW: "I would like to access an existing account on this service using my NHS login",
        SETUP: "I would like to set up an account",
    }


@enum.unique
class ApplyingOnOwnBehalfAnswers(EnumWithText):
    YES = 1
    NO = 0

    __text_values__ = {
        YES: "Yes, I'm applying on my own behalf.",
        NO: "No, I'm applying on behalf of someone else.",
    }


@enum.unique
class YesNoAnswers(EnumWithText):
    YES = 1
    NO = 0

    __text_values__ = {
        YES: "Yes",
        NO: "No",
    }


@enum.unique
class NHSLetterAnswers(EnumWithText):
    YES = 1
    NO = 2
    NOT_SURE = 3

    __text_values__ = {
        YES: "Yes, I’ve been told to shield",
        NO: "No, I haven’t been told to shield",
        NOT_SURE: "Not sure",
    }


@enum.unique
class MedicalConditionsAnswers(EnumWithText):
    YES = 1
    NO = 0

    __text_values__ = {
        YES: "Yes, I have one of the listed medical conditions",
        NO: "No, I do not have one of the listed medical conditions",
    }


def get_radio_options_from_enum(target_enum, selected_value):
    return [
        {
            "value": value.value,
            "text": value.value_as_text,
            "checked": selected_value == value.value,
        }
        for value in target_enum
    ]
