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
from datetime import timedelta

load_dotenv()
BASE_URL = os.getenv("BASE_URL")
class EpicObject:
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
            # print('compact_jws')
            # print(compact_jws)
            headers = CaseInsensitiveDict()
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

            data = {
                'grant_type': 'client_credentials',
                'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
                'client_assertion': compact_jws
            }
            
            response = requests.post(os.getenv("AUTH_TOKEN_URL"), headers=headers, data=data)
            # print('token-response')
            # print(response.text)
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

    def get_patient(self):
        token = self.get_bearer_token()
        
        # headers = {
        #     'accept' : 'application/fhir+json',
        #     'Content-type': 'application/fhir+json'
        # }

        headers = {
            "Authorization": "Bearer " + token['bearer_token'],
            'Accept' : 'application/fhir+json',
            'Content-type': 'application/json'
        }
                
        # TruamSuite Doe
        # 35 y.o., 8/26/1990
        # Legal sex: Male
        # MRN: 2000053407
        # CSN: 100000480340
        # HAR: 100000176522                
                
        patient_id = 'eHk3h3keLZ1WZEDPQm8vpfA3'
        # patient_id = '77474747'
        mrn_n = '77474747'
        url = BASE_URL + 'api/FHIR/R4/Account?subject=Patient/' + patient_id
        url = BASE_URL + 'api/FHIR/R4/Patient?name=TruamSuite%20Doe&birthdate=1990-08-26'# + patient_id
        url = BASE_URL + 'api/FHIR/R4/Patient?name=Cook%20Doe&birthdate=1999-12-22'# + patient_id
        # url = BASE_URL + 'api/FHIR/R4/Patient/' + patient_id
        url = BASE_URL + 'api/FHIR/R4/Patient/' + patient_id + "/$everything"
        
        url = BASE_URL + f"api/FHIR/R4/Observation?patient={patient_id}&category=vital-signs"
        url = BASE_URL + f"api/FHIR/R4/Observation?patient={patient_id}&category=social-history"
        url = BASE_URL + f"api/FHIR/R4/Coverage?patient={patient_id}"
        url = BASE_URL + f"api/FHIR/R4/Procedure?patient={patient_id}"
        url = BASE_URL + f"api/FHIR/R4/Account?patient={patient_id}"
        # url = BASE_URL + f"api/FHIR/R4/Encounter?patient={patient_id}"
        # url = BASE_URL + f"api/FHIR/R4/Encounter?date=2025-08-25&patient={patient_id}" # GET ENCOUNTERS
        # url = BASE_URL + f"api/FHIR/R4/Patient/eHk3h3keLZ1WZEDPQm8vpfA3/Observation?_count=50"
        print(url)
        response = requests.get(url, headers=headers)
        # response = requests.get("https://epicproxy-np.et1131.epichosted.com/FHIRProxy/api/FHIR/R4/Patient/" + patient_id, headers=headers)
        print(response.text)
        f = open('output.json', 'w')
        f.write(response.text)
        f.close()
        json_response = json.loads(response.text)
        
    def create_patient(self):
        token = self.get_bearer_token()

        headers = {
            "Authorization": "Bearer " + token['bearer_token'],
            'Accept' : 'application/json',
            'Content-type': 'application/json'
        }


        data = {
            "resourceType": "Patient",
            "meta": {
                "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]
            },
            "identifier": [
                {
                "use": "official",
                "type": {
                    "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "SS",
                        "display": "Social Security Number"
                    }
                    ],
                    "text": "SSN"
                },
                "system": "urn:oid:2.16.840.1.113883.4.1",
                "value": "521-31-1290",
                "assigner": { "display": "SSA" }
                },
            ],
            "active": True,
            "name": [
                { "use": "official", "family": "Fred", "given": ["John", "Agutu"] }
            ],
            "telecom": [
                { "system": "phone", "value": "555-555-2003", "use": "mobile" },
                { "system": "email", "value": "jagutu@gmail.com", "use": "home" }
            ],
            "gender": "male",
            "birthDate": "1989-03-25",
            "deceasedBoolean": False,
            "address": [
                {
                "use": "home",
                "line": ["123 Main Street"],
                "city": "Madison",
                "state": "WI",
                "postalCode": "53703",
                "country": "US"
                }
            ],
            "communication": [
                {
                "language": {
                    "coding": [
                    { "system": "urn:ietf:bcp:47", "code": "en-US", "display": "English" }
                    ],
                    "text": "English"
                },
                "preferred": True
                }
            ],
            "maritalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                        "code": "U",
                        "display": "Unmarried"
                    }
                ],
                "text": "Single"
            },
            }



        patient_id = 'e63wRTbPfr1p8UW81d8Seiw3'
        response = requests.post("https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Patient", headers=headers, data=json.dumps(data))
        patient_url = response.headers.get("Location")
        patient_id = patient_url.split('/')[1]
        print(patient_id)
        print(response)
        # json_response = json.loads(response.text)
        
    def create_condition(self):
        token = self.get_bearer_token()

        headers = {
            "Authorization": "Bearer " + token['bearer_token'],
            'Accept' : 'application/json',
            'Content-type': 'application/json'
        }


        data = {
            "resourceType": "Condition",
            "clinicalStatus": {
                "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active",
                    "display": "Active"
                }
                ]
            },
            "verificationStatus": {
                "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                    "code": "provisional",
                    "display": "provisional"
                }
                ]
            },
            "category": [
                {
                "coding": [
                    {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                    "code": "problem-list-item",
                    "display": "Problem List Item"
                    }
                ]
                }
            ],
            "severity": {
                "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "24484000",
                    "display": "Severe"
                }
                ]
            },
            "code": {
                "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "44054006",
                    "display": "Diabetes mellitus type 2"
                }
                ],
                "text": "Type 2 Diabetes Mellitus"
            },
            "subject": {
                "reference": "Patient/e63wRTbPfr1p8UW81d8Seiw3",
                "display": "John Doe"
            },
            "encounter": {
                "reference": "Encounter/67890"
            },
            "onsetDateTime": "2025-08-20T14:00:00Z",
            "recordedDate": "2025-08-21T09:30:00Z",
            "asserter": {
                "reference": "Practitioner/222",
                "display": "Dr. Alice Smith"
            },
            "note": [
                {
                "authorString": "Dr. Alice Smith",
                "time": "2025-08-21T09:30:00Z",
                "text": "Patient reports increased thirst and fatigue. Lab tests confirm diabetes."
                }
            ]
        }


        patient_id = 'e63wRTbPfr1p8UW81d8Seiw3'
        response = requests.post("https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Condition", headers=headers, data=json.dumps(data))
        patient_url = response.headers.get("Location")
        print(response.text)
        print(patient_url)
        
    def create_observation(self):
        token = self.get_bearer_token()

        headers = {
            "Authorization": "Bearer " + token['bearer_token'],
            'Accept' : 'application/json',
            'Content-type': 'application/json'
        }

        data = {
  "resourceType": "Observation",
  "identifier": [
  {
    "system": "http://your-system.org/obs",
    "value": "blood-pressure-20250822-1430"
  }
],"status": "final",
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/observation-category",
          "code": "vital-signs",
          "display": "Vital Signs"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "85354-9",
        "display": "Blood pressure panel with all children optional"
      }
    ],
    "text": "Blood pressure systolic & diastolic"
  },
  "subject": {
    "reference": "Patient/eBZnFnAwp8rVbEJP1yHg7rw3",
    "display": "John Doe"
  },
  "encounter": {
    "reference": "Encounter/elC.GW.gA0.Ex86-vRDqmlw3"
  },
  "effectiveDateTime": "2025-08-22T14:32:00Z",
  "performer": [
    {
      "reference": "Practitioner/6789",
      "display": "Dr. Smith"
    }
  ],
  "component": [
    {
      "code": {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "8480-6",
            "display": "Systolic blood pressure"
          }
        ]
      },
      "valueQuantity": {
        "value": 120,
        "unit": "mmHg",
        "system": "http://unitsofmeasure.org",
        "code": "mm[Hg]"
      }
    },
    {
      "code": {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "8462-4",
            "display": "Diastolic blood pressure"
          }
        ]
      },
      "valueQuantity": {
        "value": 80,
        "unit": "mmHg",
        "system": "http://unitsofmeasure.org",
        "code": "mm[Hg]"
      }
    }
  ]
}


        patient_id = 'e63wRTbPfr1p8UW81d8Seiw3'
        response = requests.post("https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Observation", headers=headers, data=json.dumps(data))
        patient_url = response.headers.get("Location")
        print(response.text)
        print(patient_url)

eo = EpicObject()
eo.get_patient()