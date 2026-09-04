"""
Unit and Integration Test Suite for Clinical Trial Eligibility Matcher
=====================================================================
Tests I/E criteria evaluation, biomarker genomics matching, lab thresholds,
missing data handling, and trial ranking.
"""

import unittest
import json
import os
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from clinical_trial_eligibility_matcher import (
    CriterionType,
    CriterionCategory,
    CriterionOperator,
    EligibilityStatus,
    TrialCriterion,
    ClinicalTrialProtocol,
    PatientClinicalProfile,
    CriterionEvaluationResult,
    TrialMatchResult,
    ClinicalTrialMatcherEngine,
    STANDARD_TRIAL_REGISTRY,
    parse_patient_profile,
)


class TestClinicalTrialCriteriaOperators(unittest.TestCase):
    """Test all relational and set operators for criterion matching."""

    def test_equals_operator(self):
        self.assertTrue(ClinicalTrialMatcherEngine._apply_operator("NSCLC", CriterionOperator.EQUALS, "nsclc"))
        self.assertFalse(ClinicalTrialMatcherEngine._apply_operator("SCLC", CriterionOperator.EQUALS, "NSCLC"))

    def test_not_equals_operator(self):
        self.assertTrue(ClinicalTrialMatcherEngine._apply_operator("Squamous", CriterionOperator.NOT_EQUALS, "Adenocarcinoma"))
        self.assertFalse(ClinicalTrialMatcherEngine._apply_operator("Adenocarcinoma", CriterionOperator.NOT_EQUALS, "Adenocarcinoma"))

    def test_greater_equal_operator(self):
        self.assertTrue(ClinicalTrialMatcherEngine._apply_operator(1.8, CriterionOperator.GREATER_EQUAL, 1.5))
        self.assertTrue(ClinicalTrialMatcherEngine._apply_operator(1.5, CriterionOperator.GREATER_EQUAL, 1.5))
        self.assertFalse(ClinicalTrialMatcherEngine._apply_operator(1.2, CriterionOperator.GREATER_EQUAL, 1.5))

    def test_less_equal_operator(self):
        self.assertTrue(ClinicalTrialMatcherEngine._apply_operator(1, CriterionOperator.LESS_EQUAL, 1))
        self.assertTrue(ClinicalTrialMatcherEngine._apply_operator(0, CriterionOperator.LESS_EQUAL, 1))
        self.assertFalse(ClinicalTrialMatcherEngine._apply_operator(2, CriterionOperator.LESS_EQUAL, 1))

    def test_greater_than_operator(self):
        self.assertTrue(ClinicalTrialMatcherEngine._apply_operator(3, CriterionOperator.GREATER_THAN, 2))
        self.assertFalse(ClinicalTrialMatcherEngine._apply_operator(2, CriterionOperator.GREATER_THAN, 2))

    def test_less_than_operator(self):
        self.assertTrue(ClinicalTrialMatcherEngine._apply_operator(1, CriterionOperator.LESS_THAN, 2))
        self.assertFalse(ClinicalTrialMatcherEngine._apply_operator(2, CriterionOperator.LESS_THAN, 2))

    def test_exists_and_not_exists_operators(self):
        self.assertTrue(ClinicalTrialMatcherEngine._apply_operator("Present", CriterionOperator.EXISTS, None))
        self.assertFalse(ClinicalTrialMatcherEngine._apply_operator(None, CriterionOperator.EXISTS, None))
        self.assertTrue(ClinicalTrialMatcherEngine._apply_operator(None, CriterionOperator.NOT_EXISTS, None))
        self.assertFalse(ClinicalTrialMatcherEngine._apply_operator("Present", CriterionOperator.NOT_EXISTS, None))

    def test_in_set_operator_list_in_list(self):
        self.assertTrue(ClinicalTrialMatcherEngine._apply_operator("L858R", CriterionOperator.IN_SET, ["Ex19del", "L858R"]))
        self.assertFalse(ClinicalTrialMatcherEngine._apply_operator("T790M", CriterionOperator.IN_SET, ["Ex19del", "L858R"]))

    def test_in_set_operator_list_in_patient(self):
        self.assertTrue(ClinicalTrialMatcherEngine._apply_operator(["Hypertension", "Active CNS Metastases"], CriterionOperator.IN_SET, "Active CNS Metastases"))
        self.assertFalse(ClinicalTrialMatcherEngine._apply_operator(["Hypertension", "GERD"], CriterionOperator.IN_SET, "Active CNS Metastases"))

    def test_not_in_set_operator(self):
        self.assertTrue(ClinicalTrialMatcherEngine._apply_operator(["Hypertension"], CriterionOperator.NOT_IN_SET, "Active CNS Metastases"))
        self.assertFalse(ClinicalTrialMatcherEngine._apply_operator(["Active CNS Metastases"], CriterionOperator.NOT_IN_SET, "Active CNS Metastases"))


