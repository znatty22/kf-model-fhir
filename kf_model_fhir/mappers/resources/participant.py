"""
This module converts Kids First participants to FHIR participants (derived from FHIR Patient).
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from common.utils import make_select, get


active = {
    constants.COMMON.TRUE: True,
    constants.COMMON.FALSE: False
}

# https://hl7.org/fhir/us/core/ValueSet-omb-ethnicity-category.html
omb_ethnicity_category = {
    constants.ETHNICITY.HISPANIC: {
        'url': 'ombCategory',
        'valueCoding': {
            'system': 'urn:oid:2.16.840.1.113883.6.238',
            'code': '2135-2',
            'display': 'Hispanic or Latino'
        }
    },
    constants.ETHNICITY.NON_HISPANIC: {
        'url': 'ombCategory',
        'valueCoding': {
            'system': 'urn:oid:2.16.840.1.113883.6.238',
            'code': '2186-5',
            'display': 'Not Hispanic or Latino'
        }
    }
}

# https://hl7.org/fhir/us/core/ValueSet-omb-race-category.html
omb_race_category = {
    constants.RACE.NATIVE_AMERICAN: {
        'url': 'ombCategory',
        'valueCoding': {
            'system': 'urn:oid:2.16.840.1.113883.6.238',
            'code': '1002-5',
            'display': 'American Indian or Alaska Native'
        }
    },
    constants.RACE.ASIAN: {
        'url': 'ombCategory',
        'valueCoding': {
            'system': 'urn:oid:2.16.840.1.113883.6.238',
            'code': '2028-9',
            'display': 'Asian'
        }
    },
    constants.RACE.BLACK: {
        'url': 'ombCategory',
        'valueCoding': {
            'system': 'urn:oid:2.16.840.1.113883.6.238',
            'code': '2054-5',
            'display': 'Black or African American'
        }
    },
    constants.RACE.PACIFIC: {
        'url': 'ombCategory',
        'valueCoding': {
            'system': 'urn:oid:2.16.840.1.113883.6.238',
            'code': '2076-8',
            'display': 'Native Hawaiian or Other Pacific Islander'
        }
    },
    constants.RACE.WHITE: {
        'url': 'ombCategory',
        'valueCoding': {
            'system': 'urn:oid:2.16.840.1.113883.6.238',
            'code': '2106-3',
            'display': 'White'
        }
    }
}

# http://hl7.org/fhir/R4/codesystem-administrative-gender.html
administrative_gender = {
    constants.GENDER.MALE: 'male',
    constants.GENDER.FEMALE: 'female',
    constants.COMMON.OTHER: 'other',
    constants.COMMON.UNKNOWN: 'unknown'
}


def yield_participants(eng, table, study_id):
    for row in make_select(
            eng, table,
            CONCEPT.PARTICIPANT.ID,
            CONCEPT.PARTICIPANT.ETHNICITY,
            CONCEPT.PARTICIPANT.RACE,
            CONCEPT.PARTICIPANT.VISIBLE,
            CONCEPT.PARTICIPANT.GENDER
        ):
        participant_id = get(row, CONCEPT.PARTICIPANT.ID)
        ethnicity = get(row, CONCEPT.PARTICIPANT.ETHNICITY)
        race = get(row, CONCEPT.PARTICIPANT.RACE)
        visible = get(row, CONCEPT.PARTICIPANT.VISIBLE)
        gender = get(row, CONCEPT.PARTICIPANT.GENDER)

        retval = {
            'resourceType': 'Patient',
            'id': participant_id,
            'meta': {
                'profile': [
                    'http://fhir.kids-first.io/StructureDefinition/participant'
                ]
            },
            'identifier': [
                {
                    'system': f'http://kf-api-dataservice.kidsfirstdrc.org/participants?study_id={study_id}', 
                    'value': participant_id
                }
            ],
            'active': active[visible]
        }

        if ethnicity:
            retval.setdefault('extension', []).append(
                {
                    'url': 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity',
                    'extension': [
                        omb_ethnicity_category[ethnicity],
                        {
                            'url': 'text',
                            'valueString': ethnicity
                        }
                    ]
                }
            )

        if race:
            retval.setdefault('extension', []).append(
                {
                    'url': 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race',
                    'extension': [
                        omb_race_category[race],
                        {
                            'url': 'text',
                            'valueString': race
                        }
                    ]
                }
            )

        if gender:
            retval['gender'] = administrative_gender[gender]

        yield retval, participant_id
