"""
Clinical trial eligibility matcher engine and bundled demonstration registry.

The bundled protocols are illustrative examples for software testing and demonstration.
They are not a live ClinicalTrials.gov registry and must not be used as a substitute
for protocol review by qualified trial staff.
"""

from typing import Any, Dict, List, Optional, Tuple

from .models import (
    ClinicalTrialProtocol,
    CriterionCategory,
    CriterionEvaluationResult,
    CriterionOperator,
    CriterionType,
    EligibilityStatus,
    PatientClinicalProfile,
    TrialCriterion,
    TrialMatchResult,
)


# Illustrative protocol registry used by the CLI, tests, and browser demo.
STANDARD_TRIAL_REGISTRY: List[ClinicalTrialProtocol] = [
    ClinicalTrialProtocol(
        trial_id="NCT04245678",
        title="Phase III Study of Targeted 4th-Gen TKI in EGFR+ Advanced Non-Small Cell Lung Cancer",
        phase="Phase III",
        indication="EGFR-Mutated Non-Small Cell Lung Cancer (NSCLC)",
        sponsor="Oncology Global Trials Inc.",
        target_enrollment=450,
        criteria=[
            TrialCriterion("INC_AGE", "Age >= 18 years", CriterionType.INCLUSION, CriterionCategory.DEMOGRAPHIC, "age", CriterionOperator.GREATER_EQUAL, 18),
            TrialCriterion("INC_DIAG", "Histologically confirmed Stage IV NSCLC", CriterionType.INCLUSION, CriterionCategory.DIAGNOSIS_HISTOLOGY, "diagnosis", CriterionOperator.EQUALS, "NSCLC"),
            TrialCriterion("INC_STAGE", "Stage IV disease", CriterionType.INCLUSION, CriterionCategory.DIAGNOSIS_HISTOLOGY, "stage", CriterionOperator.EQUALS, "Stage IV"),
            TrialCriterion("INC_EGFR", "Documented activating EGFR mutation (Ex19del or L858R)", CriterionType.INCLUSION, CriterionCategory.BIOMARKER_GENOMICS, "biomarkers.EGFR", CriterionOperator.IN_SET, ["Ex19del", "L858R", "positive"]),
            TrialCriterion("INC_ECOG", "ECOG Performance Status 0-1", CriterionType.INCLUSION, CriterionCategory.PERFORMANCE_STATUS, "ecog_ps", CriterionOperator.LESS_EQUAL, 1),
            TrialCriterion("INC_ANC", "Absolute Neutrophil Count (ANC) >= 1.5 x 10^9/L", CriterionType.INCLUSION, CriterionCategory.LAB_VALUE, "labs.ANC", CriterionOperator.GREATER_EQUAL, 1.5),
            TrialCriterion("INC_PLT", "Platelet count >= 100 x 10^9/L", CriterionType.INCLUSION, CriterionCategory.LAB_VALUE, "labs.Platelets", CriterionOperator.GREATER_EQUAL, 100.0),
            TrialCriterion("INC_CRCL", "Creatinine Clearance / eGFR >= 50 mL/min", CriterionType.INCLUSION, CriterionCategory.LAB_VALUE, "labs.CrCl", CriterionOperator.GREATER_EQUAL, 50.0),
            TrialCriterion("EXC_CNS", "Symptomatic or untreated CNS/brain metastases", CriterionType.EXCLUSION, CriterionCategory.COMORBIDITY, "comorbidities", CriterionOperator.IN_SET, "Active CNS Metastases"),
            TrialCriterion("EXC_LINES", "Prior systemic lines of therapy > 2", CriterionType.EXCLUSION, CriterionCategory.PRIOR_THERAPY, "lines_of_prior_therapy", CriterionOperator.GREATER_THAN, 2),
        ],
    ),
    ClinicalTrialProtocol(
        trial_id="NCT03829384",
        title="Phase II Trial of Neoadjuvant Immunotherapy in Triple-Negative Breast Cancer (TNBC)",
        phase="Phase II",
        indication="Triple-Negative Breast Cancer (TNBC)",
        sponsor="Breast Oncology Cooperative Group",
        target_enrollment=220,
        criteria=[
            TrialCriterion("INC_AGE", "Age >= 18 years", CriterionType.INCLUSION, CriterionCategory.DEMOGRAPHIC, "age", CriterionOperator.GREATER_EQUAL, 18),
            TrialCriterion("INC_DIAG", "Invasive Breast Carcinoma", CriterionType.INCLUSION, CriterionCategory.DIAGNOSIS_HISTOLOGY, "diagnosis", CriterionOperator.EQUALS, "Breast Cancer"),
            TrialCriterion("INC_TNBC_ER", "Estrogen Receptor (ER) Negative", CriterionType.INCLUSION, CriterionCategory.BIOMARKER_GENOMICS, "biomarkers.ER", CriterionOperator.EQUALS, "negative"),
            TrialCriterion("INC_TNBC_PR", "Progesterone Receptor (PR) Negative", CriterionType.INCLUSION, CriterionCategory.BIOMARKER_GENOMICS, "biomarkers.PR", CriterionOperator.EQUALS, "negative"),
            TrialCriterion("INC_TNBC_HER2", "HER2 Neu Negative (IHC 0-1+ or ISH non-amplified)", CriterionType.INCLUSION, CriterionCategory.BIOMARKER_GENOMICS, "biomarkers.HER2", CriterionOperator.EQUALS, "negative"),
            TrialCriterion("INC_ECOG", "ECOG Performance Status 0-1", CriterionType.INCLUSION, CriterionCategory.PERFORMANCE_STATUS, "ecog_ps", CriterionOperator.LESS_EQUAL, 1),
            TrialCriterion("EXC_AUTOIMMUNE", "Active autoimmune disease requiring systemic steroids", CriterionType.EXCLUSION, CriterionCategory.COMORBIDITY, "comorbidities", CriterionOperator.IN_SET, "Autoimmune Disease"),
            TrialCriterion("EXC_PRIOR_IO", "Prior exposure to anti-PD-1 or anti-PD-L1 antibodies", CriterionType.EXCLUSION, CriterionCategory.PRIOR_THERAPY, "prior_therapies", CriterionOperator.IN_SET, "Pembrolizumab"),
        ],
    ),
    ClinicalTrialProtocol(
        trial_id="NCT05112233",
        title="Phase III Evaluation of Novel SGLT2 Inhibitor in Heart Failure with Preserved Ejection Fraction",
        phase="Phase III",
        indication="Heart Failure with Preserved Ejection Fraction (HFpEF)",
        sponsor="Cardiovascular Therapeutics Institute",
        target_enrollment=1200,
        criteria=[
            TrialCriterion("INC_AGE", "Age >= 40 years", CriterionType.INCLUSION, CriterionCategory.DEMOGRAPHIC, "age", CriterionOperator.GREATER_EQUAL, 40),
            TrialCriterion("INC_DIAG", "Documented diagnosis of HFpEF", CriterionType.INCLUSION, CriterionCategory.DIAGNOSIS_HISTOLOGY, "diagnosis", CriterionOperator.EQUALS, "Heart Failure"),
            TrialCriterion("INC_LVEF", "Left Ventricular Ejection Fraction (LVEF) >= 50%", CriterionType.INCLUSION, CriterionCategory.BIOMARKER_GENOMICS, "biomarkers.LVEF", CriterionOperator.GREATER_EQUAL, 50.0),
            TrialCriterion("INC_BNP", "NT-proBNP >= 300 pg/mL", CriterionType.INCLUSION, CriterionCategory.LAB_VALUE, "labs.NT_proBNP", CriterionOperator.GREATER_EQUAL, 300.0),
            TrialCriterion("INC_EGFR", "eGFR >= 25 mL/min/1.73m2", CriterionType.INCLUSION, CriterionCategory.LAB_VALUE, "labs.eGFR", CriterionOperator.GREATER_EQUAL, 25.0),
            TrialCriterion("EXC_T1D", "Diagnosis of Type 1 Diabetes Mellitus", CriterionType.EXCLUSION, CriterionCategory.COMORBIDITY, "comorbidities", CriterionOperator.IN_SET, "Type 1 Diabetes"),
            TrialCriterion("EXC_ESRD", "Severe end-stage renal disease on dialysis", CriterionType.EXCLUSION, CriterionCategory.COMORBIDITY, "comorbidities", CriterionOperator.IN_SET, "End-Stage Renal Disease"),
        ],
    ),
]


