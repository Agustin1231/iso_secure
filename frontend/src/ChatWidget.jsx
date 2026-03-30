import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, ShieldCheck } from 'lucide-react';

// ── Variables de entorno ────────────────────────────────────────────────────
const CHAT_API_KEY  = import.meta.env.VITE_CHAT_API_KEY  || '';
const CHAT_BASE_URL = import.meta.env.VITE_CHAT_BASE_URL || 'https://langgraph.agustinynatalia.site';

// ── Sesión persistente por navegador ────────────────────────────────────────
const getSessionId = () => {
  let sid = localStorage.getItem('_isora_sid');
  if (!sid) {
    sid = 'u' + Math.random().toString(36).slice(2) + Date.now().toString(36);
    localStorage.setItem('_isora_sid', sid);
  }
  return sid;
};
const SESSION_ID = getSessionId();

const WELCOME = {
  id: 0,
  role: 'bot',
  text: '¡Hola! Soy ISORA, tu asistente experto en ISO/IEC 27001:2022. Puedo ayudarte con controles del Anexo A, gestión de riesgos, auditorías, cumplimiento y el uso de la plataforma. ¿En qué puedo orientarte hoy?',
  streaming: false,
};

export default function ChatWidget({ userEmail, userRole }) {
  const [open, setOpen]       = useState(false);
  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput]     = useState('');
  const [busy, setBusy]       = useState(false);
  const msgsRef  = useRef(null);
  const inputRef = useRef(null);

  // Auto-focus al abrir
  useEffect(() => {
    if (open && inputRef.current) inputRef.current.focus();
  }, [open]);

  // Auto-scroll al nuevo mensaje
  useEffect(() => {
    if (msgsRef.current) msgsRef.current.scrollTop = msgsRef.current.scrollHeight;
  }, [messages]);

  const sendMessage = async (text) => {
    if (!text.trim() || busy || !CHAT_API_KEY) return;
    setBusy(true);
    setInput('');

    const userMsg = { id: Date.now(),     role: 'user', text, streaming: false };
    const botId   = Date.now() + 1;
    const botMsg  = { id: botId, role: 'bot', text: '', streaming: true };

    setMessages(prev => [...prev, userMsg, botMsg]);

    try {
      const resp = await fetch(`${CHAT_BASE_URL}/webhook/${CHAT_API_KEY}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message:    text,
          session_id: SESSION_ID,
          user_name:  userEmail || 'Usuario',
        }),
      });

      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

      const reader  = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer    = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.trim().startsWith('data: ')) continue;
          try {
            const ev = JSON.parse(line.trim().slice(6));
            if (ev.type === 'chunk') {
              setMessages(prev => prev.map(m =>
                m.id === botId ? { ...m, text: m.text + ev.text } : m
              ));
            }
            if (ev.type === 'done') {
              setMessages(prev => prev.map(m =>
                m.id === botId ? { ...m, streaming: false } : m
              ));
            }
            if (ev.type === 'error') {
              setMessages(prev => prev.map(m =>
                m.id === botId ? { ...m, streaming: false, text: `⚠️ ${ev.text}` } : m
              ));
            }
          } catch (_) {}
        }
      }
      // Por si el stream terminó sin evento 'done'
      setMessages(prev => prev.map(m =>
        m.id === botId ? { ...m, streaming: false } : m
      ));
    } catch {
      setMessages(prev => prev.map(m =>
        m.id === botId ? { ...m, streaming: false, text: '⚠️ No se pudo conectar con ISORA. Intenta nuevamente.' } : m
      ));
    }

    setBusy(false);
    if (inputRef.current) inputRef.current.focus();
  };

  const handleSubmit = (e) => { e.preventDefault(); sendMessage(input); };

  if (!CHAT_API_KEY) return null; // No renderizar si no hay API key configurada

  return (
    <>
      <style>{`
        @keyframes isora-blink { 50% { opacity: 0; } }
        @keyframes isora-pulse { 0%,100% { box-shadow: 0 0 0 0 rgba(0,210,255,.4); } 70% { box-shadow: 0 0 0 8px rgba(0,210,255,0); } }
        #isora-msgs::-webkit-scrollbar { width: 4px; }
        #isora-msgs::-webkit-scrollbar-track { background: transparent; }
        #isora-msgs::-webkit-scrollbar-thumb { background: var(--glass-border); border-radius: 4px; }
      `}</style>

      {/* ── Botón flotante ── */}
      <button
        onClick={() => setOpen(o => !o)}
        aria-label="Abrir asistente ISORA"
        title="ISORA — Asistente ISO 27001"
        style={{
          position: 'fixed', bottom: 24, right: 24, zIndex: 9999,
          width: 52, height: 52, borderRadius: '50%',
          background: 'var(--primary)', border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 4px 20px rgba(0,210,255,.35)',
          transition: 'transform .2s, box-shadow .2s',
          animation: !open ? 'isora-pulse 2.5s ease-in-out infinite' : 'none',
        }}
        onMouseEnter={e => { e.currentTarget.style.transform = 'scale(1.09)'; e.currentTarget.style.boxShadow = '0 6px 28px rgba(0,210,255,.55)'; }}
        onMouseLeave={e => { e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.boxShadow = '0 4px 20px rgba(0,210,255,.35)'; }}
      >
        {open
          ? <X size={22} color="white" strokeWidth={2.5} />
          : <MessageCircle size={22} color="white" strokeWidth={2} />}
      </button>

      {/* ── Panel de chat ── */}
      <div style={{
        position: 'fixed', bottom: 88, right: 24, zIndex: 9998,
        width: 370, maxWidth: 'calc(100vw - 32px)',
        height: 530, maxHeight: 'calc(100vh - 116px)',
        background: 'var(--color-bg-card)',
        border: '1px solid var(--glass-border)',
        borderRadius: 16,
        display: 'flex', flexDirection: 'column', overflow: 'hidden',
        boxShadow: '0 16px 56px rgba(0,0,0,.25), 0 0 0 1px var(--glass-border)',
        transition: 'opacity .25s, transform .25s',
        opacity: open ? 1 : 0,
        transform: open ? 'translateY(0) scale(1)' : 'translateY(14px) scale(.96)',
        pointerEvents: open ? 'all' : 'none',
      }}>

        {/* Header */}
        <div style={{
          padding: '12px 14px',
          background: 'var(--color-bg-elevated)',
          borderBottom: '1px solid var(--glass-border)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          flexShrink: 0,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <div style={{
              width: 34, height: 34, borderRadius: '50%',
              background: 'rgba(0,210,255,.12)',
              border: '1px solid rgba(0,210,255,.2)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <ShieldCheck size={16} color="var(--primary)" strokeWidth={2.5} />
            </div>
            <div>
              <div style={{ fontSize: '0.88rem', fontWeight: '800', color: 'var(--text-main)', letterSpacing: '-.01em' }}>ISORA</div>
              <div style={{ fontSize: '0.68rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '0.3rem', fontWeight: '600' }}>
                <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--success)', display: 'inline-block', boxShadow: '0 0 4px var(--success)' }} />
                Asistente ISO/IEC 27001:2022
              </div>
            </div>
          </div>
          <button
            onClick={() => setOpen(false)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', padding: 4, borderRadius: 6, display: 'flex', transition: 'color .15s' }}
            onMouseEnter={e => e.currentTarget.style.color = 'var(--text-main)'}
            onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
          >
            <X size={17} />
          </button>
        </div>

        {/* Mensajes */}
        <div
          id="isora-msgs"
          ref={msgsRef}
          style={{ flex: 1, overflowY: 'auto', padding: '14px 12px', display: 'flex', flexDirection: 'column', gap: 10 }}
        >
          {messages.map(msg => (
            <div
              key={msg.id}
              style={{
                maxWidth: '84%',
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                background: msg.role === 'user'
                  ? 'var(--primary)'
                  : 'var(--color-bg-elevated)',
                color: msg.role === 'user' ? 'white' : 'var(--text-main)',
                padding: '9px 13px',
                borderRadius: msg.role === 'user' ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
                fontSize: '0.82rem',
                lineHeight: '1.6',
                border: msg.role === 'bot' ? '1px solid var(--glass-border)' : 'none',
                wordBreak: 'break-word',
                whiteSpace: 'pre-wrap',
              }}
            >
              {msg.text}
              {msg.streaming && (
                <span style={{ marginLeft: 2, animation: 'isora-blink .7s steps(1) infinite', opacity: .7 }}>▋</span>
              )}
            </div>
          ))}

          {/* Indicador "escribiendo" mientras carga sin texto aún */}
          {busy && messages.at(-1)?.text === '' && (
            <div style={{
              alignSelf: 'flex-start',
              background: 'var(--color-bg-elevated)',
              border: '1px solid var(--glass-border)',
              borderRadius: '14px 14px 14px 2px',
              padding: '10px 14px',
              display: 'flex', gap: 5, alignItems: 'center',
            }}>
              {[0, 1, 2].map(i => (
                <span key={i} style={{
                  width: 6, height: 6, borderRadius: '50%',
                  background: 'var(--primary)', opacity: .5,
                  animation: `isora-blink .9s steps(1) ${i * 0.3}s infinite`,
                }} />
              ))}
            </div>
          )}
        </div>

        {/* Sugerencias rápidas (solo al inicio) */}
        {messages.length === 1 && (
          <div style={{ padding: '0 12px 10px', display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {[
              '¿Qué es el Anexo A?',
              '¿Cómo gestionar un riesgo?',
              '¿Qué hace un auditor?',
            ].map(q => (
              <button
                key={q}
                onClick={() => sendMessage(q)}
                disabled={busy}
                style={{
                  fontSize: '0.72rem', padding: '5px 10px',
                  background: 'var(--glass)', border: '1px solid var(--glass-border)',
                  borderRadius: 20, cursor: 'pointer', color: 'var(--text-muted)',
                  transition: 'border-color .15s, color .15s',
                  fontFamily: 'inherit',
                }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--primary)'; e.currentTarget.style.color = 'var(--primary)'; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--glass-border)'; e.currentTarget.style.color = 'var(--text-muted)'; }}
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <form
          onSubmit={handleSubmit}
          style={{
            padding: '10px 12px',
            borderTop: '1px solid var(--glass-border)',
            display: 'flex', gap: 8, flexShrink: 0,
            background: 'var(--color-bg-elevated)',
          }}
        >
          <input
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Pregunta sobre ISO 27001..."
            maxLength={600}
            disabled={busy}
            style={{
              flex: 1,
              background: 'var(--color-bg)',
              border: '1px solid var(--glass-border)',
              borderRadius: 10,
              color: 'var(--text-main)',
              fontSize: '0.82rem',
              padding: '8px 12px',
              outline: 'none',
              height: 38,
              fontFamily: 'inherit',
              transition: 'border-color .15s',
            }}
            onFocus={e => e.target.style.borderColor = 'var(--primary)'}
            onBlur={e => e.target.style.borderColor = 'var(--glass-border)'}
          />
          <button
            type="submit"
            disabled={busy || !input.trim()}
            style={{
              width: 38, height: 38, borderRadius: 10, flexShrink: 0,
              background: busy || !input.trim() ? 'var(--glass)' : 'var(--primary)',
              border: '1px solid var(--glass-border)',
              cursor: busy || !input.trim() ? 'not-allowed' : 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              transition: 'background .15s',
            }}
          >
            <Send size={15} color="white" strokeWidth={2.5} />
          </button>
        </form>
      </div>
    </>
  );
}
