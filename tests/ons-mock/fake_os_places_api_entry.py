
class FakeOSPlacesAPIEntry:
    postcode = None
    city = None
    street = None
    door_number = None
    building_type = None
    uprn = None
    usrn = None
    postal_address_code = None
    lpi_key = None
    x_coordinate = None
    y_coordinate = None
    local_custodian_code = None
    topography_layer_toid = None
    last_update_date = None
    entry_date = None
    blpu_state_date = None

    def __init__(
        self,
        postcode=None,
        city=None,
        street=None,
        door_number=None,
        building_type=None,
        uprn=None,
        usrn=None,
        postal_address_code=None,
        lpi_key=None,
        x_coordinate=None,
        y_coordinate=None,
        local_custodian_code=None,
        topography_layer_toid=None,
        last_update_date=None,
        entry_date=None,
        blpu_state_date=None,
    ):
        self.postcode = postcode
        self.city = city
        self.street = street
        self.door_number = door_number
        self.building_type = building_type
        self.uprn = uprn
        self.usrn = usrn
        self.postal_address_code = postal_address_code
        self.lpi_key = lpi_key
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.local_custodian_code = local_custodian_code
        self.topography_layer_toid = topography_layer_toid
        self.last_update_date = last_update_date
        self.entry_date = entry_date
        self.blpu_state_date = blpu_state_date

    def to_json(self):
        return {
            "LPI" : {
                "UPRN" : self.uprn,
                "ADDRESS" : f'{self.door_number}, {self.street}, {self.city}, {self.postcode}',
                "USRN" : self.usrn,
                "LPI_KEY" : self.lpi_key,
                "PAO_START_NUMBER" : self.door_number,
                "STREET_DESCRIPTION" : self.street,
                "TOWN_NAME" : self.city,
                "ADMINISTRATIVE_AREA" : self.city,
                "POSTCODE_LOCATOR" : self.postcode,
                "RPC" : "1",
                "X_COORDINATE" : self.x_coordinate,
                "Y_COORDINATE" : self.y_coordinate,
                "STATUS" : "APPROVED",
                "LOGICAL_STATUS_CODE" : "1",
                "CLASSIFICATION_CODE" : "RD03",
                "CLASSIFICATION_CODE_DESCRIPTION" : self.building_type,
                "LOCAL_CUSTODIAN_CODE" : self.local_custodian_code,
                "LOCAL_CUSTODIAN_CODE_DESCRIPTION" : self.city,
                "POSTAL_ADDRESS_CODE" : self.postal_address_code,
                "POSTAL_ADDRESS_CODE_DESCRIPTION" : "A record which is linked to PAF",
                "BLPU_STATE_CODE" : "2",
                "BLPU_STATE_CODE_DESCRIPTION" : "In use",
                "TOPOGRAPHY_LAYER_TOID" : self.topography_layer_toid,
                "LAST_UPDATE_DATE" : self.last_update_date,
                "ENTRY_DATE" : self.entry_date,
                "BLPU_STATE_DATE" : self.blpu_state_date,
                "STREET_STATE_CODE" : "2",
                "STREET_STATE_CODE_DESCRIPTION" : "Open",
                "STREET_CLASSIFICATION_CODE" : "8",
                "STREET_CLASSIFICATION_CODE_DESCRIPTION" : "All vehicles",
                "LPI_LOGICAL_STATUS_CODE" : "1",
                "LPI_LOGICAL_STATUS_CODE_DESCRIPTION" : "APPROVED",
                "LANGUAGE" : "EN",
                "MATCH" : 1.0,
                "MATCH_DESCRIPTION" : "EXACT"
            }
        }


def fake_os_places_api_entry(faker):
    def func(
        postcode=None,
        city=None,
        street=None,
        door_number=None,
        building_type=None,
        uprn=None,
        usrn=None,
        postal_address_code=None,
        lpi_key=None,
        x_coordinate=None,
        y_coordinate=None,
        local_custodian_code=None,
        topography_layer_toid=None,
        last_update_date=None,
        entry_date=None,
        blpu_state_date=None,
    ):

        return FakeOSPlacesAPIEntry(
            postcode=postcode or faker.postcode(),
            city=city or faker.city(),
            street=street or faker.street_name(),
            door_number=door_number or faker.building_number(),
            building_type=building_type or faker.random_element(elements=('Semi-Detached', 'Terraced', 'Detached')),
            uprn=uprn or faker.random_int(10000000, 99999999),
            usrn=usrn or faker.random_int(10000000, 99999999),
            postal_address_code=postal_address_code or faker.random_element(elements=('D', 'S', 'N', 'C', 'M')),
            lpi_key=lpi_key or faker.bothify('####?#########'),
            x_coordinate=x_coordinate or faker.numerify(text='######.0'),
            y_coordinate=y_coordinate or faker.numerify(text='######.0'),
            local_custodian_code=local_custodian_code or faker.random_int(1000, 9999),
            topography_layer_toid=topography_layer_toid or faker.numerify('osgb#############'),
            last_update_date=last_update_date or faker.date(pattern='%d/%m/%Y'),
            entry_date=entry_date or faker.date(pattern='%d/%m/%Y'),
            blpu_state_date=blpu_state_date or faker.date(pattern='%d/%m/%Y'),
        )
    return func
