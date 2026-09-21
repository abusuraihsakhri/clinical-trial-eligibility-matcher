#!/usr/bin/env python3
"""Command-line interface for the clinical trial eligibility matcher."""

import argparse
import csv
import json
import os
import sys
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from clinical_trial_eligibility_matcher import (
    ClinicalTrialMatcherEngine,
    PatientClinicalProfile,
    STANDARD_TRIAL_REGISTRY,
    TrialMatchResult,
    parse_patient_profile,
)


def get_sample_nsclc_patient() -> Dict[str, Any]:
    return {
        "patient_id": "PT-EGFR-NSCLC-01",
        "age": 62,
        "gender": "female",
        "diagnosis": "NSCLC",
        "stage": "Stage IV",
        "histology": "Adenocarcinoma",
        "ecog_ps": 1,
        "biomarkers": {
            "EGFR": "L858R",
            "PD-L1": 45.0,
            "ALK": "negative",
            "ROS1": "negative",
        },
        "labs": {
            "ANC": 2.4,
            "Platelets": 195.0,
            "CrCl": 72.0,
            "ALT": 28.0,
            "AST": 24.0,
            "Total_Bilirubin": 0.7,
        },
        "prior_therapies": ["Carboplatin + Pemetrexed"],
        "lines_of_prior_therapy": 1,
        "comorbidities": ["Hypertension (Controlled)"],
    }


def format_trial_match_report(results: List[TrialMatchResult]) -> str:
    lines: List[str] = []
    lines.append("=" * 78)
    lines.append(
        f" CLINICAL TRIAL ELIGIBILITY SCREENING REPORT - "
        f"{results[0].patient_id if results else 'N/A'}"
    )
    lines.append("=" * 78)
    lines.append(f"Screened against {len(results)} bundled protocol(s):")
    lines.append("-" * 78)

    for idx, result in enumerate(results, start=1):
        lines.append(f"[{idx}] {result.trial_id}: {result.trial_title}")
        lines.append(f"    Phase: {result.phase} | Indication: {result.indication}")
        lines.append(f"    Eligibility Status:  [{result.eligibility_status.value}]")
        lines.append(f"    Match Score:         {result.overall_match_score_pct:.1f}%")
        lines.append(
            "    Criteria Summary:    "
            f"Inclusions Met: {result.inclusions_met}/{result.inclusions_total} | "
            f"Exclusions Avoided: {result.exclusions_avoided}/{result.exclusions_total} | "
            f"Missing: {result.missing_critical_data_count}"
        )
        lines.append("    Detailed Criteria Breakdown:")
        for evaluation in result.evaluation_details:
            mark = (
                "[MISSING]"
                if evaluation.is_missing_data
                else ("[PASS]" if evaluation.passed else "[FAIL]")
            )
            lines.append(
                f"      * {mark:<9} ({evaluation.criterion_type.value}) "
                f"{evaluation.description}"
            )
            lines.append(
                f"                 Observed: {evaluation.observed_value} | "
                f"Expected: {evaluation.expected_value}"
            )
            if not evaluation.passed or evaluation.is_missing_data:
                lines.append(f"                 Note: {evaluation.message}")
        lines.append("    Next Steps:")
        for step in result.actionable_next_steps:
            lines.append(f"      -> {step}")
        lines.append("-" * 78)

    lines.append(
        "Bundled protocols are illustrative. Confirm eligibility against the "
        "authoritative current study protocol."
    )
    lines.append("=" * 78)
    return "\n".join(lines)


