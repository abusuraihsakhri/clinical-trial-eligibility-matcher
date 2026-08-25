"""
Clinical Trial Eligibility Matcher Engine & Protocol Registry
Domain: Clinical Trial Protocol Matching & Patient Phenotyping
Standards: CDISC SDTM/CDASH, NCI Thesaurus, ClinicalTrials.gov Protocol Specifications
"""

from typing import Dict, List, Optional, Any, Tuple
from .models import (
    CriterionType,
    CriterionCategory,
    CriterionOperator,
    EligibilityStatus,
    TrialCriterion,
    ClinicalTrialProtocol,
    PatientClinicalProfile,
    CriterionEvaluationResult,
    TrialMatchResult,
)


# Standard Reference Trial Protocol Registry
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
        ]
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
        ]
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
        ]
    ),
]


class ClinicalTrialMatcherEngine:
    """
    Algorithmic Matcher for Clinical Trial Inclusion/Exclusion Criteria.
    """

    @classmethod
    def evaluate_criterion(cls, criterion: TrialCriterion, patient: PatientClinicalProfile) -> CriterionEvaluationResult:
        """
        Evaluate a single criterion against patient clinical attributes.
        """
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

        # For EXCLUSION criteria:
        # If passed == True, that means the exclusion condition IS present (which is bad -> exclusion triggered!)
        # So from an eligibility standpoint, avoiding exclusion means passed should be False!
        if criterion.criterion_type == CriterionType.EXCLUSION:
            exclusion_triggered = passed
            passed_eligibility = not exclusion_triggered
            msg = "Exclusion condition avoided" if passed_eligibility else f"Exclusion triggered: {criterion.description} (Observed: {val})"
        else:
            passed_eligibility = passed
            msg = "Inclusion met" if passed_eligibility else f"Inclusion failed: Expected {criterion.operator.value} {criterion.expected_value}, got {val}"

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
        """
        Match a patient profile against all criteria of a clinical trial.
        """
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
            res = cls.evaluate_criterion(crit, patient)
            eval_results.append(res)
            total_weight += crit.weight

            if crit.criterion_type == CriterionType.INCLUSION:
                inclusions_total += 1
                if res.is_missing_data:
                    missing_count += 1
                elif res.passed:
                    inclusions_met += 1
                    earned_weight += crit.weight
                else:
                    if crit.is_mandatory:
                        has_mandatory_inclusion_failed = True
            else:
                exclusions_total += 1
                if res.is_missing_data:
                    # Missing data on exclusion -> noted but not hard failure unless specified
                    exclusions_avoided += 1
                    earned_weight += crit.weight
                elif res.passed:
                    exclusions_avoided += 1
                    earned_weight += crit.weight
                else:
                    has_exclusion_triggered = True

        next_steps = []
        if has_exclusion_triggered:
            status = EligibilityStatus.INELIGIBLE
            match_score = 0.0
            next_steps.append("Patient has active exclusion criteria; investigate alternative trial protocols.")
        elif has_mandatory_inclusion_failed:
            status = EligibilityStatus.INELIGIBLE
            match_score = (earned_weight / total_weight * 100.0) if total_weight > 0 else 0.0
            next_steps.append("Patient does not satisfy essential inclusion criteria.")
        elif missing_count > 0:
            status = EligibilityStatus.INCONCLUSIVE_MISSING_DATA
            match_score = (earned_weight / total_weight * 100.0) if total_weight > 0 else 0.0
            next_steps.append(f"Order missing confirmatory testing: {missing_count} criteria require additional diagnostics.")
        else:
            status = EligibilityStatus.ELIGIBLE
            match_score = 100.0
            next_steps.append("Patient meets all I/E criteria! Schedule pre-screening trial visit and informed consent.")

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
        cls, patient: PatientClinicalProfile, registry: Optional[List[ClinicalTrialProtocol]] = None
    ) -> List[TrialMatchResult]:
        """
        Screen a patient against an entire clinical trial registry and rank by match score.
        """
        if registry is None:
            registry = STANDARD_TRIAL_REGISTRY

        results = [cls.match_patient_to_trial(patient, trial) for trial in registry]
        # Rank by score descending, prioritizing ELIGIBLE > INCONCLUSIVE > INELIGIBLE
        status_priority = {
            EligibilityStatus.ELIGIBLE: 3,
            EligibilityStatus.INCONCLUSIVE_MISSING_DATA: 2,
            EligibilityStatus.INELIGIBLE: 1,
        }
        results.sort(key=lambda r: (status_priority[r.eligibility_status], r.overall_match_score_pct), reverse=True)
        return results

    @classmethod
    def _extract_field_value(cls, patient: PatientClinicalProfile, field_path: str) -> Tuple[Any, bool]:
        """Extract a nested field value from patient profile."""
        parts = field_path.split(".")
        root_name = parts[0]

        if root_name == "age":
            return patient.age, True
        if root_name == "gender":
            return patient.gender, True
        if root_name == "diagnosis":
            return patient.diagnosis, True
        if root_name == "stage":
            return patient.stage, patient.stage is not None
        if root_name == "histology":
            return patient.histology, patient.histology is not None
        if root_name == "ecog_ps":
            return patient.ecog_ps, True
        if root_name == "lines_of_prior_therapy":
            return patient.lines_of_prior_therapy, True
        if root_name == "prior_therapies":
            return patient.prior_therapies, True
        if root_name == "comorbidities":
            return patient.comorbidities, True
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
    def _apply_operator(cls, observed: Any, operator: CriterionOperator, expected: Any) -> bool:
        """Evaluate logical/relational operator."""
        try:
            if operator == CriterionOperator.EQUALS:
                return str(observed).strip().lower() == str(expected).strip().lower()
            elif operator == CriterionOperator.NOT_EQUALS:
                return str(observed).strip().lower() != str(expected).strip().lower()
            elif operator == CriterionOperator.GREATER_EQUAL:
                return float(observed) >= float(expected)
            elif operator == CriterionOperator.LESS_EQUAL:
                return float(observed) <= float(expected)
            elif operator == CriterionOperator.GREATER_THAN:
                return float(observed) > float(expected)
            elif operator == CriterionOperator.LESS_THAN:
                return float(observed) < float(expected)
            elif operator == CriterionOperator.IN_SET:
                # If observed is a list, check if expected in observed or any overlap
                if isinstance(observed, list):
                    exp_str = str(expected).lower()
                    return any(exp_str in str(item).lower() for item in observed)
                # If expected is a list, check if observed in expected
                if isinstance(expected, list):
                    obs_str = str(observed).lower()
                    return any(obs_str == str(item).lower() or str(item).lower() in obs_str for item in expected)
                return str(expected).lower() in str(observed).lower()
            elif operator == CriterionOperator.NOT_IN_SET:
                if isinstance(observed, list):
                    exp_str = str(expected).lower()
                    return not any(exp_str in str(item).lower() for item in observed)
                if isinstance(expected, list):
                    obs_str = str(observed).lower()
                    return not any(obs_str == str(item).lower() for item in expected)
                return str(expected).lower() not in str(observed).lower()
            elif operator == CriterionOperator.EXISTS:
                return observed is not None
            elif operator == CriterionOperator.NOT_EXISTS:
                return observed is None
        except (ValueError, TypeError):
            return False
        return False


def parse_patient_profile(data: Dict[str, Any]) -> PatientClinicalProfile:
    """Parse dictionary to PatientClinicalProfile."""
    return PatientClinicalProfile(
        patient_id=str(data.get("patient_id", "PT-TRIAL-001")),
        age=int(data.get("age", 55)),
        gender=str(data.get("gender", "unknown")),
        diagnosis=str(data.get("diagnosis", "NSCLC")),
        stage=data.get("stage"),
        histology=data.get("histology"),
        ecog_ps=int(data.get("ecog_ps", 0)),
        biomarkers=data.get("biomarkers", {}),
        labs=data.get("labs", {}),
        prior_therapies=data.get("prior_therapies", []),
        lines_of_prior_therapy=int(data.get("lines_of_prior_therapy", 0)),
        comorbidities=data.get("comorbidities", []),
    )
