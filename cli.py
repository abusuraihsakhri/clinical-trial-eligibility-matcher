#!/usr/bin/env python3
"""
Command-Line Interface for Clinical Trial Eligibility Matcher
============================================================
Matches patient phenotypes against clinical trial protocols, evaluates
inclusion/exclusion criteria, flags missing data, and ranks trial options.
"""

import sys
import os
import json
import argparse
from typing import Dict, List, Any, Optional

# Ensure project path is accessible
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from clinical_trial_eligibility_matcher import (
    ClinicalTrialMatcherEngine,
    PatientClinicalProfile,
    ClinicalTrialProtocol,
    TrialMatchResult,
    STANDARD_TRIAL_REGISTRY,
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
            "ROS1": "negative"
        },
        "labs": {
            "ANC": 2.4,
            "Platelets": 195.0,
            "CrCl": 72.0,
            "ALT": 28.0,
            "AST": 24.0,
            "Total_Bilirubin": 0.7
        },
        "prior_therapies": ["Carboplatin + Pemetrexed"],
        "lines_of_prior_therapy": 1,
        "comorbidities": ["Hypertension (Controlled)"]
    }


def format_trial_match_report(results: List[TrialMatchResult]) -> str:
    lines = []
    lines.append("=" * 78)
    lines.append(f" CLINICAL TRIAL ELIGIBILITY SCREENING REPORT - {results[0].patient_id if results else 'N/A'}")
    lines.append("=" * 78)
    lines.append(f"Screened against {len(results)} active clinical trial protocol(s):")
    lines.append("-" * 78)

    for idx, r in enumerate(results, start=1):
        lines.append(f"[{idx}] {r.trial_id}: {r.trial_title}")
        lines.append(f"    Phase: {r.phase} | Indication: {r.indication}")
        lines.append(f"    Eligibility Status:  [{r.eligibility_status.value}]")
        lines.append(f"    Match Score:         {r.overall_match_score_pct:.1f}%")
        lines.append(f"    Criteria Summary:    Inclusions Met: {r.inclusions_met}/{r.inclusions_total} | Exclusions Avoided: {r.exclusions_avoided}/{r.exclusions_total} | Missing: {r.missing_critical_data_count}")
        lines.append("    Detailed Criteria Breakdown:")
        for ev in r.evaluation_details:
            mark = "[PASS]" if ev.passed else ("[MISSING]" if ev.is_missing_data else "[FAIL]")
            lines.append(f"      * {mark:<9} ({ev.criterion_type.value}) {ev.description}")
            lines.append(f"                 Observed: {ev.observed_value} | Expected: {ev.expected_value}")
            if not ev.passed or ev.is_missing_data:
                lines.append(f"                 Note: {ev.message}")
        lines.append("    Actionable Next Steps:")
        for step in r.actionable_next_steps:
            lines.append(f"      -> {step}")
        lines.append("-" * 78)

    lines.append("=" * 78)
    return "\n".join(lines)


