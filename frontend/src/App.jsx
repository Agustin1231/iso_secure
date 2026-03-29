import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  ShieldAlert,
  ShieldCheck,
  Activity,
  History,
  LogOut,
  LogIn,
  RefreshCcw,
  Download,
  Search,
  Plus,
  Filter,
  Sun,
  Moon,
  Menu,
  X,
  FileCode,
  Building2,
  Users,
  Eye,
  EyeOff,
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
import { authApi, empresaApi } from './api.js';

// Supabase config (anon key is public by design)
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || 'https://rhvzjqvyimaavkdjxcvj.supabase.co';
// anon key is intentionally public (read-only JWT for browser auth)
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJodnpqcXZ5aW1hYXZrZGp4Y3ZqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3OTM5NjUsImV4cCI6MjA4OTM2OTk2NX0.g7VkSF0oXl7lirJcvtu-NbrYtlYUDmHwOanzbw_WEqE';

// API Configuration
const api = axios.create({ baseURL: '/api/v1' });
const dashboardApi = {
  getSummary: () => api.get('/dashboard/summary').then(res => res.data),
  getKpis: () => api.get('/dashboard/kpis').then(res => res.data),
  getIncidents: (params) => api.get('/incidents/', { params }).then(res => res.data),
  getIncidentStats: () => api.get('/incidents/stats').then(res => res.data),
  getControls: (params) => api.get('/controls/', { params }).then(res => res.data),
  getCompliance: () => api.get('/controls/compliance').then(res => res.data),
  getRiskCurrent: () => api.get('/risk/current').then(res => res.data),
  getRiskByDomain: () => api.get('/risk/by-domain').then(res => res.data),
  getRiskHistory: (params) => api.get('/risk/history', { params }).then(res => res.data),
  getSnapshots: (params) => api.get('/snapshots/', { params }).then(res => res.data),
};

// Chart.js Registration
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler);

// Role-based nav items
const ALL_NAV_ITEMS = [
  { id: 'dashboard', icon: <LayoutDashboard size={20} />, label: 'Resumen', roles: ['admin', 'auditor', 'supervisor', 'analista'] },
  { id: 'incidents', icon: <ShieldAlert size={20} />, label: 'Incidentes', roles: ['admin', 'analista', 'auditor'] },
  { id: 'controls', icon: <ShieldCheck size={20} />, label: 'Controles ISO', roles: ['admin', 'auditor', 'analista'] },
  { id: 'risk', icon: <Activity size={20} />, label: 'Riesgos', roles: ['admin', 'auditor'] },
  { id: 'history', icon: <History size={20} />, label: 'Historial', roles: ['admin', 'supervisor'] },
  { id: 'empresas', icon: <Building2 size={20} />, label: 'Empresas', roles: ['admin', 'auditor'] },
];

const viewTitles = {
  dashboard: 'Resumen del SGSI',
  incidents: 'Centro de Incidentes',
  controls: 'Controles ISO 27001',
  risk: 'Gestión de Riesgos',
  history: 'Historial de Snapshots',
  empresas: 'Registro de Empresas',
};

