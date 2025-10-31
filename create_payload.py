import os
import json
import logging
import requests
import secrets
from datetime import datetime, timedelta, timezone
from requests.structures import CaseInsensitiveDict
import jwt
import Crypto.PublicKey.RSA as RSA
from dotenv import load_dotenv
from datetime import timedelta, datetime

load_dotenv()
BASE_URL = os.getenv("BASE_URL")
class EpicObject:
    def __init__(self):
        self._token = self.get_bearer_token()
        self._payload = {
            "sender": "Orlando",
            "resourceType": "Bundle",
            "id": "example-bundle",
            "type": "transaction",
            "entry": []
        }

    def get_bearer_token(self):
        
        try:
            client_id = os.getenv("CLIENT_ID")
            private_key_file = 'private_key.pem'

            message = {
                'iss': client_id,
                'sub': client_id,
                'aud': os.getenv("AUTH_TOKEN_URL"),
                'jti': secrets.token_hex(16),
                'iat': int(datetime.now(timezone.utc).timestamp()),
                'exp': int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
            }
            
            with open(private_key_file, 'r') as fh:
                signing_key = fh.read()

            headers = {
                "alg": "RS384",
                "typ": "JWT"
            }
            
            compact_jws = jwt.encode(message, signing_key, algorithm='RS384', headers=headers)
            headers = CaseInsensitiveDict()
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

            data = {
                'grant_type': 'client_credentials',
                'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
                'client_assertion': compact_jws
            }
            
            response = requests.post(os.getenv("AUTH_TOKEN_URL"), headers=headers, data=data)

            response_data = json.loads(response.text)
            
            bearer_token = response_data['access_token']
            
            response = {
                'error_found': False,
                'error_message': '',
                'bearer_token': bearer_token
            }

        except Exception as e:
            response = {
                'error_found': True,
                'error_message': str(e),
                'bearer_token': None
            }

        return response

    def createPayload(self, patient_id, resource:str=''):
        token = self._token
        
        headers = {
            "Authorization": "Bearer " + token['bearer_token'],
            'Accept' : 'application/fhir+json',
            'Content-type': 'application/json'
        }
                
        # patient_id = 'eiLtB3rWviwFjei5r8ikZdg3'
        
        # url = BASE_URL + f"api/FHIR/R4/{resource}/{patient_id}"

        if resource == 'Observation':
            url = BASE_URL + f"api/FHIR/R4/Observation?patient={patient_id}&category=vital-signs"
        elif resource == 'Patient':
            url = BASE_URL + f"api/FHIR/R4/{resource}/{patient_id}"
        else:
            url = BASE_URL + f"api/FHIR/R4/{resource}?patient={patient_id}"
        # url = BASE_URL + f"api/FHIR/R4/Condition?patient={patient_id}"
        # url = BASE_URL + f"api/FHIR/R4/Observation?patient={patient_id}&category=vital-signs"
        # url = BASE_URL + f"api/FHIR/R4/Observation?patient={patient_id}&category=social-history"
        # url = BASE_URL + f"api/FHIR/R4/Coverage?patient={patient_id}"
        # url = BASE_URL + f"api/FHIR/R4/Encounter?patient={patient_id}"

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            self.add_payload_to_container(response, resource)
            # f = open('output.json', 'a')
            # f.write(response.text)
            # f.close()
        json_response = json.loads(response.text)
        
    def add_payload_to_container(self, response, resource):
        try:
            json_response = json.loads(response.text)

            while True:
                if json_response['resourceType'] == 'Bundle':
                    items_count = int(json_response['total'])

                    if items_count > 0:
                        for bundle_resource in json_response['entry']:
                            if bundle_resource['resource']['resourceType'] != 'OperationOutcome':
                                res = {
                                    "resource":{
                                        "resourceType": bundle_resource['resource']['resourceType'],
                                        "id": bundle_resource['resource']['id']
                                    }
                                }
                                self._payload['entry'].append(res)

                if json_response['resourceType'] == 'Patient':
                    res = {
                            "resource":{
                                "resourceType": json_response['resourceType'],
                                "id": json_response['id']
                        }
                    }
                    self._payload['entry'].append(res)

                break

        except Exception as err:
            print(err)

if __name__ == '__main__':
    eo = EpicObject()

    patient_ids = [
        'eiLtB3rWviwFjei5r8ikZdg3',
        'ec7Q1MXSOklybLY-.dpzkpQ3',
        'eeWQ7mvzYE4vdGiILEab4pg3',
        'eiB6H1UFUh4oETfwyCYCIAg3',
        'ebAN8NdK4vsahC59GIKM.BA3',
        'eAN-MU91KyeraEnGEM-SPvA3',
        'e2.ZV0YmRJc7kklJL3TKEHg3',
        'eN55ZUQfbURf9gW8rklg8kw3',
        'esQ0bxBAlh2MFrcs9veJeQw3'
    ]

    resources = ['Patient','Condition', 'Observation', 'Coverage', 'Encounter']
    start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(start)
    for patient_id in patient_ids:
        for resource in resources:
            eo.createPayload(patient_id, resource)

        f = open(patient_id + '.txt', 'w')
        f.write(str(eo._payload))
        f.close()
        eo._payload['entry'].clear()

    end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(end)