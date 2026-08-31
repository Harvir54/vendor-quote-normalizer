"use client";

import { FormEvent, useState } from "react";

type ScopeValue = {
  status: "included" | "excluded" | "not_stated" | "unclear";
  evidence: string | null;
  coat_count?: number | null;
  duration_years?: number | null;
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

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

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
        <span className="prototype-badge">Private prototype</span>
      </header>

      <section className="hero" id="top">
        <div className="eyebrow">Estimate intelligence for property teams</div>
        <h1>Compare the scope, not just the price.</h1>
        <p>
          Upload two contractor estimates. We normalize the details, expose missing
          scope, and show the document evidence behind every warning.
        </p>
      </section>

      <section className="workspace" aria-label="Estimate comparison workspace">
        <form onSubmit={submitComparison}>
          <div className="upload-grid">
            <FilePicker
              number="01"
              label="First estimate"
              file={firstFile}
              onChange={setFirstFile}
            />
            <FilePicker
              number="02"
              label="Second estimate"
              file={secondFile}
              onChange={setSecondFile}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button className="compare-button" type="submit" disabled={loading}>
            {loading ? "Analyzing estimates..." : "Compare estimates"}
            <span aria-hidden="true">→</span>
          </button>
          <p className="privacy-note">
            PDFs are processed temporarily and removed after analysis.
          </p>
        </form>
      </section>

      {result && <Results result={result} />}

      <section className="principles">
        <article>
          <span>01</span>
          <h2>Evidence first</h2>
          <p>Every material classification retains the source language.</p>
        </article>
        <article>
          <span>02</span>
          <h2>No silent assumptions</h2>
          <p>Missing scope stays “not stated” instead of being guessed.</p>
        </article>
        <article>
          <span>03</span>
          <h2>Built for decisions</h2>
          <p>Differences become questions to resolve before approving work.</p>
        </article>
      </section>
    </main>
  );
}

function FilePicker({
  number,
  label,
  file,
  onChange,
}: {
  number: string;
  label: string;
  file: File | null;
  onChange: (file: File | null) => void;
}) {
  return (
    <label className={`file-picker ${file ? "has-file" : ""}`}>
      <span className="file-number">{number}</span>
      <span className="upload-icon" aria-hidden="true">↑</span>
      <strong>{file ? file.name : label}</strong>
      <span>{file ? `${(file.size / 1024).toFixed(0)} KB` : "Choose a PDF estimate"}</span>
      <input
        type="file"
        accept="application/pdf,.pdf"
        onChange={(event) => onChange(event.target.files?.[0] ?? null)}
      />
    </label>
  );
}

function Results({ result }: { result: Comparison }) {
  return (
    <section className="results" aria-live="polite">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Comparison ready</span>
          <h2>What separates these estimates</h2>
        </div>
        <div className="difference-card">
          <span>Price difference</span>
          <strong>{formatCents(result.price_difference_cents)}</strong>
          <small>{result.lower_bidder} submitted the lower price</small>
        </div>
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
      {value.coat_count !== undefined && value.coat_count !== null && (
        <small>{value.coat_count} coat{value.coat_count === 1 ? "" : "s"}</small>
      )}
      {value.duration_years !== undefined && value.duration_years !== null && (
        <small>{value.duration_years}-year term</small>
      )}
      {value.evidence && <details><summary>View evidence</summary><p>{value.evidence}</p></details>}
    </div>
  );
}
