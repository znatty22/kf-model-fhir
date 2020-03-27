"""
This module converts Kids First biospecimens to FHIR biospecimens (derived from FHIR Patient).
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from common.utils import make_select, get


# http://hl7.org/fhir/R4/valueset-specimen-status.html
status = {
    constants.COMMON.FALSE: 'unavailable',
    constants.COMMON.TRUE: 'available',
}

# https://www.hl7.org/fhir/v2/0487/index.html
biospecimen_type = {
    constants.SPECIMEN.COMPOSITION.BLOOD: {
        'system': 'http://terminology.hl7.org/CodeSystem/v2-0487',
        'code': 'BLD',
        'display': 'Whole blood',
    },
    constants.SPECIMEN.COMPOSITION.SALIVA: {
        'system': 'http://terminology.hl7.org/CodeSystem/v2-0487',
        'code': 'SAL',
        'display': 'Saliva',
    },
    constants.SPECIMEN.COMPOSITION.TISSUE: {
        'system': 'http://terminology.hl7.org/CodeSystem/v2-0487',
        'code': 'TISS',
        'display': 'Tissue',
    },
}


def yield_participants(eng, table, study_id, participants):
    for row in make_select(
            eng, table,
            CONCEPT.BIOSPECIMEN.ID,
            CONCEPT.BIOSPECIMEN.CONCENTRATION_MG_PER_ML,
            CONCEPT.BIOSPECIMEN.VISIBLE,
            CONCEPT.BIOSPECIMEN.COMPOSITION,
            CONCEPT.PARTICIPANT.ID,
            CONCEPT.BIOSPECIMEN_GROUP.ID,
            CONCEPT.BIOSPECIMEN.VOLUME_UL  
        ):
        biospecimen_id = get(row, CONCEPT.BIOSPECIMEN.ID)
        concentration_mg_per_ml = get(row, CONCEPT.BIOSPECIMEN.CONCENTRATION_MG_PER_ML)
        visible = get(row, CONCEPT.BIOSPECIMEN.VISIBLE)
        composition = get(row, CONCEPT.BIOSPECIMEN.COMPOSITION)
        participant_id = get(row, CONCEPT.PARTICIPANT.ID)
        biospecimen_group_id = get(row, CONCEPT.BIOSPECIMEN_GROUP.ID)
        volume_ul = get(row, CONCEPT.BIOSPECIMEN.VOLUME_UL)

        retval = {
            'resourceType': 'Specimen',
            'id': biospecimen_id,
            'meta': {
                'profile': [
                    'http://fhir.kids-first.io/StructureDefinition/biospecimen'
                ]
            },
            'identifier': [
                {
                    'system': f'http://kf-api-dataservice.kidsfirstdrc.org/biospecimens?study_id={study_id}', 
                    'value': biospecimen_id
                }
            ],
            'status': status[visible]
            'subject': {
                'reference': f'Patient/{participants[participant_id]["id"]}'
            }
        }

        if concentration_mg_per_ml:
            retval.setdefault('extension', []).append(
                {
                    'url': 'http://fhir.kids-first.io/StructureDefinition/concentration',
                    'valueQuantity': {
                        'value': concentration_mg_per_ml,
                        'unit': 'mg/mL'
                    }
                }
            )

        if composition:
            retval['type'] = {
                'coding': biospecimen_type[composition],
                'text': composition
            }

        if biospecimen_group_id:
            retval['parent'] = {
                'reference': f'Specimen/{biospecimen_group_id}'
            }

        if volume_ul:
            retval.setdefault('collection', {})['quantity'] = {
                'unit': 'uL',
                'value': float(volume_ul),
            }

        yield retval, biospecimen_id