class ClinicalTrialMatcherEngine:
    """Deterministic matcher for structured inclusion and exclusion criteria."""

    @classmethod
    def evaluate_criterion(
        cls, criterion: TrialCriterion, patient: PatientClinicalProfile
    ) -> CriterionEvaluationResult:
        """Evaluate one criterion against a patient profile."""
        val, exists = cls._extract_field_value(patient, criterion.field_path)

        if not exists or val is None:
            return CriterionEvaluationResult(
                criterion_id=criterion.criterion_id,
                description=criterion.description,
                criterion_type=criterion.criterion_type,
                category=criterion.category,
                field_path=criterion.field_path,
                observed_value=None,
                expected_value=criterion.expected_value,
                passed=False,
                is_missing_data=True,
                message=f"Missing clinical data: '{criterion.field_path}' required for {criterion.description}",
            )

        passed = cls._apply_operator(val, criterion.operator, criterion.expected_value)

        if criterion.criterion_type == CriterionType.EXCLUSION:
            exclusion_triggered = passed
            passed_eligibility = not exclusion_triggered
            msg = (
                "Exclusion condition avoided"
                if passed_eligibility
                else f"Exclusion triggered: {criterion.description} (Observed: {val})"
            )
        else:
            passed_eligibility = passed
            msg = (
                "Inclusion met"
                if passed_eligibility
                else f"Inclusion failed: Expected {criterion.operator.value} {criterion.expected_value}, got {val}"
            )

        return CriterionEvaluationResult(
            criterion_id=criterion.criterion_id,
            description=criterion.description,
            criterion_type=criterion.criterion_type,
            category=criterion.category,
            field_path=criterion.field_path,
            observed_value=val,
            expected_value=criterion.expected_value,
            passed=passed_eligibility,
            is_missing_data=False,
            message=msg,
        )

    @classmethod
    def match_patient_to_trial(
        cls, patient: PatientClinicalProfile, trial: ClinicalTrialProtocol
    ) -> TrialMatchResult:
        """Match a patient profile against every criterion in one protocol."""
        eval_results: List[CriterionEvaluationResult] = []
        inclusions_met = 0
        inclusions_total = 0
        exclusions_avoided = 0
        exclusions_total = 0
        missing_count = 0
        has_exclusion_triggered = False
        has_mandatory_inclusion_failed = False
        total_weight = 0.0
        earned_weight = 0.0

        for crit in trial.criteria:
            if crit.weight < 0:
                raise ValueError(f"Criterion weight must be non-negative: {crit.criterion_id}")

            res = cls.evaluate_criterion(crit, patient)
            eval_results.append(res)
            total_weight += crit.weight

            if res.is_missing_data:
                missing_count += 1
                if crit.criterion_type == CriterionType.INCLUSION:
                    inclusions_total += 1
                else:
                    exclusions_total += 1
                # Missing exclusion data must never be treated as an avoided exclusion.
                continue

            if crit.criterion_type == CriterionType.INCLUSION:
                inclusions_total += 1
                if res.passed:
                    inclusions_met += 1
                    earned_weight += crit.weight
                elif crit.is_mandatory:
                    has_mandatory_inclusion_failed = True
            else:
                exclusions_total += 1
                if res.passed:
                    exclusions_avoided += 1
                    earned_weight += crit.weight
                else:
                    has_exclusion_triggered = True

        weighted_score = (earned_weight / total_weight * 100.0) if total_weight > 0 else 0.0
        next_steps: List[str] = []

        if has_exclusion_triggered:
            status = EligibilityStatus.INELIGIBLE
            match_score = 0.0
            next_steps.append("One or more exclusion criteria are present; review alternative protocols.")
        elif has_mandatory_inclusion_failed:
            status = EligibilityStatus.INELIGIBLE
            match_score = weighted_score
            next_steps.append("One or more mandatory inclusion criteria are not satisfied.")
        elif missing_count > 0:
            status = EligibilityStatus.INCONCLUSIVE_MISSING_DATA
            match_score = weighted_score
            missing_fields = sorted(
                {r.field_path for r in eval_results if r.is_missing_data}
            )
            next_steps.append(
                "Eligibility cannot be determined until missing protocol data are resolved: "
                + ", ".join(missing_fields)
            )
        else:
            status = EligibilityStatus.ELIGIBLE
            match_score = 100.0
            next_steps.append(
                "All encoded criteria are satisfied; confirm against the authoritative protocol before any enrollment decision."
            )

        return TrialMatchResult(
            patient_id=patient.patient_id,
            trial_id=trial.trial_id,
            trial_title=trial.title,
            phase=trial.phase,
            indication=trial.indication,
            eligibility_status=status,
            overall_match_score_pct=match_score,
            total_criteria_evaluated=len(trial.criteria),
            inclusions_met=inclusions_met,
            inclusions_total=inclusions_total,
            exclusions_avoided=exclusions_avoided,
            exclusions_total=exclusions_total,
            missing_critical_data_count=missing_count,
            evaluation_details=eval_results,
            actionable_next_steps=next_steps,
        )

    @classmethod
    def match_patient_against_registry(
        cls,
        patient: PatientClinicalProfile,
        registry: Optional[List[ClinicalTrialProtocol]] = None,
    ) -> List[TrialMatchResult]:
        """Screen a patient against a registry and rank deterministic results."""
        if registry is None:
            registry = STANDARD_TRIAL_REGISTRY

        results = [cls.match_patient_to_trial(patient, trial) for trial in registry]
        status_priority = {
            EligibilityStatus.ELIGIBLE: 3,
            EligibilityStatus.INCONCLUSIVE_MISSING_DATA: 2,
            EligibilityStatus.INELIGIBLE: 1,
        }
        results.sort(
            key=lambda r: (status_priority[r.eligibility_status], r.overall_match_score_pct),
            reverse=True,
        )
        return results

    @classmethod
    def _extract_field_value(
        cls, patient: PatientClinicalProfile, field_path: str
    ) -> Tuple[Any, bool]:
        """Extract a nested field value and whether it is known."""
        parts = field_path.split(".")
        root_name = parts[0]

        simple_fields = {
            "age": patient.age,
            "gender": patient.gender,
            "diagnosis": patient.diagnosis,
            "stage": patient.stage,
            "histology": patient.histology,
            "ecog_ps": patient.ecog_ps,
            "lines_of_prior_therapy": patient.lines_of_prior_therapy,
            "prior_therapies": patient.prior_therapies,
            "comorbidities": patient.comorbidities,
        }
        if root_name in simple_fields:
            value = simple_fields[root_name]
            return value, value is not None

        if root_name == "biomarkers" and len(parts) > 1:
            key = parts[1]
            if key in patient.biomarkers:
                return patient.biomarkers[key], True
            return None, False

        if root_name == "labs" and len(parts) > 1:
            key = parts[1]
            if key in patient.labs:
                return patient.labs[key], True
            return None, False

        return None, False

    @classmethod
    def _apply_operator(
        cls, observed: Any, operator: CriterionOperator, expected: Any
    ) -> bool:
        """Evaluate a supported criterion operator."""
        try:
            if operator == CriterionOperator.EQUALS:
                return str(observed).strip().lower() == str(expected).strip().lower()
            if operator == CriterionOperator.NOT_EQUALS:
                return str(observed).strip().lower() != str(expected).strip().lower()
            if operator == CriterionOperator.GREATER_EQUAL:
                return float(observed) >= float(expected)
            if operator == CriterionOperator.LESS_EQUAL:
                return float(observed) <= float(expected)
            if operator == CriterionOperator.GREATER_THAN:
                return float(observed) > float(expected)
            if operator == CriterionOperator.LESS_THAN:
                return float(observed) < float(expected)
            if operator == CriterionOperator.RANGE_BETWEEN:
                if not isinstance(expected, (list, tuple)) or len(expected) != 2:
                    return False
                lower, upper = expected
                return float(lower) <= float(observed) <= float(upper)
            if operator == CriterionOperator.IN_SET:
                if isinstance(observed, list):
                    exp_str = str(expected).strip().lower()
                    return any(exp_str in str(item).strip().lower() for item in observed)
                if isinstance(expected, list):
                    obs_str = str(observed).strip().lower()
                    return any(
                        obs_str == str(item).strip().lower()
                        or str(item).strip().lower() in obs_str
                        for item in expected
                    )
                return str(expected).strip().lower() in str(observed).strip().lower()
            if operator == CriterionOperator.NOT_IN_SET:
                if isinstance(observed, list):
                    exp_str = str(expected).strip().lower()
                    return not any(exp_str in str(item).strip().lower() for item in observed)
                if isinstance(expected, list):
                    obs_str = str(observed).strip().lower()
                    return not any(
                        obs_str == str(item).strip().lower() for item in expected
                    )
                return str(expected).strip().lower() not in str(observed).strip().lower()
            if operator == CriterionOperator.EXISTS:
                return observed is not None
            if operator == CriterionOperator.NOT_EXISTS:
                return observed is None
        except (ValueError, TypeError):
            return False
        return False


