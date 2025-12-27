import React, { useState, useEffect } from 'react';

const Dashboard = ({ user }) => {
  const [requests, setRequests] = useState([]);
  const [kpi, setKpi] = useState({ critical_count: 0, tech_load: 0, open_requests: 0, overdue: 0 });
  const [options, setOptions] = useState({ equipment: [], teams: [], technicians: [], work_centers: [], companies: [] });
  
  const [showModal, setShowModal] = useState(false);
  const [activeTab, setActiveTab] = useState('notes');
  const [isLocked, setIsLocked] = useState(true);
  const [activeReqId, setActiveReqId] = useState(null);
  
  const [formData, setFormData] = useState({
    subject: '', stage: 'New Request', target_type: 'equipment', equipment_id: '',
    work_center_id: '', category: '', m_type: 'Corrective', team: '', technician: '',
    scheduled_date: '', duration: '', priority: 'low', company: '', notes: '', instructions: '', status_color: 'grey'
  });

  const fetchData = async () => {
    try {
      const res = await fetch('/api/equipment-data', { credentials: 'include' });
      const data = await res.json();
      setRequests(data.requests || []); 
      setKpi(data.kpi || { critical_count: 0, tech_load: 0, open_requests: 0, overdue: 0 });
      setOptions({
        equipment: data.equipment || [],
        teams: data.teams || [],
        technicians: data.users || [],
        work_centers: data.work_centers || [],
        companies: data.companies || []
      });
    } catch (err) { console.error("Fetch error:", err); }
  };

  useEffect(() => { fetchData(); }, []);

  const autoSaveField = async (field, value) => {
    if (!activeReqId) return;
    await fetch('/api/request/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: activeReqId, field, value }),
      credentials: 'include'
    });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (activeReqId && !isLocked) autoSaveField(name, value);
  };

  const openModal = async (id = null) => {
    setActiveReqId(id);
    if (id) {
      const res = await fetch(`/api/request/${id}`, { credentials: 'include' });
      const data = await res.json();
      setFormData(data);
      setIsLocked(true);
    } else {
      setFormData({
        subject: '', stage: 'New Request', target_type: 'equipment', equipment_id: '',
        work_center_id: '', category: '', m_type: 'Corrective', team: '', technician: '',
        scheduled_date: '', duration: '', priority: 'low', company: '', notes: '', instructions: '', status_color: 'grey'
      });
      setIsLocked(false);
    }
    setShowModal(true);
  };

  const saveRequest = async (e) => {
    e.preventDefault();
    await fetch('/api/request/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...formData, request_id: activeReqId }),
      credentials: 'include'
    });
    setShowModal(false);
    fetchData();
  };

  const deleteRequest = async () => {
    if (window.confirm("Are you sure?")) {
      await fetch(`/api/request/delete/${activeReqId}`, { method: 'POST', credentials: 'include' });
      setShowModal(false);
      fetchData();
    }
  };

  return (
    <div style={styles.dashboardContainer}>
      <div style={styles.kpiRow}>
        <div style={{ ...styles.kpiCard, background: '#ffe5e5', borderColor: '#ffcccc' }}>
          <h3 style={{ color: '#cc0000', margin: 0 }}>Critical Equipment</h3>
          <h1 style={styles.kpiValue}>{kpi.critical_count} Units</h1>
          <small>(Health &lt; 30%)</small>
        </div>
        <div style={{ ...styles.kpiCard, background: '#e6f2ff', borderColor: '#cce5ff' }}>
          <h3 style={{ color: '#0056b3', margin: 0 }}>Technician Load</h3>
          <h1 style={styles.kpiValue}>{kpi.tech_load}%</h1>
          <small>Utilized</small>
        </div>
        <div style={{ ...styles.kpiCard, background: '#e6fffa', borderColor: '#ccf2eb' }}>
          <h3 style={{ color: '#006644', margin: 0 }}>Open Requests</h3>
          <h1 style={styles.kpiValue}>{kpi.open_requests} Pending</h1>
          <small>{kpi.overdue} Overdue</small>
        </div>
      </div>

      <div style={styles.actionBar}>
        <button onClick={() => openModal()} style={styles.newBtn}>New</button>
        <input type="text" placeholder="🔍 Search..." style={styles.searchInput} />
      </div>

      <div style={styles.tableWrapper}>
        <table style={styles.table}>
          <thead style={{ background: '#f9f9f9' }}>
            <tr>
              <th style={styles.th}>Subject</th>
              <th style={styles.th}>Employee</th>
              <th style={styles.th}>Technician</th>
              <th style={styles.th}>Stage & Status</th>
            </tr>
          </thead>
          <tbody>
            {requests.map(req => (
              <tr key={req._id} onClick={() => openModal(req._id)} style={styles.tr}>
                <td style={styles.td}>{req.subject}</td>
                <td style={styles.td}>{req.employee}</td>
                <td style={styles.td}>{req.technician}</td>
                <td style={{ ...styles.td, display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={styles.stageBadge}>{req.stage}</span>
                  <div style={{ ...styles.statusDot, background: req.status_color || 'grey' }}></div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div style={styles.modalOverlay}>
          <div style={styles.modalContent}>
            <div style={styles.modalHeader}>
              <div>
                <small style={{ color: '#666' }}>Maintenance /</small>
                <h2 style={{ margin: '5px 0' }}>{formData.subject || "New Request"}</h2>
              </div>
              <div style={styles.stageTracker}>
                {['New Request', 'In Progress', 'Done', 'Scrap'].map(s => (
                  <div 
                    key={s} 
                    style={{ ...styles.stageStep, ...(formData.stage === s ? styles.stageStepActive : {}) }}
                    onClick={() => !isLocked && setFormData({ ...formData, stage: s })}
                  >
                    {s.replace(' Request', '')}
                  </div>
                ))}
                <span onClick={() => setShowModal(false)} style={styles.closeX}>&times;</span>
              </div>
            </div>

            <form onSubmit={saveRequest}>
              <div style={styles.grid}>
                <div className="col-left">
                  <label style={styles.label}>Subject</label>
                  <input name="subject" value={formData.subject} onChange={handleInputChange} disabled={isLocked} style={styles.titleInput} />
                  
                  <label style={styles.label}>Maintenance For:</label>
                  <select name="target_type" value={formData.target_type} onChange={handleInputChange} disabled={isLocked} style={styles.input}>
                    <option value="equipment">Equipment</option>
                    <option value="work_center">Work Center</option>
                  </select>

                  {formData.target_type === 'equipment' ? (
                    <>
                      <label style={styles.label}>Select Equipment</label>
                      <select name="equipment_id" value={formData.equipment_id} onChange={handleInputChange} disabled={isLocked} style={styles.input}>
                        <option value="">-- Choose --</option>
                        {options.equipment.map(e => <option key={e._id} value={e._id}>{e.name}</option>)}
                      </select>
                    </>
                  ) : (
                    <>
                      <label style={styles.label}>Select Work Center</label>
                      <select name="work_center_id" value={formData.work_center_id} onChange={handleInputChange} disabled={isLocked} style={styles.input}>
                        <option value="">-- Choose --</option>
                        {options.work_centers.map(w => <option key={w._id} value={w._id}>{w.name}</option>)}
                      </select>
                    </>
                  )}
                </div>

                <div style={{ ...styles.colRight, borderLeft: '1px solid #eee', paddingLeft: '40px' }}>
                   <label style={styles.label}>Technician</label>
                   <select name="technician" value={formData.technician} onChange={handleInputChange} disabled={isLocked} style={styles.input}>
                     <option value="">Select Technician</option>
                     {options.technicians.map(t => <option key={t.name} value={t.name}>{t.name}</option>)}
                   </select>
                   
                   <label style={styles.label}>Priority</label>
                   <div style={{ display: 'flex', gap: '10px' }}>
                     {['low', 'medium', 'high'].map((p, i) => (
                       <span 
                         key={p} 
                         onClick={() => !isLocked && setFormData({...formData, priority: p})} 
                         style={{ ...styles.prioIcon, color: formData.priority === p ? '#1a1a1a' : '#ccc' }}
                       >
                         {Array(i + 1).fill('♦').join('')}
                       </span>
                     ))}
                   </div>
                </div>
              </div>

              <div style={{ marginTop: '30px' }}>
                <div style={{ display: 'flex', gap: '20px', borderBottom: '1px solid #ddd' }}>
                  <div onClick={() => setActiveTab('notes')} style={{ ...styles.tabBtn, ...(activeTab === 'notes' ? styles.tabBtnActive : {}) }}>Notes</div>
                  <div onClick={() => setActiveTab('instructions')} style={{ ...styles.tabBtn, ...(activeTab === 'instructions' ? styles.tabBtnActive : {}) }}>Instructions</div>
                </div>
                <textarea name={activeTab} value={formData[activeTab]} onChange={handleInputChange} disabled={isLocked} style={styles.textarea} />
              </div>

              <div style={styles.modalFooter}>
                {activeReqId && <button type="button" onClick={deleteRequest} style={styles.deleteBtn}>🗑 Delete</button>}
                {isLocked ? (
                  <button type="button" onClick={() => setIsLocked(false)} style={styles.editBtn}>🔓 Unlock to Edit</button>
                ) : (
                  <button type="submit" style={styles.saveBtn}>Save Changes</button>
                )}
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

const styles = {
  dashboardContainer: { padding: '20px', fontFamily: 'Inter, sans-serif' },
  kpiRow: { display: 'flex', gap: '20px', marginBottom: '30px' },
  kpiCard: { flex: 1, padding: '20px', border: '1px solid', borderRadius: '10px', textAlign: 'center' },
  kpiValue: { margin: '10px 0', fontSize: '32px' },
  actionBar: { display: 'flex', gap: '15px', marginBottom: '20px' },
  newBtn: { background: 'white', border: '2px solid #333', padding: '8px 25px', fontWeight: 'bold', borderRadius: '8px', cursor: 'pointer', boxShadow: '3px 3px 0px #ccc' },
  searchInput: { padding: '10px', width: '350px', border: '1px solid #ddd', borderRadius: '6px' },
  tableWrapper: { background: 'white', border: '1px solid #eee', borderRadius: '8px', overflow: 'hidden' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: { padding: '12px', textAlign: 'left', borderBottom: '2px dashed #999', fontSize: '13px', color: '#666' },
  td: { padding: '12px', borderBottom: '1px dashed #eee' },
  tr: { cursor: 'pointer' },
  stageBadge: { background: '#eee', padding: '4px 10px', borderRadius: '12px', fontSize: '11px', fontWeight: 'bold' },
  statusDot: { width: '10px', height: '10px', borderRadius: '50%' },
  modalOverlay: { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 },
  modalContent: { background: 'white', width: '850px', padding: '30px', borderRadius: '12px', maxHeight: '90vh', overflowY: 'auto' },
  modalHeader: { display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #eee', paddingBottom: '15px', marginBottom: '20px' },
  closeX: { cursor: 'pointer', fontSize: '24px', marginLeft: '20px' },
  grid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '40px' },
  label: { display: 'block', fontSize: '11px', fontWeight: 'bold', margin: '15px 0 5px', textTransform: 'uppercase', color: '#666' },
  input: { width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '4px' },
  titleInput: { width: '100%', fontSize: '24px', fontWeight: 'bold', border: 'none', borderBottom: '1px solid #ddd', marginBottom: '10px' },
  stageStep: { fontSize: '12px', color: '#888', background: '#f4f4f4', padding: '5px 15px', borderRadius: '20px', cursor: 'pointer' },
  stageStepActive: { background: '#1a1a1a', color: 'white' },
  stageTracker: { display: 'flex', alignItems: 'center', gap: '8px' },
  tabBtn: { padding: '10px 15px', cursor: 'pointer', fontWeight: 'bold', color: '#888' },
  tabBtnActive: { color: '#000', borderBottom: '3px solid #1a1a1a' },
  textarea: { width: '100%', height: '120px', padding: '10px', border: '1px solid #ddd', borderTop: 'none', background: '#fcfcfc', resize: 'none' },
  modalFooter: { marginTop: '30px', display: 'flex', justifyContent: 'space-between' },
  saveBtn: { background: '#1a1a1a', color: 'white', padding: '10px 40px', border: 'none', borderRadius: '5px', fontWeight: 'bold', cursor: 'pointer' },
  editBtn: { background: '#4ecca3', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '5px', fontWeight: 'bold', cursor: 'pointer' },
  deleteBtn: { background: 'none', border: '1px solid #ff6b6b', color: '#ff6b6b', padding: '10px 15px', borderRadius: '5px', fontWeight: 'bold' },
  prioIcon: { fontSize: '24px', cursor: 'pointer' }
};

export default Dashboard;