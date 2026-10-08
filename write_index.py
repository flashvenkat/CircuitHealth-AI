html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VoiceMed Open \u2014 Intelligent Medical Decision Support</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
        .glass-card { background: rgba(255,255,255,0.03); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.08); }
        .glow-teal { box-shadow: 0 0 40px -10px rgba(20,184,166,0.25); }
        .prose-result h1,.prose-result h2,.prose-result h3 { color: #e2e8f0; font-weight: 700; margin-bottom: 0.5rem; margin-top: 1rem; }
        .prose-result p { color: #94a3b8; margin-bottom: 0.5rem; line-height: 1.7; }
        .prose-result ul,.prose-result ol { color: #94a3b8; padding-left: 1.25rem; margin-bottom: 0.5rem; }
        .prose-result li { margin-bottom: 0.25rem; }
        .prose-result strong { color: #e2e8f0; }
        .prose-result code { background: rgba(255,255,255,0.06); padding: 0.1rem 0.4rem; border-radius: 0.25rem; font-size: 0.8em; }
        .prose-result blockquote { border-left: 3px solid #14b8a6; padding-left: 1rem; color: #64748b; font-style: italic; margin: 0.75rem 0; }
        .prose-result hr { border-color: rgba(255,255,255,0.08); margin: 1rem 0; }
    </style>
</head>
<body class="bg-[#07090e] text-slate-100 min-h-screen flex flex-col selection:bg-teal-500 selection:text-black">

    <!-- AUTH / ONBOARDING VIEW -->
    <div id="authView" class="fixed inset-0 z-50 flex items-center justify-center bg-[#07090e]/95 backdrop-blur-xl p-4">
        <div class="max-w-md w-full glass-card p-8 rounded-3xl glow-teal">
            <div class="text-center mb-8">
                <div class="inline-flex bg-teal-500 text-black p-3 rounded-2xl font-bold text-2xl mb-3 shadow-lg shadow-teal-500/20">\U0001f3e5</div>
                <h2 class="text-2xl font-bold text-white tracking-tight">Welcome to VoiceMed Open</h2>
                <p class="text-sm text-slate-400 mt-1">Secure, offline-first multilingual clinical companion</p>
            </div>
            <form id="authForm" onsubmit="handleAuth(event)" class="space-y-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-400 uppercase mb-1.5">Full Name</label>
                    <input type="text" id="userName" required placeholder="e.g. Rahul Sharma" class="w-full bg-slate-900/80 border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-teal-500 text-slate-200">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-400 uppercase mb-1.5">Patient Age</label>
                    <input type="number" id="userAge" required placeholder="e.g. 28" class="w-full bg-slate-900/80 border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-teal-500 text-slate-200">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-400 uppercase mb-1.5">Preferred Language</label>
                    <select id="prefLang" class="w-full bg-slate-900/80 border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-teal-500 text-slate-200">
                        <option value="English">English (en-IN)</option>
                        <option value="Hindi">Hindi (\u0939\u093f\u0902\u0926\u0940)</option>
                        <option value="Telugu">Telugu (\u0c24\u0c46\u0c32\u0c41\u0c17\u0c41)</option>
                        <option value="Spanish">Spanish (espa\u00f1ol)</option>
                    </select>
                </div>
                <button type="submit" class="w-full bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold py-3.5 rounded-xl transition shadow-lg shadow-teal-500/10 mt-2">Launch Clinical Dashboard</button>
            </form>
        </div>
    </div>

    <!-- MAIN DASHBOARD VIEW -->
    <div id="mainApp" class="flex-1 flex flex-col hidden">
        <!-- Sticky Navbar -->
        <header class="border-b border-slate-800/80 bg-[#0b0e17]/80 backdrop-blur-md sticky top-0 z-40 px-6 py-4">
            <div class="max-w-7xl mx-auto flex justify-between items-center">
                <div class="flex items-center gap-3">
                    <div class="bg-teal-500 text-black p-2 rounded-xl font-bold text-lg">\U0001f3e5</div>
                    <div>
                        <h1 class="font-bold text-white flex items-center gap-2 text-sm">VoiceMed Open <span class="text-[10px] bg-teal-950 text-teal-300 px-2 py-0.5 rounded-full border border-teal-800/60">v2.1 PRO</span></h1>
                        <p class="text-xs text-slate-400">Logged in as <span id="profileNameDisplay" class="text-teal-400 font-semibold"></span> &middot; <span id="profileAgeDisplay"></span> yrs</p>
                    </div>
                </div>
                <div class="flex items-center gap-3">
                    <div class="hidden sm:flex items-center gap-2 bg-slate-900 px-3 py-1.5 rounded-full border border-slate-800 text-xs">
                        <span id="statusDot" class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
                        <span id="statusText">Connecting...</span>
                    </div>
                    <select id="topLangSelect" onchange="syncLanguage(this.value)" class="bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-1.5 text-xs focus:outline-none focus:border-teal-500">
                        <option value="English">English</option>
                        <option value="Hindi">Hindi</option>
                        <option value="Telugu">Telugu</option>
                        <option value="Spanish">Spanish</option>
                    </select>
                    <button onclick="logout()" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-xl border border-slate-700 transition">Switch Profile</button>
                </div>
            </div>
        </header>

        <!-- Main Workspace -->
        <main class="flex-1 max-w-7xl w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">

            <!-- Left Sidebar -->
            <div class="lg:col-span-3 space-y-4">
                <div class="glass-card p-4 rounded-2xl">
                    <h3 class="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-3 px-1">Clinical Modules</h3>
                    <div class="space-y-1.5">
                        <button onclick="switchModule('prescription')" id="nav-prescription" class="w-full text-left p-3 rounded-xl border border-teal-500/50 bg-teal-500/10 text-teal-300 font-medium transition flex items-center justify-between text-sm">
                            <span>\U0001f48a Prescription Decoder</span>
                        </button>
                        <button onclick="switchModule('bill_analysis')" id="nav-bill_analysis" class="w-full text-left p-3 rounded-xl border border-transparent hover:bg-slate-900/60 text-slate-300 font-medium transition flex items-center justify-between text-sm">
                            <span>\u20b9 Hospital Bill Auditor</span>
                        </button>
                        <button onclick="switchModule('insurance')" id="nav-insurance" class="w-full text-left p-3 rounded-xl border border-transparent hover:bg-slate-900/60 text-slate-300 font-medium transition flex items-center justify-between text-sm">
                            <span>\U0001f6e1\ufe0f Insurance Explainer</span>
                        </button>
                        <button onclick="switchModule('pocket_doctor')" id="nav-pocket_doctor" class="w-full text-left p-3 rounded-xl border border-transparent hover:bg-slate-900/60 text-slate-300 font-medium transition flex items-center justify-between text-sm">
                            <span>\U0001fa7a Pocket Doctor Triage</span>
                        </button>
                    </div>
                </div>
                <div class="glass-card p-4 rounded-2xl text-xs space-y-2 text-slate-400">
                    <div class="flex justify-between font-semibold text-slate-300">
                        <span>Drug Knowledge Base</span>
                        <span class="text-teal-400">20 Profiles</span>
                    </div>
                    <p>Formulary verified with max dosages &amp; food timing directives via local RAG engine.</p>
                </div>
            </div>

            <!-- Center Input Panel -->
            <div class="lg:col-span-5 glass-card p-6 rounded-2xl flex flex-col justify-between shadow-xl">
                <div>
                    <div class="flex justify-between items-center mb-2">
                        <h2 id="moduleHeaderTitle" class="font-bold text-base text-white">Prescription Decoder &amp; Safety Check</h2>
                        <button onclick="loadSampleData()" class="text-xs bg-slate-800 hover:bg-slate-700 text-teal-400 border border-slate-700/60 px-3 py-1.5 rounded-lg transition">Load Sample</button>
                    </div>
                    <p id="moduleHeaderDesc" class="text-xs text-slate-400 mb-4">Translate medical shorthand and check drug dosage safeguards.</p>
                    <div class="mb-4">
                        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Input Text or OCR Data</label>
                        <textarea id="mainInputText" rows="7" class="w-full bg-slate-900/90 border border-slate-800 rounded-xl p-3.5 text-sm focus:outline-none focus:border-teal-500 text-slate-200 placeholder-slate-600 shadow-inner resize-none" placeholder="Paste prescription text, hospital bill, insurance clause, or symptom description..."></textarea>
                    </div>
                    <div class="grid grid-cols-2 gap-3 mb-6">
                        <div>
                            <label class="block text-[10px] font-semibold text-slate-500 uppercase mb-1">Patient Age</label>
                            <input type="text" id="inputAge" class="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-teal-500 text-slate-300" placeholder="e.g. 45">
                        </div>
                        <div>
                            <label class="block text-[10px] font-semibold text-slate-500 uppercase mb-1">Allergies / Notes</label>
                            <input type="text" id="inputAllergies" class="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-teal-500 text-slate-300" placeholder="e.g. Penicillin">
                        </div>
                    </div>
                </div>
                <button onclick="submitAnalysis()" class="w-full bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold py-3.5 rounded-xl transition shadow-lg shadow-teal-500/10 text-sm">
                    Analyze &amp; Simplify
                </button>
            </div>

            <!-- Right Output Panel -->
            <div class="lg:col-span-4 glass-card p-6 rounded-2xl flex flex-col justify-between shadow-xl">
                <div class="flex-1 flex flex-col">
                    <div class="flex justify-between items-center mb-4 pb-3 border-b border-slate-800">
                        <h2 class="font-bold text-sm text-white">Clinical Guidance &amp; Summary</h2>
                        <div class="flex items-center gap-1.5">
                            <button onclick="copySummary()" id="copyBtn" disabled class="text-[11px] bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 px-2.5 py-1 rounded-lg disabled:opacity-40 transition">Copy</button>
                            <button onclick="downloadMarkdown()" id="saveBtn" disabled class="text-[11px] bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 px-2.5 py-1 rounded-lg disabled:opacity-40 transition">Save</button>
                            <button onclick="playAudioSpeech()" id="audioBtn" disabled class="text-[11px] bg-indigo-950 hover:bg-indigo-900 text-indigo-300 border border-indigo-800 px-2.5 py-1 rounded-lg disabled:opacity-40 transition">Listen</button>
                        </div>
                    </div>
                    <div id="outputContainer" class="flex-1 min-h-[340px] max-h-[460px] overflow-y-auto bg-slate-900/50 border border-slate-800/80 rounded-xl p-4 text-sm text-slate-300">
                        <div class="flex flex-col items-center justify-center h-64 text-center text-slate-500">
                            <div class="w-10 h-10 rounded-full bg-slate-800/60 flex items-center justify-center text-lg mb-2">\u2728</div>
                            <p class="text-xs font-medium">Ready for Analysis</p>
                            <p class="text-[11px] text-slate-600 mt-1 max-w-[200px]">Select a module, input data, and click Analyze to generate grounded clinical output.</p>
                        </div>
                    </div>
                </div>
                <div class="mt-4 pt-3 border-t border-slate-800/80 text-[10px] text-slate-500 flex justify-between items-center">
                    <span>Offline RAG Engine Active</span>
                    <span>INR (\u20b9) Billing Mode</span>
                </div>
            </div>

        </main>
    </div>

    <script>
        let currentUser = { name: '', age: '', lang: 'English' };
        let currentModule = 'prescription';
        let rawMarkdownResult = '';

        function handleAuth(e) {
            e.preventDefault();
            const name = document.getElementById('userName').value.trim();
            const age  = document.getElementById('userAge').value.trim();
            const lang = document.getElementById('prefLang').value;
            if (!name || !age) return;
            currentUser = { name, age, lang };
            document.getElementById('profileNameDisplay').innerText = name;
            document.getElementById('profileAgeDisplay').innerText  = age;
            document.getElementById('topLangSelect').value = lang;
            document.getElementById('inputAge').value = age;
            document.getElementById('authView').classList.add('hidden');
            document.getElementById('mainApp').classList.remove('hidden');
        }

        function logout() {
            document.getElementById('mainApp').classList.add('hidden');
            document.getElementById('authView').classList.remove('hidden');
        }

        function syncLanguage(val) { currentUser.lang = val; }

        async function checkServerHealth() {
            try {
                const res = await fetch('http://127.0.0.1:8000/api/health');
                if (res.ok) {
                    document.getElementById('statusDot').className  = 'w-2 h-2 rounded-full bg-emerald-400';
                    document.getElementById('statusText').innerText = 'Online (Connected)';
                } else { throw new Error(); }
            } catch (e) {
                document.getElementById('statusDot').className  = 'w-2 h-2 rounded-full bg-rose-500';
                document.getElementById('statusText').innerText = 'Offline \u2014 Run server.py';
            }
        }
        setInterval(checkServerHealth, 4000);
        checkServerHealth();

        function switchModule(mod) {
            currentModule = mod;
            ['prescription','bill_analysis','insurance','pocket_doctor'].forEach(m => {
                document.getElementById('nav-' + m).className = m === mod
                    ? 'w-full text-left p-3 rounded-xl border border-teal-500/50 bg-teal-500/10 text-teal-300 font-medium transition flex items-center justify-between text-sm'
                    : 'w-full text-left p-3 rounded-xl border border-transparent hover:bg-slate-900/60 text-slate-300 font-medium transition flex items-center justify-between text-sm';
            });
            const meta = {
                prescription:  ['Prescription Decoder & Safety Check',  'Translate medical shorthand and check drug dosage safeguards.'],
                bill_analysis: ['Hospital Bill Auditor (INR \u20b9)',         'Audit invoices, detect consumable markups, and categorize charges.'],
                insurance:     ['Insurance Claim Explainer',             'Understand co-pays, room rent caps, and pre-authorization terms.'],
                pocket_doctor: ['Pocket Doctor Triage',                  'Analyze symptoms and receive structured urgency guidance.'],
            };
            document.getElementById('moduleHeaderTitle').innerText = meta[mod][0];
            document.getElementById('moduleHeaderDesc').innerText  = meta[mod][1];
        }

        function loadSampleData() {
            const n = currentUser.name || 'Patient';
            const samples = {
                prescription:  'Patient: ' + n + '\\nRx: Tab. Augmentin 625mg 1-0-1 PC x 5 days\\nCap. Pantocid 40mg 1-0-0 AC x 7 days\\nInj. Monocef 1g IV BD',
                bill_analysis: 'INVOICE #8892\\nRoom Rent (Private): \u20b915,000\\nSurgeon Fees: \u20b930,000\\nConsumables & PPE: \u20b99,500\\nPharmacy & IV Fluids: \u20b911,200\\nTotal: \u20b965,700',
                insurance:     'Policy Clause: Room rent is capped at 1% of Sum Insured (\u20b95,000/day). Non-medical consumables are excluded under list IV.',
                pocket_doctor: 'Patient reports sudden chest tightness, shortness of breath, and left arm pain starting 30 minutes ago while resting.',
            };
            document.getElementById('mainInputText').value = samples[currentModule];
        }

        async function submitAnalysis() {
            const input_text = document.getElementById('mainInputText').value.trim();
            const language   = currentUser.lang || 'English';
            if (!input_text) { alert('Please enter text or load sample data.'); return; }

            document.getElementById('outputContainer').innerHTML =
                '<div class="flex flex-col items-center justify-center h-64 space-y-3">' +
                '<div class="w-7 h-7 border-2 border-teal-500 border-t-transparent rounded-full animate-spin"></div>' +
                '<p class="text-xs text-teal-400 font-medium animate-pulse">Synthesizing Clinical RAG + Local SLM...</p>' +
                '</div>';
            ['copyBtn','saveBtn','audioBtn'].forEach(id => document.getElementById(id).disabled = true);

            try {
                const res  = await fetch('http://127.0.0.1:8000/api/process-medical', {
                    method:  'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body:    JSON.stringify({ feature_type: currentModule, input_text, language }),
                });
                const data = await res.json();
                if (res.ok) {
                    rawMarkdownResult = data.processed_summary || JSON.stringify(data, null, 2);
                    document.getElementById('outputContainer').innerHTML =
                        '<div class="prose-result">' + marked.parse(rawMarkdownResult) + '</div>';
                    ['copyBtn','saveBtn','audioBtn'].forEach(id => document.getElementById(id).disabled = false);
                } else {
                    document.getElementById('outputContainer').innerHTML =
                        '<p class="text-rose-400 text-xs">' + JSON.stringify(data) + '</p>';
                }
            } catch (e) {
                document.getElementById('outputContainer').innerHTML =
                    '<p class="text-rose-400 text-xs">Connection failed. Ensure server.py is running on port 8000.</p>';
            }
        }

        function copySummary() {
            navigator.clipboard.writeText(rawMarkdownResult);
            const btn = document.getElementById('copyBtn');
            btn.innerText = 'Copied!';
            setTimeout(() => { btn.innerText = 'Copy'; }, 2000);
        }

        function downloadMarkdown() {
            const blob = new Blob([rawMarkdownResult], { type: 'text/markdown' });
            const url  = URL.createObjectURL(blob);
            const a    = document.createElement('a');
            a.href = url; a.download = 'VoiceMed_Clinical_Report.md'; a.click();
        }

        function playAudioSpeech() {
            if (!rawMarkdownResult) return;
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(rawMarkdownResult.replace(/[#*_`>]/g, ''));
            const langMap   = { Hindi: 'hi-IN', Telugu: 'te-IN', Spanish: 'es-ES' };
            utterance.lang  = langMap[currentUser.lang] || 'en-US';
            window.speechSynthesis.speak(utterance);
        }
    </script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully written premium index.html!")