def interactive_mode() -> None:
    print("\n--- Interactive Clinical Trial Eligibility Matcher ---")
    pid = input("Patient ID [PT-2026-001]: ").strip() or "PT-2026-001"
    age = int(input("Age [58]: ").strip() or "58")
    gender = input("Sex/gender [female]: ").strip().lower() or "female"
    diagnosis = (
        input("Primary diagnosis [NSCLC]: ").strip() or "NSCLC"
    )
    stage = input("Disease stage [Stage IV]: ").strip() or "Stage IV"
    ecog = int(input("ECOG performance status [0]: ").strip() or "0")

    biomarkers: Dict[str, Any] = {}
    if "NSCLC" in diagnosis.upper():
        biomarkers["EGFR"] = (
            input("EGFR status (Ex19del/L858R/Wildtype) [L858R]: ").strip()
            or "L858R"
        )
    elif "BREAST" in diagnosis.upper():
        biomarkers.update(
            {
                "ER": input("ER status [negative]: ").strip() or "negative",
                "PR": input("PR status [negative]: ").strip() or "negative",
                "HER2": input("HER2 status [negative]: ").strip() or "negative",
            }
        )
    elif "HEART" in diagnosis.upper():
        biomarkers["LVEF"] = float(input("LVEF % [55]: ").strip() or "55")

    labs: Dict[str, float] = {
        "ANC": float(input("ANC x10^9/L [2.0]: ").strip() or "2.0"),
        "Platelets": float(
            input("Platelet count x10^9/L [180]: ").strip() or "180"
        ),
        "CrCl": float(input("Creatinine clearance mL/min [65]: ").strip() or "65"),
    }
    if "HEART" in diagnosis.upper():
        labs["NT_proBNP"] = float(
            input("NT-proBNP pg/mL [450]: ").strip() or "450"
        )
        labs["eGFR"] = float(
            input("eGFR mL/min/1.73m2 [60]: ").strip() or "60"
        )

    lines_tx = int(
        input("Lines of prior systemic therapy [1]: ").strip() or "1"
    )

    patient = PatientClinicalProfile(
        patient_id=pid,
        age=age,
        gender=gender,
        diagnosis=diagnosis,
        stage=stage,
        ecog_ps=ecog,
        biomarkers=biomarkers,
        labs=labs,
        prior_therapies=None,
        lines_of_prior_therapy=lines_tx,
        comorbidities=[],
    )

    results = ClinicalTrialMatcherEngine.match_patient_against_registry(patient)
    print("\n" + format_trial_match_report(results))


def _optional_int(value: Any, field_name: str) -> Optional[int]:
    if value is None or str(value).strip() == "":
        return None
    try:
        return int(str(value).strip())
    except ValueError as exc:
        raise ValueError(f"Invalid integer for '{field_name}': {value!r}") from exc


def _parse_json_object(value: Any, field_name: str) -> Dict[str, Any]:
    if value is None or value == "":
        return {}
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(str(value))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in '{field_name}': {exc.msg}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"'{field_name}' must contain a JSON object")
    return parsed


def _parse_list(value: Any, delimiter: str) -> Optional[List[str]]:
    if value is None or str(value).strip() == "":
        return None
    text = str(value).strip()
    if text.lower() in {"none", "no", "n/a", "na"}:
        return []
    return [item.strip() for item in text.split(delimiter) if item.strip()]


def parse_patient_from_csv_row(row: Dict[str, Any]) -> PatientClinicalProfile:
    """Parse one CSV row without substituting clinical defaults."""
    patient_id = row.get("patient_id") or row.get("case_id") or "PT-UNKNOWN"
    biomarkers = _parse_json_object(row.get("biomarkers"), "biomarkers")
    raw_labs = _parse_json_object(row.get("labs"), "labs")

    try:
        labs = {key: float(value) for key, value in raw_labs.items()}
    except (TypeError, ValueError) as exc:
        raise ValueError("'labs' values must be numeric") from exc

    return PatientClinicalProfile(
        patient_id=str(patient_id),
        age=_optional_int(row.get("age"), "age"),
        gender=(str(row["gender"]).strip() if row.get("gender") else None),
        diagnosis=(str(row["diagnosis"]).strip() if row.get("diagnosis") else None),
        stage=(str(row["stage"]).strip() if row.get("stage") else None),
        histology=(str(row["histology"]).strip() if row.get("histology") else None),
        ecog_ps=_optional_int(row.get("ecog_ps"), "ecog_ps"),
        biomarkers=biomarkers,
        labs=labs,
        prior_therapies=_parse_list(row.get("prior_therapies"), ";"),
        lines_of_prior_therapy=_optional_int(
            row.get("lines_of_prior_therapy"), "lines_of_prior_therapy"
        ),
        comorbidities=_parse_list(row.get("comorbidities"), ","),
    )