class TestNSCLCTrialMatching(unittest.TestCase):
    """Test matching against NCT04245678 (EGFR+ NSCLC Trial)."""

    def setUp(self):
        self.trial = [t for t in STANDARD_TRIAL_REGISTRY if t.trial_id == "NCT04245678"][0]

    def test_eligible_nsclc_patient(self):
        patient = PatientClinicalProfile(
            patient_id="PT-NSCLC-ELIGIBLE",
            age=55,
            gender="female",
            diagnosis="NSCLC",
            stage="Stage IV",
            ecog_ps=0,
            biomarkers={"EGFR": "L858R"},
            labs={"ANC": 2.2, "Platelets": 210.0, "CrCl": 85.0},
            prior_therapies=["Carboplatin"],
            lines_of_prior_therapy=1,
            comorbidities=["Hypertension"],
        )
        res = ClinicalTrialMatcherEngine.match_patient_to_trial(patient, self.trial)
        self.assertEqual(res.eligibility_status, EligibilityStatus.ELIGIBLE)
        self.assertEqual(res.overall_match_score_pct, 100.0)
        self.assertEqual(res.missing_critical_data_count, 0)

    def test_ineligible_due_to_cns_exclusion(self):
        patient = PatientClinicalProfile(
            patient_id="PT-NSCLC-CNS",
            age=55,
            gender="female",
            diagnosis="NSCLC",
            stage="Stage IV",
            ecog_ps=0,
            biomarkers={"EGFR": "L858R"},
            labs={"ANC": 2.2, "Platelets": 210.0, "CrCl": 85.0},
            prior_therapies=["Carboplatin"],
            lines_of_prior_therapy=1,
            comorbidities=["Active CNS Metastases"],
        )
        res = ClinicalTrialMatcherEngine.match_patient_to_trial(patient, self.trial)
        self.assertEqual(res.eligibility_status, EligibilityStatus.INELIGIBLE)
        self.assertEqual(res.overall_match_score_pct, 0.0)

    def test_ineligible_due_to_high_ecog(self):
        patient = PatientClinicalProfile(
            patient_id="PT-NSCLC-ECOG3",
            age=55,
            gender="male",
            diagnosis="NSCLC",
            stage="Stage IV",
            ecog_ps=3,  # Requires <= 1
            biomarkers={"EGFR": "Ex19del"},
            labs={"ANC": 2.0, "Platelets": 150.0, "CrCl": 60.0},
        )
        res = ClinicalTrialMatcherEngine.match_patient_to_trial(patient, self.trial)
        self.assertEqual(res.eligibility_status, EligibilityStatus.INELIGIBLE)

    def test_ineligible_due_to_low_anc(self):
        patient = PatientClinicalProfile(
            patient_id="PT-NSCLC-NEUTROPENIC",
            age=55,
            gender="male",
            diagnosis="NSCLC",
            stage="Stage IV",
            ecog_ps=1,
            biomarkers={"EGFR": "Ex19del"},
            labs={"ANC": 0.8, "Platelets": 150.0, "CrCl": 60.0},  # ANC < 1.5
        )
        res = ClinicalTrialMatcherEngine.match_patient_to_trial(patient, self.trial)
        self.assertEqual(res.eligibility_status, EligibilityStatus.INELIGIBLE)

    def test_ineligible_due_to_excess_prior_lines(self):
        patient = PatientClinicalProfile(
            patient_id="PT-NSCLC-LINES-EXCEEDED",
            age=55,
            gender="female",
            diagnosis="NSCLC",
            stage="Stage IV",
            ecog_ps=0,
            biomarkers={"EGFR": "L858R"},
            labs={"ANC": 2.0, "Platelets": 150.0, "CrCl": 60.0},
            lines_of_prior_therapy=4,  # Exclusion > 2
        )
        res = ClinicalTrialMatcherEngine.match_patient_to_trial(patient, self.trial)
        self.assertEqual(res.eligibility_status, EligibilityStatus.INELIGIBLE)

    def test_inconclusive_missing_biomarker(self):
        patient = PatientClinicalProfile(
            patient_id="PT-NSCLC-NO-BIOMARKER",
            age=55,
            gender="male",
            diagnosis="NSCLC",
            stage="Stage IV",
            ecog_ps=0,
            biomarkers={},  # Missing EGFR
            labs={"ANC": 2.0, "Platelets": 150.0, "CrCl": 60.0},
        )
        res = ClinicalTrialMatcherEngine.match_patient_to_trial(patient, self.trial)
        self.assertEqual(res.eligibility_status, EligibilityStatus.INCONCLUSIVE_MISSING_DATA)
        self.assertGreater(res.missing_critical_data_count, 0)


