from http.server import HTTPServer, BaseHTTPRequestHandler

import json
import re
from fake_os_places_api_entry import FakeOSPlacesAPIEntry

_postcode_to_uprn = {"LS287TQ": 10000000,
                     "BB11TA": 1000000,
                     "LE674AY": 1000,
                     "L244AD":  2000,
                     "LU11AA":  10000001,
                     "QJ57VC": 3000}


class OnsMockHandler(BaseHTTPRequestHandler):

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()

    def do_GET(self):
        postcode_re = re.compile("postcode=([A-Za-z0-9 ]*)&")
        postcode = postcode_re.search(self.path).group(1)
        data = None
        if postcode == "QJ57VC":
            self.send_response(400)
            self.send_header('Content-type', 'text/json')
            self.end_headers()
        else:
            self._set_response()
            data = {
                    "header": {
                        "uri": f'https://api.ordnancesurvey.co.uk/places/v1/addresses/postcode?postcode={postcode}&dataset=LPI',  # noqa E501
                        "query": f'postcode={postcode}',
                        "offset": 0,
                        "totalresults": 1,
                        "format": "JSON",
                        "dataset": "LPI",
                        "lr": "EN,CY",
                        "maxresults": 100,
                        "epoch": "78",
                        "output_srs": "EPSG:27700"
                    },
                    "results": [FakeOSPlacesAPIEntry(
                            postcode=postcode,
                            city="London",
                            street="Carnegie Street",
                            door_number="1",
                            building_type="Terraced",
                            uprn=10000000,
                            usrn=10000000,
                            postal_address_code="D",
                            lpi_key="1111A111111111",
                            x_coordinate="000000.0",
                            y_coordinate="000000.0",
                            local_custodian_code=1000,
                            topography_layer_toid='osgb01234567891234',
                            last_update_date='01/02/1942',
                            entry_date='01/02/1942',
                            blpu_state_date='01/02/1942'
                            ).to_json()]
                    }
        self.wfile.write(json.dumps(data).encode('utf-8'))


server_address = ('', 8000)
httpd = HTTPServer(server_address, OnsMockHandler)
httpd.serve_forever()
