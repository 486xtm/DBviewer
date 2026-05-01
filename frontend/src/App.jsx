import { useEffect, useMemo, useState } from "react";

/**
 * Parses /db/{database}/{table}/{column}/{value}.html (single-segment value).
 */
export function parseTablePath(pathname) {
  const m = pathname.match(
    /^\/db\/([^/]+)\/([^/]+)\/([^/]+)\/([^/]+)\.html$/,
  );
  if (!m) return null;
  return {
    database: m[1],
    table: m[2],
    column: m[3],
    value: m[4],
  };
}

function buildApiUrl({ database, table, column, value }) {
  const enc = encodeURIComponent;
  return `/api/db/${enc(database)}/${enc(table)}/${enc(column)}/${enc(value)}`;
}

export default function App() {
  const parsed = useMemo(
    () => parseTablePath(window.location.pathname),
    [],
  );
  const [data, setData] = useState(null);
  const [err, setErr] = useState(null);
  const [loading, setLoading] = useState(Boolean(parsed));

  useEffect(() => {
    if (!parsed) {
      setLoading(false);
      return;
    }
    const url = buildApiUrl(parsed);
    let cancelled = false;
    setLoading(true);
    setErr(null);
    fetch(url)
      .then(async (res) => {
        const body = await res.json();
        if (!res.ok) {
          throw new Error(body.message || body.error || res.statusText);
        }
        return body;
      })
      .then((json) => {
        if (!cancelled) setData(json);
      })
      .catch((e) => {
        if (!cancelled) setErr(e.message || String(e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [parsed]);

  if (!parsed) {
    return (
      <div className="wrap">
        <p>
          Open a SlashDB-style URL, for example{" "}
          <code>/db/Chinook/Customer/Country/Brazil.html</code>
        </p>
      </div>
    );
  }

  if (loading) return <div className="wrap">Loading…</div>;
  if (err) return <div className="wrap err">{err}</div>;
  if (!data || data.error) {
    return (
      <div className="wrap err">
        {data?.message || data?.error || "Unknown error"}
      </div>
    );
  }

  return (
    <div className="wrap">
      <header className="hdr">
        <h1>
          {data.database} / {data.table}
        </h1>
        <p>
          <code>
            {data.column} = {String(data.value)}
          </code>
          {data.truncated_hint ? (
            <span className="hint"> (may be truncated — max rows cap)</span>
          ) : null}
        </p>
      </header>
      <div className="table-scroll">
        <table className="grid">
          <thead>
            <tr>
              {data.columns.map((c) => (
                <th key={c}>{c}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.rows.map((row, i) => (
              <tr key={i}>
                {row.map((cell, j) => (
                  <td key={j}>{cell == null ? "" : String(cell)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
