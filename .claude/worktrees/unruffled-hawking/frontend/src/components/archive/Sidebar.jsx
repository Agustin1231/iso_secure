import React from 'react';
import { LayoutDashboard, ShieldAlert, ShieldCheck, Activity, History, LogOut } from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { icon: <LayoutDashboard size={20} />, label: 'Dashboard', active: true },
    { icon: <ShieldAlert size={20} />, label: 'Incidentes' },
    { icon: <ShieldCheck size={20} />, label: 'Controles ISO' },
    { icon: <Activity size={20} />, label: 'Riesgos' },
    { icon: <History size={20} />, label: 'Historial' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <ShieldCheck size={32} strokeWidth={2.5} />
        <span>ISO_SECURE</span>
      </div>
      
      <nav>
        {navItems.map((item, index) => (
          <a key={index} href="#" className={`nav-link ${item.active ? 'active' : ''}`}>
            {item.icon}
            <span>{item.label}</span>
          </a>
        ))}
      </nav>

      <div style={{ marginTop: 'auto', paddingTop: '2rem' }}>
        <a href="#" className="nav-link" style={{ color: 'var(--danger)' }}>
          <LogOut size={20} />
          <span>Cerrar Sesión</span>
        </a>
      </div>
    </aside>
  );
};

export default Sidebar;
