# Clinical Trial Eligibility Matcher

> **Protocol Inclusion/Exclusion (I/E) Criteria Evaluation & Patient Screening Engine**  
> Reference Standards: **ClinicalTrials.gov Protocol Schema, CDISC SDTM/CDASH, NCI Thesaurus, RECIST 1.1**

---

## Overview

The **Clinical Trial Eligibility Matcher** is a clinical research matching platform that screens patient EHR phenotypes against trial protocols.

It evaluates multi-attribute eligibility criteria across **Demographics**, **Histology/Staging**, **Biomarker Genomics**, **ECOG Performance Status**, **Laboratory Thresholds**, and **Prior Therapies / Comorbidities**, providing match scoring, missing diagnostic alerts, and registry ranking.

```
                    +----------------------------------------------+
                    |          Patient Clinical Profile            |
                    |   (Genomics, Labs, ECOG, Staging, Meds)      |
                    +----------------------------------------------+
                                           |
                                           v
                    +----------------------------------------------+
                    |     Protocol Eligibility Screening Engine    |
                    |  - Inclusions vs Exclusions Evaluation       |
                    |  - Relational, Range & Set-Based Operators   |
                    |  - Missing Data Detection & Uncertainty      |
                    +----------------------------------------------+
                                           |
                                           v
                    +----------------------------------------------+
                    |            Trial Match Dossier               |
                    |  - Eligibility Status: ELIGIBLE / INELIGIBLE |
                    |  - Multi-Protocol Match Scoring & Ranking    |
                    |  - Actionable Confirmatory Testing Directives|
                    +----------------------------------------------+
```

---

## Eligibility Status Classification

- **`ELIGIBLE`**: All mandatory inclusion criteria satisfied and zero active exclusion conditions triggered.
- **`INELIGIBLE`**: Failure of mandatory inclusions (e.g., histology mismatch, ECOG > 1) or triggered exclusion criteria (e.g., active untreated CNS metastases).
- **`INCONCLUSIVE_MISSING_DATA`**: No hard failures observed, but essential diagnostic tests or biomarker profiles are missing/pending (e.g., NGS panel pending).

$$\text{Match Score (\%)} = \begin{cases} 0\% & \text{if hard exclusion triggered} \\ \frac{\sum_{i \in \text{Met Inclusions}} w_i}{\sum_{i \in \text{All Inclusions}} w_i} \times 100\% & \text{otherwise} \end{cases}$$

---

## Built-In Reference Trial Protocols

| Trial ID | Study Title | Indication | Phase | Key Eligibility Criteria |
| :--- | :--- | :--- | :---: | :--- |
| **NCT04245678** | Targeted 4th-Gen TKI Study | EGFR+ NSCLC | Phase III | Stage IV NSCLC, EGFR Ex19del/L858R, ECOG 0-1, ANC ≥ 1.5, CrCl ≥ 50, No active CNS mets |
| **NCT03829384** | Neoadjuvant Immunotherapy | TNBC Breast Cancer | Phase II | ER-/PR-/HER2- invasive breast cancer, ECOG 0-1, No prior anti-PD-1/PD-L1 |
| **NCT05112233** | SGLT2 Inhibitor in HFpEF | Heart Failure | Phase III | LVEF ≥ 50%, NT-proBNP ≥ 300 pg/mL, eGFR ≥ 25, No Type 1 Diabetes |

---

## Command-Line Interface (CLI)

### Demonstration Mode (EGFR+ NSCLC Patient)
```bash
python cli.py --demo
```

### JSON Output for EHR / CTMS Integration
```bash
python cli.py --demo --json
```

### Interactive Patient Assessment Prompt
```bash
python cli.py --interactive
```

### Target a Specific Trial Protocol
```bash
python cli.py --trial NCT04245678
```

### List Registered Trial Protocols
```bash
python cli.py --list-trials
```

### Screen Custom Patient JSON File
```bash
python cli.py --file patient_phenotype.json
```

---

## Python API Usage

```python
from clinical_trial_eligibility_matcher import (
    ClinicalTrialMatcherEngine,
    PatientClinicalProfile,
    STANDARD_TRIAL_REGISTRY,
    parse_patient_profile,
)

patient = PatientClinicalProfile(
    patient_id="PT-ONC-002",
    age=58,
    gender="female",
    diagnosis="NSCLC",
    stage="Stage IV",
    ecog_ps=1,
    biomarkers={"EGFR": "L858R"},
    labs={"ANC": 2.1, "Platelets": 180.0, "CrCl": 68.0},
    prior_therapies=["Carboplatin + Pemetrexed"],
    lines_of_prior_therapy=1,
)

# Screen against all registry trials
ranked_trials = ClinicalTrialMatcherEngine.match_patient_against_registry(patient)

for trial_res in ranked_trials:
    print(f"[{trial_res.eligibility_status.value}] {trial_res.trial_id}: {trial_res.overall_match_score_pct:.1f}%")
```

---

## Test Suite Execution

Run unit tests verifying operator evaluations, biomarker rules, lab thresholds, and edge cases:

```bash
python -m unittest discover -s tests -v
```

```
test_equals_operator ... ok
test_in_set_operator_list_in_patient ... ok
test_eligible_nsclc_patient ... ok
test_ineligible_due_to_cns_exclusion ... ok
test_inconclusive_missing_biomarker ... ok
test_eligible_tnbc_patient ... ok
test_eligible_hfpef ... ok
test_registry_ranking_order ... ok
----------------------------------------------------------------------
Ran 25 tests in 0.002s

OK
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
