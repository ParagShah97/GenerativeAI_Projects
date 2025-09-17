// === CONFIG ===
const API_URL = "http://127.0.0.1:8000/complete_once"; // one-shot endpoint
const DEBOUNCE_MS = 500;
const MIN_CHARS = 20;  // min length of fragment since last '.' before calling

// === INIT QUILL ===
const quill = new Quill('#editor', { theme: 'snow' });

// === STATE ===
let ghost;                         // overlay node
let currentSuggestion = "";
let lastSentPrefix = "";
let inflightController = null;
let lastCaretIndex = 0;
let latestRequestId = 0;
let blockSuggestionsUntilType = false; // true right after accept; cleared on next user keystroke

// === UTILS ===
function makeDebounce(fn, ms) {
  let t = null;
  const debounced = (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
  debounced.cancel = () => { clearTimeout(t); t = null; };
  return debounced;
}

/** Mount ghost OVERLAY as a sibling of .ql-editor (inside .ql-container) */
function ensureGhostMounted() {
  const container = quill.container; // .ql-container
  if (!container) return;

  const cs = window.getComputedStyle(container);
  if (cs.position === "static") container.style.position = "relative";

  if (!ghost || !container.contains(ghost)) {
    ghost = document.createElement("div");
    ghost.className = "ghost-suggestion";
    container.appendChild(ghost);
  }
}

/** Plain text up to caret */
function getPrefixUpToCaret() {
  const sel = quill.getSelection();
  if (!sel) return "";
  const idx = Math.max(0, Math.min(sel.index, quill.getLength() - 1));
  return quill.getText(0, idx);
}

/** Only the fragment since the last '.' (or the whole text if none) */
function getSentencePrefixUpToCaret() {
  const uptoCaret = getPrefixUpToCaret();
  const lastDot = uptoCaret.lastIndexOf(".");
  return lastDot >= 0 ? uptoCaret.slice(lastDot + 1).trimStart() : uptoCaret;
}

/** Position ghost relative to container using editor bounds + offsets */
function positionGhostAtCaret() {
  if (!ghost) return;
  const sel = quill.getSelection();
  if (!sel) return;

  lastCaretIndex = sel.index;

  const editor = quill.root;         // .ql-editor
  const safeIdx = Math.max(0, Math.min(sel.index, quill.getLength() - 1));
  const b = quill.getBounds(safeIdx);
  if (!b) return;

  const top  = editor.offsetTop - editor.scrollTop  + b.top;
  const left = editor.offsetLeft - editor.scrollLeft + b.left;

  ghost.style.top = `${top}px`;
  ghost.style.left = `${left}px`;
  ghost.style.display = currentSuggestion ? "block" : "none";

  const cs = window.getComputedStyle(editor);
  ghost.style.fontFamily = cs.fontFamily;
  ghost.style.fontSize   = cs.fontSize;
  ghost.style.lineHeight = cs.lineHeight;
}

/** Clear ghost text */
function clearSuggestion() {
  currentSuggestion = "";
  if (ghost) { ghost.textContent = ""; ghost.style.display = "none"; }
}

/** Accept suggestion; prevent double spaces; then block further suggestions until user types */
function acceptSuggestion() {
  if (!currentSuggestion) return;

  quill.focus();

  let sel = quill.getSelection();
  let idx = sel && typeof sel.index === "number" ? sel.index : lastCaretIndex;
  if (typeof idx !== "number") idx = Math.max(0, quill.getLength() - 1);

  const prevChar = idx > 0 ? quill.getText(idx - 1, 1) : "";
  let toInsert = currentSuggestion;

  // Avoid extra space if both sides are whitespace
  if (/^\s/.test(toInsert) && /\s/.test(prevChar)) {
    toInsert = toInsert.replace(/^\s+/, "");
  }
  if (!toInsert) { clearSuggestion(); return; }

  quill.insertText(idx, toInsert, "user");
  quill.setSelection(idx + toInsert.length, 0, "user");

  // Stop pending requests and debounce timer; require next keystroke
  if (inflightController) inflightController.abort();
  debouncedFetch.cancel();
  blockSuggestionsUntilType = true;
  lastSentPrefix = ""; // optional: allow next query after typing

  clearSuggestion();
}

/** Cancelable debounce for fetch */
const debouncedFetch = makeDebounce(() => {
  fetchSuggestion(); // builds prefix and checks threshold inside
}, DEBOUNCE_MS);

// === NETWORK ===
async function fetchSuggestion() {
  // hard gate: do not fetch until the user types again after an accept
  if (blockSuggestionsUntilType) return;

  const rawPrefix = getSentencePrefixUpToCaret();  // only since last '.'
  if (!rawPrefix || rawPrefix.trim().length < MIN_CHARS) {
    clearSuggestion();
    return;
  }

  // avoid duplicate queries
  if (rawPrefix === lastSentPrefix) return;
  lastSentPrefix = rawPrefix;

  // cancel previous request
  if (inflightController) inflightController.abort();
  inflightController = new AbortController();
  const signal = inflightController.signal;

  const myId = ++latestRequestId;

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: rawPrefix }),
      signal
    });

    if (!res.ok) { clearSuggestion(); return; }

    let text = (await res.text() || "").trim();
    // sanitize to avoid new blocks when showing/inserting
    text = text.replace(/\r?\n+/g, " ");

    if (myId !== latestRequestId) return; // stale response

    currentSuggestion = text;
    ensureGhostMounted();
    ghost.textContent = currentSuggestion;
    requestAnimationFrame(positionGhostAtCaret);

  } catch (e) {
    if (e.name !== "AbortError") console.error(e);
    clearSuggestion();
  }
}

// === EVENTS ===
ensureGhostMounted();

// On user typing
quill.on("text-change", (d, o, source) => {
  if (source !== "user") return;

  const sel = quill.getSelection();
  if (sel) lastCaretIndex = sel.index;

  // If we just accepted, consume this keystroke and re-enable for next one
  if (blockSuggestionsUntilType) {
    blockSuggestionsUntilType = false;
    requestAnimationFrame(positionGhostAtCaret);
    return; // skip fetch for this event
  }

  requestAnimationFrame(() => { positionGhostAtCaret(); debouncedFetch(); });
});

// On caret move
quill.on("selection-change", () => {
  const sel = quill.getSelection();
  if (sel) lastCaretIndex = sel.index;
  requestAnimationFrame(positionGhostAtCaret);
});

// Override Tab behavior with Quill binding (cleaner than keydown)
quill.keyboard.addBinding({ key: 9 }, (range, context) => { // 9 = Tab
  if (currentSuggestion) {
    acceptSuggestion();
    return false; // prevent default tab/indent
  }
  return false;   // prevent indent even without suggestion (optional)
});

// Keep ArrowRight and Escape on the editable element
quill.root.addEventListener("keydown", (e) => {
  if (e.key === "ArrowRight" && currentSuggestion) {
    e.preventDefault();
    acceptSuggestion();
  } else if (e.key === "Escape") {
    clearSuggestion();
  }
});

// Hide ghost when clicking outside editor
document.addEventListener("click", (e) => {
  const editor = quill.root;
  if (!editor.contains(e.target)) clearSuggestion();
});

// Initial focus/position
quill.focus();
requestAnimationFrame(positionGhostAtCaret);
