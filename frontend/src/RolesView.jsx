import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  ShieldCheck, KeyRound, Users, Plus, Trash2, X, Check,
  Save, Search, Lock, Layers, Pencil,
} from 'lucide-react';
import { rbacApi, authApi } from './api.js';

const ROLE_LABELS = {
  super_admin: 'Super Administrador', admin: 'Administrador',
  auditor: 'Auditor', supervisor: 'Supervisor', analista: 'Analista',
};
const ROLE_COLORS = {
  super_admin: '#a855f7', admin: 'var(--danger)', auditor: 'var(--primary)',
  supervisor: 'var(--warning)', analista: 'var(--success)',
};

const card = { background: 'var(--glass)', border: '1px solid var(--glass-border)', borderRadius: '12px' };
const inputStyle = {
  padding: '0.6rem 0.75rem', background: 'var(--color-bg-elevated)',
  border: '1px solid var(--glass-border)', borderRadius: '8px',
  color: 'var(--text-main)', fontSize: '0.85rem', outline: 'none', width: '100%',
};
const btnPrimary = {
  padding: '0.6rem 1.1rem', background: 'var(--primary)', border: 'none',
  borderRadius: '8px', color: 'white', fontWeight: 600, fontSize: '0.85rem',
  cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '0.4rem',
};