class TestTNBCTrialMatching(unittest.TestCase):
    """Test matching against NCT03829384 (TNBC Trial)."""

    def setUp(self):
        self.trial = [t for t in STANDARD_TRIAL_REGISTRY if t.trial_id == "NCT03829384"][0]

    def test_eligible_tnbc_patient(self):
        patient = PatientClinicalProfile(
            patient_id="PT-TNBC-OK",
            age=48,
            gender="female",
            diagnosis="Breast Cancer",
            ecog_ps=0,
            biomarkers={"ER": "negative", "PR": "negative", "HER2": "negative"},
            prior_therapies=[],
            comorbidities=[],
        )
        res = ClinicalTrialMatcherEngine.match_patient_to_trial(patient, self.trial)
        self.assertEqual(res.eligibility_status, EligibilityStatus.ELIGIBLE)

    def test_ineligible_er_positive(self):
        patient = PatientClinicalProfile(
            patient_id="PT-BC-ER-POS",
            age=48,
            gender="female",
            diagnosis="Breast Cancer",
            ecog_ps=0,
            biomarkers={"ER": "positive", "PR": "negative", "HER2": "negative"},
        )
        res = ClinicalTrialMatcherEngine.match_patient_to_trial(patient, self.trial)
        self.assertEqual(res.eligibility_status, EligibilityStatus.INELIGIBLE)

    def test_ineligible_prior_immunotherapy(self):
        patient = PatientClinicalProfile(
            patient_id="PT-TNBC-PRIOR-IO",
            age=48,
            gender="female",
            diagnosis="Breast Cancer",
            ecog_ps=0,
            biomarkers={"ER": "negative", "PR": "negative", "HER2": "negative"},
            prior_therapies=["Pembrolizumab + Carboplatin"],
        )
        res = ClinicalTrialMatcherEngine.match_patient_to_trial(patient, self.trial)
        self.assertEqual(res.eligibility_status, EligibilityStatus.INELIGIBLE)


class TestHeartFailureTrialMatching(unittest.TestCase):
    """Test matching against NCT05112233 (HFpEF Trial)."""

    def setUp(self):
        self.trial = [t for t in STANDARD_TRIAL_REGISTRY if t.trial_id == "NCT05112233"][0]

    def test_eligible_hfpef(self):
        patient = PatientClinicalProfile(
            patient_id="PT-HFPEF-01",
            age=68,
            gender="male",
            diagnosis="Heart Failure",
            biomarkers={"LVEF": 55.0},
            labs={"NT_proBNP": 650.0, "eGFR": 52.0},
            comorbidities=["Hypertension"],
        )
        res = ClinicalTrialMatcherEngine.match_patient_to_trial(patient, self.trial)
        self.assertEqual(res.eligibility_status, EligibilityStatus.ELIGIBLE)

    def test_ineligible_t1d(self):
        patient = PatientClinicalProfile(
            patient_id="PT-HFPEF-T1D",
            age=68,
            gender="male",
            diagnosis="Heart Failure",
            biomarkers={"LVEF": 55.0},
            labs={"NT_proBNP": 650.0, "eGFR": 52.0},
            comorbidities=["Type 1 Diabetes"],
        )
        res = ClinicalTrialMatcherEngine.match_patient_to_trial(patient, self.trial)
        self.assertEqual(res.eligibility_status, EligibilityStatus.INELIGIBLE)


