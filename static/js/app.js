/**
 * app.js — AI Email Writer frontend logic
 * ========================================
 * Handles form interaction, API calls, output rendering,
 * copy/download, live counters, and toast notifications.
 */

'use strict';

/* ══════════════════════════════════════════════════════════════
   CONSTANTS
═══════════════════════════════════════════════════════════════ */
const API = {
  GENERATE : '/generate-email',
  HEALTH   : '/health',
  CLEAR    : '/clear',
};

const LOADING_STEPS = [
  'Analysing your request…',
  'Crafting the perfect tone…',
  'Writing the introduction…',
  'Building the email body…',
  'Polishing the closing…',
  'Finalising your email…',
];

/* ══════════════════════════════════════════════════════════════
   APPLICATION STATE
═══════════════════════════════════════════════════════════════ */
const state = {
  /** @type {'idle'|'loading'|'success'|'error'} */
  status : 'idle',
  /** @type {object|null} */
  email  : null,
  /** @type {string} */
  error  : '',
  /** @type {string} */
  errorDetail : '',
  /** @type {string} */
  selectedTone : '',
};

/* ══════════════════════════════════════════════════════════════
   DOM ELEMENT CACHE
═══════════════════════════════════════════════════════════════ */
const el = {
  // Form
  form          : document.getElementById('email-form'),
  subject       : document.getElementById('subject'),
  recipientName : document.getElementById('recipient_name'),
  senderName    : document.getElementById('sender_name'),
  emailType     : document.getElementById('email_type'),
  toneHidden    : document.getElementById('tone'),
  language      : document.getElementById('language'),
  purpose       : document.getElementById('purpose'),
  instructions  : document.getElementById('additional_instructions'),
  toneBtns      : document.querySelectorAll('.tone-btn'),

  // Counters
  subjectCounter      : document.getElementById('subject-counter'),
  purposeCounter      : document.getElementById('purpose-counter'),
  purposeWordCounter  : document.getElementById('purpose-word-counter'),
  instructionsCounter : document.getElementById('instructions-counter'),

  // Buttons
  btnGenerate   : document.getElementById('btn-generate'),
  btnRegenerate : document.getElementById('btn-regenerate'),
  btnClear      : document.getElementById('btn-clear'),
  btnCopy       : document.getElementById('btn-copy'),
  btnDownload   : document.getElementById('btn-download'),

  // Output panels
  outputEmpty   : document.getElementById('output-empty'),
  outputLoading : document.getElementById('output-loading'),
  outputError   : document.getElementById('output-error'),
  outputResult  : document.getElementById('output-result'),
  outputActions : document.getElementById('output-actions'),
  errorMsgText  : document.getElementById('error-msg-text'),
  errorDetail   : document.getElementById('error-detail'),
  loadingSteps  : document.getElementById('loading-steps'),

  // Result fields
  resultSubject   : document.getElementById('result-subject'),
  resultGreeting  : document.getElementById('result-greeting'),
  resultBody      : document.getElementById('result-body'),
  resultClosing   : document.getElementById('result-closing'),
  resultSignature : document.getElementById('result-signature'),
  resultEmailType : document.getElementById('result-email-type'),
  resultTone      : document.getElementById('result-tone'),
  statsWords      : document.getElementById('stats-words'),
  statsChars      : document.getElementById('stats-chars'),

  // Header
  providerName : document.getElementById('provider-name'),
  toast        : document.getElementById('toast'),
};

/* ══════════════════════════════════════════════════════════════
   API LAYER
═══════════════════════════════════════════════════════════════ */
const EmailAPI = {
  /**
   * POST /generate-email
   * @param {object} payload
   * @returns {Promise<object>}
   */
  async generate(payload) {
    const response = await fetch(API.GENERATE, {
      method  : 'POST',
      headers : { 'Content-Type': 'application/json' },
      body    : JSON.stringify(payload),
    });
    const data = await response.json();
    return { data, status: response.status };
  },

  /** GET /health */
  async health() {
    const response = await fetch(API.HEALTH);
    return response.json();
  },
};

