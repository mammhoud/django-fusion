/* Shared GitHub-Flavored Markdown renderer (dependency-free).
   Used by the browser (note cards, previews) and the server (public share
   pages) so a note renders identically everywhere. All input is escaped
   before any tags are emitted, so note content can never inject HTML. */

const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]));

const SAFE_URL = /^(https?:\/\/|\/|mailto:)/i;

function safeUrl(url) {
  const trimmed = String(url || '').trim();
  return SAFE_URL.test(trimmed) ? trimmed : '#';
}

/* Inline formatting. Input must already be HTML-escaped. */
function inline(text) {
  let out = text;
  // Images before links; alt text is already escaped.
  out = out.replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, (_, alt, url) => `<img src="${safeUrl(url)}" alt="${alt}" loading="lazy">`);
  out = out.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, label, url) => `<a href="${safeUrl(url)}" rel="noopener" target="_blank">${label}</a>`);
  // Bare URLs become links.
  out = out.replace(/(^|[\s(])((?:https?:\/\/)[^\s<)]+)/g, (_, pad, url) => `${pad}<a href="${url}" rel="noopener" target="_blank">${url}</a>`);
  out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  out = out.replace(/(^|\W)\*([^*\n]+)\*(?=\W|$)/g, '$1<em>$2</em>');
  out = out.replace(/(^|\W)_([^_\n]+)_(?=\W|$)/g, '$1<em>$2</em>');
  out = out.replace(/~~([^~]+)~~/g, '<del>$1</del>');
  out = out.replace(/`([^`]+)`/g, '<code>$1</code>');
  out = out.replace(/==([^=]+)==/g, '<mark>$1</mark>');
  // Wiki-style links ([[Note title]]) from the linked-note PKM pattern:
  // rendered as chips the client can bind to a search/backlink jump.
  out = out.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (_, target, label) => `<span class="wikilink" data-wikilink="${target.trim()}" role="link" tabindex="0">${(label || target).trim()}</span>`);
  return out;
}

function taskItem(body) {
  const checked = /^\[(x|X)\]\s+/.test(body);
  const box = checked ? '<input type="checkbox" checked disabled>' : '<input type="checkbox" disabled>';
  const label = body.replace(/^\[(x|X|\s)\]\s+/, '');
  return `<li class="task-item">${box}<span>${inline(label)}</span></li>`;
}

const alignmentFor = (cell) => {
  if (/^:-+:$/.test(cell)) return ' style="text-align:center"';
  if (/-+:$/.test(cell)) return ' style="text-align:right"';
  return '';
};

/* Block-level renderer for the full document. */
export function renderMarkdown(raw) {
  const lines = String(raw ?? '').replace(/\r\n/g, '\n').split('\n');
  const out = [];
  let list = null;        // 'ul' | 'ol' | null
  let quote = false;
  let quoteBuf = [];      // paragraphs inside the open blockquote
  let para = [];
  const closeList = () => { if (list) { out.push(`</${list}>`); list = null; } };
  const flushQuotePara = () => { if (quoteBuf.length) { out.push(`<p>${quoteBuf.map(inline).join('<br>')}</p>`); quoteBuf = []; } };
  const closeQuote = () => { if (quote) { flushQuotePara(); out.push('</blockquote>'); quote = false; } };
  const closePara = () => { if (para.length) { out.push(`<p>${para.map(inline).join('<br>')}</p>`); para = []; } };
  const closeAll = () => { closeList(); closeQuote(); closePara(); };

  let inCode = false;
  let codeLang = '';
  let code = [];

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const fence = line.trim().match(/^```\s*([A-Za-z0-9_+#.-]*)\s*$/);
    if (fence) {
      if (inCode) {
        closeAll();
        out.push(`<pre${codeLang ? ` data-lang="${escapeHtml(codeLang)}"` : ''}><code>${escapeHtml(code.join('\n'))}</code></pre>`);
        code = []; inCode = false; codeLang = '';
      } else {
        closeAll();
        inCode = true; codeLang = fence[1] || '';
      }
      continue;
    }
    if (inCode) { code.push(line); continue; }

    const trimmed = line.trim();

    if (!trimmed) { closeAll(); continue; }

    // Blockquote: consecutive `>` lines share one block.
    if (/^>\s?/.test(trimmed)) {
      if (!quote) { closeList(); closePara(); out.push('<blockquote>'); quote = true; }
      const body = trimmed.replace(/^>\s?/, '');
      if (body) quoteBuf.push(escapeHtml(body));
      else flushQuotePara();
      continue;
    }
    closeQuote();

    // Horizontal rule.
    if (/^(-{3,}|\*{3,}|_{3,})$/.test(trimmed)) { closeAll(); out.push('<hr>'); continue; }

    // Heading (ATX) with optional closing hashes.
    const heading = trimmed.match(/^(#{1,6})\s+(.*?)(?:\s+#+)?$/);
    if (heading) {
      closeAll();
      const level = heading[1].length;
      out.push(`<h${level}>${inline(escapeHtml(heading[2]))}</h${level}>`);
      continue;
    }

    // Table: a header row followed by a delimiter row.
    if (trimmed.includes('|') && index + 1 < lines.length) {
      const delimiter = lines[index + 1].trim();
      if (/^\|?[\s:-]*-[\s:|-]*\|?[\s:|-]*$/.test(delimiter) && delimiter.includes('|')) {
        closeAll();
        const cells = (row) => row.replace(/^\||\|$/g, '').split('|').map((cell) => cell.trim());
        const headerCells = cells(trimmed);
        const aligns = cells(delimiter).map(alignmentFor);
        const rows = [];
        let cursor = index + 2;
        while (cursor < lines.length && lines[cursor].includes('|') && lines[cursor].trim()) {
          rows.push(cells(lines[cursor].trim()));
          cursor += 1;
        }
        out.push(`<table><thead><tr>${headerCells.map((cell, position) => `<th${aligns[position] || ''}>${inline(escapeHtml(cell))}</th>`).join('')}</tr></thead>`);
        out.push(`<tbody>${rows.map((cellsRow) => `<tr>${cellsRow.map((cell, position) => `<td${aligns[position] || ''}>${inline(escapeHtml(cell))}</td>`).join('')}</tr>`).join('')}</tbody></table>`);
        index = cursor - 1; // consumed through cursor-1; loop's += 1 moves to cursor
        continue;
      }
    }

    // Unordered list, including task-list items.
    const bullet = trimmed.match(/^[-*+]\s+(.*)$/);
    if (bullet) {
      closePara();
      if (list !== 'ul') { closeList(); out.push('<ul>'); list = 'ul'; }
      if (/^\[(x|X|\s)\]\s/.test(bullet[1])) out.push(taskItem(escapeHtml(bullet[1])));
      else out.push(`<li>${inline(escapeHtml(bullet[1]))}</li>`);
      continue;
    }

    // Ordered list.
    const numbered = trimmed.match(/^\d+[.)]\s+(.*)$/);
    if (numbered) {
      closePara();
      if (list !== 'ol') { closeList(); out.push('<ol>'); list = 'ol'; }
      out.push(`<li>${inline(escapeHtml(numbered[1]))}</li>`);
      continue;
    }

    closeList();
    para.push(escapeHtml(trimmed));
  }
  if (inCode && code.length) out.push(`<pre${codeLang ? ` data-lang="${escapeHtml(codeLang)}"` : ''}><code>${escapeHtml(code.join('\n'))}</code></pre>`);
  closeAll();
  return out.join('');
}
