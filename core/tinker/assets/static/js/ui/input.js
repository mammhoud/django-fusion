// ================================================================
//   INPUT - Chat input handling
// ================================================================

import { MockApi } from '../utils/mock-api';

export class InputHandler {
    constructor(dom, state, chatRenderer, historyRenderer) {
        this.dom = dom;
        this.state = state;
        this.chatRenderer = chatRenderer;
        this.historyRenderer = historyRenderer;
        this.mockApi = new MockApi();
    }

    setup() {
        this.dom.sendBtn.addEventListener('click', () => this.sendMessage());
        this.dom.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        this.dom.userInput.addEventListener('input', () => {
            this.dom.userInput.style.height = 'auto';
            this.dom.userInput.style.height = Math.min(this.dom.userInput.scrollHeight, 120) + 'px';
        });
    }

    async sendMessage() {
        const text = this.dom.userInput.value.trim();
        if (!text || this.state.isProcessing) return;

        const chat = this.state.getCurrentChat();
        chat.messages.push({
            role: 'user',
            content: text,
            timestamp: Date.now(),
        });

        this.dom.userInput.value = '';
        this.state.isProcessing = true;
        this.dom.sendBtn.disabled = true;
        this.dom.userInput.disabled = true;

        // Show loading overlay
        const card = document.querySelector(`.code-editor[data-chatid="${this.state.currentChatId}"]`);
        const overlay = card ? card.querySelector('.code-editor__loading-overlay') : null;
        if (overlay) overlay.classList.add('code-editor__loading-overlay--visible');

        // Add typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = 
            `<span>AI is thinking</span><span class="typing-indicator__dots"><span></span><span></span><span></span></span>`;
        const slideCard = document.querySelector('.slide-card');
        if (slideCard) slideCard.appendChild(typingDiv);

        await new Promise(resolve => setTimeout(resolve, 1200 + Math.random() * 1000));

        const response = this.mockApi.getResponse(text);
        chat.messages.push({
            role: 'assistant',
            content: response,
            timestamp: Date.now(),
        });

        if (typingDiv.parentNode) typingDiv.remove();
        if (overlay) overlay.classList.remove('code-editor__loading-overlay--visible');

        if (chat.messages.length === 2) {
            const title = text.length > 30 ? text.slice(0, 30) + '…' : text;
            chat.title = title;
            this.dom.chatTitle.textContent = title;
            this.historyRenderer.render();
        }

        const slides = this.state.getSlides(chat);
        this.state.currentSlideIndex = slides.length - 1;
        this.chatRenderer.render(this.state.currentChatId);

        this.state.isProcessing = false;
        this.dom.sendBtn.disabled = false;
        this.dom.userInput.disabled = false;
        this.dom.userInput.focus();
    }
}