// ─── LoginPage ────────────────────────────────────────────────────────────────
const LoginPage = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      // 1. Authenticate with Supabase
      const authRes = await axios.post(
        `${SUPABASE_URL}/auth/v1/token?grant_type=password`,
        { email, password },
        { headers: { apikey: SUPABASE_ANON_KEY, 'Content-Type': 'application/json' } }
      );
      const token = authRes.data.access_token;

      // 2. Fetch or create user profile from our backend
      let profile;
      try {
        profile = await axios.get('/api/v1/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        }).then(r => r.data);
      } catch (profileErr) {
        if (profileErr.response?.status === 403) {
          // Auto-register profile with default role
          profile = await axios.post('/api/v1/auth/register-profile', {}, {
            headers: { Authorization: `Bearer ${token}` }
          }).then(r => r.data);
        } else {
          throw profileErr;
        }
      }

      onLogin(token, profile);
    } catch (err) {
      if (err.response?.status === 400 || err.response?.status === 422) {
        setError('Credenciales incorrectas. Verifica tu email y contraseña.');
      } else {
        setError('Error al conectar. Intenta nuevamente.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--color-bg)',
      padding: '1rem',
    }}>
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        style={{ width: '100%', maxWidth: '420px' }}
      >
        <div className="glass-card" style={{ padding: '2.5rem' }}>
          {/* Logo */}
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <ShieldCheck size={36} color="var(--primary)" strokeWidth={2.5} />
              <span style={{ fontSize: '1.8rem', fontWeight: '800', letterSpacing: '-0.5px' }}>ISO_SECURE</span>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              Sistema de Gestión de Seguridad de la Información
            </p>
          </div>

          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                Correo electrónico
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="usuario@empresa.com"
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  background: 'var(--color-bg-elevated)',
                  border: '1px solid var(--glass-border)',
                  borderRadius: '8px',
                  color: 'var(--text-main)',
                  fontSize: '0.95rem',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                Contraseña
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  style={{
                    width: '100%',
                    padding: '0.75rem 3rem 0.75rem 1rem',
                    background: 'var(--color-bg-elevated)',
                    border: '1px solid var(--glass-border)',
                    borderRadius: '8px',
                    color: 'var(--text-main)',
                    fontSize: '0.95rem',
                    outline: 'none',
                    boxSizing: 'border-box',
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '0.75rem',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: 'var(--text-muted)',
                    padding: 0,
                  }}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {error && (
              <div style={{
                padding: '0.75rem 1rem',
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: '8px',
                color: 'var(--danger)',
                fontSize: '0.85rem',
              }}>
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              style={{
                padding: '0.85rem',
                background: 'var(--primary)',
                border: 'none',
                borderRadius: '8px',
                color: 'white',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                transition: 'opacity 0.2s',
              }}
            >
              {loading ? (
                <Activity size={18} className="animate-spin" />
              ) : (
                <LogIn size={18} />
              )}
              {loading ? 'Ingresando...' : 'Ingresar'}
            </button>
          </form>

          <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Acceso restringido · ISO/IEC 27001:2022
          </p>
        </div>
      </motion.div>
    </div>
  );
};

// ─── Sidebar ──────────────────────────────────────────────────────────────────
const Sidebar = ({ currentView, setView, theme, toggleTheme, isOpen, onClose, userRole, onLogout, userEmail }) => {
  const navItems = ALL_NAV_ITEMS.filter(item => !userRole || item.roles.includes(userRole));

  const handleNavClick = (id) => {
    setView(id);
    if (onClose) onClose();
  };

  const ROLE_LABELS = {
    admin: 'Administrador',
    auditor: 'Auditor',
    supervisor: 'Supervisor',
    analista: 'Analista',
  };

  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-logo">
        <ShieldCheck size={32} strokeWidth={2.5} />
        <span>ISO_SECURE</span>
      </div>

      {/* User info */}
      {userEmail && (
        <div style={{
          padding: '0.75rem 1rem',
          marginBottom: '0.5rem',
          background: 'var(--glass)',
          borderRadius: '8px',
          fontSize: '0.8rem',
        }}>
          <div style={{ color: 'var(--text-main)', fontWeight: '600', marginBottom: '0.15rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {userEmail}
          </div>
          <div style={{ color: 'var(--primary)', fontSize: '0.75rem' }}>
            {ROLE_LABELS[userRole] || userRole}
          </div>
        </div>
      )}

      <nav>
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => handleNavClick(item.id)}
            className={`nav-link ${currentView === item.id ? 'active' : ''}`}
            style={{ width: '100%', border: 'none', background: 'none', cursor: 'pointer', textAlign: 'left' }}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div style={{ marginTop: 'auto', paddingTop: '2rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <a
          href="/docs.html"
          target="_blank"
          className="nav-link"
          style={{ width: '100%', textDecoration: 'none' }}
        >
          <FileCode size={20} />
          <span>API Docs</span>
        </a>
        <button
          onClick={toggleTheme}
          className="nav-link"
          style={{ width: '100%', border: 'none', background: 'none', cursor: 'pointer', textAlign: 'left' }}
        >
          {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
          <span>{theme === 'light' ? 'Modo Oscuro' : 'Modo Claro'}</span>
        </button>
        <button
          onClick={onLogout}
          className="nav-link"
          style={{ width: '100%', border: 'none', background: 'none', cursor: 'pointer', textAlign: 'left', color: 'var(--danger)' }}
        >
          <LogOut size={20} />
          <span>Cerrar Sesión</span>
        </button>
      </div>
    </aside>
  );
};

// ─── KPICard ──────────────────────────────────────────────────────────────────
const KPICard = ({ title, value, unit, status, description }) => (
  <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card kpi-card">
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <span className="kpi-label">{title}</span>
      <span className={`status-dot status-${status}`}></span>
    </div>
    <div className="kpi-value">
      {typeof value === 'number' ? value.toFixed(2) : value}
      <span style={{ fontSize: '1rem', color: 'var(--text-muted)', marginLeft: '4px' }}>{unit}</span>
    </div>
    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>{description}</p>
  </motion.div>
);

// ─── Pagination ───────────────────────────────────────────────────────────────
const Pagination = ({ currentPage, totalPages, pageSize, onPageChange, onPageSizeChange, totalItems }) => {
  const pageSizeOptions = [5, 10, 15, 50, 'Todas'];
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 1.5rem', borderTop: '1px solid var(--glass-border)', flexWrap: 'wrap', gap: '1rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Mostrar:</span>
        <select
          value={pageSize}
          onChange={(e) => onPageSizeChange(e.target.value === 'Todas' ? 'all' : parseInt(e.target.value))}
          style={{ background: 'var(--color-bg-card)', border: '1px solid var(--glass-border)', borderRadius: '6px', padding: '0.5rem 0.75rem', color: 'var(--text-main)', fontSize: '0.85rem', cursor: 'pointer' }}
        >
          {pageSizeOptions.map(opt => (
            <option key={opt} value={opt} style={{ background: 'var(--color-bg-card)', color: 'var(--text-main)' }}>
              {opt === 'Todas' ? 'Todas' : opt}
            </option>
          ))}
        </select>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>de {totalItems} registros</span>
      </div>
      {pageSize !== 'all' && totalPages > 1 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button onClick={() => onPageChange(currentPage - 1)} disabled={currentPage === 1} style={{ background: currentPage === 1 ? 'var(--glass)' : 'var(--color-bg-elevated)', border: '1px solid var(--glass-border)', borderRadius: '6px', padding: '0.5rem 0.75rem', color: currentPage === 1 ? 'var(--text-subtle)' : 'var(--text-main)', cursor: currentPage === 1 ? 'not-allowed' : 'pointer', fontSize: '0.85rem' }}>← Anterior</button>
          <div style={{ display: 'flex', gap: '0.25rem' }}>
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum;
              if (totalPages <= 5) pageNum = i + 1;
              else if (currentPage <= 3) pageNum = i + 1;
              else if (currentPage >= totalPages - 2) pageNum = totalPages - 4 + i;
              else pageNum = currentPage - 2 + i;
              return (
                <button key={pageNum} onClick={() => onPageChange(pageNum)} style={{ background: currentPage === pageNum ? 'var(--primary)' : 'var(--color-bg-elevated)', border: '1px solid var(--glass-border)', borderRadius: '6px', padding: '0.5rem 0.75rem', color: currentPage === pageNum ? 'white' : 'var(--text-main)', cursor: 'pointer', fontSize: '0.85rem', minWidth: '36px' }}>
                  {pageNum}
                </button>
              );
            })}
          </div>
          <button onClick={() => onPageChange(currentPage + 1)} disabled={currentPage === totalPages} style={{ background: currentPage === totalPages ? 'var(--glass)' : 'var(--color-bg-elevated)', border: '1px solid var(--glass-border)', borderRadius: '6px', padding: '0.5rem 0.75rem', color: currentPage === totalPages ? 'var(--text-subtle)' : 'var(--text-main)', cursor: currentPage === totalPages ? 'not-allowed' : 'pointer', fontSize: '0.85rem' }}>Siguiente →</button>
        </div>
      )}
    </div>
  );
};

