# Clinical Trial Eligibility Matcher & Protocol Screener

> **Domain:** Clinical Research Informatics & Protocol Feasibility  
> **Reference Guidelines & Standards:** CDISC SDTM/CDASH, NCI Thesaurus, ClinicalTrials.gov Protocol Registration System (PRS), Good Clinical Practice (ICH-GCP E6(R2))

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![Pytest Suite](https://img.shields.io/badge/Pytest-Passing-brightgreen.svg?logo=pytest&logoColor=white)
![Standards](https://img.shields.io/badge/Standards-CDISC%20%7C%20NCI%20Thesaurus-blueviolet.svg)

</div>

---

## 📖 Overview & Clinical Architecture

**Clinical Trial Eligibility Matcher** evaluates complex multi-dimensional patient phenotypes against structured clinical trial protocols. It models inclusion and exclusion (I/E) criteria across demographics, histopathology, molecular genomics/biomarkers, functional performance status, laboratory safety thresholds, prior therapeutic regimens, and medical comorbidities.

The engine executes deterministic multi-attribute rule checking, computes weighted eligibility scores, flags missing clinical attributes with confirmatory test recommendations, and triages eligible trial opportunities.

```
+-----------------------------------------------------------------------------+
|                          PATIENT CLINICAL PHENOTYPE                         |
|  - Demographics (Age, Gender)           - Genomics (EGFR, ER, PR, HER2)     |
|  - Staging & Histology (Stage IV NSCLC) - Labs (ANC, Platelets, CrCl, BNP)  |
|  - Performance Status (ECOG 0-4)        - Prior Regimens & Comorbidities    |
+-------------------------------------+---------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
|                    ELIGIBILITY EVALUATION PIPELINE                          |
|                                                                             |
|  1. INCLUSION CRITERIA CHECK            2. EXCLUSION CRITERIA CHECK         |
|     * All mandatory criteria met?          * Active contraindication?       |
|     * Operator check (==, >=, <=, IN)      * Hard-stop exclusionary flag?   |
|                                                                             |
|  3. MISSING DATA AUDIT                  4. WEIGHTED MATCH SCORING           |
|     * Missing required labs/genomics?      * S = (Earned Wt / Total Wt)     |
|     * Inconclusive state classification    * Ranking: ELIGIBLE > INCONCLUSIVE|
+-------------------------------------+---------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
|                     CLINICAL DECISION OUTPUT & TRIAGE                       |
|  - Status: [ELIGIBLE] | [INCONCLUSIVE_MISSING_DATA] | [INELIGIBLE]          |
|  - Match Score (%): 0.0% to 100.0%                                          |
|  - Actionable Next Steps: Pre-screening consent vs. confirmatory diagnostic  |
+-----------------------------------------------------------------------------+
```

---

## 🔬 Mathematical Formulations & Criteria Logic

### 1. Weighted Eligibility Score ($S_{match}$)

For protocol $T$ with criteria set $C = \{c_1, c_2, \dots, c_n\}$ each assigned weight $w_i \ge 0$:

$$S_{match} = \begin{cases} 0.0\% & \text{if any exclusion criterion is triggered} \\ \left( \frac{\sum_{i \in \text{Satisfied}} w_i}{\sum_{i=1}^n w_i} \right) \times 100 & \text{otherwise} \end{cases}$$

### 2. Tri-State Eligibility Decision Hierarchy

$$\text{Status}(P, T) = \begin{cases} 
\text{INELIGIBLE} & \text{if } \exists c \in C_{exc} \text{ where } c(P) = \text{True, or } \exists c \in C_{inc}^{mand} \text{ where } c(P) = \text{False} \\
\text{INCONCLUSIVE} & \text{if no exclusions triggered, no mandatory failed, but } \exists c \text{ where } \text{Data}(P, c) = \text{Missing} \\
\text{ELIGIBLE} & \text{if } \forall c \in C_{inc}: c(P) = \text{True} \land \forall c \in C_{exc}: c(P) = \text{False}
\end{cases}$$

---

## 📋 Active Protocol Registry Specification

The system includes pre-configured standard trial protocols representing major therapeutic areas:

| Trial ID | Phase | Indication | Key Inclusion Criteria | Critical Exclusion Criteria |
|:---------|:------|:-----------|:-----------------------|:----------------------------|
| `NCT04245678` | Phase III | EGFR+ Advanced NSCLC | Age $\ge 18$, Stage IV NSCLC, activating EGFR (Ex19del/L858R), ECOG $\le 1$, ANC $\ge 1.5$, Platelets $\ge 100$, CrCl $\ge 50$ | Active CNS metastases, prior lines of therapy $> 2$ |
| `NCT03829384` | Phase II | Triple-Negative Breast Cancer (TNBC) | Age $\ge 18$, Invasive Breast Carcinoma, ER(-), PR(-), HER2(-), ECOG $\le 1$ | Active autoimmune disease requiring steroids, prior anti-PD-(L)1 therapy |
| `NCT05112233` | Phase III | HFpEF (Heart Failure) | Age $\ge 40$, Heart Failure, LVEF $\ge 50\%$, NT-proBNP $\ge 300$ pg/mL, eGFR $\ge 25$ mL/min/1.73m² | Type 1 Diabetes, severe ESRD on dialysis |

---

## 💻 CLI Quickstart & Usage

### 1. Batch Cohort Screening (Recommended)
Screen an entire patient cohort CSV against registered clinical trials:
```bash
python cli.py batch -i sample.csv -o batch_results.csv
```
Or filter the batch evaluation to a single trial identifier:
```bash
python cli.py batch -i sample.csv -o batch_results.csv --trial NCT04245678
```

### 2. Built-in Demonstration Mode
Execute screening for a sample Stage IV EGFR-mutant NSCLC patient against the registry:
```bash
python cli.py --demo
```

### 3. Screen from Patient JSON File
```bash
python cli.py --file patient_profile.json
```
Export structured JSON results for EHR/EDC integration:
```bash
python cli.py --file patient_profile.json --json
```

### 4. Interactive Clinical Screening Prompt
Launch an interactive questionnaire to evaluate a patient in real time:
```bash
python cli.py --interactive
```

### 5. List Registered Trial Protocols
```bash
python cli.py --list-trials
```

---

## 📊 Patient Data Schema (`sample.csv`)

| Field | Type | Description / Accepted Format | Example |
|:------|:-----|:------------------------------|:--------|
| `patient_id` | String | Unique synthetic patient identifier | `PT-001` |
| `age` | Integer | Patient age in years | `62` |
| `gender` | String | Patient sex (`male`, `female`, `other`) | `female` |
| `diagnosis` | String | Primary diagnostic indication | `NSCLC`, `Breast Cancer`, `Heart Failure` |
| `stage` | String | Disease staging classification | `Stage IV`, `Stage II` |
| `histology` | String | Microscopic histology subtype | `Adenocarcinoma`, `Invasive Ductal` |
| `ecog_ps` | Integer | ECOG Performance Status score (0 to 4) | `0` (Fully active), `1` (Restricted) |
| `biomarkers` | JSON Dict | Genomic mutations, IHC receptor status, functional indices | `{"EGFR": "L858R", "PD-L1": 45.0}` |
| `labs` | JSON Dict | Serum laboratory chemistry and hematology | `{"ANC": 2.4, "Platelets": 195.0, "CrCl": 72.0}` |
| `prior_therapies` | String | Semicolon-delimited prior systemic regimens | `Carboplatin + Pemetrexed; Osimertinib` |
| `lines_of_prior_therapy` | Integer | Total completed systemic therapy lines | `1` |
| `comorbidities` | String | Comorbid diagnoses | `Hypertension (Controlled), Active CNS Metastases` |

---

## 🧪 Testing & Verification

Run the full pytest suite:
```bash
python -m pytest -p no:zarr -v
```

Execute the batch smoke verification:
```bash
python cli.py batch -i sample.csv -o out_smoke.csv
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

