"use client";

import { FormEvent, useEffect, useState } from "react";

type ScopeValue = {
  status: "included" | "partial" | "excluded" | "not_stated" | "unclear";
  evidence: string | null;
  source: "rule" | "ai" | "human";
  confidence: number;
  review_required: boolean;
  coat_count?: number | null;
  duration_years?: number | null;
  area_sq_ft?: number | null;
  material_type?: string | null;
  wear_layer_mil?: number | null;
  thickness_mm?: number | null;
  fixture_count?: number | null;
  fixture_types?: string[];
};

type Comparison = {
  vendors: Array<{
    vendor_name: string | null;
    estimate_total: string | null;
    total_cents: number | null;
  }>;
  price_difference_cents: number | null;
  lower_bidder: string | null;
  scope_comparison: Record<
    string,
    { label: string; first: ScopeValue; second: ScopeValue }
  >;
  risk_flags: Array<{
    code: string;
    severity: string;
    vendor_name: string | null;
    message: string;
    evidence: string | null;
  }>;
};

type EngineStatus = "checking" | "ai" | "rules" | "unavailable";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

const PAINTING_DEMOS = [
  {
    id: "blue-oak",
    name: "Blue Oak Painting Co.",
    path: "/samples/blue-oak.pdf",
    filename: "synthetic-painting-estimate-blue-oak.pdf",
  },
  {
    id: "inland-pro",
    name: "Inland Pro Paint & Repair",
    path: "/samples/inland-pro.pdf",
    filename: "synthetic-painting-estimate-inland-pro.pdf",
  },
  {
    id: "canyon-view",
    name: "Canyon View Coatings",
    path: "/samples/canyon-view.pdf",
    filename: "synthetic-painting-proposal-canyon-view.pdf",
  },
] as const;

const FLOORING_DEMOS = [
  {
    id: "pacific-floorworks",
    name: "Pacific Floorworks",
    path: "/samples/synthetic-flooring-estimate-pacific.pdf",
    filename: "synthetic-flooring-estimate-pacific.pdf",
  },
  {
    id: "valley-flooring",
    name: "Valley Flooring Group",
    path: "/samples/synthetic-flooring-estimate-valley.pdf",
    filename: "synthetic-flooring-estimate-valley.pdf",
  },
] as const;

const PLUMBING_DEMOS = [
  {
    id: "clearflow-plumbing",
    name: "ClearFlow Plumbing",
    path: "/samples/synthetic-plumbing-estimate-clearflow.pdf",
    filename: "synthetic-plumbing-estimate-clearflow.pdf",
  },
  {
    id: "rapid-rooter",
    name: "Rapid Rooter Services",
    path: "/samples/synthetic-plumbing-estimate-rapid.pdf",
    filename: "synthetic-plumbing-estimate-rapid.pdf",
  },
] as const;

const TRADE_OPTIONS = [
  {
    key: "painting",
    label: "Interior painting",
    description: "Coats, primer, repairs, ceilings, cleanup, and warranty",
    demos: PAINTING_DEMOS,
  },
  {
    key: "flooring",
    label: "Flooring",
    description: "Area, product specs, removal, subfloor, barriers, and trim",
    demos: FLOORING_DEMOS,
  },
  {
    key: "plumbing",
    label: "Plumbing",
    description: "Fixtures, supply and drain lines, valves, permits, and testing",
    demos: PLUMBING_DEMOS,
  },
] as const;

function formatCents(cents: number | null) {
  if (cents === null) return "Not available";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(cents / 100);
}

function displayStatus(status: ScopeValue["status"]) {
  return status.replace("_", " ");
}

