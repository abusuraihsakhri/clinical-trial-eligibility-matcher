"""
Data Models & Criteria Definitions for Clinical Trial Eligibility Matching.
Domain: Clinical Trial Protocol Matching & Patient Phenotyping
Standards: CDISC SDTM/CDASH, NCI Thesaurus, ClinicalTrials.gov Protocol Specifications
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union


class CriterionType(str, Enum):
    INCLUSION = "INCLUSION"
    EXCLUSION = "EXCLUSION"


class CriterionCategory(str, Enum):
    DEMOGRAPHIC = "DEMOGRAPHIC"
    DIAGNOSIS_HISTOLOGY = "DIAGNOSIS_HISTOLOGY"
    BIOMARKER_GENOMICS = "BIOMARKER_GENOMICS"
    PERFORMANCE_STATUS = "PERFORMANCE_STATUS"
    LAB_VALUE = "LAB_VALUE"
    PRIOR_THERAPY = "PRIOR_THERAPY"
    COMORBIDITY = "COMORBIDITY"


class CriterionOperator(str, Enum):
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    IN_SET = "IN"
    NOT_IN_SET = "NOT_IN"
    RANGE_BETWEEN = "BETWEEN"
    EXISTS = "EXISTS"
    NOT_EXISTS = "NOT_EXISTS"


class EligibilityStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"
    INCONCLUSIVE_MISSING_DATA = "INCONCLUSIVE_MISSING_DATA"


@dataclass
class TrialCriterion:
    criterion_id: str
    description: str
    criterion_type: CriterionType
    category: CriterionCategory
    field_path: str  # e.g., 'age', 'ecog_ps', 'biomarkers.EGFR', 'labs.ANC', 'prior_therapies'
    operator: CriterionOperator
    expected_value: Any
    weight: float = 1.0
    is_mandatory: bool = True


@dataclass
class ClinicalTrialProtocol:
    trial_id: str  # e.g., 'NCT04245678'
    title: str
    phase: str  # e.g., 'Phase III', 'Phase II'
    indication: str
    sponsor: str
    target_enrollment: int
    criteria: List[TrialCriterion] = field(default_factory=list)


@dataclass
class PatientClinicalProfile:
    patient_id: str
    age: int
    gender: str
    diagnosis: str
    stage: Optional[str] = None
    histology: Optional[str] = None
    ecog_ps: int = 0
    biomarkers: Dict[str, Any] = field(default_factory=dict)
    labs: Dict[str, float] = field(default_factory=dict)
    prior_therapies: List[str] = field(default_factory=list)
    lines_of_prior_therapy: int = 0
    comorbidities: List[str] = field(default_factory=list)


@dataclass
class CriterionEvaluationResult:
    criterion_id: str
    description: str
    criterion_type: CriterionType
    category: CriterionCategory
    field_path: str
    observed_value: Any
    expected_value: Any
    passed: bool
    is_missing_data: bool = False
    message: str = ""


@dataclass
class TrialMatchResult:
    patient_id: str
    trial_id: str
    trial_title: str
    phase: str
    indication: str
    eligibility_status: EligibilityStatus
    overall_match_score_pct: float
    total_criteria_evaluated: int
    inclusions_met: int
    inclusions_total: int
    exclusions_avoided: int
    exclusions_total: int
    missing_critical_data_count: int
    evaluation_details: List[CriterionEvaluationResult] = field(default_factory=list)
    actionable_next_steps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "patient_id": self.patient_id,
            "trial_id": self.trial_id,
            "trial_title": self.trial_title,
            "phase": self.phase,
            "indication": self.indication,
            "eligibility_status": self.eligibility_status.value,
            "overall_match_score_pct": round(self.overall_match_score_pct, 2),
            "counts": {
                "total_criteria": self.total_criteria_evaluated,
                "inclusions_met": self.inclusions_met,
                "inclusions_total": self.inclusions_total,
                "exclusions_avoided": self.exclusions_avoided,
                "exclusions_total": self.exclusions_total,
                "missing_critical_data": self.missing_critical_data_count,
            },
            "evaluations": [
                {
                    "criterion_id": e.criterion_id,
                    "description": e.description,
                    "type": e.criterion_type.value,
                    "category": e.category.value,
                    "field": e.field_path,
                    "observed": e.observed_value,
                    "expected": e.expected_value,
                    "passed": e.passed,
                    "missing": e.is_missing_data,
                    "message": e.message,
                }
                for e in self.evaluation_details
            ],
            "actionable_next_steps": self.actionable_next_steps,
        }
