import React, { useState, useEffect, useRef } from 'react';
import './App.css';

// remark---> the frontend is served by the same FastAPI process
// the CRA dev-server "proxy" field in package.json forwards
// relative "/api/..." requests to http://127.0.0.1:8000 automatically.
const API_BASE = process.env.REACT_APP_API_URL || '';

function App() {
  const [topic, setTopic] = useState('');
  const [maxPapers, setMaxPapers] = useState(5);
  const [uploadedCount, setUploadedCount] = useState(0);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isChatLoading, setIsChatLoading] = useState(false);
  
  const [state, setState] = useState({
    status: 'idle',
    step: 0,
    topic_meta: {},
    papers: [],
    matrix: [],
    review: '',
    publication_review: '',
    evaluation: {}
  });

  const chatEndRef = useRef(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatHistory, isChatOpen]);

  useEffect(() => {
    let interval = null;
    if (state.status === 'processing') {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`${API_BASE}/api/state`);
          const data = await res.json();
          setState(data);
          if (data.status !== 'processing') {
            clearInterval(interval);
          }
        } catch (err) {
          console.error("Error polling system tracking matrix:", err);
        }
      }, 2500);
    }
    return () => clearInterval(interval);
  }, [state.status]);

  const handleBulkUpload = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    try {
      const res = await fetch(`${API_BASE}/api/upload-multiple`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      setUploadedCount(prev => prev + data.uploaded_count);
      alert(`Successfully cached ${data.uploaded_count} local core papers.`);
    } catch (err) {
      alert("Bulk ingestion parsing failed.");
    }
  };

  const executeResearchPipeline = async () => {
    if (!topic.trim()) return alert("Provide a valid topic directive.");
    try {
      setState(prev => ({ ...prev, status: 'processing', step: 1 }));
      const res = await fetch(`${API_BASE}/api/pipeline/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, max_papers: parseInt(maxPapers) })
      });
      const data = await res.json();
      setState(data);
    } catch (err) {
      setState(prev => ({ ...prev, status: 'failed' }));
      alert("Pipeline run faulted.");
    }
  };

  const dispatchChatMessage = async () => {
    if (!chatInput.trim()) return;
    const query = chatInput;
    setChatInput('');
    setChatHistory(prev => [...prev, { role: 'user', text: query }]);
    setIsChatLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query })
      });
      const data = await res.json();
      setChatHistory(prev => [...prev, { role: 'assistant', text: data.answer }]);
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'assistant', text: "Error fetching local context." }]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const resetSystemWorkspace = async () => {
    if (!window.confirm("Reset all local storage and reset environment?")) return;
    try {
      await fetch(`${API_BASE}/api/reset`, { method: 'POST' });
      setTopic('');
      setUploadedCount(0);
      setChatHistory([]);
      setState({
        status: 'idle',
        step: 0,
        topic_meta: {},
        papers: [],
        matrix: [],
        review: '',
        publication_review: '',
        evaluation: {}
      });
    } catch (err) {
      alert("Reset execution failed.");
    }
  };

  const downloadTextFile = (content, filename) => {
    const element = document.createElement("a");
    const file = new Blob([content], { type: 'text/plain;charset=utf-8' });
    element.href = URL.createObjectURL(file);
    element.download = filename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const exportMatrixToXLS = () => {
    if (state.matrix.length === 0) return;
    let excelRows = [
      ["Paper No", "Title", "Authors", "Year", "Problem", "Methodology", "Findings", "Limitations", "Place and Link"].join("\t")
    ];
    state.matrix.forEach(row => {
      excelRows.push([
        row.paper_no,
        row.title.replace(/\t|\n/g, " "),
        row.authors.replace(/\t|\n/g, " "),
        row.year,
        row.research_problem.replace(/\t|\n/g, " "),
        row.methodology.replace(/\t|\n/g, " "),
        row.key_findings.replace(/\t|\n/g, " "),
        row.limitations.replace(/\t|\n/g, " "),
        row.venueAndLink.replace(/\t|\n/g, " ")
      ].join("\t"));
    });
    downloadTextFile(excelRows.join("\n"), "architectural_matrix.xls");
  };

  // Only base styles without media queries or pseudo-elements
  const styles = {
    container: {
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      backgroundColor: '#f8fafc',
      minHeight: '100vh',
      padding: '32px',
      color: '#0f172a',
      maxWidth: '1600px',
      margin: '0 auto'
    },
    appBar: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      borderBottom: '1px solid #e2e8f0',
      paddingBottom: '18px',
      marginBottom: '28px',
      flexWrap: 'wrap',
      gap: '12px'
    },
    title: {
      fontSize: '26px',
      fontWeight: '800',
      letterSpacing: '-0.05em',
      color: '#1e293b',
      margin: 0
    },
    btnDanger: {
      padding: '8px 18px',
      borderRadius: '8px',
      border: '1.5px solid #ef4444',
      color: '#ef4444',
      backgroundColor: 'transparent',
      fontWeight: '600',
      cursor: 'pointer',
      fontSize: '14px'
    },
    card: {
      backgroundColor: '#ffffff',
      borderRadius: '12px',
      border: '1px solid #e2e8f0',
      padding: '24px',
      marginBottom: '24px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.02)'
    },
    flexRow: {
      display: 'flex',
      gap: '16px',
      alignItems: 'center',
      marginBottom: '16px',
      flexWrap: 'wrap'
    },
    inputField: {
      flex: 1,
      padding: '12px 16px',
      borderRadius: '8px',
      border: '1.5px solid #e2e8f0',
      fontSize: '15px',
      color: '#334155',
      outline: 'none',
      minWidth: '200px'
    },
    numInput: {
      width: '100px',
      padding: '12px',
      borderRadius: '8px',
      border: '1.5px solid #e2e8f0',
      fontSize: '15px',
      textAlign: 'center',
      outline: 'none'
    },
    btnAction: {
      padding: '12px 24px',
      backgroundColor: '#2563eb',
      color: '#ffffff',
      border: 'none',
      borderRadius: '8px',
      fontSize: '15px',
      fontWeight: '600',
      cursor: 'pointer'
    },
    btnExport: {
      padding: '6px 14px',
      backgroundColor: '#f8fafc',
      border: '1.5px solid #e2e8f0',
      borderRadius: '6px',
      fontSize: '13px',
      cursor: 'pointer',
      fontWeight: '500',
      color: '#475569'
    },
    splitGrid: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '24px',
      marginBottom: '24px'
    },
    scrollBox: {
      height: '420px',
      overflowY: 'auto',
      border: '1px solid #f1f5f9',
      padding: '16px',
      borderRadius: '8px',
      backgroundColor: '#fafbfc',
      fontSize: '14px',
      lineHeight: '1.7',
      whiteSpace: 'pre-wrap',
      color: '#334155'
    },
    badge: {
      display: 'inline-flex',
      alignItems: 'center',
      padding: '6px 14px',
      borderRadius: '9999px',
      fontSize: '13px',
      fontWeight: '500',
      backgroundColor: '#f8fafc',
      color: '#64748b',
      marginRight: '8px',
      marginBottom: '8px',
      border: '1px solid #e2e8f0'
    },
    badgeActive: {
      backgroundColor: '#eff6ff',
      color: '#2563eb',
      borderColor: '#bfdbfe'
    },
    th: {
      backgroundColor: '#f8fafc',
      color: '#475569',
      padding: '12px',
      borderBottom: '2px solid #e2e8f0',
      fontSize: '13px',
      textTransform: 'uppercase',
      fontWeight: '600',
      textAlign: 'left',
      whiteSpace: 'nowrap'
    },
    td: {
      padding: '12px',
      borderBottom: '1px solid #f1f5f9',
      fontSize: '13px',
      color: '#334155',
      verticalAlign: 'top'
    },
    floatingWidget: {
      position: 'fixed',
      bottom: '24px',
      right: '24px',
      width: '380px',
      height: '500px',
      backgroundColor: '#ffffff',
      borderRadius: '16px',
      boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1)',
      border: '1px solid #e2e8f0',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      zIndex: 10000
    },
    chatTrigger: {
      position: 'fixed',
      bottom: '24px',
      right: '24px',
      width: '56px',
      height: '56px',
      borderRadius: '50%',
      backgroundColor: '#2563eb',
      color: '#ffffff',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '22px',
      cursor: 'pointer',
      boxShadow: '0 4px 12px rgba(37,99,235,0.3)',
      zIndex: 10000,
      fontWeight: 'bold'
    },
    tableWrapper: {
      overflowX: 'auto',
      marginTop: '8px',
      borderRadius: '8px',
      border: '1px solid #f1f5f9'
    },
    fileInput: {
      padding: '8px',
      fontSize: '13px',
      color: '#475569',
      cursor: 'pointer'
    }
  };

  const steps = ["Query Parsing", "Meta Discovery", "Ingest Download", "Structural Extraction", "Review Processing", "Index Generation", "System Verification Audit"];

  return (
    <div className="app-container" style={styles.container}>
      <div className="app-bar" style={{
          ...styles.appBar, backgroundColor: '#0f172a', padding: '20px 28px', borderRadius: '12px', marginBottom: '28px', background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
          boxShadow: '0 4px 20px rgba(15, 23, 42, 0.3)', border: '1px solid rgba(255,255,255,0.05)' }}>
        <h1 className="app-title" style={{...styles.title, color: '#ffffff', fontFamily: '"Playfair Display", "Georgia", serif',fontSize: '22px',}}>🔬 Agentic Academic AI Research Suite</h1>
        <button className="btn-danger" onClick={resetSystemWorkspace} style={styles.btnDanger}>Reset Environment</button>
      </div>

      <div className="card" style={styles.card}>
        <h3 style={{ marginTop: 0, marginBottom: '16px', color: '#1e293b', fontSize: '20px' }}>
                  Research Configuration <span style={{ fontWeight: '400', color: '#35598b', fontStyle: 'italic' }}>- share your idea</span>
        </h3>
        <div className="flex-row" style={styles.flexRow}>
          <input 
            className="input-field"
            style={{
              ...styles.inputField,
              border: '2px solid transparent',
              backgroundImage: 'linear-gradient(#ffffff, #ffffff), linear-gradient(135deg, #2563eb, #7c3aed)',
              backgroundOrigin: 'border-box',
              backgroundClip: 'padding-box, border-box'
            }} 
            type="text" 
            placeholder="Define research objective statement..." 
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            disabled={state.status === 'processing'}
          />
          <label style={{ fontSize: '14px', fontWeight: '500', color: '#514769', whiteSpace: 'nowrap' }}>Max Paper Limit:</label>
          <input 
            className="num-input"
            style={styles.numInput} 
            type="number" 
            min="1" 
            max="20"
            value={maxPapers}
            onChange={(e) => setMaxPapers(e.target.value)}
            disabled={state.status === 'processing'}
            title="Choose 3 for better Output"
          />
          <button className="btn-action" style={styles.btnAction} onClick={executeResearchPipeline} disabled={state.status === 'processing'}>
            {state.status === 'processing' ? 'Running Framework Pipeline...' : 'Launch Operations'}
          </button>
        </div>
        <div style={{ borderTop: '1px solid #f1f5f9', paddingTop: '16px', display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '14px', fontWeight: '600', color: '#475569' }}>You can submit papers from local too:</span>
          <div className="file-input-wrapper" style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            <input 
              type="file" 
              multiple 
              accept=".pdf" 
              onChange={handleBulkUpload} 
              disabled={state.status === 'processing'} 
              className="file-input"
              style={styles.fileInput}
            />
            {uploadedCount > 0 && <span style={{ fontSize: '13px', color: '#16a34a', fontWeight: '600' }}>📄 {uploadedCount} locally prioritized files queued.</span>}
          </div>
        </div>
      </div>

      <div className="card" style={styles.card}>
        <h4 style={{ margin: '0 0 12px 0', color: '#000000', fontSize: '15px', fontWeight: '600' }}>Pipeline Verification Milestone Monitor</h4>
        <div className="badge-container">
          {steps.map((label, idx) => {
            const currentStepMarker = idx + 1;
            const isCompleted = state.step >= currentStepMarker || state.status === 'completed';
            return (
              <div key={label} style={{ ...styles.badge, ...(isCompleted ? styles.badgeActive : {}) }} className={isCompleted ? 'badge badge-active' : 'badge'}>
                {currentStepMarker}. {label} {isCompleted ? '✓' : ''}
              </div>
            );
          })}
        </div>
      </div>

      <div className="split-grid" style={styles.splitGrid}>
        <div className="card" style={styles.card}>
          <div style={{ marginBottom: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
            <h3 style={{ margin: 0, fontSize: '16px', color: '#1e293b' }}>Synthesized Literature Review</h3>
            <button className="btn-export" style={styles.btnExport} onClick={() => downloadTextFile(state.review, "literature_review.txt")}>Download Plain (.txt)</button>
          </div>
          <div className="scroll-box" style={styles.scrollBox}>{state.review || "Awaiting operation metrics."}</div>
        </div>

        <div className="card" style={styles.card}>
          <div style={{ marginBottom: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
            <h3 style={{ margin: 0, fontSize: '16px', color: '#1e293b' }}>Direct Manuscript-Ready Publication Text</h3>
            <button className="btn-export" style={styles.btnExport} onClick={() => downloadTextFile(state.publication_review, "publication_ready_section.txt")}>Download Manuscript-Ready-Lit (.txt)</button>
          </div>
          <div className="scroll-box" style={styles.scrollBox}>{state.publication_review || "Awaiting operation metrics."}</div>
        </div>
      </div>

      <div className="card" style={styles.card}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
          <h3 style={{ margin: 0, fontSize: '16px', color: '#1e293b' }}>Comparative Analytical Architectural Matrix Table</h3>
          <button className="btn-export" style={styles.btnExport} onClick={exportMatrixToXLS}>Export Spreadsheet (.xls)</button>
        </div>
        <div className="table-wrapper" style={styles.tableWrapper}>
          {state.matrix.length === 0 ? (
            <p style={{ color: '#94a3b8', margin: 0, fontSize: '14px', padding: '16px' }}>No execution metrics processed into matrix structures yet.</p>
          ) : (
            <table className="matrix-table" style={{ width: '100%', borderCollapse: 'collapse', minWidth: '900px' }}>
              <thead>
                <tr>
                  <th style={styles.th}>No</th>
                  <th style={styles.th}>Academic Title</th>
                  <th style={styles.th}>Authorship Group</th>
                  <th style={styles.th}>Year</th>
                  <th style={styles.th}>Problem Statement</th>
                  <th style={styles.th}>Methodology Framework</th>
                  <th style={styles.th}>Key Findings</th>
                  <th style={styles.th}>Limitations</th>
                  <th style={styles.th}>Place and Link</th>
                </tr>
              </thead>
              <tbody>
                {state.matrix.map((row) => (
                  <tr key={row.paper_no}>
                    <td style={styles.td}>{row.paper_no}</td>
                    <td style={{ ...styles.td, fontWeight: '700', color: '#1e293b' }}>{row.title}</td>
                    <td style={styles.td}>{row.authors}</td>
                    <td style={styles.td}>{row.year}</td>
                    <td style={styles.td}>{row.research_problem}</td>
                    <td style={styles.td}>{row.methodology}</td>
                    <td style={styles.td}>{row.key_findings}</td>
                    <td style={styles.td}>{row.limitations}</td>
                    <td style={styles.td}>
                      <div style={{ fontWeight: '600', color: '#475569', marginBottom: '4px' }}>
                        {row.publication_venue || "ArXiv Pre-print"}
                      </div>
                      {row.online_link && row.online_link !== "#" ? (
                        <a 
                          href={row.online_link} 
                          target="_blank" 
                          rel="noreferrer" 
                          style={{ color: '#2563eb', textDecoration: 'none', fontWeight: '500' }}
                        >
                          🔗 Open Reference Source
                        </a>
                      ) : (
                        <span style={{ color: '#94a3b8', fontStyle: 'italic' }}>Local File Stream</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {state.evaluation && state.evaluation.score && (
        <div className="card" style={{ ...styles.card, borderLeft: '4px solid #2563eb' }}>
          <h3 style={{ marginTop: 0, color: '#1e293b', fontSize: '16px' }}>Auditor Verification Framework Evaluation Report</h3>
          <p style={{ fontSize: '15px' }}>Overall Data Synthesis Score: <strong style={{ color: '#2563eb' }}>{state.evaluation.score} / 10</strong></p>
          <ul style={{ paddingLeft: '20px', margin: 0, fontSize: '14px', color: '#475569', lineHeight: '1.6' }}>
            {state.evaluation.issues?.map((item, idx) => <li key={idx} style={{ marginBottom: '4px' }}>⚠️ {item}</li>)}
          </ul>
        </div>
      )}

      {isChatOpen ? (
        <div className="floating-widget" style={styles.floatingWidget}>
          <div style={{ backgroundColor: '#2563eb', padding: '14px 18px', color: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontWeight: '700', fontSize: '14px' }}>Local Context Copilot Chatroom</span>
            <span style={{ cursor: 'pointer', fontWeight: 'bold', fontSize: '18px', opacity: 0.8 }} onClick={() => setIsChatOpen(false)}>✕</span>
          </div>
          <div className="chat-messages" style={{ flex: 1, padding: '16px', overflowY: 'auto', backgroundColor: '#f8fafc', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {chatHistory.length === 0 && <p style={{ color: '#94a3b8', fontSize: '13px', margin: 0, textAlign: 'center', marginTop: '40px' }}>Ask structural analysis questions relative to the cached library files...</p>}
            {chatHistory.map((msg, i) => (
              <div key={i} style={{ alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '85%' }}>
                <div style={{ backgroundColor: msg.role === 'user' ? '#2563eb' : '#ffffff', color: msg.role === 'user' ? '#ffffff' : '#334155', padding: '10px 14px', borderRadius: '12px', fontSize: '13px', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', border: msg.role === 'user' ? 'none' : '1px solid #e2e8f0', lineHeight: '1.5' }}>
                  {msg.text}
                </div>
              </div>
            ))}
            {isChatLoading && <span style={{ fontStyle: 'italic', fontSize: '12px', color: '#64748b', paddingLeft: '4px' }}>Analyzing library snippets...</span>}
            <div ref={chatEndRef} />
          </div>
          <div style={{ padding: '12px 16px', borderTop: '1px solid #e2e8f0', display: 'flex', gap: '8px', backgroundColor: '#ffffff' }}>
            <input 
              className="chat-input"
              style={{ ...styles.inputField, padding: '10px 14px', fontSize: '13px', minWidth: 'auto' }} 
              type="text" 
              placeholder="Ask about equations, findings..." 
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && dispatchChatMessage()}
            />
            <button className="chat-send-btn" style={{ ...styles.btnAction, padding: '10px 18px', fontSize: '13px', whiteSpace: 'nowrap' }} onClick={dispatchChatMessage}>Send</button>
          </div>
        </div>
      ) : (
        <div className="chat-trigger" style={styles.chatTrigger} onClick={() => setIsChatOpen(true)}>💬</div>
      )}
    </div>
  );
}

export default App;