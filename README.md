# Clinical Trial Eligibility Matcher

A deterministic Python rule engine for evaluating structured patient data against bundled inclusion and exclusion criteria.

> **Important:** The bundled protocols are illustrative software examples. They are not synchronized with ClinicalTrials.gov and must not be used as authoritative trial eligibility criteria. Any real screening decision requires review of the current study protocol by qualified trial staff.

## What it does

- Evaluates structured inclusion and exclusion criteria.
- Distinguishes **eligible**, **ineligible**, and **inconclusive due to missing data** states.
- Reports criterion-level pass, fail, and missing-data results.
- Supports JSON patient profiles, interactive CLI use, and CSV batch screening.
- Provides a browser interface that runs the Python matcher locally with Pyodide.
- Keeps missing clinical fields unknown instead of substituting clinically meaningful defaults.

## Browser interface

The repository includes a static GitHub Pages interface in `index.html`.

The browser app loads Pyodide and the repository's Python matcher, then performs analysis locally in the browser. Patient values entered into the form are not submitted to a server by this application. Loading the Python runtime requires network access to the pinned Pyodide CDN.

## CLI

Install for development:

```bash
python -m pip install -e ".[dev]"
```

List the bundled protocols:

```bash
clinical-trial-eligibility-matcher --list-trials
```

Run the built-in sample:

```bash
clinical-trial-eligibility-matcher --demo
```

Screen a JSON patient profile:

```bash
clinical-trial-eligibility-matcher --file patient.json --json
```

Batch-screen a CSV file:

```bash
clinical-trial-eligibility-matcher batch -i sample.csv -o results.csv
```

Filter to one bundled protocol:

```bash
clinical-trial-eligibility-matcher batch -i sample.csv -o results.csv --trial NCT04245678
```

## Input conventions

Patient profiles can contain demographics, diagnosis/stage, ECOG performance status, biomarkers, laboratory values, prior therapies, therapy-line count, and comorbidities.

For CSV input:

- `biomarkers` and `labs` are JSON objects.
- `prior_therapies` is semicolon-separated.
- `comorbidities` is comma-separated.
- Blank clinical fields remain missing and can produce an inconclusive result.
- Invalid JSON or non-numeric numeric fields fail with an explicit validation error.

See `sample.csv` for a complete example.

## Development and testing

The project has no runtime Python dependencies outside the standard library.

Run the test suite:

```bash
python -m pytest -p no:zarr -q
```

Compile-check the Python sources:

```bash
python -m compileall -q cli.py clinical_trial_eligibility_matcher tests
```

The GitHub Actions CI matrix tests Python 3.9 through 3.12, installs the package, verifies the console entry point, and runs a batch smoke test.

## Technology

- Python standard library
- `dataclasses`-based domain models
- Pytest for regression tests
- Static HTML/CSS/JavaScript browser UI
- Pyodide for running the Python matcher in-browser
- GitHub Actions for CI and GitHub Pages deployment

## Browser compatibility

The web interface requires a modern browser with WebAssembly support and JavaScript enabled. Initial page use downloads the Pyodide runtime; subsequent matcher execution occurs locally.

## Privacy

The CLI reads local files only. The browser interface does not transmit patient form data to the repository or a project backend. Do not use real identifiable patient information unless your local workflow and applicable governance requirements permit it.

## License

MIT License. See [LICENSE](LICENSE).