// ─── ControlsView ─────────────────────────────────────────────────────────────
const ControlsView = ({ controls, stats, loading }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);
  const [searchTerm, setSearchTerm] = useState('');

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'compliant': return 'var(--success)';
      case 'en_proceso': return 'var(--warning)';
      case 'non_compliant': return 'var(--danger)';
      default: return 'var(--text-muted)';
    }
  };

  const getStatusLabel = (status) => {
    switch (status?.toLowerCase()) {
      case 'compliant': return 'Cumple';
      case 'en_proceso': return 'En Proceso';
      case 'non_compliant': return 'No Cumple';
      default: return status;
    }
  };

  const filteredControls = controls.filter(c =>
    c.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.iso_control_ref?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.iso_domain?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalItems = filteredControls.length;
  const totalPages = pageSize === 'all' ? 1 : Math.ceil(totalItems / pageSize);
  const paginatedControls = pageSize === 'all' ? filteredControls : filteredControls.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  return (
    <div className="animate-fade-in">
      <div className="kpi-grid" style={{ marginBottom: '2rem' }}>
        <KPICard title="Cumplimiento Global" value={stats?.global_compliance_pct || 0} unit="%" status={stats?.global_compliance_pct > 80 ? 'green' : stats?.global_compliance_pct > 50 ? 'amber' : 'red'} description="Alineación normativa" />
        <KPICard title="Controles Totales" value={stats?.total_controls || 0} unit="und." status="primary" description="Inventario de controles" />
        <KPICard title="No Cumplimiento" value={stats?.non_compliant || 0} unit="cont." status="red" description="Brechas críticas" />
      </div>
      <div className="glass-card" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', margin: 0 }}>
            <ShieldCheck size={20} color="var(--primary)" />
            Matriz de Controles
          </h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--color-bg-elevated)', borderRadius: '8px', padding: '0.5rem 1rem', border: '1px solid var(--glass-border)' }}>
              <Search size={16} color="var(--text-muted)" />
              <input type="text" placeholder="Buscar control..." value={searchTerm} onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }} style={{ background: 'none', border: 'none', color: 'var(--text-main)', outline: 'none', width: '180px', fontSize: '0.9rem' }} />
            </div>
            <button className="glass-card" style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-main)', cursor: 'pointer', fontSize: '0.85rem', border: '1px solid var(--glass-border)' }}>
              <Download size={16} />Exportar
            </button>
          </div>
        </div>
        <div className="table-responsive">
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '700px' }}>
            <thead>
              <tr style={{ background: 'var(--glass)', textAlign: 'left', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                <th style={{ padding: '1rem' }}>ESTADO</th>
                <th style={{ padding: '1rem' }}>REF & NOMBRE</th>
                <th style={{ padding: '1.25rem' }}>DOMINIO</th>
                <th style={{ padding: '1.25rem' }}>CUMPLIMIENTO</th>
                <th style={{ padding: '1.25rem' }}>RESPONSABLE</th>
              </tr>
            </thead>
            <tbody>
              {paginatedControls.map((control) => (
                <tr key={control.id} style={{ borderTop: '1px solid var(--glass-border)', transition: 'background 0.2s' }} className="table-row-hover">
                  <td style={{ padding: '1.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: getStatusColor(control.status) }}></div>
                      <span style={{ fontSize: '0.9rem' }}>{getStatusLabel(control.status)}</span>
                    </div>
                  </td>
                  <td style={{ padding: '1.25rem' }}>
                    <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>{control.iso_control_ref} - {control.name}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{control.description?.substring(0, 60)}...</div>
                  </td>
                  <td style={{ padding: '1.25rem', fontSize: '0.9rem' }}>{control.iso_domain}</td>
                  <td style={{ padding: '1.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div style={{ width: '60px', height: '6px', backgroundColor: 'var(--glass-border)', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ width: `${control.compliance_pct}%`, height: '100%', backgroundColor: getStatusColor(control.status) }}></div>
                      </div>
                      <span style={{ fontSize: '0.85rem', fontWeight: 'bold' }}>{control.compliance_pct}%</span>
                    </div>
                  </td>
                  <td style={{ padding: '1.25rem', fontSize: '0.9rem' }}>{control.responsible}</td>
                </tr>
              ))}
              {paginatedControls.length === 0 && !loading && (
                <tr><td colSpan="5" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>{searchTerm ? 'No se encontraron controles con ese criterio.' : 'No se encontraron controles registrados.'}</td></tr>
              )}
            </tbody>
          </table>
        </div>
        <Pagination currentPage={currentPage} totalPages={totalPages} pageSize={pageSize} onPageChange={setCurrentPage} onPageSizeChange={(s) => { setPageSize(s); setCurrentPage(1); }} totalItems={totalItems} />
      </div>
    </div>
  );
};

// ─── IncidentsView ────────────────────────────────────────────────────────────
const IncidentsView = ({ incidents, stats, loading }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);
  const [searchTerm, setSearchTerm] = useState('');

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'open': return 'var(--danger)';
      case 'in_progress': return 'var(--warning)';
      case 'resolved': case 'closed': return 'var(--success)';
      default: return 'var(--text-muted)';
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

  const filteredIncidents = incidents.filter(i =>
    i.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    i.id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    i.category?.toLowerCase().includes(searchTerm.toLowerCase())
  );
  const totalItems = filteredIncidents.length;
  const totalPages = pageSize === 'all' ? 1 : Math.ceil(totalItems / pageSize);
  const paginatedIncidents = pageSize === 'all' ? filteredIncidents : filteredIncidents.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  return (
    <div className="animate-fade-in">
      <div className="kpi-grid" style={{ marginBottom: '2rem' }}>
        <KPICard title="Total Incidentes" value={stats?.total || 0} unit="inc." status="amber" description="Histórico acumulado" />
        <KPICard title="Tasa Resolución" value={stats?.resolution_rate_pct || 0} unit="%" status="green" description="Efectividad de cierre" />
        <KPICard title="MTTR Promedio" value={stats?.avg_resolution_hrs || 0} unit="hrs" status="primary" description="Tiempo medio de respuesta" />
      </div>
      <div className="glass-card" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', margin: 0 }}>
            <ShieldAlert size={20} color="var(--warning)" />
            Registro de Incidentes
          </h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--color-bg-elevated)', borderRadius: '8px', padding: '0.5rem 1rem', border: '1px solid var(--glass-border)' }}>
              <Search size={16} color="var(--text-muted)" />
              <input type="text" placeholder="Buscar incidente..." value={searchTerm} onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }} style={{ background: 'none', border: 'none', color: 'var(--text-main)', outline: 'none', width: '180px', fontSize: '0.9rem' }} />
            </div>
            <button className="glass-card" style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-main)', cursor: 'pointer', fontSize: '0.85rem', border: '1px solid var(--glass-border)' }}>
              <Plus size={16} />Nuevo
            </button>
          </div>
        </div>
        <div className="table-responsive">
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '650px' }}>
            <thead>
              <tr style={{ background: 'var(--glass)', textAlign: 'left', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                <th style={{ padding: '1rem' }}>ESTADO</th>
                <th style={{ padding: '1rem' }}>ID & TÍTULO</th>
                <th style={{ padding: '1.25rem' }}>CATEGORÍA</th>
                <th style={{ padding: '1.25rem' }}>SEVERIDAD</th>
                <th style={{ padding: '1.25rem' }}>FECHA REPORTE</th>
              </tr>
            </thead>
            <tbody>
              {paginatedIncidents.map((incident) => (
                <tr key={incident.id} style={{ borderTop: '1px solid var(--glass-border)', transition: 'background 0.2s' }} className="table-row-hover">
                  <td style={{ padding: '1.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: getStatusColor(incident.status) }}></div>
                      <span style={{ fontSize: '0.9rem', textTransform: 'capitalize' }}>{incident.status?.replace('_', ' ')}</span>
                    </div>
                  </td>
                  <td style={{ padding: '1.25rem' }}>
                    <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>{incident.title}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>{incident.id?.slice(0, 8)}...</div>
                  </td>
                  <td style={{ padding: '1.25rem', fontSize: '0.9rem' }}>{incident.category || 'N/A'}</td>
                  <td style={{ padding: '1.25rem' }}>
                    <span style={{ fontSize: '0.8rem', padding: '0.25rem 0.6rem', background: 'var(--glass)', borderRadius: '4px', ...getSeverityStyle(incident.severity) }}>
                      {incident.severity?.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ padding: '1.25rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>{new Date(incident.reported_at).toLocaleDateString()}</td>
                </tr>
              ))}
              {paginatedIncidents.length === 0 && !loading && (
                <tr><td colSpan="5" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>{searchTerm ? 'No se encontraron incidentes con ese criterio.' : 'No se encontraron incidentes registrados.'}</td></tr>
              )}
            </tbody>
          </table>
        </div>
        <Pagination currentPage={currentPage} totalPages={totalPages} pageSize={pageSize} onPageChange={setCurrentPage} onPageSizeChange={(s) => { setPageSize(s); setCurrentPage(1); }} totalItems={totalItems} />
      </div>
    </div>
  );
};

// ─── RiskView ─────────────────────────────────────────────────────────────────
const RiskView = ({ riskCurrent, riskDomains, loading }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);

  const domains = riskDomains?.domains || [];
  const totalItems = domains.length;
  const totalPages = pageSize === 'all' ? 1 : Math.ceil(totalItems / pageSize);
  const paginatedDomains = pageSize === 'all' ? domains : domains.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const getLevelColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'critical': return 'var(--danger)';
      case 'high': return '#fb923c';
      case 'medium': return 'var(--warning)';
      case 'low': return 'var(--success)';
      default: return 'var(--text-muted)';
    }
  };

  const getLevelBg = (level) => {
    switch (level?.toLowerCase()) {
      case 'critical': return 'rgba(239, 68, 68, 0.15)';
      case 'high': return 'rgba(251, 146, 60, 0.15)';
      case 'medium': return 'rgba(234, 179, 8, 0.15)';
      case 'low': return 'rgba(34, 197, 94, 0.15)';
      default: return 'var(--glass)';
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="kpi-grid" style={{ marginBottom: '2rem' }}>
        <KPICard title="Score Global de Riesgo" value={riskCurrent?.global_score || 0} unit="pts" status={riskCurrent?.global_level === 'critical' ? 'red' : riskCurrent?.global_level === 'high' ? 'amber' : 'green'} description="Promedio ponderado de todos los dominios" />
        <KPICard title="Nivel de Riesgo" value={riskCurrent?.global_level?.toUpperCase() || 'N/A'} unit="" status={riskCurrent?.global_level === 'critical' ? 'red' : riskCurrent?.global_level === 'high' ? 'amber' : 'green'} description="Clasificación general del SGSI" />
        <KPICard title="Dominios Evaluados" value={riskCurrent?.total_domains || 0} unit="dom." status="primary" description="Áreas de riesgo monitoreadas" />
        <KPICard title="Dominio Más Crítico" value={riskCurrent?.highest_risk_domain || 'N/A'} unit="" status="red" description="Requiere atención prioritaria" />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
        {['critical', 'high', 'medium', 'low'].map((level) => (
          <div key={level} className="glass-card" style={{ padding: '1.5rem', borderLeft: `4px solid ${getLevelColor(level)}`, background: getLevelBg(level) }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Riesgo {level}</div>
            <div style={{ fontSize: '2rem', fontWeight: '800', color: getLevelColor(level) }}>{riskCurrent?.by_level?.[level] || 0}</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>dominios</div>
          </div>
        ))}
      </div>
      <div className="glass-card" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}><Activity size={20} color="var(--primary)" />Matriz de Riesgos por Dominio</h3>
          <button className="glass-card" style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-main)', cursor: 'pointer', fontSize: '0.85rem' }}>
            <Plus size={16} />Nueva Evaluación
          </button>
        </div>
        <div className="table-responsive">
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '700px' }}>
            <thead>
              <tr style={{ background: 'var(--glass)', textAlign: 'left', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                <th style={{ padding: '1rem' }}>DOMINIO</th>
                <th style={{ padding: '1rem' }}>NIVEL</th>
                <th style={{ padding: '1.25rem' }}>SCORE</th>
                <th style={{ padding: '1.25rem' }}>PROBABILIDAD</th>
                <th style={{ padding: '1.25rem' }}>IMPACTO</th>
                <th style={{ padding: '1.25rem' }}>ÚLTIMA EVALUACIÓN</th>
              </tr>
            </thead>
            <tbody>
              {paginatedDomains.map((risk, index) => (
                <tr key={index} style={{ borderTop: '1px solid var(--glass-border)', transition: 'background 0.2s' }} className="table-row-hover">
                  <td style={{ padding: '1.25rem' }}><div style={{ fontWeight: '600' }}>{risk.domain}</div></td>
                  <td style={{ padding: '1.25rem' }}>
                    <span style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem', background: getLevelBg(risk.level), color: getLevelColor(risk.level), borderRadius: '4px', fontWeight: 'bold', textTransform: 'uppercase' }}>{risk.level}</span>
                  </td>
                  <td style={{ padding: '1.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div style={{ width: '50px', height: '6px', backgroundColor: 'var(--glass-border)', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ width: `${(risk.score / 25) * 100}%`, height: '100%', backgroundColor: getLevelColor(risk.level) }}></div>
                      </div>
                      <span style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>{risk.score}</span>
                    </div>
                  </td>
                  <td style={{ padding: '1.25rem', textAlign: 'center' }}><span style={{ display: 'inline-block', width: '28px', height: '28px', lineHeight: '28px', textAlign: 'center', borderRadius: '50%', background: 'var(--color-bg-elevated)', fontWeight: 'bold', fontSize: '0.85rem' }}>{risk.probability}</span></td>
                  <td style={{ padding: '1.25rem', textAlign: 'center' }}><span style={{ display: 'inline-block', width: '28px', height: '28px', lineHeight: '28px', textAlign: 'center', borderRadius: '50%', background: 'var(--color-bg-elevated)', fontWeight: 'bold', fontSize: '0.85rem' }}>{risk.impact}</span></td>
                  <td style={{ padding: '1.25rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>{new Date(risk.recorded_at).toLocaleDateString()}</td>
                </tr>
              ))}
              {paginatedDomains.length === 0 && !loading && (
                <tr><td colSpan="6" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>No hay evaluaciones de riesgo registradas.</td></tr>
              )}
            </tbody>
          </table>
        </div>
        <Pagination currentPage={currentPage} totalPages={totalPages} pageSize={pageSize} onPageChange={setCurrentPage} onPageSizeChange={(s) => { setPageSize(s); setCurrentPage(1); }} totalItems={totalItems} />
      </div>
    </div>
  );
};

// ─── HistoryView ──────────────────────────────────────────────────────────────
const HistoryView = ({ snapshots, loading }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);
  const snapshotList = snapshots || [];
  const totalItems = snapshotList.length;
  const totalPages = pageSize === 'all' ? 1 : Math.ceil(totalItems / pageSize);
  const paginatedSnapshots = pageSize === 'all' ? snapshotList : snapshotList.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  return (
    <div className="animate-fade-in">
      <div className="kpi-grid" style={{ marginBottom: '2rem' }}>
        <KPICard title="Total Snapshots" value={snapshotList.length} unit="reg." status="primary" description="Capturas de estado guardadas" />
        <KPICard title="Último Snapshot" value={snapshotList[0] ? new Date(snapshotList[0].created_at).toLocaleDateString() : 'N/A'} unit="" status="green" description="Fecha de última captura" />
      </div>
      <div className="glass-card" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', margin: 0 }}><History size={20} color="var(--primary)" />Historial de Snapshots del SGSI</h3>
          <button className="glass-card" style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-main)', cursor: 'pointer', fontSize: '0.85rem' }}>
            <Plus size={16} />Crear Snapshot
          </button>
        </div>
        <div className="table-responsive">
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '650px' }}>
            <thead>
              <tr style={{ background: 'var(--glass)', textAlign: 'left', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                <th style={{ padding: '1rem' }}>FECHA</th>
                <th style={{ padding: '1rem' }}>CUMPLIMIENTO</th>
                <th style={{ padding: '1.25rem' }}>INCIDENTES ABIERTOS</th>
                <th style={{ padding: '1.25rem' }}>SCORE RIESGO</th>
                <th style={{ padding: '1.25rem' }}>CONTROLES ACTIVOS</th>
              </tr>
            </thead>
            <tbody>
              {paginatedSnapshots.map((snapshot, index) => (
                <tr key={snapshot.id || index} style={{ borderTop: '1px solid var(--glass-border)', transition: 'background 0.2s' }} className="table-row-hover">
                  <td style={{ padding: '1.25rem' }}>
                    <div style={{ fontWeight: '600', color: 'var(--text-main)' }}>{new Date(snapshot.created_at).toLocaleDateString()}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{new Date(snapshot.created_at).toLocaleTimeString()}</div>
                  </td>
                  <td style={{ padding: '1.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div style={{ width: '60px', height: '6px', backgroundColor: 'var(--glass-border)', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ width: `${snapshot.compliance_pct || 0}%`, height: '100%', backgroundColor: snapshot.compliance_pct > 80 ? 'var(--success)' : snapshot.compliance_pct > 50 ? 'var(--warning)' : 'var(--danger)' }}></div>
                      </div>
                      <span style={{ fontWeight: 'bold', fontSize: '0.9rem', color: 'var(--text-main)' }}>{snapshot.compliance_pct?.toFixed(1) || 0}%</span>
                    </div>
                  </td>
                  <td style={{ padding: '1.25rem', textAlign: 'center' }}>
                    <span style={{ display: 'inline-block', padding: '0.25rem 0.75rem', borderRadius: '12px', background: snapshot.open_incidents > 5 ? 'rgba(220, 38, 38, 0.1)' : 'rgba(22, 163, 74, 0.1)', color: snapshot.open_incidents > 5 ? 'var(--danger)' : 'var(--success)', fontWeight: 'bold', fontSize: '0.85rem' }}>{snapshot.open_incidents || 0}</span>
                  </td>
                  <td style={{ padding: '1.25rem', textAlign: 'center' }}><span style={{ fontWeight: 'bold', fontSize: '0.9rem', color: 'var(--text-main)' }}>{snapshot.risk_score?.toFixed(1) || 0}</span></td>
                  <td style={{ padding: '1.25rem', textAlign: 'center' }}><span style={{ fontWeight: 'bold', fontSize: '0.9rem', color: 'var(--text-main)' }}>{snapshot.active_controls || 0}</span></td>
                </tr>
              ))}
              {paginatedSnapshots.length === 0 && !loading && (
                <tr><td colSpan="5" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>No hay snapshots registrados.</td></tr>
              )}
            </tbody>
          </table>
        </div>
        <Pagination currentPage={currentPage} totalPages={totalPages} pageSize={pageSize} onPageChange={setCurrentPage} onPageSizeChange={(s) => { setPageSize(s); setCurrentPage(1); }} totalItems={totalItems} />
      </div>
    </div>
  );
};

// ─── EmpresasView ─────────────────────────────────────────────────────────────
const EmpresasView = ({ empresas, loading, userRole, onRefresh }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);
  const [searchTerm, setSearchTerm] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ nombre: '', tipo_empresa: '', actividad_economica: '', representante_legal: '', email: '', telefono: '', nit: '', direccion: '' });
  const [saving, setSaving] = useState(false);

  const TIPO_OPTIONS = ['SAS', 'SA', 'Ltda', 'Persona Natural', 'SRL', 'Cooperativa', 'ONG', 'Empresa Pública'];
  const ACTIVIDAD_OPTIONS = ['Salud / Clínica', 'Alimentos / Bebidas', 'Tecnología / Software', 'Financiero / Bancario', 'Comercio', 'Manufactura', 'Educación', 'Transporte / Logística', 'Construcción', 'Servicios Profesionales', 'Otro'];

  const filtered = empresas.filter(e =>
    e.nombre?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    e.actividad_economica?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    e.nit?.toLowerCase().includes(searchTerm.toLowerCase())
  );
  const totalItems = filtered.length;
  const totalPages = pageSize === 'all' ? 1 : Math.ceil(totalItems / pageSize);
  const paginated = pageSize === 'all' ? filtered : filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await empresaApi.create(formData);
      setShowForm(false);
      setFormData({ nombre: '', tipo_empresa: '', actividad_economica: '', representante_legal: '', email: '', telefono: '', nit: '', direccion: '' });
      onRefresh();
    } catch (err) {
      alert('Error al guardar la empresa.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="kpi-grid" style={{ marginBottom: '2rem' }}>
        <KPICard title="Empresas Registradas" value={empresas.length} unit="" status="primary" description="Clientes activos en el sistema" />
      </div>

      <div className="glass-card" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', margin: 0 }}>
            <Building2 size={20} color="var(--primary)" />
            Directorio de Empresas
          </h3>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--color-bg-elevated)', borderRadius: '8px', padding: '0.5rem 1rem', border: '1px solid var(--glass-border)' }}>
              <Search size={16} color="var(--text-muted)" />
              <input type="text" placeholder="Buscar empresa..." value={searchTerm} onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }} style={{ background: 'none', border: 'none', color: 'var(--text-main)', outline: 'none', width: '180px', fontSize: '0.9rem' }} />
            </div>
            {userRole === 'admin' && (
              <button
                onClick={() => setShowForm(!showForm)}
                className="glass-card"
                style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary)', cursor: 'pointer', fontSize: '0.85rem', border: '1px solid var(--primary)' }}
              >
                <Plus size={16} />{showForm ? 'Cancelar' : 'Nueva Empresa'}
              </button>
            )}
          </div>
        </div>

        {showForm && (
          <form onSubmit={handleSubmit} style={{ padding: '1.5rem', borderBottom: '1px solid var(--glass-border)', background: 'var(--color-bg-elevated)' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
              {[
                { key: 'nombre', label: 'Nombre de la empresa *', type: 'text', required: true },
                { key: 'representante_legal', label: 'Representante legal *', type: 'text', required: true },
                { key: 'nit', label: 'NIT / RUT', type: 'text' },
                { key: 'email', label: 'Email', type: 'email' },
                { key: 'telefono', label: 'Teléfono', type: 'text' },
                { key: 'direccion', label: 'Dirección', type: 'text' },
              ].map(({ key, label, type, required }) => (
                <div key={key}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>{label}</label>
                  <input
                    type={type}
                    required={required}
                    value={formData[key]}
                    onChange={(e) => setFormData({ ...formData, [key]: e.target.value })}
                    style={{ width: '100%', padding: '0.6rem 0.75rem', background: 'var(--color-bg-card)', border: '1px solid var(--glass-border)', borderRadius: '6px', color: 'var(--text-main)', fontSize: '0.9rem', outline: 'none', boxSizing: 'border-box' }}
                  />
                </div>
              ))}
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>Tipo de empresa *</label>
                <select required value={formData.tipo_empresa} onChange={(e) => setFormData({ ...formData, tipo_empresa: e.target.value })} style={{ width: '100%', padding: '0.6rem 0.75rem', background: 'var(--color-bg-card)', border: '1px solid var(--glass-border)', borderRadius: '6px', color: 'var(--text-main)', fontSize: '0.9rem', outline: 'none' }}>
                  <option value="">Seleccionar...</option>
                  {TIPO_OPTIONS.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>Actividad económica *</label>
                <select required value={formData.actividad_economica} onChange={(e) => setFormData({ ...formData, actividad_economica: e.target.value })} style={{ width: '100%', padding: '0.6rem 0.75rem', background: 'var(--color-bg-card)', border: '1px solid var(--glass-border)', borderRadius: '6px', color: 'var(--text-main)', fontSize: '0.9rem', outline: 'none' }}>
                  <option value="">Seleccionar...</option>
                  {ACTIVIDAD_OPTIONS.map(a => <option key={a} value={a}>{a}</option>)}
                </select>
              </div>
            </div>
            <div style={{ marginTop: '1rem', display: 'flex', gap: '0.75rem' }}>
              <button type="submit" disabled={saving} style={{ padding: '0.6rem 1.5rem', background: 'var(--primary)', border: 'none', borderRadius: '6px', color: 'white', fontWeight: '600', cursor: saving ? 'not-allowed' : 'pointer', opacity: saving ? 0.7 : 1 }}>
                {saving ? 'Guardando...' : 'Guardar Empresa'}
              </button>
              <button type="button" onClick={() => setShowForm(false)} style={{ padding: '0.6rem 1.5rem', background: 'var(--glass)', border: '1px solid var(--glass-border)', borderRadius: '6px', color: 'var(--text-main)', cursor: 'pointer' }}>Cancelar</button>
            </div>
          </form>
        )}

        <div className="table-responsive">
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '700px' }}>
            <thead>
              <tr style={{ background: 'var(--glass)', textAlign: 'left', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                <th style={{ padding: '1rem' }}>NOMBRE</th>
                <th style={{ padding: '1rem' }}>TIPO</th>
                <th style={{ padding: '1.25rem' }}>ACTIVIDAD ECONÓMICA</th>
                <th style={{ padding: '1.25rem' }}>REPRESENTANTE LEGAL</th>
                <th style={{ padding: '1.25rem' }}>CONTACTO</th>
              </tr>
            </thead>
            <tbody>
              {paginated.map((empresa) => (
                <tr key={empresa.id} style={{ borderTop: '1px solid var(--glass-border)', transition: 'background 0.2s' }} className="table-row-hover">
                  <td style={{ padding: '1.25rem' }}>
                    <div style={{ fontWeight: '600' }}>{empresa.nombre}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>NIT: {empresa.nit || '—'}</div>
                  </td>
                  <td style={{ padding: '1.25rem' }}>
                    <span style={{ fontSize: '0.8rem', padding: '0.25rem 0.6rem', background: 'var(--glass)', borderRadius: '4px', color: 'var(--primary)' }}>{empresa.tipo_empresa}</span>
                  </td>
                  <td style={{ padding: '1.25rem', fontSize: '0.9rem' }}>{empresa.actividad_economica}</td>
                  <td style={{ padding: '1.25rem', fontSize: '0.9rem' }}>{empresa.representante_legal}</td>
                  <td style={{ padding: '1.25rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    <div>{empresa.email || '—'}</div>
                    <div>{empresa.telefono || '—'}</div>
                  </td>
                </tr>
              ))}
              {paginated.length === 0 && !loading && (
                <tr><td colSpan="5" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>{searchTerm ? 'No se encontraron empresas.' : 'No hay empresas registradas aún.'}</td></tr>
              )}
            </tbody>
          </table>
        </div>
        <Pagination currentPage={currentPage} totalPages={totalPages} pageSize={pageSize} onPageChange={setCurrentPage} onPageSizeChange={(s) => { setPageSize(s); setCurrentPage(1); }} totalItems={totalItems} />
      </div>
    </div>
  );
};

// ─── Main App Component ───────────────────────────────────────────────────────
function App() {
  // Auth state
  const [authToken, setAuthToken] = useState(() => localStorage.getItem('iso_token'));
  const [userProfile, setUserProfile] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  // UI state
  const [view, setView] = useState('dashboard');
  const [theme, setTheme] = useState('light');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  // Data state
  const [summary, setSummary] = useState(null);
  const [kpis, setKpis] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [incidentStats, setIncidentStats] = useState(null);
  const [controls, setControls] = useState([]);
  const [complianceStats, setComplianceStats] = useState(null);
  const [riskCurrent, setRiskCurrent] = useState(null);
  const [riskDomains, setRiskDomains] = useState(null);
  const [snapshots, setSnapshots] = useState([]);
  const [empresas, setEmpresas] = useState([]);

  // Inject token in every api request
  useEffect(() => {
    if (authToken) {
      api.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
    } else {
      delete api.defaults.headers.common['Authorization'];
    }
  }, [authToken]);

  // Validate token on mount
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    const validateToken = async () => {
      if (!authToken) { setAuthLoading(false); return; }
      try {
        const profile = await axios.get('/api/v1/auth/me', {
          headers: { Authorization: `Bearer ${authToken}` }
        }).then(r => r.data);
        setUserProfile(profile);
      } catch {
        handleLogout();
      } finally {
        setAuthLoading(false);
      }
    };
    validateToken();
  }, []);

  const handleLogin = (token, profile) => {
    localStorage.setItem('iso_token', token);
    setAuthToken(token);
    setUserProfile(profile);
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  };

  const handleLogout = () => {
    localStorage.removeItem('iso_token');
    setAuthToken(null);
    setUserProfile(null);
    delete api.defaults.headers.common['Authorization'];
  };

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  const exportReport = async () => {
    try {
      const reportData = {
        filename: `Reporte_SGSI_${new Date().toISOString().split('T')[0]}.pdf`,
        generated_at: new Date().toISOString(),
        view, summary, kpis, incidents, incident_stats: incidentStats,
        controls, compliance_stats: complianceStats,
        risk_current: riskCurrent, risk_domains: riskDomains, snapshots
      };
      const response = await fetch('https://n8n.agustinynatalia.site/webhook/bcc86df1-874b-4314-80ea-b4da42acb961', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reportData)
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = reportData.filename;
        document.body.appendChild(a); a.click();
        window.URL.revokeObjectURL(url); a.remove();
      } else {
        alert('Error al generar el reporte. Intente nuevamente.');
      }
    } catch {
      alert('Error al conectar con el servicio de reportes.');
    }
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      if (view === 'dashboard') {
        const [sumData, kpiData] = await Promise.all([dashboardApi.getSummary(), dashboardApi.getKpis()]);
        setSummary(sumData); setKpis(kpiData.kpis);
      } else if (view === 'incidents') {
        const [list, st] = await Promise.all([dashboardApi.getIncidents({ limit: 50 }), dashboardApi.getIncidentStats()]);
        setIncidents(list.items); setIncidentStats(st);
      } else if (view === 'controls') {
        const [list, cp] = await Promise.all([dashboardApi.getControls({ limit: 50 }), dashboardApi.getCompliance()]);
        setControls(list.items); setComplianceStats(cp);
      } else if (view === 'risk') {
        const [current, domains] = await Promise.all([dashboardApi.getRiskCurrent(), dashboardApi.getRiskByDomain()]);
        setRiskCurrent(current); setRiskDomains(domains);
      } else if (view === 'history') {
        const data = await dashboardApi.getSnapshots({ limit: 50 });
        setSnapshots(data.items || data);
      } else if (view === 'empresas') {
        const data = await api.get('/empresas/').then(r => r.data);
        setEmpresas(data.items || []);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (authToken && userProfile) fetchData();
  }, [view, authToken, userProfile]);

  const chartOptions = {
    responsive: true,
    plugins: { legend: { display: false }, tooltip: { backgroundColor: 'rgba(15, 23, 42, 0.9)', titleFont: { family: 'Outfit', size: 14 }, bodyFont: { family: 'Outfit', size: 13 }, padding: 12, cornerRadius: 8 } },
    scales: { y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } }, x: { grid: { display: false }, ticks: { color: '#94a3b8' } } }
  };
  const dummyChartData = {
    labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
    datasets: [{ label: 'Cumplimiento %', data: [65, 72, 68, 75, 82, 88], borderColor: '#00d2ff', backgroundColor: 'rgba(0, 210, 255, 0.1)', fill: true, tension: 0.4 }]
  };

  const renderDashboard = () => (
    <div className="animate-fade-in">
      <div className="kpi-grid">
        {kpis.map((kpi, index) => (
          <KPICard key={index} title={kpi.name} value={kpi.value} unit={kpi.unit} status={kpi.status} description={kpi.description} />
        ))}
      </div>
      <div className="dashboard-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1rem' }}>
            <Activity size={18} color="var(--primary)" />
            Evolución de Cumplimiento Global
          </h3>
          <Line data={dummyChartData} options={chartOptions} height={100} />
        </div>
        <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1rem' }}>
            <ShieldAlert size={18} color="var(--danger)" />
            Dominio Más Crítico
          </h3>
          <div style={{ fontSize: '1.5rem', fontWeight: '700', fontFamily: 'var(--font-serif)', color: 'var(--text-main)', marginBottom: '0.5rem' }}>
            {summary?.risk_highest_domain || 'Sin datos'}
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>Área con mayor exposición al riesgo según la última evaluación</p>
        </div>
      </div>
      <div className="glass-card" style={{ padding: '1.5rem', overflow: 'hidden' }}>
        <h3 style={{ marginBottom: '1rem' }}>Últimos Incidentes Detectados</h3>
        <div className="table-responsive">
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '400px' }}>
            <thead>
              <tr style={{ textAlign: 'left', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                <th style={{ padding: '0.75rem' }}>ESTADO</th>
                <th style={{ padding: '0.75rem' }}>TÍTULO</th>
                <th style={{ padding: '0.75rem' }}>SEVERIDAD</th>
                <th style={{ padding: '0.75rem' }}>FECHA</th>
              </tr>
            </thead>
            <tbody>
              {summary?.active_incidents?.length > 0 ? (
                summary.active_incidents.map(inc => (
                  <tr key={inc.id} style={{ borderTop: '1px solid var(--glass-border)' }}>
                    <td style={{ padding: '1rem' }}><span className="status-dot status-amber"></span> {inc.status}</td>
                    <td style={{ padding: '1rem', color: 'var(--text-main)' }}>{inc.title}</td>
                    <td style={{ padding: '1rem' }}><span style={{ color: inc.severity === 'critical' ? 'var(--danger)' : 'var(--warning)' }}>{inc.severity?.toUpperCase()}</span></td>
                    <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>{new Date(inc.reported_at).toLocaleDateString()}</td>
                  </tr>
                ))
              ) : (
                <tr><td colSpan="4" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No hay incidentes activos en este momento.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  // ── Loading splash while validating token ──
  if (authLoading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-bg)' }}>
        <Activity size={40} color="var(--primary)" className="animate-pulse" />
      </div>
    );
  }

  // ── Show login if not authenticated ──
  if (!authToken || !userProfile) {
    return <LoginPage onLogin={handleLogin} />;
  }

  // ── Main dashboard ──
  return (
    <div className="dashboard-container">
      <div className="mobile-header">
        <button className="mobile-menu-btn" onClick={() => setSidebarOpen(true)}><Menu size={24} /></button>
        <div className="mobile-logo"><ShieldCheck size={24} /><span>ISO Secure</span></div>
        <button className="mobile-menu-btn" onClick={toggleTheme}>{theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}</button>
      </div>
      <div className={`sidebar-overlay ${sidebarOpen ? 'open' : ''}`} onClick={() => setSidebarOpen(false)} />
      <Sidebar
        currentView={view}
        setView={setView}
        theme={theme}
        toggleTheme={toggleTheme}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        userRole={userProfile?.role}
        userEmail={userProfile?.email}
        onLogout={handleLogout}
      />
      <main className="main-content">
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '2.2rem', marginBottom: '0.5rem' }}>{viewTitles[view] || view}</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Plataforma de Gestión ISO_SECURE</p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button className="glass-card" style={{ padding: '0.75rem', color: 'var(--text-main)', cursor: 'pointer' }} onClick={fetchData}>
              <RefreshCcw size={20} className={loading ? 'animate-spin' : ''} />
            </button>
            <button className="glass-card desktop-only" style={{ padding: '0.75rem 1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-main)', cursor: 'pointer' }} onClick={exportReport}>
              <Download size={20} /><span>Exportar Reporte</span>
            </button>
          </div>
        </header>

        {loading && !summary && view === 'dashboard' ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '5rem' }}>
            <Activity className="animate-pulse" size={48} color="var(--primary)" />
          </div>
        ) : (
          <AnimatePresence mode="wait">
            <motion.div key={view} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} transition={{ duration: 0.2 }}>
              {view === 'dashboard' && renderDashboard()}
              {view === 'incidents' && <IncidentsView incidents={incidents} stats={incidentStats} loading={loading} />}
              {view === 'controls' && <ControlsView controls={controls} stats={complianceStats} loading={loading} />}
              {view === 'risk' && <RiskView riskCurrent={riskCurrent} riskDomains={riskDomains} loading={loading} />}
              {view === 'history' && <HistoryView snapshots={snapshots} loading={loading} />}
              {view === 'empresas' && <EmpresasView empresas={empresas} loading={loading} userRole={userProfile?.role} onRefresh={fetchData} />}
            </motion.div>
          </AnimatePresence>
        )}
      </main>
    </div>
  );
}

export default App;