// ─── Panel de Permisos (super administradores) ────────────────────────────────
function PermisosPanel({ permissions, onCreate, onDelete }) {
  const [form, setForm] = useState({ codigo: '', nombre: '', modulo: '', descripcion: '' });
  const [saving, setSaving] = useState(false);

  const grouped = useMemo(() => {
    const g = {};
    permissions.forEach(p => { (g[p.modulo] = g[p.modulo] || []).push(p); });
    return g;
  }, [permissions]);

  const submit = async (e) => {
    e.preventDefault();
    if (!form.codigo.trim() || !form.nombre.trim()) return;
    setSaving(true);
    const ok = await onCreate({
      codigo: form.codigo.trim(),
      nombre: form.nombre.trim(),
      modulo: form.modulo.trim() || 'general',
      descripcion: form.descripcion.trim() || null,
    });
    setSaving(false);
    if (ok) setForm({ codigo: '', nombre: '', modulo: '', descripcion: '' });
  };

  return (
    <div className="animate-fade-in">
      <form onSubmit={submit} style={{ ...card, padding: '1.25rem', marginBottom: '1.5rem' }}>
        <h3 style={{ margin: '0 0 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1rem' }}>
          <Plus size={18} color="var(--primary)" /> Crear permiso
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem' }}>
          <input style={inputStyle} placeholder="Código (ej: incidents.manage)" value={form.codigo}
            onChange={e => setForm({ ...form, codigo: e.target.value })} />
          <input style={inputStyle} placeholder="Nombre" value={form.nombre}
            onChange={e => setForm({ ...form, nombre: e.target.value })} />
          <input style={inputStyle} placeholder="Módulo (ej: incidentes)" value={form.modulo}
            onChange={e => setForm({ ...form, modulo: e.target.value })} />
          <input style={inputStyle} placeholder="Descripción" value={form.descripcion}
            onChange={e => setForm({ ...form, descripcion: e.target.value })} />
        </div>
        <button type="submit" disabled={saving} style={{ ...btnPrimary, marginTop: '1rem', opacity: saving ? 0.6 : 1 }}>
          <Check size={16} /> {saving ? 'Guardando...' : 'Crear permiso'}
        </button>
      </form>

      {Object.keys(grouped).sort().map(modulo => (
        <div key={modulo} style={{ ...card, marginBottom: '1rem', overflow: 'hidden' }}>
          <div style={{ padding: '0.75rem 1.25rem', borderBottom: '1px solid var(--glass-border)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Layers size={15} color="var(--primary)" />
            <strong style={{ fontSize: '0.85rem', textTransform: 'capitalize' }}>{modulo}</strong>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>· {grouped[modulo].length} permisos</span>
          </div>
          {grouped[modulo].map(p => (
            <div key={p.id} style={{ padding: '0.85rem 1.25rem', borderTop: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
              <div style={{ minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                  <code style={{ fontSize: '0.78rem', background: 'var(--color-bg-elevated)', padding: '0.15rem 0.45rem', borderRadius: '5px', color: 'var(--primary)' }}>{p.codigo}</code>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{p.nombre}</span>
                </div>
                {p.descripcion && <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{p.descripcion}</div>}
              </div>
              <button onClick={() => onDelete(p)} title="Eliminar permiso"
                style={{ background: 'rgba(239,68,68,0.1)', border: 'none', borderRadius: '6px', padding: '0.4rem', cursor: 'pointer', color: 'var(--danger)' }}>
                <Trash2 size={15} />
              </button>
            </div>
          ))}
        </div>
      ))}
      {permissions.length === 0 && (
        <div style={{ ...card, padding: '2.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          No hay permisos registrados todavía.
        </div>
      )}
    </div>
  );
}

// ─── Editor de permisos de un rol (checkboxes agrupados) ──────────────────────
function PermissionPicker({ permissions, selected, onToggle }) {
  const grouped = useMemo(() => {
    const g = {};
    permissions.forEach(p => { (g[p.modulo] = g[p.modulo] || []).push(p); });
    return g;
  }, [permissions]);

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '1rem' }}>
      {Object.keys(grouped).sort().map(modulo => (
        <div key={modulo}>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>{modulo}</div>
          {grouped[modulo].map(p => {
            const on = selected.includes(p.id);
            return (
              <label key={p.id} title={p.descripcion || ''}
                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.35rem 0', cursor: 'pointer', fontSize: '0.82rem' }}>
                <input type="checkbox" checked={on} onChange={() => onToggle(p.id)} />
                <span style={{ color: on ? 'var(--text-main)' : 'var(--text-muted)' }}>{p.nombre}</span>
              </label>
            );
          })}
        </div>
      ))}
    </div>
  );
}

// ─── Panel de Roles (super administradores) ───────────────────────────────────
function RolesPanel({ roles, permissions, onCreate, onUpdate, onDelete }) {
  const [form, setForm] = useState({ nombre: '', descripcion: '', permission_ids: [] });
  const [saving, setSaving] = useState(false);
  const [editId, setEditId] = useState(null);
  const [editForm, setEditForm] = useState({ nombre: '', descripcion: '', permission_ids: [] });

  const toggle = (list, id) => list.includes(id) ? list.filter(x => x !== id) : [...list, id];

  const submit = async (e) => {
    e.preventDefault();
    if (!form.nombre.trim()) return;
    setSaving(true);
    const ok = await onCreate({
      nombre: form.nombre.trim(),
      descripcion: form.descripcion.trim() || null,
      permission_ids: form.permission_ids,
    });
    setSaving(false);
    if (ok) setForm({ nombre: '', descripcion: '', permission_ids: [] });
  };

  const startEdit = (role) => {
    setEditId(role.id);
    setEditForm({
      nombre: role.nombre,
      descripcion: role.descripcion || '',
      permission_ids: role.permissions.map(p => p.id),
    });
  };

  const saveEdit = async (role) => {
    await onUpdate(role.id, {
      nombre: editForm.nombre.trim(),
      descripcion: editForm.descripcion.trim() || null,
      permission_ids: editForm.permission_ids,
    });
    setEditId(null);
  };

  return (
    <div className="animate-fade-in">
      <form onSubmit={submit} style={{ ...card, padding: '1.25rem', marginBottom: '1.5rem' }}>
        <h3 style={{ margin: '0 0 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1rem' }}>
          <Plus size={18} color="var(--primary)" /> Crear rol
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.75rem', marginBottom: '1rem' }}>
          <input style={inputStyle} placeholder="Nombre del rol" value={form.nombre}
            onChange={e => setForm({ ...form, nombre: e.target.value })} />
          <input style={inputStyle} placeholder="Descripción" value={form.descripcion}
            onChange={e => setForm({ ...form, descripcion: e.target.value })} />
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.6rem' }}>Permisos del rol:</div>
        <PermissionPicker permissions={permissions} selected={form.permission_ids}
          onToggle={(id) => setForm({ ...form, permission_ids: toggle(form.permission_ids, id) })} />
        <button type="submit" disabled={saving} style={{ ...btnPrimary, marginTop: '1rem', opacity: saving ? 0.6 : 1 }}>
          <Check size={16} /> {saving ? 'Guardando...' : 'Crear rol'}
        </button>
      </form>

      {roles.map(role => (
        <div key={role.id} style={{ ...card, marginBottom: '1rem', padding: '1.25rem' }}>
          {editId === role.id ? (
            <div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.75rem', marginBottom: '1rem' }}>
                <input style={inputStyle} value={editForm.nombre}
                  onChange={e => setEditForm({ ...editForm, nombre: e.target.value })} />
                <input style={inputStyle} value={editForm.descripcion}
                  onChange={e => setEditForm({ ...editForm, descripcion: e.target.value })} />
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.6rem' }}>Permisos del rol:</div>
              <PermissionPicker permissions={permissions} selected={editForm.permission_ids}
                onToggle={(id) => setEditForm({ ...editForm, permission_ids: toggle(editForm.permission_ids, id) })} />
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                <button onClick={() => saveEdit(role)} style={btnPrimary}><Save size={15} /> Guardar</button>
                <button onClick={() => setEditId(null)}
                  style={{ padding: '0.6rem 1rem', background: 'var(--glass)', border: '1px solid var(--glass-border)', borderRadius: '8px', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.85rem' }}>
                  Cancelar
                </button>
              </div>
            </div>
          ) : (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', flexWrap: 'wrap' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    <ShieldCheck size={18} color="var(--primary)" />
                    <strong style={{ fontSize: '1rem' }}>{role.nombre}</strong>
                    {role.es_sistema && (
                      <span style={{ fontSize: '0.68rem', background: 'rgba(168,85,247,0.15)', color: '#a855f7', padding: '0.15rem 0.5rem', borderRadius: '20px', fontWeight: 600 }}>SISTEMA</span>
                    )}
                  </div>
                  {role.descripcion && <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>{role.descripcion}</div>}
                </div>
                <div style={{ display: 'flex', gap: '0.4rem' }}>
                  <button onClick={() => startEdit(role)} title="Editar rol"
                    style={{ background: 'var(--glass)', border: '1px solid var(--glass-border)', borderRadius: '6px', padding: '0.4rem', cursor: 'pointer', color: 'var(--text-main)' }}>
                    <Pencil size={15} />
                  </button>
                  <button onClick={() => onDelete(role)} disabled={role.es_sistema} title={role.es_sistema ? 'Rol de sistema protegido' : 'Eliminar rol'}
                    style={{ background: 'rgba(239,68,68,0.1)', border: 'none', borderRadius: '6px', padding: '0.4rem', cursor: role.es_sistema ? 'not-allowed' : 'pointer', color: 'var(--danger)', opacity: role.es_sistema ? 0.4 : 1 }}>
                    <Trash2 size={15} />
                  </button>
                </div>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginTop: '0.85rem' }}>
                {role.permissions.length === 0 && <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Sin permisos asignados.</span>}
                {role.permissions.map(p => (
                  <span key={p.id} style={{ fontSize: '0.72rem', background: 'var(--color-bg-elevated)', border: '1px solid var(--glass-border)', padding: '0.2rem 0.55rem', borderRadius: '6px', color: 'var(--text-muted)' }}>
                    {p.codigo}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
      {roles.length === 0 && (
        <div style={{ ...card, padding: '2.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          No hay roles definidos todavía.
        </div>
      )}
    </div>
  );
}

// ─── Panel de Asignación de roles (administradores de empresa) ────────────────
function AsignarPanel({ users, roles, userRolesMap, onAssign, onRemove }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [picker, setPicker] = useState({}); // { [userId]: roleId }
  const [busyId, setBusyId] = useState(null);

  const filtered = users.filter(u =>
    (u.email || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleAssign = async (user) => {
    const roleId = picker[user.id];
    if (!roleId) return;
    setBusyId(user.id);
    await onAssign(user, roleId);
    setPicker(prev => ({ ...prev, [user.id]: '' }));
    setBusyId(null);
  };

  const handleRemove = async (user, roleId) => {
    setBusyId(user.id);
    await onRemove(user, roleId);
    setBusyId(null);
  };

  return (
    <div className="animate-fade-in">
      <div style={{ ...card, padding: '0.9rem 1.25rem', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Search size={16} color="var(--text-muted)" />
        <input placeholder="Buscar usuario por correo..." value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          style={{ background: 'none', border: 'none', color: 'var(--text-main)', outline: 'none', width: '100%', fontSize: '0.88rem' }} />
      </div>

      {filtered.map(user => {
        const assigned = userRolesMap[user.id] || [];
        const assignedIds = assigned.map(a => a.role_id);
        const available = roles.filter(r => !assignedIds.includes(r.id));
        return (
          <div key={user.id} style={{ ...card, marginBottom: '0.85rem', padding: '1.1rem 1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{user.email || '—'}</div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                  Rol base:{' '}
                  <span style={{ color: ROLE_COLORS[user.role] || 'var(--text-muted)', fontWeight: 600 }}>
                    {ROLE_LABELS[user.role] || user.role}
                  </span>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <select value={picker[user.id] || ''} onChange={e => setPicker(prev => ({ ...prev, [user.id]: e.target.value }))}
                  style={{ ...inputStyle, width: 'auto', minWidth: '180px', cursor: 'pointer' }}>
                  <option value="">Seleccionar rol...</option>
                  {available.map(r => <option key={r.id} value={r.id}>{r.nombre}</option>)}
                </select>
                <button onClick={() => handleAssign(user)} disabled={!picker[user.id] || busyId === user.id}
                  style={{ ...btnPrimary, opacity: (!picker[user.id] || busyId === user.id) ? 0.5 : 1 }}>
                  <Plus size={15} /> Asignar
                </button>
              </div>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.45rem', marginTop: '0.85rem' }}>
              {assigned.length === 0 && <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Sin roles asignados.</span>}
              {assigned.map(a => (
                <span key={a.id} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', background: 'rgba(0,210,255,0.1)', border: '1px solid rgba(0,210,255,0.25)', color: 'var(--primary)', padding: '0.25rem 0.4rem 0.25rem 0.65rem', borderRadius: '20px' }}>
                  {a.role_nombre || 'Rol'}
                  <button onClick={() => handleRemove(user, a.role_id)} disabled={busyId === user.id} title="Quitar rol"
                    style={{ background: 'rgba(239,68,68,0.15)', border: 'none', borderRadius: '50%', width: 18, height: 18, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: 'var(--danger)' }}>
                    <X size={11} />
                  </button>
                </span>
              ))}
            </div>
          </div>
        );
      })}
      {filtered.length === 0 && (
        <div style={{ ...card, padding: '2.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          No hay usuarios para mostrar.
        </div>
      )}
    </div>
  );
}

// ─── Vista principal ──────────────────────────────────────────────────────────
export default function RolesView({ userRole, empresaId }) {
  const isSuper = userRole === 'super_admin';
  const [tab, setTab] = useState(isSuper ? 'roles' : 'asignar');
  const [permissions, setPermissions] = useState([]);
  const [roles, setRoles] = useState([]);
  const [users, setUsers] = useState([]);
  const [userRolesMap, setUserRolesMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadAll = async () => {
    setLoading(true); setError('');
    try {
      const rolesData = await rbacApi.listRoles();
      setRoles(Array.isArray(rolesData) ? rolesData : []);

      if (isSuper) {
        const permsData = await rbacApi.listPermissions();
        setPermissions(Array.isArray(permsData) ? permsData : []);
      }

      const usersData = await authApi.listUsers();
      let items = usersData.items || [];
      if (!isSuper && empresaId) items = items.filter(u => u.empresa_id === empresaId);
      setUsers(items);

      const entries = await Promise.all(items.map(async (u) => {
        try { return [u.id, await rbacApi.listUserRoles(u.id)]; }
        catch { return [u.id, []]; }
      }));
      setUserRolesMap(Object.fromEntries(entries));
    } catch (e) {
      setError('No se pudieron cargar los datos de roles y permisos.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadAll(); }, []);

  // ── Handlers de permisos ──
  const createPermission = async (data) => {
    try {
      const created = await rbacApi.createPermission(data);
      setPermissions(prev => [...prev, created]);
      return true;
    } catch (e) {
      alert(e.response?.data?.detail || 'Error al crear el permiso.');
      return false;
    }
  };
  const deletePermission = async (perm) => {
    if (!window.confirm(`¿Eliminar el permiso "${perm.nombre}"?`)) return;
    try {
      await rbacApi.deletePermission(perm.id);
      setPermissions(prev => prev.filter(p => p.id !== perm.id));
      loadAll();
    } catch (e) {
      alert(e.response?.data?.detail || 'Error al eliminar el permiso.');
    }
  };

  // ── Handlers de roles ──
  const createRole = async (data) => {
    try {
      const created = await rbacApi.createRole(data);
      setRoles(prev => [...prev, created].sort((a, b) => a.nombre.localeCompare(b.nombre)));
      return true;
    } catch (e) {
      alert(e.response?.data?.detail || 'Error al crear el rol.');
      return false;
    }
  };
  const updateRole = async (id, data) => {
    try {
      const updated = await rbacApi.updateRole(id, data);
      setRoles(prev => prev.map(r => r.id === id ? updated : r));
    } catch (e) {
      alert(e.response?.data?.detail || 'Error al actualizar el rol.');
    }
  };
  const deleteRole = async (role) => {
    if (!window.confirm(`¿Eliminar el rol "${role.nombre}"?`)) return;
    try {
      await rbacApi.deleteRole(role.id);
      setRoles(prev => prev.filter(r => r.id !== role.id));
    } catch (e) {
      alert(e.response?.data?.detail || 'Error al eliminar el rol.');
    }
  };

  // ── Handlers de asignación ──
  const assignRole = async (user, roleId) => {
    try {
      const created = await rbacApi.assignRole(user.id, roleId);
      setUserRolesMap(prev => ({ ...prev, [user.id]: [...(prev[user.id] || []), created] }));
    } catch (e) {
      alert(e.response?.data?.detail || 'Error al asignar el rol.');
    }
  };
  const removeRole = async (user, roleId) => {
    try {
      await rbacApi.removeRole(user.id, roleId);
      setUserRolesMap(prev => ({ ...prev, [user.id]: (prev[user.id] || []).filter(a => a.role_id !== roleId) }));
    } catch (e) {
      alert(e.response?.data?.detail || 'Error al quitar el rol.');
    }
  };

  const tabs = isSuper
    ? [
        { id: 'roles', label: 'Roles', icon: <ShieldCheck size={16} /> },
        { id: 'permisos', label: 'Permisos', icon: <KeyRound size={16} /> },
        { id: 'asignar', label: 'Asignar a usuarios', icon: <Users size={16} /> },
      ]
    : [{ id: 'asignar', label: 'Asignar roles a usuarios', icon: <Users size={16} /> }];

  return (
    <div className="animate-fade-in">
      {/* Banner contextual */}
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
        className="glass-card"
        style={{ padding: '1rem 1.25rem', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.85rem', borderLeft: `4px solid ${isSuper ? '#a855f7' : 'var(--danger)'}` }}>
        <Lock size={22} color={isSuper ? '#a855f7' : 'var(--danger)'} />
        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          {isSuper
            ? 'Como super administrador puedes crear permisos, definir roles y asignarlos a cualquier usuario.'
            : 'Como administrador de empresa puedes asignar y quitar roles a los usuarios de tu empresa.'}
        </div>
      </motion.div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        {tabs.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            style={{
              padding: '0.55rem 1.1rem', borderRadius: '8px', cursor: 'pointer',
              display: 'inline-flex', alignItems: 'center', gap: '0.45rem', fontSize: '0.85rem', fontWeight: 600,
              background: tab === t.id ? 'var(--primary)' : 'var(--glass)',
              color: tab === t.id ? 'white' : 'var(--text-muted)',
              border: `1px solid ${tab === t.id ? 'var(--primary)' : 'var(--glass-border)'}`,
            }}>
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      {error && (
        <div style={{ ...card, padding: '1rem', marginBottom: '1rem', color: 'var(--danger)', fontSize: '0.85rem' }}>{error}</div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>Cargando...</div>
      ) : (
        <>
          {tab === 'permisos' && isSuper && (
            <PermisosPanel permissions={permissions} onCreate={createPermission} onDelete={deletePermission} />
          )}
          {tab === 'roles' && isSuper && (
            <RolesPanel roles={roles} permissions={permissions} onCreate={createRole} onUpdate={updateRole} onDelete={deleteRole} />
          )}
          {tab === 'asignar' && (
            <AsignarPanel users={users} roles={roles} userRolesMap={userRolesMap} onAssign={assignRole} onRemove={removeRole} />
          )}
        </>
      )}
    </div>
  );
}
