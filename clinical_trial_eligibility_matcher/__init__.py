"""
Clinical Trial Eligibility Matcher Package
Domain: Clinical Trial Protocol Matching & Patient Phenotyping
Standards: CDISC SDTM/CDASH, NCI Thesaurus, ClinicalTrials.gov Specifications
"""

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
from .engine import (
    ClinicalTrialMatcherEngine,
    STANDARD_TRIAL_REGISTRY,
    parse_patient_profile,
)

__all__ = [
    "CriterionType",
    "CriterionCategory",
    "CriterionOperator",
    "EligibilityStatus",
    "TrialCriterion",
    "ClinicalTrialProtocol",
    "PatientClinicalProfile",
    "CriterionEvaluationResult",
    "TrialMatchResult",
    "ClinicalTrialMatcherEngine",
    "STANDARD_TRIAL_REGISTRY",
    "parse_patient_profile",
]
