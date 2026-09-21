const byId = (id) => document.getElementById(id);

const form = byId("patient-form");
const resultsRoot = byId("results");
const resultSummary = byId("result-summary");
const runtimeStatus = byId("runtime-status");
const analyzeButton = byId("analyze-button");
const themeToggle = byId("theme-toggle");
const sampleButton = byId("sample-button");
const resultsPanel = document.querySelector(".results-panel");

let pyodide = null;
let runtimeReady = false;

const PYODIDE_BASE = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/";
const PYTHON_FILES = [
  "clinical_trial_eligibility_matcher/__init__.py",
  "clinical_trial_eligibility_matcher/models.py",
  "clinical_trial_eligibility_matcher/engine.py",
];

const samplePatient = {
  patient_id: "PT-001",
  age: 62,
  gender: "female",
  diagnosis: "NSCLC",
  stage: "Stage IV",
  ecog_ps: 1,
  biomarkers: { EGFR: "L858R", "PD-L1": 45 },
  labs: { ANC: 2.4, Platelets: 195, CrCl: 72 },
  prior_therapies: ["Carboplatin + Pemetrexed"],
  lines_of_prior_therapy: 1,
  comorbidities: ["Hypertension (Controlled)"],
};

function setRuntimeStatus(message, state = "") {
  runtimeStatus.textContent = message;
  runtimeStatus.className = "runtime-status";
  if (state) runtimeStatus.classList.add(state);
}

async function initializeRuntime() {
  try {
    if (typeof loadPyodide !== "function") {
      throw new Error("Pyodide loader is unavailable.");
    }

    analyzeButton.disabled = true;
    setRuntimeStatus("Loading Python runtime…");

    pyodide = await loadPyodide({ indexURL: PYODIDE_BASE });
    pyodide.FS.mkdirTree("/app/clinical_trial_eligibility_matcher");

    for (const path of PYTHON_FILES) {
      const response = await fetch("./" + path, { cache: "no-store" });
      if (!response.ok) {
        throw new Error("Could not load " + path + " (" + response.status + ").");
      }
      const source = await response.text();
      pyodide.FS.writeFile("/app/" + path, source);
    }

    const bootstrap = [
      "import sys",
      "if '/app' not in sys.path:",
      "    sys.path.insert(0, '/app')",
      "from clinical_trial_eligibility_matcher import (",
      "    ClinicalTrialMatcherEngine,",
      "    STANDARD_TRIAL_REGISTRY,",
      "    parse_patient_profile,",
      ")",
    ].join("\n");
    await pyodide.runPythonAsync(bootstrap);

    runtimeReady = true;
    analyzeButton.disabled = false;
    setRuntimeStatus(
      "Python runtime ready. Analysis runs locally in this browser.",
      "ready",
    );
  } catch (error) {
    console.error(error);
    runtimeReady = false;
    analyzeButton.disabled = true;
    setRuntimeStatus(
      "Python runtime failed to load. Check the network connection and reload the page.",
      "error",
    );
  }
}

function optionalNumber(id) {
  const raw = byId(id).value.trim();
  if (raw === "") return null;
  const value = Number(raw);
  if (!Number.isFinite(value)) {
    throw new Error(id.replaceAll("_", " ") + " must be numeric.");
  }
  return value;
}

function optionalText(id) {
  const value = byId(id).value.trim();
  return value === "" ? null : value;
}

function parseObjectField(id, label) {
  const raw = byId(id).value.trim();
  if (!raw) return {};
  let value;
  try {
    value = JSON.parse(raw);
  } catch {
    throw new Error(label + " must be valid JSON.");
  }
  if (!value || Array.isArray(value) || typeof value !== "object") {
    throw new Error(label + " must be a JSON object.");
  }
  return value;
}

function parseDelimitedList(id, delimiter) {
  const raw = byId(id).value.trim();
  if (!raw) return null;
  if (["none", "no", "n/a", "na"].includes(raw.toLowerCase())) return [];
  return raw
    .split(delimiter)
    .map((item) => item.trim())
    .filter(Boolean);
}

function collectPatient() {
  return {
    patient_id: optionalText("patient_id") || "PT-UNKNOWN",
    age: optionalNumber("age"),
    gender: optionalText("gender"),
    diagnosis: optionalText("diagnosis"),
    stage: optionalText("stage"),
    ecog_ps: optionalNumber("ecog_ps"),
    biomarkers: parseObjectField("biomarkers", "Biomarkers"),
    labs: parseObjectField("labs", "Labs"),
    prior_therapies: parseDelimitedList("prior_therapies", ";"),
    lines_of_prior_therapy: optionalNumber("lines_of_prior_therapy"),
    comorbidities: parseDelimitedList("comorbidities", ","),
  };
}

async function analyzePatient(patient, trialId) {
  pyodide.globals.set("patient_json_js", JSON.stringify(patient));
  pyodide.globals.set("trial_id_js", trialId || "");

  const program = [
    "import json",
    "payload = json.loads(str(patient_json_js))",
    "patient = parse_patient_profile(payload)",
    "selected_trial_id = str(trial_id_js)",
    "if selected_trial_id:",
    "    registry = [trial for trial in STANDARD_TRIAL_REGISTRY if trial.trial_id == selected_trial_id]",
    "    results = ClinicalTrialMatcherEngine.match_patient_against_registry(patient, registry=registry)",
    "else:",
    "    results = ClinicalTrialMatcherEngine.match_patient_against_registry(patient)",
    "json.dumps([result.to_dict() for result in results])",
  ].join("\n");

  try {
    const raw = await pyodide.runPythonAsync(program);
    return JSON.parse(raw);
  } finally {
    pyodide.globals.delete("patient_json_js");
    pyodide.globals.delete("trial_id_js");
  }
}

function makeElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined && text !== null) element.textContent = String(text);
  return element;
}

function statusClass(status) {
  if (status === "ELIGIBLE") return "eligible";
  if (status === "INELIGIBLE") return "ineligible";
  return "inconclusive";
}

function renderCriterion(item) {
  const row = makeElement("div", "criterion");
  const outcome = item.missing ? "MISSING" : item.passed ? "PASS" : "FAIL";
  const heading = makeElement(
    "strong",
    "",
    outcome + " · " + item.type + " · " + item.description,
  );
  const values = makeElement(
    "small",
    "",
    "Observed: " +
      (item.observed ?? "unknown") +
      " · Expected: " +
      JSON.stringify(item.expected),
  );

  row.append(heading, values);
  if (item.message) row.append(makeElement("small", "", item.message));
  return row;
}

function renderResult(result) {
  const card = makeElement("article", "result-card");
  const topLine = makeElement("div", "result-topline");
  const titleWrap = makeElement("div");
  const title = makeElement(
    "div",
    "result-title",
    result.trial_id + " · " + result.trial_title,
  );
  const meta = makeElement(
    "div",
    "result-meta",
    result.phase + " · " + result.indication,
  );
  titleWrap.append(title, meta);

  const badge = makeElement(
    "span",
    "status " + statusClass(result.eligibility_status),
    result.eligibility_status.replaceAll("_", " "),
  );
  topLine.append(titleWrap, badge);

  const metrics = makeElement("div", "metrics");
  const metricData = [
    [result.overall_match_score_pct.toFixed(1) + "%", "Encoded match score"],
    [
      result.counts.inclusions_met + "/" + result.counts.inclusions_total,
      "Inclusions met",
    ],
    [
      result.counts.exclusions_avoided + "/" + result.counts.exclusions_total,
      "Exclusions avoided",
    ],
    [result.counts.missing_critical_data, "Missing criteria"],
  ];
  for (const [value, label] of metricData) {
    const metric = makeElement("div", "metric");
    metric.append(makeElement("b", "", value), makeElement("span", "", label));
    metrics.append(metric);
  }

  const nextStepText = (result.actionable_next_steps || []).join(" ");
  const nextStep = makeElement(
    "div",
    "next-step",
    nextStepText || "No next-step message was generated.",
  );

  const details = document.createElement("details");
  const summary = makeElement(
    "summary",
    "",
    "Criterion details (" + result.evaluations.length + ")",
  );
  const list = makeElement("div", "criteria-list");
  result.evaluations.forEach((item) => list.append(renderCriterion(item)));
  details.append(summary, list);

  card.append(topLine, metrics, nextStep, details);
  return card;
}

function renderResults(results) {
  resultsRoot.replaceChildren();
  resultsRoot.className = "";

  if (!results.length) {
    resultsRoot.className = "results-empty";
    resultsRoot.append(
      makeElement("p", "", "No matching bundled protocol was found."),
    );
    resultSummary.textContent = "No result returned.";
    return;
  }

  results.forEach((result) => resultsRoot.append(renderResult(result)));
  const top = results[0];
  resultSummary.textContent =
    "Top result: " +
    top.trial_id +
    " — " +
    top.eligibility_status.replaceAll("_", " ").toLowerCase() +
    ".";
}

function showError(message) {
  resultsRoot.replaceChildren();
  resultsRoot.className = "results-empty";
  const error = makeElement("p", "", message);
  error.setAttribute("role", "alert");
  resultsRoot.append(error);
  resultSummary.textContent = "Analysis could not be completed.";
}

function loadSample() {
  byId("patient_id").value = samplePatient.patient_id;
  byId("age").value = samplePatient.age;
  byId("gender").value = samplePatient.gender;
  byId("diagnosis").value = samplePatient.diagnosis;
  byId("stage").value = samplePatient.stage;
  byId("ecog_ps").value = samplePatient.ecog_ps;
  byId("biomarkers").value = JSON.stringify(samplePatient.biomarkers);
  byId("labs").value = JSON.stringify(samplePatient.labs);
  byId("prior_therapies").value = samplePatient.prior_therapies.join("; ");
  byId("lines_of_prior_therapy").value = samplePatient.lines_of_prior_therapy;
  byId("comorbidities").value = samplePatient.comorbidities.join(", ");
}

function applyTheme(theme) {
  const resolved = theme === "dark" ? "dark" : "light";
  document.documentElement.dataset.theme = resolved;
  themeToggle.textContent = resolved === "dark" ? "Light" : "Dark";
  themeToggle.setAttribute(
    "aria-label",
    resolved === "dark" ? "Switch to light mode" : "Switch to dark mode",
  );
}

themeToggle.addEventListener("click", () => {
  const next =
    document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  localStorage.setItem("theme", next);
  applyTheme(next);
});

sampleButton.addEventListener("click", loadSample);

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!runtimeReady) {
    showError("The Python runtime is not ready.");
    return;
  }

  analyzeButton.disabled = true;
  resultsPanel.setAttribute("aria-busy", "true");
  resultSummary.textContent = "Analyzing encoded criteria…";

  try {
    const patient = collectPatient();
    const trialId = byId("trial-filter").value;
    const results = await analyzePatient(patient, trialId);
    renderResults(results);
  } catch (error) {
    console.error(error);
    showError(error instanceof Error ? error.message : String(error));
  } finally {
    analyzeButton.disabled = false;
    resultsPanel.setAttribute("aria-busy", "false");
  }
});

applyTheme(localStorage.getItem("theme") || "light");
loadSample();
initializeRuntime();
