import { useEffect, useMemo, useState } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000/api/discrepancies/";

function App() {
  const [rows, setRows] = useState([]);
  const [org, setOrg] = useState("ORG-A");
  const [reason, setReason] = useState("");
  const [ordering, setOrdering] = useState("");
  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    setLoading(true);

    try {
      const params = { org_id: org };

      if (reason) params.reason = reason;
      if (ordering) params.ordering = ordering;

      const response = await axios.get(API, { params });
      setRows(response.data.results);
    } catch (err) {
      console.error(err);
      alert("Failed to load data");
    }

    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, [org, reason, ordering]);

  const summary = useMemo(() => {
    return {
      total: rows.length,
      mismatch: rows.filter((r) => r.reason === "VALUE_MISMATCH").length,
      missing: rows.filter((r) => r.reason === "MISSING_IN_SYSTEM_B").length,
      duplicate: rows.filter((r) => r.reason === "DUPLICATE_IN_SYSTEM_B").length,
    };
  }, [rows]);

  const badgeColor = (reason) => {
    switch (reason) {
      case "VALUE_MISMATCH":
        return "#ffe5e5";
      case "MISSING_IN_SYSTEM_B":
        return "#fff3cd";
      case "DUPLICATE_IN_SYSTEM_B":
        return "#dbeafe";
      case "ORPHAN_IN_SYSTEM_B":
        return "#e9ecef";
      default:
        return "#f5f5f5";
    }
  };

  return (
    <div style={container}>
      <h1>Cross-System Reconciliation Dashboard</h1>
      <p style={{ color: "#666" }}>
        Tenant-aware discrepancy viewer
      </p>

      <div style={filterRow}>
        <div>
          <label>Organization</label>
          <br />
          <select value={org} onChange={(e) => setOrg(e.target.value)}>
            <option value="ORG-A">ORG-A</option>
            <option value="ORG-B">ORG-B</option>
          </select>
        </div>

        <div>
          <label>Reason</label>
          <br />
          <select value={reason} onChange={(e) => setReason(e.target.value)}>
            <option value="">All</option>
            <option value="VALUE_MISMATCH">Value Mismatch</option>
            <option value="MISSING_IN_SYSTEM_B">Missing in B</option>
            <option value="DUPLICATE_IN_SYSTEM_B">Duplicate</option>
            <option value="ORPHAN_IN_SYSTEM_B">Orphan</option>
          </select>
        </div>

        <div>
          <label>Sort</label>
          <br />
          <select
            value={ordering}
            onChange={(e) => setOrdering(e.target.value)}
          >
            <option value="">Default</option>
            <option value="system_a">System A</option>
            <option value="system_b">System B</option>
          </select>
        </div>
      </div>

      <div style={cardRow}>
        <div style={card}>
          <h2>{summary.total}</h2>
          <p>Total</p>
        </div>

        <div style={card}>
          <h2>{summary.mismatch}</h2>
          <p>Mismatch</p>
        </div>

        <div style={card}>
          <h2>{summary.missing}</h2>
          <p>Missing</p>
        </div>

        <div style={card}>
          <h2>{summary.duplicate}</h2>
          <p>Duplicate</p>
        </div>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <p>
          <strong>{rows.length}</strong> discrepancies found
        </p>
      )}

      <table style={table}>
        <thead>
          <tr style={{ background: "#f3f4f6" }}>
            <th style={th}>Reason</th>
            <th style={th}>Record</th>
            <th style={th}>Location</th>
            <th style={th}>System A</th>
            <th style={th}>System B</th>
          </tr>
        </thead>

        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              <td style={td}>
                <span
                  style={{
                    background: badgeColor(r.reason),
                    padding: "4px 8px",
                    borderRadius: 6,
                    fontSize: 12,
                  }}
                >
                  {r.reason}
                </span>
              </td>

              <td style={td}>{r.record}</td>
              <td style={td}>{r.location}</td>
              <td style={td}>{r.system_a ?? "—"}</td>
              <td style={td}>{r.system_b ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const container = {
  padding: 30,
  fontFamily: "Arial, sans-serif",
};

const filterRow = {
  display: "flex",
  gap: 20,
  flexWrap: "wrap",
  margin: "24px 0",
};

const cardRow = {
  display: "flex",
  gap: 16,
  flexWrap: "wrap",
  marginBottom: 20,
};

const card = {
  border: "1px solid #ddd",
  borderRadius: 10,
  padding: 16,
  minWidth: 120,
  background: "#fafafa",
  textAlign: "center",
};

const table = {
  width: "100%",
  borderCollapse: "collapse",
};

const th = {
  border: "1px solid #ddd",
  padding: 10,
  textAlign: "left",
};

const td = {
  border: "1px solid #ddd",
  padding: 10,
};

export default App;