def _optional_int(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    return int(value)


def _optional_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _optional_list(value: Any) -> Optional[List[str]]:
    if value is None:
        return None
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, tuple):
        return [str(item) for item in value]
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    raise TypeError("Expected a list, tuple, string, or null value")


def parse_patient_profile(data: Dict[str, Any]) -> PatientClinicalProfile:
    """Parse a dictionary without inventing clinically meaningful defaults."""
    if not isinstance(data, dict):
        raise TypeError("Patient profile must be a dictionary")

    biomarkers = data.get("biomarkers") or {}
    labs = data.get("labs") or {}
    if not isinstance(biomarkers, dict):
        raise TypeError("'biomarkers' must be an object")
    if not isinstance(labs, dict):
        raise TypeError("'labs' must be an object")

    return PatientClinicalProfile(
        patient_id=str(data.get("patient_id") or "PT-UNKNOWN"),
        age=_optional_int(data.get("age")),
        gender=_optional_text(data.get("gender")),
        diagnosis=_optional_text(data.get("diagnosis")),
        stage=_optional_text(data.get("stage")),
        histology=_optional_text(data.get("histology")),
        ecog_ps=_optional_int(data.get("ecog_ps")),
        biomarkers=biomarkers,
        labs=labs,
        prior_therapies=_optional_list(data.get("prior_therapies")),
        lines_of_prior_therapy=_optional_int(data.get("lines_of_prior_therapy")),
        comorbidities=_optional_list(data.get("comorbidities")),
    )
