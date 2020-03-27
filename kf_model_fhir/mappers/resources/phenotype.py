"""
This module converts Kids First phenotypes to FHIR phenotypes (derived from FHIR Observation).
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from common.utils import make_select, get, make_identifier


# ttps://www.hl7.org/fhir/valueset-observation-status.html
status = {
    constants.COMMON.TRUE: 'registered'
    constants.COMMON.FALSE: 'unknwon'
}

# https://www.hl7.org/fhir/valueset-observation-interpretation.html
interpretation = {
    constants.PHENOTYPE.OBSERVED.NO: {
        'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation',
        'code': 'NEG',
        'display': 'Negative'
    },
    constants.PHENOTYPE.OBSERVED.YES: {
        'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation',
        'code': 'POS',
        'display': 'Positive'
    }
}

def yield_participants(eng, table, study_id, participants):
    for row in make_select(
            eng, table,
            CONCEPT.PHENOTYPE.EVENT_AGE_DAYS,
            CONCEPT.PHENOTYPE.VISIBLE,
            CONCEPT.PHENOTYPE.NAME,
            CONCEPT.PARTICIPANT.ID,
            CONCEPT.PHENOTYPE.OBSERVED,
        ):
        event_age_days = get(row, CONCEPT.PHENOTYPE.EVENT_AGE_DAYS)
        visible = get(row, ONCEPT.PHENOTYPE.VISIBLE)
        name = get(row, CONCEPT.PHENOTYPE.NAME)
        participant_id = get(row, CONCEPT.PARTICIPANT.ID)
        observed = get(row, CONCEPT.PHENOTYPE.OBSERVED)

        if not name:
            continue

        retval = {
            'resourceType': 'Observation',
            'id': make_identifier('phenotype', study_id,
                                  participant_id, name,
                                  observed, event_age_days),
            'meta': {
                'profile': [
                    'http://fhir.kids-first.io/StructureDefinition/phenotype'
                ]
            },
            'status': status[visible],
            'code': {
                'text': name
            },
            'subject': {
                'reference': f'Patient/{participants[participant_id]["id"]}'
            }
        }

        if event_age_days:
            retval.setdefault('extension', []).append({
                'url': 'http://fhir.kids-first.io/StructureDefinition/age-at-event',
                'valueAge': {
                    'value': int(event_age_days),
                    'unit': 'd',
                    'system': 'http://unitsofmeasure.org',
                    'code': 'days'
                }
            })

        if observed:
            retval.setdefault('interpretation', []).append({
                'coding': interpretation[observed],
                'text': observed
            })

        yield retval
