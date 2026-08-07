// ================================================================
//   HISTORY - Render chat history as code blocks
// ================================================================

export class HistoryRenderer {
    constructor(dom, state) {
        this.dom = dom;
        this.state = state;
    }

    render() {
        this.dom.chatHistoryEl.innerHTML = '';
        const ids = Object.keys(this.state.conversations);
        
        if (ids.length === 0) {
            this.dom.chatHistoryEl.innerHTML = 
                '<div style="padding:12px 20px;color:#94a3b8;font-size:13px;">No chats yet</div>';
            return;
        }

        ids.forEach(id => {
            const chat = this.state.getChat(id);
            const div = document.createElement('div');
            div.className = `chat-history__item${id === this.state.currentChatId ? ' chat-history__item--active' : ''}`;
            
            const clickableArea = document.createElement('div');
            clickableArea.className = 'chat-history__clickable';
            clickableArea.addEventListener('click', () => this.switchChat(id));
            
            const prefixSpan = document.createElement('span');
            prefixSpan.className = 'chat-history__prefix';
            prefixSpan.textContent = '> ';
            
            const titleSpan = document.createElement('span');
            titleSpan.className = 'chat-history__title';
            titleSpan.textContent = chat.title || 'Untitled';
            
            clickableArea.appendChild(prefixSpan);
            clickableArea.appendChild(titleSpan);
            
            const renameBtn = document.createElement('button');
            renameBtn.className = 'chat-history__rename-btn';
            renameBtn.innerHTML = '<i class="fas fa-pen"></i>';
            renameBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.renameChat(id);
            });
            
            div.appendChild(clickableArea);
            div.appendChild(renameBtn);
            this.dom.chatHistoryEl.appendChild(div);
        });
    }

    switchChat(id) {
        if (id === this.state.currentChatId) return;
        this.state.currentChatId = id;
        this.state.currentSlideIndex = 0;
        
        // Re-render everything
        this.render();
        import('./messages').then(({ ChatRenderer }) => {
            const renderer = new ChatRenderer(this.dom, this.state);
            renderer.render(id);
        });
        this.dom.userInput.focus();
    }

    renameChat(id) {
        const chat = this.state.getChat(id);
        if (!chat) return;
        const newName = prompt('Rename this chat:', chat.title);
        if (newName && newName.trim() !== '') {
            chat.title = newName.trim();
            this.render();
            if (id === this.state.currentChatId) {
                this.dom.chatTitle.textContent = chat.title;
            }
        }
    }
}