export default function Home() {
  const [firstFile, setFirstFile] = useState<File | null>(null);
  const [secondFile, setSecondFile] = useState<File | null>(null);
  const [result, setResult] = useState<Comparison | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [engineStatus, setEngineStatus] = useState<EngineStatus>("checking");
  const [trade, setTrade] = useState<"painting" | "flooring" | "plumbing">("painting");
  const [firstDemo, setFirstDemo] = useState("blue-oak");
  const [secondDemo, setSecondDemo] = useState("inland-pro");
  const demos = TRADE_OPTIONS.find(({ key }) => key === trade)?.demos ?? PAINTING_DEMOS;
  const selectedTrade = TRADE_OPTIONS.find(({ key }) => key === trade);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${API_URL}/health`, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error("Health check failed");
        return response.json();
      })
      .then((health: { ai_enabled: boolean }) => {
        setEngineStatus(health.ai_enabled ? "ai" : "rules");
      })
      .catch((healthError) => {
        if (healthError instanceof Error && healthError.name !== "AbortError") {
          setEngineStatus("unavailable");
        }
      });
    return () => controller.abort();
  }, []);

  function changeTrade(nextTrade: "painting" | "flooring" | "plumbing") {
    const nextDemos = TRADE_OPTIONS.find(({ key }) => key === nextTrade)?.demos ?? PAINTING_DEMOS;
    setTrade(nextTrade);
    setFirstDemo(nextDemos[0].id);
    setSecondDemo(nextDemos[1].id);
    setFirstFile(null);
    setSecondFile(null);
    setResult(null);
    setError(null);
  }

  function resetComparison() {
    setFirstFile(null);
    setSecondFile(null);
    setResult(null);
    setError(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  useEffect(() => {
    if (result) {
      document
        .getElementById("comparison-results")
        ?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [result]);

  async function loadDemoEstimates() {
    setError(null);
    setResult(null);

    if (firstDemo === secondDemo) {
      setError("Choose two different demo estimates.");
      return;
    }

    const firstEstimate = demos.find(({ id }) => id === firstDemo);
    const secondEstimate = demos.find(({ id }) => id === secondDemo);
    if (!firstEstimate || !secondEstimate) {
      setError("The selected demo estimates could not be found.");
      return;
    }

    const [firstResponse, secondResponse] = await Promise.all([
      fetch(firstEstimate.path),
      fetch(secondEstimate.path),
    ]);

    if (!firstResponse.ok || !secondResponse.ok) {
      setError("The demo estimates could not be loaded.");
      return;
    }

    const [firstBlob, secondBlob] = await Promise.all([
      firstResponse.blob(),
      secondResponse.blob(),
    ]);

    setFirstFile(
      new File([firstBlob], firstEstimate.filename, {
        type: "application/pdf",
      }),
    );
    setSecondFile(
      new File([secondBlob], secondEstimate.filename, {
        type: "application/pdf",
      }),
    );
  }

  async function submitComparison(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!firstFile || !secondFile) {
      setError("Choose two PDF estimates before comparing.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("trade", trade);
    formData.append("first_estimate", firstFile);
    formData.append("second_estimate", secondFile);

    try {
      const response = await fetch(`${API_URL}/estimates/compare`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail ?? "The estimates could not be compared.");
      }
      setResult(data);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The API could not be reached.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <header className="site-header">
        <a className="brand" href="#top" aria-label="Vendor Quote Normalizer home">
          <span className="brand-mark">VQ</span>
          <span>Vendor Quote Normalizer</span>
        </a>
        <span className="prototype-label">Painting · Flooring · Plumbing</span>
      </header>

      <section className="hero" id="top">
        <h1>Compare contractor estimates</h1>
        <p>
          See price and scope differences side by side, with the original quote
          language available for every finding.
        </p>
      </section>

      <section className="workspace" aria-label="Estimate comparison workspace">
        <form onSubmit={submitComparison}>
          <div className={`engine-status ${engineStatus}`}>
            <span className="engine-dot" aria-hidden="true" />
            <div>
              <strong>
                {engineStatus === "ai" ? "AI-assisted evidence review" : "Evidence rules"}
              </strong>
              <span>
                {engineStatus === "checking" && "Checking analysis engine..."}
                {engineStatus === "ai" && "Ambiguous wording is reviewed by AI and verified against the PDF."}
                {engineStatus === "rules" && "AI is off. Comparisons still run with deterministic evidence rules."}
                {engineStatus === "unavailable" && "The analysis service is currently unreachable."}
              </span>
            </div>
          </div>
          <div className="trade-selector" role="group" aria-label="Estimate category">
            <span>Estimate category</span>
            {TRADE_OPTIONS.map((option) => (
              <button
                className={trade === option.key ? "active" : ""}
                key={option.key}
                type="button"
                onClick={() => changeTrade(option.key)}
              >
                {option.label}
              </button>
            ))}
          </div>
          <p className="trade-description">{selectedTrade?.description}</p>
          <div className="upload-grid">
            <FilePicker
              label="First estimate"
              file={firstFile}
              onChange={setFirstFile}
            />
            <FilePicker
              label="Second estimate"
              file={secondFile}
              onChange={setSecondFile}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="demo-library">
            <div className="demo-library-heading">
              <div>
                <strong>Demo library</strong>
                <span>Choose two sample bids to explore the comparison.</span>
              </div>
              <span className="sample-count">
                {TRADE_OPTIONS.find(({ key }) => key === trade)?.label} estimates
              </span>
            </div>
            <div className="demo-controls">
              <label>
                First demo
                <select
                  value={firstDemo}
                  onChange={(event) => setFirstDemo(event.target.value)}
                >
                  {demos.map((estimate) => (
                    <option value={estimate.id} key={estimate.id}>
                      {estimate.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Second demo
                <select
                  value={secondDemo}
                  onChange={(event) => setSecondDemo(event.target.value)}
                >
                  {demos.map((estimate) => (
                    <option value={estimate.id} key={estimate.id}>
                      {estimate.name}
                    </option>
                  ))}
                </select>
              </label>
              <button className="demo-button" type="button" onClick={loadDemoEstimates}>
                Use selected demos
              </button>
            </div>
          </div>

          <button className="compare-button" type="submit" disabled={loading}>
            {loading ? "Analyzing estimates..." : "Compare estimates"}
          </button>
          <p className="privacy-note">
            PDFs are processed temporarily and removed after analysis.
          </p>
        </form>
      </section>

      {result && <Results result={result} trade={trade} onReset={resetComparison} />}

      <footer className="site-footer">
        Vendor Quote Normalizer keeps missing scope marked as not stated.
      </footer>
    </main>
  );
}

function FilePicker({
  label,
  file,
  onChange,
}: {
  label: string;
  file: File | null;
  onChange: (file: File | null) => void;
}) {
  const inputId = `estimate-${label.toLowerCase().replaceAll(" ", "-")}`;

  return (
    <div className={`file-picker ${file ? "has-file" : ""}`}>
      <strong>{label}</strong>
      <span>
        {file
          ? `${file.name} · ${(file.size / 1024).toFixed(0)} KB`
          : "Choose a PDF estimate"}
      </span>
      <input
        id={inputId}
        className="native-file-input"
        type="file"
        accept="application/pdf,.pdf"
        onChange={(event) => onChange(event.target.files?.[0] ?? null)}
      />
    </div>
  );
}

function Results({
  result,
  trade,
  onReset,
}: {
  result: Comparison;
  trade: string;
  onReset: () => void;
}) {
  function downloadResult() {
    const report = {
      generated_at: new Date().toISOString(),
      trade,
      ...result,
    };
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(report, null, 2)], { type: "application/json" }),
    );
    const link = document.createElement("a");
    link.href = url;
    link.download = `${trade}-estimate-comparison.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="results" id="comparison-results" aria-live="polite">
      <div className="section-heading">
        <div>
          <span className="section-kicker">Comparison</span>
          <h2>Estimate review</h2>
        </div>
        <div className="difference-card">
          <span>Price difference</span>
          <strong>{formatCents(result.price_difference_cents)}</strong>
          <small>{result.lower_bidder} submitted the lower price</small>
        </div>
      </div>

      <div className="report-actions" aria-label="Report actions">
        <button type="button" onClick={() => window.print()}>Print / save PDF</button>
        <button type="button" onClick={downloadResult}>Download data</button>
        <button className="reset-button" type="button" onClick={onReset}>New comparison</button>
      </div>

      <div className="vendor-grid">
        {result.vendors.map((vendor, index) => (
          <article className="vendor-card" key={`${vendor.vendor_name}-${index}`}>
            <span>Estimate {index + 1}</span>
            <h3>{vendor.vendor_name ?? "Unknown vendor"}</h3>
            <strong>{vendor.estimate_total ?? "Total not found"}</strong>
          </article>
        ))}
      </div>

      <div className="results-panel">
        <h3>Scope comparison</h3>
        <div className="scope-table">
          <div className="scope-row scope-header">
            <span>Scope item</span>
            <span>{result.vendors[0]?.vendor_name}</span>
            <span>{result.vendors[1]?.vendor_name}</span>
          </div>
          {Object.entries(result.scope_comparison).map(([key, row]) => (
            <div className="scope-row" key={key}>
              <strong>{row.label}</strong>
              <ScopeCell value={row.first} />
              <ScopeCell value={row.second} />
            </div>
          ))}
        </div>
      </div>

      <div className="results-panel">
        <h3>Items to clarify</h3>
        <div className="risk-list">
          {result.risk_flags.length === 0 && (
            <p className="empty-risks">
              No material scope differences were found. Review the evidence before making a final decision.
            </p>
          )}
          {result.risk_flags.map((flag) => (
            <article className="risk-card" key={flag.code}>
              <div>
                <span className={`severity ${flag.severity}`}>{flag.severity}</span>
                <strong>{flag.vendor_name}</strong>
              </div>
              <p>{flag.message}</p>
              {flag.evidence && <blockquote>“{flag.evidence}”</blockquote>}
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function ScopeCell({ value }: { value: ScopeValue }) {
  return (
    <div className="scope-cell">
      <span className={`status ${value.status}`}>{displayStatus(value.status)}</span>
      <span className={`extraction-meta ${value.review_required ? "review" : ""}`}>
        {value.review_required
          ? `Needs review · ${Math.round(value.confidence * 100)}% rule confidence`
          : `${Math.round(value.confidence * 100)}% confidence · ${value.source} extracted`}
      </span>
      {value.coat_count !== undefined && value.coat_count !== null && (
        <small>{value.coat_count} coat{value.coat_count === 1 ? "" : "s"}</small>
      )}
      {value.duration_years !== undefined && value.duration_years !== null && (
        <small>{value.duration_years}-year term</small>
      )}
      {value.area_sq_ft !== undefined && value.area_sq_ft !== null && (
        <small>{value.area_sq_ft.toLocaleString()} sq ft</small>
      )}
      {value.material_type && <small>{value.material_type}</small>}
      {value.wear_layer_mil !== undefined && value.wear_layer_mil !== null && (
        <small>{value.wear_layer_mil} mil wear layer</small>
      )}
      {value.thickness_mm !== undefined && value.thickness_mm !== null && (
        <small>{value.thickness_mm} mm thickness</small>
      )}
      {value.fixture_count !== undefined && value.fixture_count !== null && (
        <small>{value.fixture_count} fixtures</small>
      )}
      {value.evidence && <details><summary>View evidence</summary><p>{value.evidence}</p></details>}
    </div>
  );
}
