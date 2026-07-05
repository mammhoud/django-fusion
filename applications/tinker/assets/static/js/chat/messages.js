// ================================================================
//   CHAT MESSAGES - Render slide cards
// ================================================================

import { escapeHtml } from '../utils/helpers';
import { EditorManager } from '../editor/editor';

export class ChatRenderer {
    constructor(dom, state) {
        this.dom = dom;
        this.state = state;
        this.editorManager = new EditorManager(dom, state);
    }

    render(chatId) {
        const chat = this.state.getChat(chatId);
        if (!chat) return;

        const slides = this.state.getSlides(chat);
        if (slides.length === 0) {
            this.dom.messagesContainer.innerHTML = 
                `<div class="slide-card" style="text-align:center;color:#64748b;">No messages yet. Start the conversation!</div>`;
            this.updateNavButtons(0);
            return;
        }

        // Clamp index
        if (this.state.currentSlideIndex === undefined || this.state.currentSlideIndex >= slides.length) {
            this.state.currentSlideIndex = slides.length - 1;
        }
        if (this.state.currentSlideIndex < 0) this.state.currentSlideIndex = 0;

        const slide = slides[this.state.currentSlideIndex] || { user: null, assistant: null };

        // Dispose old editor
        this.editorManager.dispose(chatId);

        this.dom.messagesContainer.innerHTML = '';

        const slideCard = document.createElement('div');
        slideCard.className = 'slide-card';

        // User message
        if (slide.user) {
            const userDiv = this.createUserMessage(slide.user);
            slideCard.appendChild(userDiv);
        }

        // Assistant message or code editor
        if (slide.assistant) {
            const assistantDiv = this.createAssistantMessage(slide.assistant, chatId);
            slideCard.appendChild(assistantDiv);
        }

        this.dom.messagesContainer.appendChild(slideCard);
        this.updateNavButtons(slides.length);
    }

    createUserMessage(msg) {
        const div = document.createElement('div');
        div.className = 'message message--user';
        div.textContent = msg.content;
        
        const meta = document.createElement('div');
        meta.className = 'message__meta';
        const time = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'now';
        meta.innerHTML = `<i class="far fa-user"></i> You · ${time}`;
        div.appendChild(meta);
        
        return div;
    }

    createAssistantMessage(msg, chatId) {
        const div = document.createElement('div');
        div.className = 'message message--assistant';

        if (msg.role === 'code_editor') {
            div.classList.add('message--code-editor');
            const time = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'now';

            // Ensure versions array exists
            if (!msg.versions || !Array.isArray(msg.versions)) {
                msg.versions = [msg.content];
                msg.currentVersionIndex = 0;
            }
            if (msg.currentVersionIndex === undefined || msg.currentVersionIndex >= msg.versions.length) {
                msg.currentVersionIndex = 0;
            }
            const currentCode = msg.versions[msg.currentVersionIndex] || msg.content;

            const cardHtml = this.editorManager.buildEditorHTML(chatId, msg, currentCode);
            div.innerHTML = cardHtml;

            // Init Monaco
            setTimeout(() => {
                this.editorManager.init(chatId, currentCode);
            }, 80);

        } else {
            // Regular assistant message
            let content = msg.content;
            content = content.replace(/```([\s\S]*?)```/g, (match, code) => {
                return `<pre><code>${escapeHtml(code.trim())}</code></pre>`;
            });
            content = content.replace(/`([^`]+)`/g, (match, code) => {
                return `<code>${escapeHtml(code)}</code>`;
            });
            content = content.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
            content = content.replace(/\*([^*]+)\*/g, '<em>$1</em>');
            div.innerHTML = content;
            
            const meta = document.createElement('div');
            meta.className = 'message__meta';
            const time = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'now';
            meta.innerHTML = `<i class="far fa-clock"></i> ${time} <i class="fas fa-robot" style="margin-left:8px;"></i>`;
            div.appendChild(meta);
        }

        return div;
    }

    updateNavButtons(totalSlides) {
        if (!totalSlides) totalSlides = this.state.getSlides(this.state.getCurrentChat()).length;
        const current = this.state.currentSlideIndex;
        this.dom.prevBtn.disabled = (current <= 0);
        this.dom.nextBtn.disabled = (current >= totalSlides - 1);
    }
}