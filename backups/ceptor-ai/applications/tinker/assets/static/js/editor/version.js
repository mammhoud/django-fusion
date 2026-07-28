// ================================================================
//   VERSION - Version control for code editor
// ================================================================

export class VersionManager {
    constructor(dom, state, editorManager) {
        this.dom = dom;
        this.state = state;
        this.editorManager = editorManager;
    }

    applyVersion(chatId) {
        const editor = this.editorManager.getEditor(chatId);
        if (!editor) return;
        const currentCode = editor.getValue();
        const msg = this.state.getCodeEditorMessage(chatId);
        if (!msg) return;

        if (!msg.versions) msg.versions = [];
        msg.versions.push(currentCode);
        msg.currentVersionIndex = msg.versions.length - 1;
        msg.content = currentCode;

        this.updateVersionDisplay(chatId);
        this.updateVersionButtons(chatId);
    }

    navigateVersion(chatId, direction) {
        const msg = this.state.getCodeEditorMessage(chatId);
        if (!msg) return;
        if (!msg.versions || msg.versions.length === 0) return;
        
        const newIndex = msg.currentVersionIndex + direction;
        if (newIndex < 0 || newIndex >= msg.versions.length) return;

        msg.currentVersionIndex = newIndex;
        const code = msg.versions[newIndex];
        msg.content = code;

        const editor = this.editorManager.getEditor(chatId);
        if (editor) {
            editor.setValue(code);
        }

        this.updateVersionDisplay(chatId);
        this.updateVersionButtons(chatId);
    }

    updateVersionDisplay(chatId) {
        const msg = this.state.getCodeEditorMessage(chatId);
        if (!msg) return;
        const info = document.getElementById(`versionInfo-${chatId}`);
        if (info) {
            const total = msg.versions ? msg.versions.length : 1;
            const current = (msg.currentVersionIndex !== undefined) ? msg.currentVersionIndex + 1 : 1;
            info.textContent = `${current}/${total}`;
        }
    }

    updateVersionButtons(chatId) {
        const msg = this.state.getCodeEditorMessage(chatId);
        if (!msg) return;
        const card = document.querySelector(`.code-editor[data-chatid="${chatId}"]`);
        if (!card) return;
        
        const prevBtn = card.querySelector('.version-prev');
        const nextBtn = card.querySelector('.version-next');
        
        if (prevBtn) {
            prevBtn.disabled = (msg.currentVersionIndex <= 0);
        }
        if (nextBtn) {
            nextBtn.disabled = (msg.currentVersionIndex >= (msg.versions ? msg.versions.length - 1 : 0));
        }
    }
}