"""Regression tests for safety-critical matcher behaviour."""

import pytest

from cli import parse_patient_from_csv_row
from clinical_trial_eligibility_matcher import (
    ClinicalTrialMatcherEngine,
    CriterionOperator,
    EligibilityStatus,
    PatientClinicalProfile,
    STANDARD_TRIAL_REGISTRY,
    parse_patient_profile,
)


def test_missing_exclusion_data_is_inconclusive():
    trial = next(t for t in STANDARD_TRIAL_REGISTRY if t.trial_id == "NCT04245678")
    patient = PatientClinicalProfile(
        patient_id="PT-MISSING-EXCLUSION",
        age=55,
        gender="female",
        diagnosis="NSCLC",
        stage="Stage IV",
        ecog_ps=0,
        biomarkers={"EGFR": "L858R"},
        labs={"ANC": 2.2, "Platelets": 210.0, "CrCl": 85.0},
        prior_therapies=["Carboplatin"],
        lines_of_prior_therapy=1,
        comorbidities=None,
    )

    result = ClinicalTrialMatcherEngine.match_patient_to_trial(patient, trial)

    assert result.eligibility_status is EligibilityStatus.INCONCLUSIVE_MISSING_DATA
    assert result.missing_critical_data_count == 1
    assert result.exclusions_avoided == 1
    missing = [item for item in result.evaluation_details if item.is_missing_data]
    assert [item.field_path for item in missing] == ["comorbidities"]


def test_dictionary_parser_does_not_invent_clinical_defaults():
    patient = parse_patient_profile({"patient_id": "PT-SPARSE"})

    assert patient.age is None
    assert patient.diagnosis is None
    assert patient.ecog_ps is None
    assert patient.prior_therapies is None
    assert patient.lines_of_prior_therapy is None
    assert patient.comorbidities is None


def test_range_between_operator_is_supported():
    assert ClinicalTrialMatcherEngine._apply_operator(
        5, CriterionOperator.RANGE_BETWEEN, [1, 10]
    )
    assert not ClinicalTrialMatcherEngine._apply_operator(
        11, CriterionOperator.RANGE_BETWEEN, [1, 10]
    )
    assert not ClinicalTrialMatcherEngine._apply_operator(
        5, CriterionOperator.RANGE_BETWEEN, [1]
    )


def test_csv_parser_rejects_invalid_biomarker_json():
    row = {
        "patient_id": "PT-BAD-JSON",
        "age": "60",
        "gender": "female",
        "diagnosis": "NSCLC",
        "biomarkers": "{not-json}",
        "labs": "{}",
    }

    with pytest.raises(ValueError, match="Invalid JSON in 'biomarkers'"):
        parse_patient_from_csv_row(row)


def test_csv_parser_preserves_missing_clinical_fields():
    patient = parse_patient_from_csv_row(
        {
            "patient_id": "PT-SPARSE-CSV",
            "age": "",
            "gender": "",
            "diagnosis": "",
            "ecog_ps": "",
            "biomarkers": "{}",
            "labs": "{}",
            "prior_therapies": "",
            "lines_of_prior_therapy": "",
            "comorbidities": "",
        }
    )

    assert patient.age is None
    assert patient.diagnosis is None
    assert patient.ecog_ps is None
    assert patient.prior_therapies is None
    assert patient.lines_of_prior_therapy is None
    assert patient.comorbidities is None