def run_batch_processing(
    input_path: str, output_path: str, trial_id: Optional[str] = None
) -> None:
    """Batch-screen patients from CSV and write an enriched result CSV."""
    with open(input_path, mode="r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    if not fieldnames:
        raise ValueError("Input CSV has no header row")

    target_trials = None
    if trial_id:
        target_trials = [
            trial
            for trial in STANDARD_TRIAL_REGISTRY
            if trial.trial_id.lower() == trial_id.lower()
        ]
        if not target_trials:
            raise ValueError(f"Trial {trial_id} not found in bundled registry.")

    output_fields = fieldnames + [
        "top_match_trial_id",
        "top_match_trial_title",
        "eligibility_status",
        "match_score_pct",
        "inclusions_met",
        "inclusions_total",
        "exclusions_avoided",
        "exclusions_total",
        "missing_critical_data_count",
        "actionable_next_steps",
    ]

    output_rows: List[Dict[str, Any]] = []
    for row_number, row in enumerate(rows, start=2):
        try:
            patient = parse_patient_from_csv_row(row)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid patient data on CSV row {row_number}: {exc}") from exc

        results = ClinicalTrialMatcherEngine.match_patient_against_registry(
            patient, registry=target_trials
        )
        top = results[0] if results else None

        output_row = dict(row)
        output_row["top_match_trial_id"] = top.trial_id if top else "NONE"
        output_row["top_match_trial_title"] = top.trial_title if top else "NONE"
        output_row["eligibility_status"] = (
            top.eligibility_status.value if top else "N/A"
        )
        output_row["match_score_pct"] = (
            round(top.overall_match_score_pct, 2) if top else 0.0
        )
        output_row["inclusions_met"] = top.inclusions_met if top else 0
        output_row["inclusions_total"] = top.inclusions_total if top else 0
        output_row["exclusions_avoided"] = top.exclusions_avoided if top else 0
        output_row["exclusions_total"] = top.exclusions_total if top else 0
        output_row["missing_critical_data_count"] = (
            top.missing_critical_data_count if top else 0
        )
        output_row["actionable_next_steps"] = (
            "; ".join(top.actionable_next_steps) if top else ""
        )
        output_rows.append(output_row)

    with open(output_path, mode="w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Batch processed {len(output_rows)} records -> {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clinical Trial Eligibility Matcher"
    )
    subparsers = parser.add_subparsers(dest="subcommand")

    batch_parser = subparsers.add_parser(
        "batch", help="Batch process a patient CSV against the bundled registry"
    )
    batch_parser.add_argument("-i", "--input", required=True, help="Input patient CSV")
    batch_parser.add_argument(
        "-o", "--output", default="batch_results.csv", help="Output results CSV"
    )
    batch_parser.add_argument("--trial", help="Filter to one bundled trial ID")

    parser.add_argument("--demo", action="store_true", help="Run the sample NSCLC case")
    parser.add_argument("--file", help="Patient clinical profile JSON file")
    parser.add_argument("--trial", help="Filter to one bundled trial ID")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument(
        "--interactive", action="store_true", help="Run the interactive prompt"
    )
    parser.add_argument(
        "--list-trials", action="store_true", help="List bundled protocols"
    )
    parser.add_argument("-i", "--input", dest="root_input", help="Batch input CSV")
    parser.add_argument(
        "-o",
        "--output",
        dest="root_output",
        default="batch_results.csv",
        help="Batch output CSV",
    )

    args = parser.parse_args()

    if args.subcommand == "batch":
        run_batch_processing(args.input, args.output, trial_id=args.trial)
        return

    if args.root_input:
        run_batch_processing(args.root_input, args.root_output, trial_id=args.trial)
        return

    if args.list_trials:
        print("\n=== Bundled Demonstration Protocols ===")
        for trial in STANDARD_TRIAL_REGISTRY:
            print(f"  * [{trial.trial_id}] ({trial.phase}) {trial.title}")
            print(
                f"      Indication: {trial.indication} | "
                f"Sponsor label: {trial.sponsor} | Criteria: {len(trial.criteria)}"
            )
        return

    if args.interactive:
        interactive_mode()
        return

    if args.file:
        with open(args.file, "r", encoding="utf-8") as handle:
            patient = parse_patient_profile(json.load(handle))
    else:
        patient = parse_patient_profile(get_sample_nsclc_patient())

    if args.trial:
        target_trials = [
            trial
            for trial in STANDARD_TRIAL_REGISTRY
            if trial.trial_id.lower() == args.trial.lower()
        ]
        if not target_trials:
            parser.error(f"Trial {args.trial} not found in bundled registry")
        results = [
            ClinicalTrialMatcherEngine.match_patient_to_trial(
                patient, target_trials[0]
            )
        ]
    else:
        results = ClinicalTrialMatcherEngine.match_patient_against_registry(patient)

    if args.json:
        print(json.dumps([result.to_dict() for result in results], indent=2))
    else:
        print(format_trial_match_report(results))


if __name__ == "__main__":
    main()