/* ══════════════════════════════════════════════════════════════
   TOAST
═══════════════════════════════════════════════════════════════ */
let toastTimer = null;

function showToast(message, type = 'info', duration = 3000) {
  clearTimeout(toastTimer);
  el.toast.textContent = message;
  el.toast.className = `toast toast-${type} show`;
  toastTimer = setTimeout(() => el.toast.classList.remove('show'), duration);
}

/* ══════════════════════════════════════════════════════════════
   LOADING TICKER
═══════════════════════════════════════════════════════════════ */
let loadingTimer = null;

function startLoadingTicker() {
  let idx = 0;
  el.loadingSteps.textContent = LOADING_STEPS[0];
  loadingTimer = setInterval(() => {
    idx = (idx + 1) % LOADING_STEPS.length;
    el.loadingSteps.textContent = LOADING_STEPS[idx];
  }, 1200);
}

function stopLoadingTicker() {
  clearInterval(loadingTimer);
}

/* ══════════════════════════════════════════════════════════════
   STATE → UI RENDERER
═══════════════════════════════════════════════════════════════ */

function renderOutput() {
  // Hide all panels
  el.outputEmpty.classList.add('hidden');
  el.outputLoading.classList.add('hidden');
  el.outputError.classList.add('hidden');
  el.outputResult.classList.add('hidden');
  el.outputActions.classList.add('hidden');
  el.btnRegenerate.classList.add('hidden');

  switch (state.status) {

    case 'idle':
      el.outputEmpty.classList.remove('hidden');
      break;

    case 'loading':
      el.outputLoading.classList.remove('hidden');
      el.btnGenerate.disabled = true;
      el.btnGenerate.classList.add('loading');
      el.btnGenerate.textContent = 'Generating…';
      startLoadingTicker();
      break;

    case 'success': {
      stopLoadingTicker();
      resetGenerateButton();

      el.outputResult.classList.remove('hidden');
      el.outputActions.classList.remove('hidden');
      el.btnRegenerate.classList.remove('hidden');

      const { email } = state;
      if (!email) break;

      el.resultSubject.textContent   = email.subject   || '';
      el.resultGreeting.textContent  = email.greeting  || '';
      el.resultBody.textContent      = email.body      || '';
      el.resultClosing.textContent   = email.closing   || '';
      el.resultSignature.textContent = email.signature || '';

      el.resultEmailType.textContent = el.emailType.value || '';
      el.resultTone.textContent      = state.selectedTone  || '';

      const fullText = buildFullEmailText(email);
      const wordCount = fullText.trim().split(/\s+/).filter(Boolean).length;
      el.statsWords.textContent = `${wordCount} words`;
      el.statsChars.textContent = `${fullText.length.toLocaleString()} characters`;
      break;
    }

    case 'error':
      stopLoadingTicker();
      resetGenerateButton();

      el.outputError.classList.remove('hidden');
      el.errorMsgText.textContent = state.error || 'An unknown error occurred.';

      if (state.errorDetail) {
        el.errorDetail.textContent    = state.errorDetail;
        el.errorDetail.style.display  = 'block';
      } else {
        el.errorDetail.style.display  = 'none';
      }
      break;
  }
}

function resetGenerateButton() {
  el.btnGenerate.disabled = false;
  el.btnGenerate.classList.remove('loading');
  el.btnGenerate.innerHTML =
    '<span class="btn-icon-left" aria-hidden="true">✨</span> Generate Email';
}

/* ══════════════════════════════════════════════════════════════
   FORM HELPERS
═══════════════════════════════════════════════════════════════ */

function collectFormData() {
  return {
    subject                : el.subject.value.trim(),
    recipient_name         : el.recipientName.value.trim(),
    sender_name            : el.senderName.value.trim(),
    email_type             : el.emailType.value,
    tone                   : el.toneHidden.value,
    language               : el.language.value,
    purpose                : el.purpose.value.trim(),
    additional_instructions: el.instructions.value.trim(),
  };
}

