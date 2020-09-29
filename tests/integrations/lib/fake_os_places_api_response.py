
class FakeOSPlacesAPIResponse():
    postcode = None
    address_entries = []

    def __init__(self, postcode=None, address_entries=None):
        self.postcode = postcode
        self.address_entries = address_entries

    def to_json(self):
        entries = []
        for entry in self.address_entries:
            entries.append(entry.to_json())

        response = {
          "header" : {
            "uri" : f'https://api.ordnancesurvey.co.uk/places/v1/addresses/postcode?postcode={self.postcode}&dataset=LPI', # noqa E501
            "query" : f'postcode={self.postcode}',
            "offset" : 0,
            "totalresults" : len(self.address_entries),
            "format" : "JSON",
            "dataset" : "LPI",
            "lr" : "EN,CY",
            "maxresults" : 100,
            "epoch" : "78",
            "output_srs" : "EPSG:27700"
          },
          "results" : entries
        }
        return response
