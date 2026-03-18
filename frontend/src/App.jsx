import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  ShieldAlert, 
  ShieldCheck, 
  Activity, 
  History, 
  LogOut,
  RefreshCcw, 
  Download,
  Search,
  Plus,
  Filter
} from 'lucide-react';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement,
  Title, 
  Tooltip, 
  Legend, 
  Filler 
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

// API Configuration
const api = axios.create({ baseURL: '/api/v1' });
const dashboardApi = {
  getSummary: () => api.get('/dashboard/summary').then(res => res.data),
  getKpis: () => api.get('/dashboard/kpis').then(res => res.data),
  getIncidents: (params) => api.get('/incidents/', { params }).then(res => res.data),
  getIncidentStats: () => api.get('/incidents/stats').then(res => res.data),
  getControls: (params) => api.get('/controls/', { params }).then(res => res.data),
  getCompliance: () => api.get('/controls/compliance').then(res => res.data),
};

// Chart.js Registration
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler);

// Internal Components
const Sidebar = ({ currentView, setView }) => {
  const navItems = [
    { id: 'dashboard', icon: <LayoutDashboard size={20} />, label: 'Dashboard' },
    { id: 'incidents', icon: <ShieldAlert size={20} />, label: 'Incidentes' },
    { id: 'controls', icon: <ShieldCheck size={20} />, label: 'Controles ISO' },
    { id: 'risk', icon: <Activity size={20} />, label: 'Riesgos' },
    { id: 'history', icon: <History size={20} />, label: 'Historial' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <ShieldCheck size={32} strokeWidth={2.5} />
        <span>ISO_SECURE</span>
      </div>
      <nav>
        {navItems.map((item) => (
          <button 
            key={item.id} 
            onClick={() => setView(item.id)}
            className={`nav-link ${currentView === item.id ? 'active' : ''}`}
            style={{ width: '100%', border: 'none', background: 'none', cursor: 'pointer', textAlign: 'left' }}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
      <div style={{ marginTop: 'auto', paddingTop: '2rem' }}>
        <button className="nav-link" style={{ width: '100%', border: 'none', background: 'none', cursor: 'pointer', textAlign: 'left', color: 'var(--danger)' }}>
          <LogOut size={20} />
          <span>Cerrar Sesión</span>
        </button>
      </div>
    </aside>
  );
};

const KPICard = ({ title, value, unit, status, description }) => {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card kpi-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <span className="kpi-label">{title}</span>
        <span className={`status-dot status-${status}`}></span>
      </div>
      <div className="kpi-value">
        {typeof value === 'number' ? value.toFixed(2) : value}
        <span style={{ fontSize: '1rem', color: 'var(--text-muted)', marginLeft: '4px' }}>
          {unit}
        </span>
      </div>
      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
        {description}
      </p>
    </motion.div>
  );
};
// --- New Component: ControlsView ---
const ControlsView = ({ controls, stats, loading }) => {
  console.log("ControlsView Render:", { controlsCount: controls?.length, hasStats: !!stats, loading });

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'compliant': return 'var(--success)';
      case 'partial': return 'var(--warning)';
      case 'non_compliant': return 'var(--danger)';
      default: return 'var(--text-muted)';
    }
  };

  const getStatusLabel = (status) => {
    switch (status?.toLowerCase()) {
      case 'compliant': return 'Cumple';
      case 'partial': return 'Parcial';
      case 'non_compliant': return 'No Cumple';
      default: return status;
    }
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="view-title">Centro de Controles ISO 27001</h1>
          <p className="view-subtitle">Gestión de cumplimiento y estado de controles</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button className="glass-card" style={{ padding: '0.75rem', color: 'white', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Download size={18} />
            <span>Reporte ISO</span>
          </button>
        </div>
      </div>

      <div className="kpi-grid">
        <KPICard 
          title="Cumplimiento Global" 
          value={stats?.global_compliance_pct || 0} 
          unit="%" 
          status={stats?.global_compliance_pct > 80 ? "green" : stats?.global_compliance_pct > 50 ? "amber" : "red"}
          description="Alineación normativa" 
        />
        <KPICard 
          title="Controles Totales" 
          value={stats?.total_controls || 0} 
          unit="und." 
          status="blue" 
          description="Inventario de controles" 
        />
        <KPICard 
          title="No Cumplimiento" 
          value={stats?.non_compliant || 0} 
          unit="cont." 
          status="red" 
          description="Brechas críticas" 
        />
      </div>

      <div className="glass-card table-section">
        <div className="table-header">
          <h2 className="table-title">Matriz de Controles</h2>
          <div className="table-actions">
            <div className="search-bar">
              <Search size={18} />
              <input type="text" placeholder="Buscar por dominio o referencia..." />
            </div>
          </div>
        </div>

        <div className="table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>ESTADO</th>
                <th>REF & NOMBRE</th>
                <th>DOMINIO</th>
                <th>CUMPLIMIENTO</th>
                <th>RESPONSABLE</th>
              </tr>
            </thead>
            <tbody>
              {controls.map((control) => (
                <tr key={control.id}>
                  <td style={{ padding: '1.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div className="status-dot" style={{ backgroundColor: getStatusColor(control.status) }}></div>
                      <span style={{ fontSize: '0.9rem' }}>{getStatusLabel(control.status)}</span>
                    </div>
                  </td>
                  <td style={{ padding: '1.25rem' }}>
                    <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>{control.iso_control_ref} - {control.name}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{control.description.substring(0, 60)}...</div>
                  </td>
                  <td style={{ padding: '1.25rem', fontSize: '0.9rem' }}>{control.iso_domain}</td>
                  <td style={{ padding: '1.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <div style={{ flex: 1, height: '6px', backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ width: `${control.compliance_pct}%`, height: '100%', backgroundColor: getStatusColor(control.status) }}></div>
                      </div>
                      <span style={{ fontSize: '0.85rem', fontWeight: 'bold' }}>{control.compliance_pct}%</span>
                    </div>
                  </td>
                  <td style={{ padding: '1.25rem', fontSize: '0.9rem' }}>{control.responsible}</td>
                </tr>
              ))}
              {controls.length === 0 && !loading && (
                <tr>
                  <td colSpan="5" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>No se encontraron controles registrados.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// --- New Component: IncidentsView ---
const IncidentsView = ({ incidents, stats, loading }) => {
  console.log("IncidentsView Render:", { incidentsCount: incidents?.length, hasStats: !!stats, loading });

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'open': return 'status-red';
      case 'in_progress': return 'status-amber';
      case 'resolved': return 'status-green';
      case 'closed': return 'status-green';
      default: return 'status-muted';
    }
  };

  const getSeverityStyle = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return { color: 'var(--danger)', fontWeight: 'bold' };
      case 'high': return { color: '#fb923c', fontWeight: 'bold' };
      case 'medium': return { color: 'var(--warning)' };
      default: return { color: 'var(--text-muted)' };
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Mini Stats Bar */}
      <div className="kpi-grid" style={{ marginBottom: '2rem' }}>
        <KPICard title="Total Incidentes" value={stats?.total || 0} unit="inc." status="amber" description="Histórico acumulado" />
        <KPICard title="Tasa Resolución" value={stats?.resolution_rate_pct || 0} unit="%" status="green" description="Efectividad de cierre" />
        <KPICard title="MTTR Promedio" value={stats?.avg_resolution_hrs || 0} unit="hrs" status="primary" description="Tiempo medio de respuesta" />
      </div>

      {/* Toolbar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem', gap: '1rem' }}>
        <div className="glass-card" style={{ flex: 1, padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Search size={18} color="var(--text-muted)" />
          <input 
            type="text" 
            placeholder="Buscar incidente por título o ID..." 
            style={{ background: 'none', border: 'none', color: 'white', outline: 'none', width: '100%' }}
          />
        </div>
        <button className="glass-card" style={{ padding: '0.5rem 1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'white', cursor: 'pointer' }}>
          <Plus size={20} />
          <span>Nuevo Incidente</span>
        </button>
      </div>

      {/* Table */}
      <div className="glass-card" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between' }}>
          <h3>Registro Detallado</h3>
          <Filter size={18} color="var(--text-muted)" style={{ cursor: 'pointer' }} />
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: 'rgba(255,255,255,0.02)', textAlign: 'left', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                <th style={{ padding: '1.25rem' }}>ESTADO</th>
                <th style={{ padding: '1.25rem' }}>ID & TÍTULO</th>
                <th style={{ padding: '1.25rem' }}>CATEGORÍA</th>
                <th style={{ padding: '1.25rem' }}>SEVERIDAD</th>
                <th style={{ padding: '1.25rem' }}>FECHA REPORTE</th>
              </tr>
            </thead>
            <tbody>
              {incidents.map((incident) => (
                <tr key={incident.id} style={{ borderTop: '1px solid var(--glass-border)', transition: 'background 0.2s' }} className="table-row-hover">
                  <td style={{ padding: '1.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span className={`status-dot ${getStatusColor(incident.status)}`}></span>
                      <span style={{ fontSize: '0.9rem', textTransform: 'capitalize' }}>{incident.status.replace('_', ' ')}</span>
                    </div>
                  </td>
                  <td style={{ padding: '1.25rem' }}>
                    <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>{incident.title}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>{incident.id.slice(0, 8)}...</div>
                  </td>
                  <td style={{ padding: '1.25rem', fontSize: '0.9rem' }}>{incident.category || 'N/A'}</td>
                  <td style={{ padding: '1.25rem' }}>
                    <span style={{ fontSize: '0.8rem', padding: '0.25rem 0.6rem', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', ...getSeverityStyle(incident.severity) }}>
                      {incident.severity.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ padding: '1.25rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    {new Date(incident.reported_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
              {incidents.length === 0 && !loading && (
                <tr>
                  <td colSpan="5" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>No se encontraron incidentes registrados.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [view, setView] = useState('dashboard');
  const [summary, setSummary] = useState(null);
  const [kpis, setKpis] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [incidentStats, setIncidentStats] = useState(null);
  const [controls, setControls] = useState([]);
  const [complianceStats, setComplianceStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (view === 'dashboard') {
        const [sumData, kpiData] = await Promise.all([
          dashboardApi.getSummary(),
          dashboardApi.getKpis()
        ]);
        setSummary(sumData);
        setKpis(kpiData.kpis);
      } else if (view === 'incidents') {
        const [list, st] = await Promise.all([
          dashboardApi.getIncidents({ limit: 50 }),
          dashboardApi.getIncidentStats()
        ]);
        setIncidents(list.items);
        setIncidentStats(st);
      } else if (view === 'controls') {
        const [list, cp] = await Promise.all([
          dashboardApi.getControls({ limit: 50 }),
          dashboardApi.getCompliance()
        ]);
        setControls(list.items);
        setComplianceStats(cp);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [view]);

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        titleFont: { family: 'Outfit', size: 14 },
        bodyFont: { family: 'Outfit', size: 13 },
        padding: 12,
        cornerRadius: 8,
      }
    },
    scales: {
      y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
      x: { grid: { display : false }, ticks: { color: '#94a3b8' } }
    }
  };

  const dummyChartData = {
    labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
    datasets: [{
      label: 'Cumplimiento %',
      data: [65, 72, 68, 75, 82, 88],
      borderColor: '#00d2ff',
      backgroundColor: 'rgba(0, 210, 255, 0.1)',
      fill: true,
      tension: 0.4,
    }]
  };

  const renderDashboard = () => (
    <div className="animate-fade-in">
      <div className="kpi-grid">
        {kpis.map((kpi, index) => (
          <KPICard 
            key={index}
            title={kpi.name}
            value={kpi.value}
            unit={kpi.unit}
            status={kpi.status}
            description={kpi.description}
          />
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="glass-card" style={{ padding: '2rem' }}>
          <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Activity size={20} color="var(--primary)" />
            Evolución de Cumplimiento Global
          </h3>
          <Line data={dummyChartData} options={chartOptions} height={100} />
        </div>
        <div className="glass-card" style={{ padding: '2rem' }}>
          <h3 style={{ marginBottom: '1.5rem' }}>Estado de Riesgos</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ padding: '1rem', borderLeft: '4px solid var(--danger)', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '0.5rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>DOMINIO MÁS CRÍTICO</div>
              <div style={{ fontSize: '1.1rem', fontWeight: '600' }}>{summary?.risk_highest_domain || 'N/A'}</div>
            </div>
            <div style={{ padding: '1rem', borderLeft: '4px solid var(--primary)', background: 'rgba(0, 210, 255, 0.1)', borderRadius: '0.5rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>SCORE GLOBAL</div>
              <div style={{ fontSize: '1.5rem', fontWeight: '800' }}>{summary?.risk_global_score?.toFixed(1) || '0.0'}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Nivel: {summary?.risk_global_level}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="glass-card" style={{ padding: '2rem' }}>
        <h3 style={{ marginBottom: '1.5rem' }}>Últimos Incidentes Detectados</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ textAlign: 'left', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              <th style={{ padding: '1rem' }}>ESTADO</th>
              <th style={{ padding: '1rem' }}>TÍTULO</th>
              <th style={{ padding: '1rem' }}>SEVERIDAD</th>
              <th style={{ padding: '1rem' }}>FECHA</th>
            </tr>
          </thead>
          <tbody>
            {summary?.active_incidents?.map(inc => (
              <tr key={inc.id} style={{ borderTop: '1px solid var(--glass-border)' }}>
                <td style={{ padding: '1rem' }}><span className="status-dot status-amber"></span> {inc.status}</td>
                <td style={{ padding: '1rem' }}>{inc.title}</td>
                <td style={{ padding: '1rem' }}><span style={{ color: inc.severity === 'critical' ? 'var(--danger)' : 'var(--warning)' }}>{inc.severity.toUpperCase()}</span></td>
                <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>{new Date(inc.reported_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderPlaceholder = (title) => (
    <div className="animate-fade-in glass-card" style={{ padding: '3rem', textAlign: 'center' }}>
      <Activity size={48} color="var(--primary)" style={{ marginBottom: '1rem' }} />
      <h2>Vista de {title}</h2>
      <p style={{ color: 'var(--text-muted)' }}>Esta sección está bajo desarrollo interactivo.</p>
    </div>
  );

  return (
    <div className="dashboard-container">
      <Sidebar currentView={view} setView={setView} />
      <main className="main-content">
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem' }}>
          <div>
            <h1 style={{ fontSize: '2.2rem', marginBottom: '0.5rem' }}>
              {view === 'dashboard' ? 'Resumen del SGSI' : view === 'incidents' ? 'Centro de Incidentes' : view.charAt(0).toUpperCase() + view.slice(1)}
            </h1>
            <p style={{ color: 'var(--text-muted)' }}>ISO_SECURE Management Platform</p>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button className="glass-card" style={{ padding: '0.75rem', color: 'white', cursor: 'pointer' }} onClick={view === 'incidents' ? fetchData : fetchData}>
              <RefreshCcw size={20} className={loading ? 'animate-spin' : ''} />
            </button>
            <button className="glass-card" style={{ padding: '0.75rem 1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'white', cursor: 'pointer' }}>
              <Download size={20} />
              <span>Exportar Reporte</span>
            </button>
          </div>
        </header>

        {loading && !summary && view === 'dashboard' ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '5rem' }}>
            <Activity className="animate-pulse" size={48} color="var(--primary)" />
          </div>
        ) : (
          <AnimatePresence mode="wait">
            <motion.div
              key={view}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              {view === 'dashboard' && renderDashboard()}
              {view === 'incidents' && <IncidentsView incidents={incidents} stats={incidentStats} loading={loading} />}
              {view === 'controls' && <ControlsView controls={controls} stats={complianceStats} loading={loading} />}
              {view === 'risk' && renderPlaceholder('Riesgos')}
              {view === 'history' && renderPlaceholder('Historial')}
            </motion.div>
          </AnimatePresence>
        )}
      </main>
    </div>
  );
}

export default App;