class TestRegistryRankingAndParser(unittest.TestCase):
    """Test multi-trial registry ranking, dictionary parser, and JSON exports."""

    def test_registry_ranking_order(self):
        patient = PatientClinicalProfile(
            patient_id="PT-NSCLC-RANK",
            age=60,
            gender="female",
            diagnosis="NSCLC",
            stage="Stage IV",
            ecog_ps=0,
            biomarkers={"EGFR": "Ex19del"},
            labs={"ANC": 2.5, "Platelets": 200.0, "CrCl": 75.0},
            prior_therapies=[],
            lines_of_prior_therapy=0,
        )
        ranked = ClinicalTrialMatcherEngine.match_patient_against_registry(patient)
        self.assertGreater(len(ranked), 1)
        self.assertEqual(ranked[0].trial_id, "NCT04245678")
        self.assertEqual(ranked[0].eligibility_status, EligibilityStatus.ELIGIBLE)

    def test_parse_patient_profile(self):
        raw = {
            "patient_id": "PT-DICT-TEST",
            "age": 45,
            "gender": "male",
            "diagnosis": "NSCLC",
            "ecog_ps": 1,
            "biomarkers": {"EGFR": "L858R"},
            "labs": {"ANC": 3.0}
        }
        pt = parse_patient_profile(raw)
        self.assertEqual(pt.patient_id, "PT-DICT-TEST")
        self.assertEqual(pt.age, 45)
        self.assertEqual(pt.biomarkers["EGFR"], "L858R")
        self.assertEqual(pt.labs["ANC"], 3.0)

    def test_json_export_structure(self):
        patient = PatientClinicalProfile(
            patient_id="PT-EXPORT-01",
            age=50,
            gender="female",
            diagnosis="NSCLC",
        )
        res = ClinicalTrialMatcherEngine.match_patient_against_registry(patient)
        d = res[0].to_dict()
        self.assertIn("patient_id", d)
        self.assertIn("trial_id", d)
        self.assertIn("eligibility_status", d)
        self.assertIn("evaluations", d)
        self.assertIn("actionable_next_steps", d)

    def test_custom_protocol_creation(self):
        custom_trial = ClinicalTrialProtocol(
            trial_id="NCT-CUSTOM-01",
            title="Custom Trial",
            phase="Phase I",
            indication="Melanoma",
            sponsor="BioTech Co",
            target_enrollment=50,
            criteria=[
                TrialCriterion("INC_MELANOMA", "Diagnosis of Melanoma", CriterionType.INCLUSION, CriterionCategory.DIAGNOSIS_HISTOLOGY, "diagnosis", CriterionOperator.EQUALS, "Melanoma"),
                TrialCriterion("INC_BRAF", "BRAF V600E Mutation", CriterionType.INCLUSION, CriterionCategory.BIOMARKER_GENOMICS, "biomarkers.BRAF", CriterionOperator.EQUALS, "V600E")
            ]
        )
        pt = PatientClinicalProfile(
            patient_id="PT-MELANOMA",
            age=40,
            gender="male",
            diagnosis="Melanoma",
            biomarkers={"BRAF": "V600E"}
        )
        res = ClinicalTrialMatcherEngine.match_patient_to_trial(pt, custom_trial)
        self.assertEqual(res.eligibility_status, EligibilityStatus.ELIGIBLE)
        self.assertEqual(res.overall_match_score_pct, 100.0)


class TestCLIBatchProcessing(unittest.TestCase):
    """Test CLI batch CSV parsing and execution."""

    def test_parse_patient_from_csv_row(self):
        from cli import parse_patient_from_csv_row
        row = {
            "patient_id": "PT-CSV-01",
            "age": "60",
            "gender": "female",
            "diagnosis": "NSCLC",
            "stage": "Stage IV",
            "histology": "Adenocarcinoma",
            "ecog_ps": "1",
            "biomarkers": '{"EGFR": "L858R"}',
            "labs": '{"ANC": 2.5, "CrCl": 70.0}',
            "prior_therapies": "Carboplatin; Pemetrexed",
            "lines_of_prior_therapy": "1",
            "comorbidities": "Hypertension, Hyperlipidemia",
        }
        pt = parse_patient_from_csv_row(row)
        self.assertEqual(pt.patient_id, "PT-CSV-01")
        self.assertEqual(pt.age, 60)
        self.assertEqual(pt.biomarkers["EGFR"], "L858R")
        self.assertEqual(pt.labs["ANC"], 2.5)
        self.assertEqual(len(pt.prior_therapies), 2)
        self.assertEqual(len(pt.comorbidities), 2)

    def test_run_batch_processing(self):
        import tempfile
        from cli import run_batch_processing

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as out_f:
            out_path = out_f.name

        try:
            run_batch_processing("sample.csv", out_path)
            self.assertTrue(os.path.exists(out_path))
            with open(out_path, mode="r", encoding="utf-8") as f:
                lines = f.readlines()
            # 1 header + 4 data rows
            self.assertEqual(len(lines), 5)
            self.assertIn("top_match_trial_id", lines[0])
            self.assertIn("ELIGIBLE", lines[1])
        finally:
            if os.path.exists(out_path):
                os.remove(out_path)


if __name__ == "__main__":
    unittest.main()
