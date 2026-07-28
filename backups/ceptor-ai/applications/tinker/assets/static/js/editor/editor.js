// ================================================================
//   EDITOR - Monaco editor management
// ================================================================

import { MonacoLoader } from '../core/monaco-loader';
import { VersionManager } from './version';

export class EditorManager {
    constructor(dom, state) {
        this.dom = dom;
        this.state = state;
        this.monacoLoader = new MonacoLoader();
        this.versionManager = new VersionManager(dom, state, this);
        this.instances = {};
        this.initialized = false;
    }

    async init(chatId, codeContent) {
        const container = document.getElementById(`editor-${chatId}`);
        if (!container) return;

        // Dispose existing
        this.dispose(chatId);

        try {
            await this.monacoLoader.load();
            const monaco = window.monaco;
            
            const editor = monaco.editor.create(container, {
                value: codeContent,
                language: 'javascript',
                theme: 'vs-dark',
                automaticLayout: true,
                fontSize: 14,
                fontFamily: 'JetBrains Mono, "Fira Code", monospace',
                tabSize: 2,
                insertSpaces: true,
                wordWrap: 'on',
                minimap: { enabled: false },
                scrollbar: { vertical: 'auto', horizontal: 'auto' },
                bracketPairColorization: { enabled: true },
                renderWhitespace: 'selection',
            });

            this.instances[chatId] = editor;

            // Format action
            editor.addAction({
                id: 'format-code',
                label: 'Format',
                keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyF],
                run: function() {
                    editor.getAction('editor.action.formatDocument').run();
                },
            });

            // Auto-save on change
            editor.onDidChangeModelContent(() => {
                const msg = this.state.getCodeEditorMessage(chatId);
                if (msg) {
                    const newValue = editor.getValue();
                    msg.content = newValue;
                    if (msg.versions && msg.versions.length > 0 &&
                        msg.currentVersionIndex !== undefined &&
                        msg.currentVersionIndex < msg.versions.length) {
                        msg.versions[msg.currentVersionIndex] = newValue;
                    }
                }
            });

            // Attach toolbar events
            this.attachToolbarEvents(chatId, editor);

            editor.focus();
            this.initialized = true;

        } catch (error) {
            console.error('Failed to load Monaco:', error);
        }
    }

    dispose(chatId) {
        if (this.instances[chatId]) {
            this.instances[chatId].dispose();
            delete this.instances[chatId];
        }
    }

    getEditor(chatId) {
        return this.instances[chatId] || null;
    }

    attachToolbarEvents(chatId, editor) {
        const card = document.querySelector(`.code-editor[data-chatid="${chatId}"]`);
        if (!card) return;

        const runBtn = card.querySelector('.toolbar-btn--run');
        const formatBtn = card.querySelector('.toolbar-btn--format');
        const copyBtn = card.querySelector('.toolbar-btn--copy');
        const applyBtn = card.querySelector('.toolbar-btn--apply');
        const versionPrev = card.querySelector('.version-prev');
        const versionNext = card.querySelector('.version-next');

        if (runBtn) {
            runBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.runCode(chatId);
            });
        }
        if (formatBtn) {
            formatBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                editor.getAction('editor.action.formatDocument').run();
            });
        }
        if (copyBtn) {
            copyBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const code = editor.getValue();
                navigator.clipboard.writeText(code).then(() => {
                    const original = copyBtn.innerHTML;
                    copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                    setTimeout(() => copyBtn.innerHTML = original, 1200);
                }).catch(() => alert('Copy failed'));
            });
        }
        if (applyBtn) {
            applyBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.versionManager.applyVersion(chatId);
            });
        }
        if (versionPrev) {
            versionPrev.addEventListener('click', (e) => {
                e.stopPropagation();
                this.versionManager.navigateVersion(chatId, -1);
            });
        }
        if (versionNext) {
            versionNext.addEventListener('click', (e) => {
                e.stopPropagation();
                this.versionManager.navigateVersion(chatId, 1);
            });
        }
    }

    runCode(chatId) {
        const editor = this.getEditor(chatId);
        if (!editor) return;
        const code = editor.getValue();

        const outputContainer = document.getElementById(`output-${chatId}`);
        const outputContent = outputContainer?.querySelector('.output-content');
        if (!outputContainer || !outputContent) return;

        outputContainer.classList.add('code-editor__output--visible');

        let logs = [];
        const originalLog = console.log;
        console.log = (...args) => {
            logs.push(args.map(arg => {
                if (typeof arg === 'object') return JSON.stringify(arg, null, 2);
                return String(arg);
            }).join(' '));
            originalLog(...args);
        };

        try {
            const fn = new Function(code);
            const result = fn();
            if (result !== undefined && logs.length === 0) {
                logs.push(String(result));
            }
            if (logs.length === 0) {
                logs.push('✅ Code executed successfully (no output)');
            }
        } catch (err) {
            logs.push(`❌ Error: ${err.message}`);
        } finally {
            console.log = originalLog;
        }

        outputContent.textContent = logs.join('\n');
        outputContainer.scrollTop = outputContainer.scrollHeight;
    }

    buildEditorHTML(chatId, msg, currentCode) {
        const time = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'now';
        const total = msg.versions ? msg.versions.length : 1;
        const current = (msg.currentVersionIndex !== undefined) ? msg.currentVersionIndex + 1 : 1;

        return `
            <div class="code-editor" data-chatid="${chatId}">
                <div class="code-editor__toolbar">
                    <span class="toolbar-label"><i class="fas fa-terminal"></i> Code Editor</span>
                    <div class="toolbar-actions">
                        <button class="toolbar-btn version-prev" data-chatid="${chatId}" title="Previous version" ${msg.currentVersionIndex <= 0 ? 'disabled' : ''}>
                            <i class="fas fa-chevron-left"></i>
                        </button>
                        <span class="version-info" id="versionInfo-${chatId}">${current}/${total}</span>
                        <button class="toolbar-btn version-next" data-chatid="${chatId}" title="Next version" ${msg.currentVersionIndex >= msg.versions.length-1 ? 'disabled' : ''}>
                            <i class="fas fa-chevron-right"></i>
                        </button>
                        <button class="toolbar-btn toolbar-btn--apply" data-chatid="${chatId}" title="Save current code as new version">
                            <i class="fas fa-check"></i> Apply
                        </button>
                        <button class="toolbar-btn toolbar-btn--copy" data-chatid="${chatId}" title="Copy code">
                            <i class="fas fa-copy"></i>
                        </button>
                        <button class="toolbar-btn toolbar-btn--format" data-chatid="${chatId}" title="Format">
                            <i class="fas fa-magic"></i>
                        </button>
                        <button class="toolbar-btn toolbar-btn--run" data-chatid="${chatId}" title="Run code">
                            <i class="fas fa-play"></i> Run
                        </button>
                    </div>
                </div>
                <div class="code-editor__wrapper" id="editor-${chatId}"></div>
                <div class="code-editor__output" id="output-${chatId}">
                    <div class="output-label">▶ Output</div>
                    <div class="output-content"></div>
                </div>
                <div class="code-editor__loading-overlay" id="loading-${chatId}">
                    <i class="fas fa-spinner fa-pulse loading-icon"></i>
                    <span>AI is generating code…</span>
                    <span class="loading-sub">Please wait</span>
                </div>
            </div>
            <div class="message__meta"><i class="far fa-clock"></i> ${time} <i class="fas fa-robot" style="margin-left:8px;"></i></div>
        `;
    }
}