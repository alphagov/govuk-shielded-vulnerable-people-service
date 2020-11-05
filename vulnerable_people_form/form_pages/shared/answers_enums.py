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
    YES = 0
    NO = 1

    __text_values__ = {
        YES: "Myself",
        NO: "Someone else",
    }


@enum.unique
class PrioritySuperMarketDeliveriesAnswers(EnumWithText):
    YES = 1
    NO = 0

    __text_values__ = {
        YES: "Yes, I want access to priority supermarket deliveries",
        NO: "No, I do not want access to priority supermarket deliveries",
    }


@enum.unique
class ShoppingAssistanceAnswers(EnumWithText):
    YES = 1
    NO = 0

    __text_values__ = {
        YES: "Yes, there’s someone I can rely on to go shopping for me",
        NO: "No, I cannot rely on someone to go shopping for me"
    }


@enum.unique
class BasicCareNeedsAnswers(EnumWithText):
    YES = 1
    NO = 0

    __text_values__ = {
        YES: "Yes, I need someone to contact me",
        NO: "No, I already have the support I need"
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
        YES: "Yes, I have been told that I’m clinically extremely vulnerable to coronavirus",
        NO: "No, I have not been told that I’m clinically extremely vulnerable to coronavirus",
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


@enum.unique
class LiveInEnglandAnswers(EnumWithText):
    YES = 1
    NO = 0

    __text_values__ = {
        YES: "Yes, I live in England",
        NO: "No, I do not live in England",
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
