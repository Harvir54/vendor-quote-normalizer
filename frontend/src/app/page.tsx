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
    unit_price_cents: number | null;
    unit_label: string | null;
    bid_details: {
      proposal_number: string | null;
      issued_date: string | null;
      valid_until: string | null;
      contractor_license: string | null;
      project_schedule: string | null;
      payment_terms: string | null;
      exclusions: string | null;
    };
  }>;
  price_range_cents: number | null;
  lowest_bidder: string | null;
  scope_comparison: Record<
    string,
    { label: string; values: ScopeValue[] }
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
  const [files, setFiles] = useState<Array<File | null>>([null, null]);
  const [result, setResult] = useState<Comparison | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [engineStatus, setEngineStatus] = useState<EngineStatus>("checking");
  const [trade, setTrade] = useState<"painting" | "flooring" | "plumbing">("painting");
  const [selectedDemos, setSelectedDemos] = useState<string[]>([
    "blue-oak",
    "inland-pro",
    "canyon-view",
  ]);
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
    setSelectedDemos(nextDemos.slice(0, 3).map(({ id }) => id));
    setFiles([null, null]);
    setResult(null);
    setError(null);
  }

  function resetComparison() {
    setFiles([null, null]);
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

    if (selectedDemos.length < 2) {
      setError("Choose at least two demo estimates.");
      return;
    }

    const selectedEstimates = selectedDemos.map((demoId) =>
      demos.find(({ id }) => id === demoId),
    );
    if (selectedEstimates.some((estimate) => !estimate)) {
      setError("The selected demo estimates could not be found.");
      return;
    }

    const responses = await Promise.all(
      selectedEstimates.map((estimate) => fetch(estimate!.path)),
    );

    if (responses.some((response) => !response.ok)) {
      setError("The demo estimates could not be loaded.");
      return;
    }

    const blobs = await Promise.all(responses.map((response) => response.blob()));
    setFiles(
      blobs.map(
        (blob, index) =>
          new File([blob], selectedEstimates[index]!.filename, {
            type: "application/pdf",
          }),
      ),
    );
  }

  function updateFile(index: number, file: File | null) {
    setFiles((current) => current.map((value, itemIndex) =>
      itemIndex === index ? file : value,
    ));
  }

  function toggleDemo(demoId: string) {
    setSelectedDemos((current) =>
      current.includes(demoId)
        ? current.filter((id) => id !== demoId)
        : current.length < 5
          ? [...current, demoId]
          : current,
    );
  }

  async function submitComparison(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const selectedFiles = files.filter((file): file is File => file !== null);
    if (selectedFiles.length < 2 || selectedFiles.length !== files.length) {
      setError("Choose a PDF for every estimate before comparing.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("trade", trade);
    selectedFiles.forEach((file) => formData.append("estimates", file));

    try {
      const response = await fetch(`${API_URL}/estimates/compare-many`, {
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
          <div className="upload-heading">
            <div>
              <strong>Estimates</strong>
              <span>Upload between 2 and 5 vendor quotes.</span>
            </div>
            {files.length < 5 && (
              <button
                type="button"
                onClick={() => setFiles((current) => [...current, null])}
              >
                Add estimate
              </button>
            )}
          </div>
          <div className="upload-grid">
            {files.map((file, index) => (
              <FilePicker
                key={index}
                label={`Estimate ${index + 1}`}
                file={file}
                onChange={(nextFile) => updateFile(index, nextFile)}
                onRemove={files.length > 2
                  ? () => setFiles((current) => current.filter((_, itemIndex) => itemIndex !== index))
                  : undefined}
              />
            ))}
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="demo-library">
            <div className="demo-library-heading">
              <div>
                <strong>Demo library</strong>
                <span>Choose 2–5 sample bids to explore the comparison.</span>
              </div>
              <span className="sample-count">
                {TRADE_OPTIONS.find(({ key }) => key === trade)?.label} estimates
              </span>
            </div>
            <div className="demo-controls">
              <div className="demo-options">
                {demos.map((estimate) => (
                  <label key={estimate.id}>
                    <input
                      type="checkbox"
                      checked={selectedDemos.includes(estimate.id)}
                      onChange={() => toggleDemo(estimate.id)}
                    />
                    <span>{estimate.name}</span>
                  </label>
                ))}
              </div>
              <button className="demo-button" type="button" onClick={loadDemoEstimates}>
                Load selected demos
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
  onRemove,
}: {
  label: string;
  file: File | null;
  onChange: (file: File | null) => void;
  onRemove?: () => void;
}) {
  const inputId = `estimate-${label.toLowerCase().replaceAll(" ", "-")}`;

  return (
    <div className={`file-picker ${file ? "has-file" : ""}`}>
      <div className="file-picker-heading">
        <strong>{label}</strong>
        {onRemove && <button type="button" onClick={onRemove}>Remove</button>}
      </div>
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
          <span>Price range</span>
          <strong>{formatCents(result.price_range_cents)}</strong>
          <small>
            {result.lowest_bidder
              ? `${result.lowest_bidder} submitted the lowest price`
              : "No single lowest bidder was identified"}
          </small>
        </div>
      </div>

      <div className="report-actions" aria-label="Report actions">
        <button type="button" onClick={() => window.print()}>Print / save PDF</button>
        <button type="button" onClick={downloadResult}>Download data</button>
        <button className="reset-button" type="button" onClick={onReset}>New comparison</button>
      </div>

      <div
        className="vendor-grid"
        style={{ gridTemplateColumns: `repeat(${result.vendors.length}, minmax(190px, 1fr))` }}
      >
        {result.vendors.map((vendor, index) => (
          <article className="vendor-card" key={`${vendor.vendor_name}-${index}`}>
            <span>Estimate {index + 1}</span>
            <h3>{vendor.vendor_name ?? "Unknown vendor"}</h3>
            <strong>{vendor.estimate_total ?? "Total not found"}</strong>
            {vendor.unit_price_cents !== null && vendor.unit_label && (
              <small className="unit-price">
                {formatCents(vendor.unit_price_cents)} {vendor.unit_label}
              </small>
            )}
            <BidDetails details={vendor.bid_details} />
          </article>
        ))}
      </div>

      <div className="results-panel">
        <h3>Scope comparison</h3>
        <div className="scope-table">
          <div
            className="scope-row scope-header"
            style={{ gridTemplateColumns: `minmax(150px, .72fr) repeat(${result.vendors.length}, minmax(190px, 1fr))` }}
          >
            <span>Scope item</span>
            {result.vendors.map((vendor, index) => (
              <span key={`${vendor.vendor_name}-${index}`}>{vendor.vendor_name}</span>
            ))}
          </div>
          {Object.entries(result.scope_comparison).map(([key, row]) => (
            <div
              className="scope-row"
              key={key}
              style={{ gridTemplateColumns: `minmax(150px, .72fr) repeat(${result.vendors.length}, minmax(190px, 1fr))` }}
            >
              <strong>{row.label}</strong>
              {row.values.map((value, index) => (
                <ScopeCell value={value} key={index} />
              ))}
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
          {result.risk_flags.map((flag, index) => (
            <article className="risk-card" key={`${flag.code}-${flag.vendor_name}-${index}`}>
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

function BidDetails({
  details,
}: {
  details: Comparison["vendors"][number]["bid_details"];
}) {
  const rows = [
    ["Proposal", details.proposal_number],
    ["Issued", details.issued_date],
    ["Valid through", details.valid_until],
    ["License", details.contractor_license],
    ["Schedule", details.project_schedule],
    ["Payment", details.payment_terms],
    ["Exclusions", details.exclusions],
  ].filter((row): row is [string, string] => row[1] !== null);

  return (
    <details className="bid-details">
      <summary>Bid details</summary>
      {rows.length === 0 ? (
        <p>No additional contract details were found.</p>
      ) : (
        <dl>
          {rows.map(([label, value]) => (
            <div key={label}>
              <dt>{label}</dt>
              <dd>{value}</dd>
            </div>
          ))}
        </dl>
      )}
    </details>
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