def interactive_mode():
    print("\n--- Interactive Clinical Trial Patient Eligibility Matcher ---")
    pid = input("Enter Patient ID [e.g. PT-2026-001]: ").strip() or "PT-2026-001"
    age = int(input("Patient Age [e.g. 58]: ").strip() or "58")
    gender = input("Gender (male/female) [female]: ").strip().lower() or "female"
    diag = input("Primary Diagnosis (e.g. NSCLC, Breast Cancer, Heart Failure) [NSCLC]: ").strip() or "NSCLC"
    stage = input("Disease Stage (e.g. Stage IV, Stage III) [Stage IV]: ").strip() or "Stage IV"
    ecog = int(input("ECOG Performance Status (0-4) [default 0]: ").strip() or "0")

    biomarkers = {}
    if "NSCLC" in diag.upper():
        egfr = input("EGFR Mutation Status (Ex19del / L858R / Wildtype / None) [L858R]: ").strip() or "L858R"
        biomarkers["EGFR"] = egfr
    elif "BREAST" in diag.upper():
        er = input("ER Status (positive/negative) [negative]: ").strip() or "negative"
        pr = input("PR Status (positive/negative) [negative]: ").strip() or "negative"
        her2 = input("HER2 Status (positive/negative) [negative]: ").strip() or "negative"
        biomarkers.update({"ER": er, "PR": pr, "HER2": her2})
    elif "HEART" in diag.upper():
        lvef = float(input("LVEF % [e.g. 55]: ").strip() or "55")
        biomarkers["LVEF"] = lvef

    labs = {
        "ANC": float(input("ANC (x10^9/L) [default 2.0]: ").strip() or "2.0"),
        "Platelets": float(input("Platelet Count (x10^9/L) [default 180]: ").strip() or "180"),
        "CrCl": float(input("Creatinine Clearance (mL/min) [default 65]: ").strip() or "65"),
    }
    if "HEART" in diag.upper():
        labs["NT_proBNP"] = float(input("NT-proBNP (pg/mL) [default 450]: ").strip() or "450")
        labs["eGFR"] = float(input("eGFR (mL/min/1.73m2) [default 60]: ").strip() or "60")

    lines_tx = int(input("Lines of prior systemic therapy [default 1]: ").strip() or "1")

    patient = PatientClinicalProfile(
        patient_id=pid,
        age=age,
        gender=gender,
        diagnosis=diag,
        stage=stage,
        ecog_ps=ecog,
        biomarkers=biomarkers,
        labs=labs,
        lines_of_prior_therapy=lines_tx,
        comorbidities=[],
    )

    results = ClinicalTrialMatcherEngine.match_patient_against_registry(patient)
    print("\n" + format_trial_match_report(results))


import csv


def parse_patient_from_csv_row(row: Dict[str, Any]) -> PatientClinicalProfile:
    """Parse a CSV record into a PatientClinicalProfile."""
    pid = row.get("patient_id") or row.get("case_id") or "PT-UNKNOWN"
    age = int(row.get("age", 55))
    gender = row.get("gender", "unknown")
    diagnosis = row.get("diagnosis", "NSCLC")
    stage = row.get("stage") or None
    histology = row.get("histology") or None
    ecog_ps = int(row.get("ecog_ps", 0))

    # Biomarkers
    biomarkers = {}
    raw_bio = row.get("biomarkers", "")
    if raw_bio:
        if isinstance(raw_bio, str) and raw_bio.strip().startswith("{"):
            try:
                biomarkers = json.loads(raw_bio)
            except Exception:
                biomarkers = {}
        elif isinstance(raw_bio, dict):
            biomarkers = raw_bio

    # Labs
    labs = {}
    raw_labs = row.get("labs", "")
    if raw_labs:
        if isinstance(raw_labs, str) and raw_labs.strip().startswith("{"):
            try:
                labs = {k: float(v) for k, v in json.loads(raw_labs).items()}
            except Exception:
                labs = {}
        elif isinstance(raw_labs, dict):
            labs = {k: float(v) for k, v in raw_labs.items()}

    # Prior therapies
    raw_tx = row.get("prior_therapies", "")
    if raw_tx:
        prior_therapies = [t.strip() for t in str(raw_tx).split(";") if t.strip()]
    else:
        prior_therapies = []

    lines_tx = int(row.get("lines_of_prior_therapy", 0))

    # Comorbidities
    raw_comorb = row.get("comorbidities", "")
    if raw_comorb:
        comorbidities = [c.strip() for c in str(raw_comorb).split(",") if c.strip()]
    else:
        comorbidities = []

    return PatientClinicalProfile(
        patient_id=pid,
        age=age,
        gender=gender,
        diagnosis=diagnosis,
        stage=stage,
        histology=histology,
        ecog_ps=ecog_ps,
        biomarkers=biomarkers,
        labs=labs,
        prior_therapies=prior_therapies,
        lines_of_prior_therapy=lines_tx,
        comorbidities=comorbidities,
    )


