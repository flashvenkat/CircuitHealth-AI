import os
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Insert marked.js
content = content.replace('<!-- Lucide Icons -->', '<!-- Marked.js for Markdown Parsing -->\n  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>\n  <!-- Lucide Icons -->')

# Add prose CSS
css_to_add = """
    .pulse-glow {
      box-shadow: 0 0 20px rgba(16, 185, 129, 0.35);
    }
    /* Markdown Styling */
    .prose h1, .prose h2, .prose h3 {
      font-family: 'Outfit', sans-serif;
      font-weight: 700;
      color: #fff;
      margin-top: 1.25em;
      margin-bottom: 0.5em;
    }
    .prose h1 { font-size: 1.5rem; border-bottom: 1px solid #334155; padding-bottom: 0.3em; }
    .prose h2 { font-size: 1.25rem; }
    .prose h3 { font-size: 1.125rem; }
    .prose p { margin-bottom: 1em; color: #cbd5e1; }
    .prose ul { list-style-type: disc; padding-left: 1.5em; margin-bottom: 1em; color: #cbd5e1; }
    .prose ol { list-style-type: decimal; padding-left: 1.5em; margin-bottom: 1em; color: #cbd5e1; }
    .prose li { margin-bottom: 0.25em; }
    .prose strong { color: #f8fafc; font-weight: 600; }
    .prose em { color: #94a3b8; }
    .prose blockquote { border-left: 3px solid #34d399; padding-left: 1em; color: #94a3b8; font-style: italic; }
    .prose code { background-color: #1e293b; padding: 0.2em 0.4em; border-radius: 0.25em; font-family: monospace; font-size: 0.875em; color: #34d399; }
"""
content = content.replace("""    .pulse-glow {
      box-shadow: 0 0 20px rgba(16, 185, 129, 0.35);
    }""", css_to_add)

# Input Area Update
input_area_old = """          <!-- Textarea Input Area -->
          <div class="mt-4 flex-1 flex flex-col">
            <label for="medical-input" class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">Input Text / OCR Prescription / Bill Items</label>
            <textarea id="medical-input" rows="8" class="w-full flex-1 bg-slate-950/80 border border-slate-800 focus:border-brand-500 rounded-xl p-3.5 text-sm text-slate-100 placeholder:text-slate-600 focus:outline-none focus:ring-1 focus:ring-brand-500 font-mono resize-none transition" placeholder="Paste your prescription, hospital invoice, or query here..."></textarea>
          </div>"""

input_area_new = """          <!-- Textarea Input Area & Drop Zone -->
          <div class="mt-4 flex-1 flex flex-col relative group">
            <label for="medical-input" class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5 flex justify-between">
              <span>Input Text / OCR Data</span>
              <span class="text-brand-400 font-normal">Supports Drag & Drop</span>
            </label>
            <div class="relative flex-1 flex flex-col border-2 border-dashed border-slate-700/50 hover:border-brand-500/50 rounded-xl bg-slate-950/50 transition-colors group-hover:bg-slate-900/50">
              <textarea id="medical-input" rows="8" class="w-full flex-1 bg-transparent p-4 text-sm text-slate-100 placeholder:text-slate-600 focus:outline-none resize-none z-10" placeholder="Paste your prescription, hospital invoice, or query here... Alternatively, drop a file/image to extract."></textarea>
              <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none opacity-20 group-hover:opacity-40 transition-opacity">
                <i data-lucide="upload-cloud" class="w-12 h-12 text-slate-400 mb-2"></i>
                <span class="text-sm font-medium text-slate-300">Drop files to OCR</span>
              </div>
            </div>
          </div>"""
content = content.replace(input_area_old, input_area_new)

# Utilities Header Update
header_old = """            <!-- Multilingual Listen / Voice Button -->
            <button id="audio-btn" onclick="toggleAudioPlayback()" disabled class="flex items-center space-x-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-brand-400 border border-brand-500/30 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all shadow-sm">
              <i id="audio-icon" data-lucide="volume-2" class="w-4 h-4"></i>
              <span id="audio-btn-text">Listen to Summary</span>
            </button>
          </div>"""

header_new = """            <!-- Utility Buttons -->
            <div class="flex items-center space-x-2">
              <button id="copy-btn" onclick="copyReport()" disabled class="hidden sm:flex items-center space-x-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 border border-slate-700 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition-all">
                <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                <span>Copy</span>
              </button>
              <button id="download-btn" onclick="downloadReport()" disabled class="hidden sm:flex items-center space-x-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 border border-slate-700 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition-all">
                <i data-lucide="download" class="w-3.5 h-3.5"></i>
                <span>Save</span>
              </button>
              <!-- Multilingual Listen / Voice Button -->
              <button id="audio-btn" onclick="toggleAudioPlayback()" disabled class="flex items-center space-x-1.5 bg-brand-500/10 hover:bg-brand-500/20 disabled:opacity-40 disabled:cursor-not-allowed text-brand-400 border border-brand-500/30 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all shadow-sm pulse-glow">
                <i id="audio-icon" data-lucide="volume-2" class="w-4 h-4"></i>
                <span id="audio-btn-text">Listen</span>
              </button>
            </div>
          </div>"""