function validateForm(data) {
  if (!data.subject)        return { valid: false, message: 'Please enter an email subject.' };
  if (!data.recipient_name) return { valid: false, message: 'Please enter the recipient name.' };
  if (!data.sender_name)    return { valid: false, message: 'Please enter your name.' };
  if (!data.email_type)     return { valid: false, message: 'Please select an email type.' };
  if (!data.tone)           return { valid: false, message: 'Please select a tone.' };
  if (!data.purpose)        return { valid: false, message: 'Please describe the purpose of this email.' };
  return { valid: true, message: '' };
}

function clearForm() {
  el.form.reset();
  el.toneHidden.value = '';
  state.selectedTone  = '';
  el.toneBtns.forEach(btn => btn.classList.remove('active'));
  updateCounter(el.subjectCounter,      '', 200);
  updateCounter(el.purposeCounter,      '', 1000);
  updateCounter(el.instructionsCounter, '', 500);
  el.purposeWordCounter.textContent = '0 words';
  el.form.querySelectorAll('.error').forEach(f => f.classList.remove('error'));
  state.status = 'idle';
  state.email  = null;
  state.error  = '';
  state.errorDetail = '';
  renderOutput();
  showToast('Form cleared.', 'info', 2000);
}

/* ══════════════════════════════════════════════════════════════
   COUNTERS
═══════════════════════════════════════════════════════════════ */

function updateCounter(counterEl, value, max) {
  const len = value.length;
  counterEl.textContent = `${len} / ${max}`;
  counterEl.style.color = len > max * 0.9 ? '#a78bfa' : '';
}