def run_batch_processing(input_path: str, output_path: str, trial_id: Optional[str] = None):
    """Batch screen patients from CSV against trial protocols and output enriched CSV."""
    with open(input_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    target_trials = None
    if trial_id:
        target_trials = [t for t in STANDARD_TRIAL_REGISTRY if t.trial_id.lower() == trial_id.lower()]
        if not target_trials:
            raise ValueError(f"Trial {trial_id} not found in registry.")

    out_fields = fieldnames + [
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

    out_rows = []
    for r in rows:
        patient = parse_patient_from_csv_row(r)
        results = ClinicalTrialMatcherEngine.match_patient_against_registry(patient, registry=target_trials)
        top = results[0] if results else None

        row_dict = dict(r)
        row_dict["top_match_trial_id"] = top.trial_id if top else "NONE"
        row_dict["top_match_trial_title"] = top.trial_title if top else "NONE"
        row_dict["eligibility_status"] = top.eligibility_status.value if top else "N/A"
        row_dict["match_score_pct"] = round(top.overall_match_score_pct, 2) if top else 0.0
        row_dict["inclusions_met"] = top.inclusions_met if top else 0
        row_dict["inclusions_total"] = top.inclusions_total if top else 0
        row_dict["exclusions_avoided"] = top.exclusions_avoided if top else 0
        row_dict["exclusions_total"] = top.exclusions_total if top else 0
        row_dict["missing_critical_data_count"] = top.missing_critical_data_count if top else 0
        row_dict["actionable_next_steps"] = "; ".join(top.actionable_next_steps) if top else ""
        out_rows.append(row_dict)

    with open(output_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Batch processed {len(out_rows)} records -> {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Clinical Trial Eligibility Matcher & Protocol Screener"
    )
    subparsers = parser.add_subparsers(dest="subcommand")

    # Batch subcommand
    p_batch = subparsers.add_parser("batch", help="Batch process patient cohort CSV against trial registry")
    p_batch.add_argument("-i", "--input", required=True, help="Input patient CSV path")
    p_batch.add_argument("-o", "--output", default="batch_results.csv", help="Output results CSV path")
    p_batch.add_argument("--trial", type=str, help="Filter to a specific Trial ID (e.g. NCT04245678)")

    # Standard flags (can also be invoked directly without subcommand)
    parser.add_argument("--demo", action="store_true", help="Run with a sample NSCLC patient case")
    parser.add_argument("--file", type=str, help="Path to patient clinical profile JSON file")
    parser.add_argument("--trial", type=str, help="Filter screening to a specific Trial ID (e.g. NCT04245678)")
    parser.add_argument("--json", action="store_true", help="Output match results as JSON")
    parser.add_argument("--interactive", action="store_true", help="Interactive patient screening CLI prompt")
    parser.add_argument("--list-trials", action="store_true", help="List registered clinical trial protocols")
    parser.add_argument("-i", "--input", dest="root_input", help="Batch input patient CSV file")
    parser.add_argument("-o", "--output", dest="root_output", default="batch_results.csv", help="Batch output CSV file")

    args = parser.parse_args()

    if args.subcommand == "batch":
        run_batch_processing(args.input, args.output, trial_id=args.trial)
        return

    if args.root_input:
        run_batch_processing(args.root_input, args.root_output, trial_id=args.trial)
        return

    if args.list_trials:
        print("\n=== Registered Clinical Trial Protocols ===")
        for t in STANDARD_TRIAL_REGISTRY:
            print(f"  * [{t.trial_id}] ({t.phase}) {t.title}")
            print(f"      Indication: {t.indication} | Sponsor: {t.sponsor} | Criteria: {len(t.criteria)}")
        return

    if args.interactive:
        interactive_mode()
        return

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            raw = json.load(f)
        patient = parse_patient_profile(raw)
    else:
        patient = parse_patient_profile(get_sample_nsclc_patient())

    if args.trial:
        target_trials = [t for t in STANDARD_TRIAL_REGISTRY if t.trial_id.lower() == args.trial.lower()]
        if not target_trials:
            print(f"Error: Trial {args.trial} not found in registry.")
            return
        results = [ClinicalTrialMatcherEngine.match_patient_to_trial(patient, target_trials[0])]
    else:
        results = ClinicalTrialMatcherEngine.match_patient_against_registry(patient)

    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))
    else:
        print(format_trial_match_report(results))


if __name__ == "__main__":
    main()