content = content.replace(header_old, header_new)

# Loader Update
loader_old = """            <!-- Loading Spinner -->
            <div id="loading-state" class="hidden flex-1 flex flex-col items-center justify-center p-12 space-y-4">
              <div class="w-10 h-10 border-4 border-brand-500/20 border-t-brand-400 rounded-full animate-spin"></div>
              <p class="text-xs text-slate-400 animate-pulse font-medium">Executing deterministic RAG & local AI inference...</p>
            </div>"""

loader_new = """            <!-- Glowing Skeleton Loading State -->
            <div id="loading-state" class="hidden flex-1 flex flex-col space-y-4 p-4">
              <div class="flex items-center space-x-3 mb-2">
                <div class="w-10 h-10 rounded-full bg-brand-500/20 animate-pulse border border-brand-500/30 flex items-center justify-center">
                  <i data-lucide="cpu" class="w-5 h-5 text-brand-400 animate-pulse"></i>
                </div>
                <div class="space-y-2 flex-1">
                  <div class="h-4 bg-slate-800/80 rounded w-1/3 animate-pulse"></div>
                  <div class="h-3 bg-slate-800/50 rounded w-1/4 animate-pulse"></div>
                </div>
              </div>
              <div class="space-y-3">
                <div class="h-3 bg-slate-800/60 rounded w-full animate-pulse"></div>
                <div class="h-3 bg-slate-800/60 rounded w-11/12 animate-pulse"></div>
                <div class="h-3 bg-slate-800/60 rounded w-4/5 animate-pulse"></div>
                <div class="h-24 bg-slate-800/40 rounded-xl w-full animate-pulse border border-slate-700/50 mt-4"></div>
              </div>
              <div class="text-center mt-6">
                <p class="text-xs text-brand-400 animate-pulse font-medium tracking-wide">Executing AI Inference & RAG...</p>
              </div>
            </div>"""
content = content.replace(loader_old, loader_new)

# Markdown integration
content = content.replace(
    '<div id="summary-text-rendered" class="text-sm leading-relaxed text-slate-200 whitespace-pre-line font-sans"></div>',
    '<div id="summary-text-rendered" class="prose text-sm leading-relaxed text-slate-200 font-sans"></div>'
)

# JS Buttons Integration
render_old = """      // Summary text
      document.getElementById("summary-text-rendered").innerText = data.summary_text;"""
render_new = """      // Summary text (Parsed with Markdown)
      document.getElementById("summary-text-rendered").innerHTML = marked.parse(data.summary_text);
      
      // Enable utility buttons
      document.getElementById("copy-btn").disabled = false;
      document.getElementById("download-btn").disabled = false;"""
content = content.replace(render_old, render_new)

# Disable buttons on click
js_disable = """      emptyState.classList.add("hidden");
      responseContent.classList.add("hidden");
      loadingState.classList.remove("hidden");
      processBtn.disabled = true;"""
js_disable_new = """      emptyState.classList.add("hidden");
      responseContent.classList.add("hidden");
      loadingState.classList.remove("hidden");
      processBtn.disabled = true;
      document.getElementById("copy-btn").disabled = true;
      document.getElementById("download-btn").disabled = true;"""
content = content.replace(js_disable, js_disable_new)

# JS Audio button disable state fix
audio_old = """        btn.className = "flex items-center space-x-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-brand-400 border border-brand-500/30 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all shadow-sm";
        icon.setAttribute("data-lucide", "volume-2");
        text.innerText = "Listen to Summary";"""
audio_new = """        btn.className = "flex items-center space-x-1.5 bg-brand-500/10 hover:bg-brand-500/20 disabled:opacity-40 disabled:cursor-not-allowed text-brand-400 border border-brand-500/30 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all shadow-sm pulse-glow";
        icon.setAttribute("data-lucide", "volume-2");
        text.innerText = "Listen";"""
content = content.replace(audio_old, audio_new)

# JS Function Definitions
funcs = """
    function copyReport() {
      if (!currentSpeechText) return;
      navigator.clipboard.writeText(currentSpeechText).then(() => {
        const btn = document.getElementById("copy-btn");
        const originalText = btn.innerHTML;
        btn.innerHTML = `<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-400"></i><span class="text-emerald-400">Copied</span>`;
        lucide.createIcons();
        setTimeout(() => { btn.innerHTML = originalText; lucide.createIcons(); }, 2000);
      });
    }

    function downloadReport() {
      if (!currentSpeechText) return;
      const blob = new Blob([currentSpeechText], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `VoiceMed_Report_${new Date().getTime()}.md`;
      a.click();
      URL.revokeObjectURL(url);
    }
"""
content = content.replace('// Browser Native Speech Synthesis (window.speechSynthesis)', funcs + '\\n    // Browser Native Speech Synthesis (window.speechSynthesis)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Frontend updated successfully!')