function countWords(text) {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

/* ══════════════════════════════════════════════════════════════
   EMAIL TEXT BUILDER
═══════════════════════════════════════════════════════════════ */

function buildFullEmailText(email) {
  return [
    `Subject: ${email.subject || ''}`,
    '',
    email.greeting  || '',
    '',
    email.body      || '',
    '',
    email.closing   || '',
    '',
    email.signature || '',
  ].join('\n');
}

/* ══════════════════════════════════════════════════════════════
   COPY & DOWNLOAD
═══════════════════════════════════════════════════════════════ */

async function copyEmail() {
  if (!state.email) return;
  const text = buildFullEmailText(state.email);
  try {
    await navigator.clipboard.writeText(text);
    showToast('✅ Email copied to clipboard!', 'success');
  } catch {
    // Fallback
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.cssText = 'position:fixed;opacity:0;top:0;left:0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showToast('✅ Email copied!', 'success');
  }
}

function downloadEmail() {
  if (!state.email) return;
  const text     = buildFullEmailText(state.email);
  const subject  = (state.email.subject || 'email').replace(/[^a-z0-9]/gi, '_').toLowerCase();
  const filename = `email_${subject}_${Date.now()}.txt`;
  const blob     = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url      = URL.createObjectURL(blob);
  const link     = document.createElement('a');
  link.href     = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
  showToast('💾 Email downloaded!', 'success');
}

/* ══════════════════════════════════════════════════════════════
   HEALTH CHECK
═══════════════════════════════════════════════════════════════ */

async function loadHealthStatus() {
  try {
    const data = await EmailAPI.health();
    if (data.ai_provider) {
      const labels = {
        openai      : '🤖 OpenAI',
        gemini      : '♊ Gemini',
        ollama      : '🦙 Ollama',
        huggingface : '🤗 HuggingFace',
      };
      el.providerName.textContent = labels[data.ai_provider.toLowerCase()] || data.ai_provider;
    }
  } catch {
    el.providerName.textContent = 'Offline';
  }
}

/* ══════════════════════════════════════════════════════════════
   MAIN GENERATE HANDLER
═══════════════════════════════════════════════════════════════ */

async function handleGenerate(e) {
  if (e) e.preventDefault();

  const data = collectFormData();
  const { valid, message } = validateForm(data);
  if (!valid) {
    showToast(`⚠️ ${message}`, 'error', 4000);
    highlightMissingField(data);
    return;
  }

  state.status      = 'loading';
  state.email       = null;
  state.error       = '';
  state.errorDetail = '';
  renderOutput();

  try {
    const { data: result, status: httpStatus } = await EmailAPI.generate(data);

    if (result.success && result.email) {
      state.status = 'success';
      state.email  = result.email;
      showToast('✅ Email generated successfully!', 'success');
    } else {
      state.status = 'error';
      // Provide helpful context based on HTTP status
      if (httpStatus === 503) {
        state.error = 'The AI provider is unavailable. Check your API key or network connection.';
        state.errorDetail = result.error || '';
      } else if (httpStatus === 422 || httpStatus === 400) {
        state.error = result.error || 'Invalid request. Please check your inputs.';
      } else {
        state.error = result.error || `Server returned status ${httpStatus}.`;
      }
    }

  } catch (err) {
    state.status = 'error';

    // Distinguish fetch (network) errors from other JS errors
    const isNetworkErr = err instanceof TypeError && (
      err.message.toLowerCase().includes('fetch') ||
      err.message.toLowerCase().includes('network') ||
      err.message.toLowerCase().includes('failed')
    );

    if (isNetworkErr) {
      state.error = 'Cannot reach the server.';
      state.errorDetail =
        'Make sure the Flask backend is running:\n' +
        '  python app.py\n\n' +
        'Then open http://localhost:5000 in your browser.';
    } else {
      state.error       = 'An unexpected error occurred.';
      state.errorDetail = err.message;
    }
  }

  renderOutput();
}

function highlightMissingField(data) {
  const map = {
    subject       : el.subject,
    recipient_name: el.recipientName,
    sender_name   : el.senderName,
    email_type    : el.emailType,
    purpose       : el.purpose,
  };
  Object.entries(map).forEach(([key, inputEl]) => {
    if (!data[key]) {
      inputEl.classList.add('error');
      inputEl.addEventListener('input', () => inputEl.classList.remove('error'), { once: true });
    }
  });
  if (!data.tone) {
    el.toneBtns.forEach(btn => { btn.style.borderColor = '#f87171'; });
    setTimeout(() => el.toneBtns.forEach(btn => { btn.style.borderColor = ''; }), 2000);
  }
}

/* ══════════════════════════════════════════════════════════════
   EVENT LISTENERS
═══════════════════════════════════════════════════════════════ */

function bindEvents() {
  el.form.addEventListener('submit', handleGenerate);
  el.btnRegenerate.addEventListener('click', handleGenerate);
  el.btnClear.addEventListener('click', clearForm);
  el.btnCopy.addEventListener('click', copyEmail);
  el.btnDownload.addEventListener('click', downloadEmail);

  // Tone selector
  el.toneBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      el.toneBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.selectedTone  = btn.dataset.tone;
      el.toneHidden.value = btn.dataset.tone;
    });
  });

  // Live counters
  el.subject.addEventListener('input', () =>
    updateCounter(el.subjectCounter, el.subject.value, 200));

  el.purpose.addEventListener('input', () => {
    updateCounter(el.purposeCounter, el.purpose.value, 1000);
    el.purposeWordCounter.textContent = `${countWords(el.purpose.value)} words`;
  });

  el.instructions.addEventListener('input', () =>
    updateCounter(el.instructionsCounter, el.instructions.value, 500));

  // Keyboard shortcut: Ctrl / Cmd + Enter
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleGenerate(null);
    }
  });
}

/* ══════════════════════════════════════════════════════════════
   INIT
═══════════════════════════════════════════════════════════════ */

function init() {
  bindEvents();
  loadHealthStatus();
  renderOutput();

  console.log('%c✉️ AI Email Writer', 'font-size:18px;font-weight:bold;color:#8b5cf6;');
  console.log('%cv1.0 — Ctrl+Enter to generate', 'color:#6e6e88;');
}

document.readyState === 'loading'
  ? document.addEventListener('DOMContentLoaded', init)
  : init();
