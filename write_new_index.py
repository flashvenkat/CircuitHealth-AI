#!/usr/bin/env python3
"""Writes the premium VoiceMed index.html to disk."""

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>VoiceMed — Intelligent Medical Decision Support</title>
  <meta name="description" content="VoiceMed: A privacy-minded clinical companion. Decode prescriptions, audit hospital bills in INR, understand insurance, and get triage guidance." />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    /* === DESIGN TOKENS — Medical Clinical Palette === */
    :root {
      --color-bg:             #F8FAFC;
      --color-surface:        #FFFFFF;
      --color-surface-raised: #F0F4F8;
      --color-border:         #E2E8F0;
      --color-border-strong:  #CBD5E1;
      --color-navy:           #1E293B;
      --color-navy-mid:       #334155;
      --color-navy-light:     #64748B;
      --color-cyan:           #0284C7;
      --color-cyan-hover:     #0369A1;
      --color-cyan-light:     #BAE6FD;
      --color-cyan-bg:        #E0F2FE;
      --color-success:        #16A34A;
      --color-success-bg:     #DCFCE7;
      --color-warning:        #D97706;
      --color-warning-bg:     #FEF3C7;
      --color-danger:         #EF4444;
      --color-danger-bg:      #FEE2E2;
      --color-info:           #7C3AED;
      --font-base: 'Inter', Helvetica, Arial, sans-serif;
      --r-sm: 6px; --r-md: 10px; --r-lg: 14px; --r-xl: 20px; --r-pill: 99px;
      --shadow-card:  0 1px 3px rgba(0,0,0,.08), 0 4px 12px rgba(0,0,0,.05);
      --shadow-float: 0 8px 30px rgba(0,0,0,.12);
      --shadow-inset: inset 0 2px 4px rgba(0,0,0,.04);
      --sidebar-w: 260px;
    }

    /* === RESET === */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { font-size: 16px; scroll-behavior: smooth; }
    body {
      font-family: var(--font-base);
      background: var(--color-bg);
      color: var(--color-navy);
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
      display: flex;
      flex-direction: column;
    }
    a { color: var(--color-cyan); text-decoration: none; }
    :focus-visible { outline: 3px solid var(--color-cyan); outline-offset: 2px; border-radius: var(--r-sm); }
    :focus:not(:focus-visible) { outline: none; }
    ::selection { background: var(--color-cyan-light); color: var(--color-navy); }

    /* === UTILITIES === */
    .hidden { display: none !important; }
    .sr-only { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
    .flex { display: flex; } .flex-col { flex-direction: column; }
    .items-center { align-items: center; } .justify-between { justify-content: space-between; }
    .gap-2 { gap: 8px; } .gap-3 { gap: 12px; } .flex-1 { flex: 1 1 0; }
    .w-full { width: 100%; } .font-bold { font-weight: 700; }

    /* === BADGE === */
    .badge {
      display: inline-flex; align-items: center; gap: 4px;
      font-size: 0.7rem; font-weight: 600; letter-spacing: 0.03em;
      padding: 2px 8px; border-radius: var(--r-pill); white-space: nowrap;
    }
    .badge-cyan    { background: var(--color-cyan-bg);    color: var(--color-cyan-hover); }
    .badge-success { background: var(--color-success-bg); color: var(--color-success); }
    .badge-danger  { background: var(--color-danger-bg);  color: var(--color-danger); }
    .badge-warning { background: var(--color-warning-bg); color: var(--color-warning); }
    .badge-navy    { background: #E2E8F0; color: var(--color-navy-mid); }

    /* === BUTTONS === */
    .btn {
      display: inline-flex; align-items: center; justify-content: center; gap: 6px;
      font-family: var(--font-base); font-weight: 600; font-size: 0.875rem;
      cursor: pointer; border: none; border-radius: var(--r-md);
      transition: background 0.15s, box-shadow 0.15s, transform 0.1s;
      min-height: 44px; padding: 0 18px; white-space: nowrap;
    }
    .btn:active { transform: translateY(1px); }
    .btn:disabled { opacity: 0.45; cursor: not-allowed; transform: none; }
    .btn-primary { background: var(--color-cyan); color: #fff; box-shadow: 0 2px 8px rgba(2,132,199,.25); }
    .btn-primary:hover:not(:disabled) { background: var(--color-cyan-hover); box-shadow: 0 4px 16px rgba(2,132,199,.35); }
    .btn-ghost {
      background: transparent; color: var(--color-navy-light);
      border: 1px solid var(--color-border); min-height: 36px; padding: 0 12px; font-size: 0.8rem;
    }
    .btn-ghost:hover:not(:disabled) { background: var(--color-surface-raised); color: var(--color-navy); }
    .btn-lg { min-height: 52px; font-size: 1rem; padding: 0 28px; border-radius: var(--r-lg); }

    /* === FORM CONTROLS === */
    .form-label {
      display: block; font-size: 0.75rem; font-weight: 600;
      text-transform: uppercase; letter-spacing: 0.06em;
      color: var(--color-navy-light); margin-bottom: 6px;
    }
    .form-control {
      width: 100%; font-family: var(--font-base); font-size: 0.9rem;
      color: var(--color-navy); background: var(--color-surface);
      border: 1.5px solid var(--color-border-strong); border-radius: var(--r-md);
      padding: 11px 14px; transition: border-color 0.15s, box-shadow 0.15s;
      box-shadow: var(--shadow-inset);
    }
    .form-control::placeholder { color: var(--color-border-strong); }
    .form-control:focus { border-color: var(--color-cyan); box-shadow: 0 0 0 3px rgba(2,132,199,.15), var(--shadow-inset); outline: none; }
    select.form-control { cursor: pointer; }
    textarea.form-control { resize: vertical; line-height: 1.6; }

    /* === CARD === */
    .card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--r-xl); box-shadow: var(--shadow-card); }

    /* === STATUS DOT === */
    .status-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--color-warning); animation: pulse-dot 1.5s infinite; flex-shrink: 0; }
    .status-dot.online  { background: var(--color-success); animation: none; }
    .status-dot.offline { background: var(--color-danger);  animation: none; }
    @keyframes pulse-dot { 0%,100% { opacity:1; } 50% { opacity:.35; } }

    /* === AUTH VIEW === */
    #authView {
      position: fixed; inset: 0; z-index: 1000;
      display: flex; align-items: center; justify-content: center;
      background: linear-gradient(135deg, #E0F2FE 0%, #F8FAFC 40%, #EDE9FE 100%);
      padding: 16px;
    }
    .auth-card {
      max-width: 440px; width: 100%;
      background: var(--color-surface); border: 1px solid var(--color-border);
      border-radius: var(--r-xl); box-shadow: 0 20px 60px rgba(0,0,0,.12);
      padding: 40px; animation: slide-up 0.35s cubic-bezier(.22,.68,0,1.2);
    }
    @keyframes slide-up { from { opacity:0; transform:translateY(24px) scale(.97); } to { opacity:1; transform:none; } }
    .auth-logo {
      width: 56px; height: 56px;
      background: linear-gradient(135deg, var(--color-cyan) 0%, #0369A1 100%);
      border-radius: var(--r-lg); display: flex; align-items: center; justify-content: center;
      font-size: 1.6rem; margin: 0 auto 20px; box-shadow: 0 8px 24px rgba(2,132,199,.3);
    }
    .auth-title { font-size: 1.5rem; font-weight: 800; color: var(--color-navy); text-align: center; letter-spacing: -0.02em; }
    .auth-subtitle { font-size: 0.875rem; color: var(--color-navy-light); text-align: center; margin-top: 6px; margin-bottom: 28px; }
    .auth-form { display: flex; flex-direction: column; gap: 16px; }
    .auth-disclaimer { margin-top: 20px; font-size: 0.72rem; color: var(--color-navy-light); text-align: center; line-height: 1.5; }

    /* === MAIN APP === */
    #mainApp { flex: 1; display: flex; flex-direction: column; }

    /* Header */
    #appHeader { background: var(--color-surface); border-bottom: 1px solid var(--color-border); position: sticky; top: 0; z-index: 200; box-shadow: 0 1px 4px rgba(0,0,0,.05); }
    .header-inner { max-width: 1400px; margin: 0 auto; padding: 0 24px; height: 62px; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
    .header-brand { display: flex; align-items: center; gap: 10px; }
    .header-logo { width: 36px; height: 36px; background: linear-gradient(135deg, var(--color-cyan) 0%, #0369A1 100%); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.15rem; flex-shrink: 0; box-shadow: 0 3px 10px rgba(2,132,199,.25); }
    .header-brand-name { font-size: 0.95rem; font-weight: 800; color: var(--color-navy); letter-spacing: -0.01em; }
    .header-brand-sub { font-size: 0.72rem; color: var(--color-navy-light); margin-top: 1px; }
    .header-actions { display: flex; align-items: center; gap: 8px; }
    .status-pill { display: flex; align-items: center; gap: 6px; background: var(--color-surface-raised); border: 1px solid var(--color-border); border-radius: var(--r-pill); padding: 4px 12px; font-size: 0.75rem; font-weight: 500; color: var(--color-navy-mid); }

    /* Layout */
    .app-layout { flex: 1; display: flex; max-width: 1400px; width: 100%; margin: 0 auto; padding: 24px; gap: 20px; }

    /* Sidebar */
    #sidebar { width: var(--sidebar-w); flex-shrink: 0; display: flex; flex-direction: column; gap: 16px; }
    .sidebar-section-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--color-navy-light); padding: 0 4px; margin-bottom: 6px; }
    .nav-item {
      display: flex; align-items: center; gap: 10px; width: 100%;
      padding: 11px 12px; border-radius: var(--r-md); border: 1.5px solid transparent;
      background: transparent; cursor: pointer; font-family: var(--font-base);
      font-size: 0.875rem; font-weight: 500; color: var(--color-navy-mid);
      text-align: left; transition: background 0.15s, border-color 0.15s, color 0.15s;
      min-height: 48px;
    }
    .nav-item:hover { background: var(--color-cyan-bg); color: var(--color-cyan-hover); }
    .nav-item.active { background: var(--color-cyan-bg); border-color: var(--color-cyan-light); color: var(--color-cyan-hover); font-weight: 600; }
    .nav-item .nav-icon { font-size: 1.1rem; width: 22px; text-align: center; flex-shrink: 0; }
    .nav-item .nav-badge { margin-left: auto; }
    .sidebar-info-card { background: linear-gradient(135deg, var(--color-cyan-bg) 0%, #EDE9FE 100%); border: 1px solid var(--color-cyan-light); border-radius: var(--r-lg); padding: 14px; }
    .sidebar-info-card h4 { font-size: 0.8rem; font-weight: 700; color: var(--color-cyan-hover); margin-bottom: 4px; }
    .sidebar-info-card p { font-size: 0.72rem; color: var(--color-navy-light); line-height: 1.5; }

    /* Content area */
    .content-area { flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; min-width: 0; }

    /* Input panel */
    .input-panel { display: flex; flex-direction: column; }
    .panel-header { padding: 20px 22px 14px; border-bottom: 1px solid var(--color-border); }
    .panel-title { font-size: 1rem; font-weight: 700; color: var(--color-navy); letter-spacing: -0.01em; }
    .panel-desc { font-size: 0.8rem; color: var(--color-navy-light); margin-top: 3px; line-height: 1.5; }
    .panel-body { padding: 16px 22px; display: flex; flex-direction: column; gap: 14px; flex: 1; }
    .panel-footer { padding: 0 22px 20px; }

    /* Drop zone */
    .drop-zone {
      border: 2px dashed var(--color-border-strong); border-radius: var(--r-lg);
      padding: 20px; text-align: center; cursor: pointer;
      transition: border-color 0.2s, background 0.2s;
      background: var(--color-surface-raised); position: relative;
    }
    .drop-zone:hover, .drop-zone.drag-over { border-color: var(--color-cyan); background: var(--color-cyan-bg); }
    .drop-zone input[type="file"] { position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%; }
    .drop-zone-icon { font-size: 1.5rem; margin-bottom: 4px; }
    .drop-zone-label { font-size: 0.78rem; color: var(--color-navy-light); font-weight: 500; }
    .drop-zone-label span { color: var(--color-cyan); font-weight: 600; }
    .context-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

    /* Output panel */
    .output-panel { display: flex; flex-direction: column; }
    .output-toolbar { display: flex; align-items: center; gap: 6px; padding: 14px 22px; border-bottom: 1px solid var(--color-border); }
    .output-toolbar-title { font-size: 0.9rem; font-weight: 700; color: var(--color-navy); flex: 1; }
    .output-body { flex: 1; overflow-y: auto; padding: 20px 22px; min-height: 320px; max-height: 560px; }

    /* Empty state */
    .empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 260px; text-align: center; gap: 8px; }
    .empty-state-icon { width: 56px; height: 56px; border-radius: 50%; background: var(--color-surface-raised); border: 1.5px solid var(--color-border); display: flex; align-items: center; justify-content: center; font-size: 1.4rem; margin-bottom: 4px; }
    .empty-state-title { font-size: 0.9rem; font-weight: 600; color: var(--color-navy-mid); }
    .empty-state-text { font-size: 0.78rem; color: var(--color-navy-light); max-width: 200px; line-height: 1.5; }

    /* Skeleton shimmer */
    @keyframes skeleton-shimmer { 0% { background-position: -400px 0; } 100% { background-position: 400px 0; } }
    .skeleton { border-radius: var(--r-md); background: linear-gradient(90deg, #E2E8F0 25%, #F1F5F9 50%, #E2E8F0 75%); background-size: 400px 100%; animation: skeleton-shimmer 1.4s infinite linear; }
    .sk-h4 { height: 16px; margin-bottom: 10px; } .sk-h3 { height: 12px; margin-bottom: 8px; }
    .sk-full { width: 100%; } .sk-80 { width: 80%; } .sk-60 { width: 60%; } .sk-40 { width: 40%; }

    /* Prose (Markdown output) */
    .prose { font-size: 0.875rem; line-height: 1.75; color: var(--color-navy); }
    .prose h1,.prose h2,.prose h3 { font-weight: 700; color: var(--color-navy); margin-top: 1.25em; margin-bottom: 0.5em; letter-spacing: -0.01em; }
    .prose h1 { font-size: 1.2rem; } .prose h2 { font-size: 1.05rem; } .prose h3 { font-size: 0.95rem; }
    .prose p { margin-bottom: 0.75em; color: var(--color-navy-mid); }
    .prose ul,.prose ol { padding-left: 1.4em; margin-bottom: 0.75em; color: var(--color-navy-mid); }
    .prose li { margin-bottom: 0.3em; }
    .prose strong { color: var(--color-navy); font-weight: 700; }
    .prose code { background: var(--color-surface-raised); border: 1px solid var(--color-border); padding: 2px 6px; border-radius: var(--r-sm); font-size: 0.8em; font-family: 'Courier New', monospace; color: var(--color-cyan-hover); }
    .prose blockquote { border-left: 3px solid var(--color-cyan); padding-left: 14px; color: var(--color-navy-light); font-style: italic; margin: 0.75em 0; }
    .prose hr { border: none; border-top: 1px solid var(--color-border); margin: 1em 0; }

    /* Output footer */
    .output-footer { padding: 10px 22px 14px; border-top: 1px solid var(--color-border); display: flex; justify-content: space-between; align-items: center; font-size: 0.7rem; color: var(--color-navy-light); }

    /* Mobile bottom nav */
    #mobileNav { display: none; position: fixed; bottom: 0; left: 0; right: 0; z-index: 500; background: var(--color-surface); border-top: 1px solid var(--color-border); box-shadow: 0 -4px 20px rgba(0,0,0,.08); padding: 8px 0 max(8px, env(safe-area-inset-bottom)); }
    .mobile-nav-inner { display: flex; justify-content: space-around; align-items: center; }
    .mobile-nav-btn { display: flex; flex-direction: column; align-items: center; gap: 3px; background: none; border: none; cursor: pointer; padding: 6px 10px; border-radius: var(--r-md); color: var(--color-navy-light); font-family: var(--font-base); font-size: 0.62rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; min-width: 56px; min-height: 44px; transition: color 0.15s, background 0.15s; }
    .mobile-nav-btn:hover { color: var(--color-cyan); background: var(--color-cyan-bg); }
    .mobile-nav-btn.active { color: var(--color-cyan-hover); }
    .mobile-nav-btn .mn-icon { font-size: 1.25rem; }

    /* Panel toggle (mobile) */
    #panelToggle { display: none; background: var(--color-surface-raised); border-bottom: 1px solid var(--color-border); padding: 8px 16px; }
    .panel-toggle-inner { display: flex; border: 1px solid var(--color-border-strong); border-radius: var(--r-md); overflow: hidden; max-width: 320px; margin: 0 auto; }
    .panel-toggle-btn { flex: 1; background: none; border: none; cursor: pointer; font-family: var(--font-base); font-size: 0.8rem; font-weight: 600; color: var(--color-navy-light); padding: 8px 0; transition: background 0.15s, color 0.15s; }
    .panel-toggle-btn.active { background: var(--color-cyan); color: #fff; }

    /* Toast */
    #toastContainer { position: fixed; top: 80px; right: 20px; z-index: 900; display: flex; flex-direction: column; gap: 8px; pointer-events: none; }
    .toast { background: var(--color-navy); color: #fff; font-size: 0.82rem; font-weight: 500; padding: 10px 16px; border-radius: var(--r-md); box-shadow: var(--shadow-float); animation: toast-in 0.25s ease; pointer-events: all; display: flex; align-items: center; gap: 8px; max-width: 300px; }
    .toast.success { background: var(--color-success); }
    .toast.error   { background: var(--color-danger); }
    @keyframes toast-in  { from { opacity:0; transform:translateX(20px); } to { opacity:1; transform:none; } }
    @keyframes toast-out { from { opacity:1; transform:none; } to { opacity:0; transform:translateX(20px); } }

    /* Disclaimer */
    .disclaimer-bar { background: var(--color-warning-bg); border-top: 1px solid #FDE68A; padding: 6px 24px; font-size: 0.7rem; color: var(--color-warning); text-align: center; font-weight: 500; }

    /* === RESPONSIVE === */
    /* Tablet: 768–1024 → icon-only sidebar */
    @media (max-width: 1024px) {
      :root { --sidebar-w: 64px; }
      .app-layout { padding: 16px; gap: 14px; }
      .nav-item .nav-label, .nav-item .nav-badge, .sidebar-section-label, .sidebar-info-card { display: none; }
      .nav-item { justify-content: center; padding: 11px 0; }
      .content-area { gap: 14px; }
      .header-brand-sub { display: none; }
    }
    /* Mobile: <768 → single column + bottom nav */
    @media (max-width: 767px) {
      #sidebar { display: none; }
      #mobileNav { display: flex; flex-direction: column; }
      #panelToggle { display: block; }
      .app-layout { padding: 12px 12px 84px; flex-direction: column; }
      .content-area { display: flex; flex-direction: column; gap: 12px; }
      .content-area .input-panel.mobile-hidden,
      .content-area .output-panel.mobile-hidden { display: none !important; }
      .header-inner { padding: 0 16px; height: 56px; }
      .status-pill { display: none; }
      .header-actions .btn-ghost { display: none; }
      .auth-card { padding: 28px 22px; }
      .auth-title { font-size: 1.3rem; }
    }
    @media (min-width: 1200px) { .content-area { grid-template-columns: 1.05fr 0.95fr; } }
    @media (forced-colors: active) { .btn-primary { forced-color-adjust: none; } }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>

<div id="toastContainer" role="status" aria-live="polite" aria-atomic="true"></div>

<!-- AUTH OVERLAY -->
<div id="authView" role="main" aria-label="VoiceMed Onboarding">
  <div class="auth-card" role="dialog" aria-modal="true" aria-labelledby="authTitle">
    <div class="auth-logo" aria-hidden="true">&#127973;</div>
    <h1 class="auth-title" id="authTitle">VoiceMed</h1>
    <p class="auth-subtitle">Secure, offline-first multilingual clinical companion</p>
    <form id="authForm" class="auth-form" onsubmit="handleAuth(event)" novalidate>
      <div>
        <label class="form-label" for="userName">Full Name</label>
        <input class="form-control" type="text" id="userName" required placeholder="e.g. Rahul Sharma" autocomplete="name" aria-required="true" />
      </div>
      <div>
        <label class="form-label" for="userAge">Patient Age</label>
        <input class="form-control" type="number" id="userAge" required placeholder="e.g. 45" min="1" max="120" autocomplete="off" aria-required="true" />
      </div>
      <div>
        <label class="form-label" for="prefLang">Preferred Language</label>
        <select class="form-control" id="prefLang" aria-required="true">
          <option value="English">&#127470;&#127475; English (en-IN)</option>
          <option value="Hindi">&#127470;&#127475; Hindi (&#2361;&#2367;&#2306;&#2342;&#2368;)</option>
          <option value="Telugu">&#127470;&#127475; Telugu (&#3108;&#3142;&#3122;&#3137;&#3095;&#3137;)</option>
          <option value="Tamil">&#127470;&#127475; Tamil (&#2980;&#2990;&#3007;&#2996;&#3021;)</option>
          <option value="Bengali">&#127470;&#127475; Bengali (&#2476;&#2494;&#2434;&#2482;&#2494;)</option>
          <option value="Marathi">&#127470;&#127475; Marathi (&#2350;&#2352;&#2366;&#2336;&#2368;)</option>
          <option value="Spanish">&#127760; Spanish (espa&#241;ol)</option>
        </select>
      </div>
      <button type="submit" class="btn btn-primary btn-lg w-full">&#128640; Launch Clinical Dashboard</button>
    </form>
    <p class="auth-disclaimer">&#9877;&#65039; For informational purposes only. Not a substitute for professional medical advice. Always consult a qualified healthcare provider.</p>
  </div>
</div>

<!-- MAIN DASHBOARD -->
<div id="mainApp" class="hidden" aria-label="VoiceMed Clinical Dashboard">

  <header id="appHeader" role="banner">
    <div class="header-inner">
      <div class="header-brand">
        <div class="header-logo" aria-hidden="true">&#127973;</div>
        <div>
          <div class="flex items-center gap-2">
            <span class="header-brand-name">VoiceMed</span>
            <span class="badge badge-cyan">v2.1 PRO</span>
          </div>
          <div class="header-brand-sub" id="profileDisplay">Clinical Decision Support</div>
        </div>
      </div>
      <div class="header-actions">
        <div class="status-pill" id="statusPill" aria-live="polite">
          <span class="status-dot" id="statusDot" role="img" aria-label="Connecting"></span>
          <span id="statusText">Connecting&hellip;</span>
        </div>
        <label class="sr-only" for="topLangSelect">Interface Language</label>
        <select class="form-control" id="topLangSelect"
          style="max-width:130px;min-height:36px;font-size:0.8rem;padding:6px 10px;"
          onchange="syncLanguage(this.value)" aria-label="Switch interface language">
          <option value="English">English</option>
          <option value="Hindi">Hindi</option>
          <option value="Telugu">Telugu</option>
          <option value="Tamil">Tamil</option>
          <option value="Bengali">Bengali</option>
          <option value="Marathi">Marathi</option>
          <option value="Spanish">Spanish</option>
        </select>
        <button class="btn btn-ghost" onclick="logout()" aria-label="Switch profile">&#8644; Profile</button>
      </div>
    </div>
  </header>

  <!-- Mobile panel toggle -->
  <div id="panelToggle" role="navigation" aria-label="Switch between panels">
    <div class="panel-toggle-inner">
      <button class="panel-toggle-btn active" id="toggleInputBtn" onclick="showMobilePanel('input')" aria-pressed="true">&#128221; Input</button>
      <button class="panel-toggle-btn" id="toggleOutputBtn" onclick="showMobilePanel('output')" aria-pressed="false">&#128203; Results</button>
    </div>
  </div>

  <div class="app-layout">
    <!-- SIDEBAR -->
    <nav id="sidebar" aria-label="Clinical Modules Navigation">
      <div>
        <p class="sidebar-section-label">Clinical Modules</p>
        <div role="list">
          <button class="nav-item active" id="nav-prescription" onclick="switchModule('prescription')" aria-current="true" role="listitem" aria-label="Prescription Decoder">
            <span class="nav-icon" aria-hidden="true">&#128138;</span>
            <span class="nav-label">Prescription Decoder</span>
            <span class="nav-badge badge badge-cyan">OCR</span>
          </button>
          <button class="nav-item" id="nav-bill_analysis" onclick="switchModule('bill_analysis')" role="listitem" aria-label="Hospital Bill Auditor">
            <span class="nav-icon" aria-hidden="true">&#8377;</span>
            <span class="nav-label">Bill Auditor (INR)</span>
            <span class="nav-badge badge badge-success">&#8377;</span>
          </button>
          <button class="nav-item" id="nav-insurance" onclick="switchModule('insurance')" role="listitem" aria-label="Insurance Explainer">
            <span class="nav-icon" aria-hidden="true">&#128737;&#65039;</span>
            <span class="nav-label">Insurance Explainer</span>
          </button>
          <button class="nav-item" id="nav-pocket_doctor" onclick="switchModule('pocket_doctor')" role="listitem" aria-label="Pocket Doctor Triage">
            <span class="nav-icon" aria-hidden="true">&#129658;</span>
            <span class="nav-label">Pocket Doctor Triage</span>
            <span class="nav-badge badge badge-danger">AI</span>
          </button>
        </div>
      </div>
      <div class="sidebar-info-card" role="complementary">
        <h4>&#128218; Drug Knowledge Base</h4>
        <p>20 clinical profiles with dosage guards, food-timing rules, and contraindication checks via local RAG engine.</p>
      </div>
    </nav>

    <!-- CONTENT AREA -->
    <div class="content-area">

      <!-- INPUT PANEL -->
      <section class="card input-panel" id="inputPanel" aria-label="Medical Input Panel">
        <div class="panel-header">
          <div class="flex items-center justify-between gap-2">
            <div>
              <h2 class="panel-title" id="moduleHeaderTitle">Prescription Decoder &amp; Safety Check</h2>
              <p class="panel-desc" id="moduleHeaderDesc">Translate medical shorthand and check drug dosage safeguards.</p>
            </div>
            <button class="btn btn-ghost" onclick="loadSampleData()" style="flex-shrink:0;" aria-label="Load sample data">&#10022; Load Sample</button>
          </div>
        </div>
        <div class="panel-body">
          <div>
            <label class="form-label" for="mainInputText">Input Text or OCR Data</label>
            <textarea class="form-control" id="mainInputText" rows="7"
              placeholder="Paste prescription text, hospital bill (&#8377;/INR), insurance clause, or describe symptoms&hellip;"
              aria-label="Medical input text" aria-describedby="inputHint" style="min-height:140px;"></textarea>
            <p id="inputHint" style="font-size:0.7rem;color:var(--color-navy-light);margin-top:4px;">Supports plain text, OCR output, or copied clinical documents. Press Ctrl+Enter to analyze.</p>
          </div>
          <div>
            <label class="form-label">Upload Document <span style="font-weight:400;text-transform:none;">(optional)</span></label>
            <div class="drop-zone" id="dropZone" role="button" tabindex="0"
              aria-label="Drag and drop a file, or click to browse"
              ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event)"
              onkeydown="if(event.key==='Enter'||event.key===' '){document.getElementById('fileInput').click();}">
              <input type="file" id="fileInput" accept=".txt,.pdf,.png,.jpg,.jpeg" aria-label="File upload input" onchange="handleFileSelect(event)" />
              <div class="drop-zone-icon" aria-hidden="true">&#128194;</div>
              <p class="drop-zone-label"><span>Click to browse</span> or drag &amp; drop<br/><span style="color:var(--color-navy-light);font-weight:400;">TXT, PDF, PNG, JPG &mdash; max 10 MB</span></p>
              <p id="fileName" style="margin-top:6px;font-size:0.72rem;color:var(--color-cyan-hover);font-weight:600;"></p>
            </div>
          </div>
          <div class="context-grid">
            <div>
              <label class="form-label" for="inputAge">Patient Age</label>
              <input class="form-control" type="text" id="inputAge" placeholder="e.g. 45" style="font-size:0.85rem;" />
            </div>
            <div>
              <label class="form-label" for="inputAllergies">Allergies / Notes</label>
              <input class="form-control" type="text" id="inputAllergies" placeholder="e.g. Penicillin, Sulfa" style="font-size:0.85rem;" />
            </div>
          </div>
        </div>
        <div class="panel-footer">
          <button class="btn btn-primary btn-lg w-full" id="analyzeBtn" onclick="submitAnalysis()" aria-label="Analyze the provided medical data">
            <span id="analyzeBtnIcon" aria-hidden="true">&#128269;</span>
            <span id="analyzeBtnText">Analyze &amp; Simplify</span>
          </button>
        </div>
      </section>

      <!-- OUTPUT PANEL -->
      <section class="card output-panel" id="outputPanel" aria-label="Clinical Guidance Output Panel">
        <div class="output-toolbar">
          <h2 class="output-toolbar-title">Clinical Guidance &amp; Summary</h2>
          <button class="btn btn-ghost" id="copyBtn" onclick="copySummary()" disabled aria-label="Copy to clipboard">&#128203; Copy</button>
          <button class="btn btn-ghost" id="saveBtn" onclick="downloadMarkdown()" disabled aria-label="Download as Markdown">&#128190; Save</button>
          <button class="btn btn-ghost" id="audioBtn" onclick="playAudioSpeech()" disabled aria-label="Listen via speech synthesis" style="color:var(--color-info);">&#128266; Listen</button>
        </div>
        <div class="output-body" id="outputContainer" role="region" aria-live="polite" aria-label="Analysis output">
          <div class="empty-state" id="emptyState">
            <div class="empty-state-icon" aria-hidden="true">&#10024;</div>
            <p class="empty-state-title">Ready for Analysis</p>
            <p class="empty-state-text">Select a module, enter your data, and click <strong>Analyze</strong> to generate grounded clinical output.</p>
          </div>
        </div>
        <div class="output-footer" role="contentinfo">
          <span>&#128274; Offline RAG Engine Active</span>
          <span>INR (&#8377;) Billing Mode</span>
        </div>
      </section>

    </div><!-- end content-area -->
  </div><!-- end app-layout -->

  <!-- MOBILE BOTTOM NAV -->
  <nav id="mobileNav" aria-label="Mobile module navigation">
    <div class="mobile-nav-inner">
      <button class="mobile-nav-btn active" id="mnav-prescription" onclick="mobileSwitchModule('prescription')" aria-label="Prescription Decoder">
        <span class="mn-icon" aria-hidden="true">&#128138;</span>Rx
      </button>
      <button class="mobile-nav-btn" id="mnav-bill_analysis" onclick="mobileSwitchModule('bill_analysis')" aria-label="Hospital Bill Auditor">
        <span class="mn-icon" aria-hidden="true">&#8377;</span>Bill
      </button>
      <button class="mobile-nav-btn" id="mnav-insurance" onclick="mobileSwitchModule('insurance')" aria-label="Insurance Explainer">
        <span class="mn-icon" aria-hidden="true">&#128737;&#65039;</span>Insure
      </button>
      <button class="mobile-nav-btn" id="mnav-pocket_doctor" onclick="mobileSwitchModule('pocket_doctor')" aria-label="Pocket Doctor Triage">
        <span class="mn-icon" aria-hidden="true">&#129658;</span>Doctor
      </button>
    </div>
  </nav>

  <div class="disclaimer-bar" role="note">
    &#9877;&#65039; <strong>Medical Disclaimer:</strong> VoiceMed is for educational decision-support only. Not a substitute for professional medical advice, diagnosis, or treatment.
  </div>

</div><!-- end mainApp -->

<script>
  /* ── CONFIG ── */
  const API_BASE    = 'http://127.0.0.1:8000';
  const API_PROCESS = API_BASE + '/api/process-medical';
  const API_HEALTH  = API_BASE + '/api/health';

  /* ── STATE ── */
  let state = { user: { name:'', age:'', lang:'English' }, module:'prescription', rawMarkdown:'', isLoading:false };

  /* ── MODULE META ── */
  const MODULE_META = {
    prescription:  { title:'Prescription Decoder & Safety Check',  desc:'Translate medical shorthand, check dosage safeguards, and get food-timing instructions.', btnText:'Decode Prescription', placeholder:'Paste prescription text (e.g. Tab. Augmentin 625mg 1-0-1 PC x 5 days)...' },
    bill_analysis: { title:'Hospital Bill Auditor (INR \u20B9)',       desc:'Audit itemized invoices in Indian Rupees, detect consumable markups, and categorize charges.', btnText:'Audit Hospital Bill', placeholder:'Paste hospital bill items with \u20B9 amounts (e.g. Room Rent: \u20B915,000)...' },
    insurance:     { title:'Insurance Claim Explainer',             desc:'Understand co-pays, room rent caps, pre-authorization terms, and TPA claim steps.', btnText:'Explain Insurance', placeholder:'Paste insurance policy clause or claim query...' },
    pocket_doctor: { title:'Pocket Doctor Triage',                  desc:'Analyze symptoms and receive structured urgency guidance with red-flag detection.', btnText:'Triage Symptoms', placeholder:'Describe symptoms in detail (e.g. Sudden chest tightness, shortness of breath, left arm pain for 30 minutes)...' },
  };

  /* ── SAMPLE DATA ── */
  const SAMPLE_DATA = {
    prescription:  'Patient: Rahul Sharma, Age: 45\nRx: Tab. Augmentin 625mg 1-0-1 PC x 5 days\nCap. Pantocid 40mg 1-0-0 AC x 7 days\nInj. Monocef 1g IV BD x 3 days\nAllergy: Nil. Diagnosis: URTI.',
    bill_analysis: 'INVOICE #8892 \u2014 Apollo Hospitals\nRoom Rent (Private Deluxe): \u20B915,000\nSurgeon Fees: \u20B930,000\nAnesthesia Fees: \u20B98,500\nConsumables & PPE Kit: \u20B99,500\nPharmacy & IV Fluids: \u20B911,200\nLab Tests (CBC, LFT, ECG): \u20B94,800\nTotal: \u20B979,000',
    insurance:     'Policy Clause: Room rent is capped at 1% of Sum Insured per day (\u20B95,000/day on a \u20B95 Lakh policy). Non-medical consumables excluded under List IV (IRDAI). Co-payment of 10% applies to non-network hospital claims.',
    pocket_doctor: 'Patient reports sudden severe chest tightness, shortness of breath, and left arm pain starting 30 minutes ago while resting. SpO2 dropped to 92%. No prior history of cardiac disease. Age 58, male.',
  };

  /* ── AUTH ── */
  function handleAuth(e) {
    e.preventDefault();
    const name = document.getElementById('userName').value.trim();
    const age  = document.getElementById('userAge').value.trim();
    const lang = document.getElementById('prefLang').value;
    if (!name || !age) { showToast('Please fill in all fields.', 'error'); return; }
    state.user = { name, age, lang };
    document.getElementById('profileDisplay').textContent = 'Logged in as ' + name + ' \u00B7 ' + age + ' yrs';
    document.getElementById('topLangSelect').value = lang;
    document.getElementById('inputAge').value = age;
    document.getElementById('authView').classList.add('hidden');
    document.getElementById('mainApp').classList.remove('hidden');
    showToast('Welcome, ' + name + '! Dashboard ready.', 'success');
    checkServerHealth();
  }

  function logout() {
    document.getElementById('mainApp').classList.add('hidden');
    document.getElementById('authView').classList.remove('hidden');
  }
  function syncLanguage(val) { state.user.lang = val; }

  /* ── HEALTH CHECK ── */
  async function checkServerHealth() {
    const dot = document.getElementById('statusDot');
    const txt = document.getElementById('statusText');
    try {
      const res = await fetch(API_HEALTH, { signal: AbortSignal.timeout(3000) });
      if (res.ok) { dot.className = 'status-dot online'; dot.setAttribute('aria-label','Server online'); txt.textContent = 'Online'; }
      else throw new Error();
    } catch { dot.className = 'status-dot offline'; dot.setAttribute('aria-label','Server offline'); txt.textContent = 'Offline \u2014 Run server.py'; }
  }
  setInterval(checkServerHealth, 5000);

  /* ── MODULE SWITCHING ── */
  const ALL_MODULES = ['prescription','bill_analysis','insurance','pocket_doctor'];
  function switchModule(mod) {
    state.module = mod;
    ALL_MODULES.forEach(m => {
      const sBtn = document.getElementById('nav-' + m);
      sBtn.classList.toggle('active', m === mod);
      sBtn.setAttribute('aria-current', m === mod ? 'true' : 'false');
      const mBtn = document.getElementById('mnav-' + m);
      if (mBtn) mBtn.classList.toggle('active', m === mod);
    });
    const meta = MODULE_META[mod];
    document.getElementById('moduleHeaderTitle').textContent = meta.title;
    document.getElementById('moduleHeaderDesc').textContent  = meta.desc;
    document.getElementById('mainInputText').placeholder     = meta.placeholder;
    document.getElementById('analyzeBtnText').textContent    = meta.btnText;
    resetOutput();
  }
  function mobileSwitchModule(mod) { switchModule(mod); showMobilePanel('input'); }

  /* ── MOBILE PANEL TOGGLE ── */
  function showMobilePanel(panel) {
    const ip = document.getElementById('inputPanel');
    const op = document.getElementById('outputPanel');
    const bi = document.getElementById('toggleInputBtn');
    const bo = document.getElementById('toggleOutputBtn');
    if (panel === 'input') {
      ip.classList.remove('mobile-hidden'); op.classList.add('mobile-hidden');
      bi.classList.add('active'); bi.setAttribute('aria-pressed','true');
      bo.classList.remove('active'); bo.setAttribute('aria-pressed','false');
    } else {
      op.classList.remove('mobile-hidden'); ip.classList.add('mobile-hidden');
      bo.classList.add('active'); bo.setAttribute('aria-pressed','true');
      bi.classList.remove('active'); bi.setAttribute('aria-pressed','false');
    }
  }

  /* ── SAMPLE DATA ── */
  function loadSampleData() {
    document.getElementById('mainInputText').value = SAMPLE_DATA[state.module];
    showToast('Sample data loaded.', 'success');
  }

  /* ── FILE UPLOAD ── */
  function handleDragOver(e) { e.preventDefault(); document.getElementById('dropZone').classList.add('drag-over'); }
  function handleDragLeave()  { document.getElementById('dropZone').classList.remove('drag-over'); }
  function handleDrop(e)      { e.preventDefault(); document.getElementById('dropZone').classList.remove('drag-over'); if(e.dataTransfer.files.length) processFile(e.dataTransfer.files[0]); }
  function handleFileSelect(e) { if(e.target.files.length) processFile(e.target.files[0]); }
  function processFile(file) {
    if (file.size > 10 * 1024 * 1024) { showToast('File exceeds 10 MB limit.', 'error'); return; }
    const lbl = document.getElementById('fileName');
    if (file.type.startsWith('text/')) {
      const reader = new FileReader();
      reader.onload = ev => { document.getElementById('mainInputText').value = ev.target.result; lbl.textContent = '\u2713 Loaded: ' + file.name; showToast('File loaded.', 'success'); };
      reader.readAsText(file);
    } else { lbl.textContent = '\uD83D\uDCCE Attached: ' + file.name; showToast('Image attached. Server will process on submit.', 'success'); }
  }

  /* ── SKELETON ── */
  function showSkeletonLoader() {
    document.getElementById('outputContainer').innerHTML =
      '<div role="status" aria-label="Loading analysis&hellip;" style="display:flex;flex-direction:column;gap:0;">' +
      '<div style="display:flex;align-items:center;gap:10px;margin-bottom:18px;"><div class="skeleton" style="width:32px;height:32px;border-radius:50%;flex-shrink:0;"></div><div style="flex:1;"><div class="skeleton sk-h4 sk-60" style="margin-bottom:6px;"></div><div class="skeleton sk-h3 sk-40"></div></div></div>' +
      '<div class="skeleton sk-h4 sk-full"></div><div class="skeleton sk-h3 sk-80" style="margin-top:8px;"></div>' +
      '<div class="skeleton sk-h3 sk-full" style="margin-top:8px;"></div><div class="skeleton sk-h3 sk-60" style="margin-top:8px;margin-bottom:18px;"></div>' +
      '<div class="skeleton sk-h4 sk-full"></div><div class="skeleton sk-h3 sk-80" style="margin-top:8px;"></div>' +
      '<div class="skeleton sk-h3 sk-full" style="margin-top:8px;"></div><div class="skeleton sk-h3 sk-40" style="margin-top:8px;"></div>' +
      '</div>';
  }

  /* ── RESET OUTPUT ── */
  function resetOutput() {
    state.rawMarkdown = '';
    document.getElementById('outputContainer').innerHTML =
      '<div class="empty-state"><div class="empty-state-icon" aria-hidden="true">&#10024;</div>' +
      '<p class="empty-state-title">Ready for Analysis</p>' +
      '<p class="empty-state-text">Enter data and click <strong>Analyze</strong> to generate grounded clinical output.</p></div>';
    ['copyBtn','saveBtn','audioBtn'].forEach(id => { document.getElementById(id).disabled = true; });
  }

  /* ── SUBMIT ANALYSIS — core API call ── */
  async function submitAnalysis() {
    if (state.isLoading) return;
    const input_text = document.getElementById('mainInputText').value.trim();
    if (!input_text) { showToast('Please enter text or load sample data.', 'error'); return; }

    state.isLoading = true;
    const analyzeBtn = document.getElementById('analyzeBtn');
    const btnText    = document.getElementById('analyzeBtnText');
    const btnIcon    = document.getElementById('analyzeBtnIcon');
    analyzeBtn.disabled = true;
    btnIcon.innerHTML   = '';
    btnText.innerHTML   = '<span style="display:inline-flex;align-items:center;gap:8px;"><span style="width:16px;height:16px;border:2px solid rgba(255,255,255,.4);border-top-color:#fff;border-radius:50%;display:inline-block;animation:spin 0.7s linear infinite;"></span>Analyzing&hellip;</span>';

    showSkeletonLoader();
    ['copyBtn','saveBtn','audioBtn'].forEach(id => { document.getElementById(id).disabled = true; });

    /* Build payload — exact keys the server expects */
    const payload = {
      feature:    state.module,          /* prescription | bill_analysis | insurance | pocket_doctor */
      input_text: input_text,
      language:   state.user.lang || 'English',
    };
    const age       = document.getElementById('inputAge').value.trim();
    const allergies = document.getElementById('inputAllergies').value.trim();
    if (age || allergies) {
      payload.user_context = {};
      if (age)       payload.user_context.patient_age = age;
      if (allergies) payload.user_context.allergies   = allergies;
    }

    try {
      const res  = await fetch(API_PROCESS, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload),
        signal:  AbortSignal.timeout(45000),
      });
      const data = await res.json();

      if (res.ok) {
        /* Server returns summary_text (not processed_summary) */
        state.rawMarkdown = data.summary_text || JSON.stringify(data, null, 2);
        const container = document.getElementById('outputContainer');
        container.innerHTML = '<div class="prose" role="document">' + marked.parse(state.rawMarkdown) + '</div>';

        /* Triage badge for pocket_doctor */
        if (state.module === 'pocket_doctor' && data.structured_data && data.structured_data.triage_level) {
          const lvl = String(data.structured_data.triage_level).toUpperCase();
          const cls = lvl.includes('EMERGENCY') ? 'badge-danger' : lvl.includes('URGENT') ? 'badge-warning' : lvl.includes('ROUTINE') ? 'badge-success' : 'badge-navy';
          const badge = document.createElement('div');
          badge.style.marginBottom = '12px';
          badge.innerHTML = '<span class="badge ' + cls + '" style="font-size:0.78rem;padding:4px 12px;">\uD83D\uDD34 Triage: ' + escapeHtml(lvl) + '</span>';
          container.prepend(badge);
        }

        ['copyBtn','saveBtn','audioBtn'].forEach(id => { document.getElementById(id).disabled = false; });
        if (window.innerWidth < 768) showMobilePanel('output');
        if (data.execution_time_ms) showToast('Analysis complete in ' + data.execution_time_ms + 'ms', 'success');
      } else {
        showErrorOutput('API Error (' + res.status + '): ' + (data.detail || JSON.stringify(data)));
      }
    } catch (err) {
      if (err.name === 'TimeoutError' || err.name === 'AbortError') {
        showErrorOutput('Request timed out after 45 seconds. The AI model may still be loading — try again.');
        showToast('Request timed out.', 'error');
      } else {
        showErrorOutput('Connection failed. Ensure server.py is running on port 8000.');
        showToast('Connection failed \u2014 is server.py running?', 'error');
      }
    } finally {
      state.isLoading = false;
      analyzeBtn.disabled = false;
      btnIcon.textContent = '\uD83D\uDD0D';
      btnText.textContent = MODULE_META[state.module].btnText;
    }
  }

  function showErrorOutput(msg) {
    document.getElementById('outputContainer').innerHTML =
      '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:200px;gap:10px;text-align:center;">' +
      '<div style="font-size:2rem;">\u26A0\uFE0F</div>' +
      '<p style="font-weight:600;color:var(--color-danger);font-size:0.9rem;">Analysis Failed</p>' +
      '<p style="font-size:0.8rem;color:var(--color-navy-light);max-width:280px;line-height:1.5;">' + escapeHtml(msg) + '</p></div>';
  }

  /* ── COPY ── */
  async function copySummary() {
    if (!state.rawMarkdown) return;
    try {
      await navigator.clipboard.writeText(state.rawMarkdown);
      const btn = document.getElementById('copyBtn');
      const orig = btn.textContent;
      btn.textContent = '\u2713 Copied!'; btn.style.color = 'var(--color-success)';
      setTimeout(() => { btn.textContent = orig; btn.style.color = ''; }, 2000);
      showToast('Copied to clipboard!', 'success');
    } catch { showToast('Clipboard access denied.', 'error'); }
  }

  /* ── DOWNLOAD ── */
  function downloadMarkdown() {
    if (!state.rawMarkdown) return;
    const fname = 'VoiceMed_' + state.module + '_' + new Date().toISOString().slice(0,10) + '.md';
    const blob  = new Blob([state.rawMarkdown], { type: 'text/markdown;charset=utf-8' });
    const url   = URL.createObjectURL(blob);
    const a     = Object.assign(document.createElement('a'), { href: url, download: fname });
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('Saved as ' + fname, 'success');
  }

  /* ── TTS ── */
  function playAudioSpeech() {
    if (!state.rawMarkdown) return;
    const audioBtn = document.getElementById('audioBtn');
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel(); audioBtn.textContent = '\uD83D\uDD0A Listen'; return;
    }
    const clean = state.rawMarkdown.replace(/[#*_`>~\[\]()]/g, '');
    const utt = new SpeechSynthesisUtterance(clean);
    const langMap = { Hindi:'hi-IN', Telugu:'te-IN', Tamil:'ta-IN', Bengali:'bn-IN', Marathi:'mr-IN', Spanish:'es-ES', English:'en-IN' };
    utt.lang = langMap[state.user.lang] || 'en-IN';
    utt.rate = 0.92; utt.pitch = 1.0;
    utt.onstart = () => { audioBtn.textContent = '\u23F9 Stop'; };
    utt.onend   = () => { audioBtn.textContent = '\uD83D\uDD0A Listen'; };
    utt.onerror = () => { audioBtn.textContent = '\uD83D\uDD0A Listen'; };
    window.speechSynthesis.speak(utt);
  }

  /* ── TOAST ── */
  function showToast(msg, type) {
    const c = document.getElementById('toastContainer');
    const t = document.createElement('div');
    t.className = 'toast' + (type ? ' ' + type : '');
    const icon = type === 'success' ? '\u2713' : type === 'error' ? '\u26A0' : '\u2139';
    t.innerHTML = '<span>' + icon + '</span><span>' + escapeHtml(msg) + '</span>';
    c.appendChild(t);
    setTimeout(() => { t.style.animation = 'toast-out 0.3s ease forwards'; setTimeout(() => t.remove(), 320); }, 3200);
  }

  /* ── UTILS ── */
  function escapeHtml(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

  /* ── MARKED CONFIG ── */
  marked.setOptions({ breaks: true, gfm: true });

  /* ── KEYBOARD SHORTCUTS ── */
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); if (!document.getElementById('mainApp').classList.contains('hidden')) submitAnalysis(); }
    if (e.key === 'Escape' && window.speechSynthesis.speaking) { window.speechSynthesis.cancel(); document.getElementById('audioBtn').textContent = '\uD83D\uDD0A Listen'; }
  });

  /* ── INIT ── */
  checkServerHealth();
</script>
</body>
</html>"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(HTML)

lines = HTML.count('\n')
size  = len(HTML.encode('utf-8'))
print(f"Written index.html: {lines} lines, {size:,} bytes")
