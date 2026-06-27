// ================================================================
//   STATE MANAGEMENT
// ================================================================

export class State {
    constructor() {
        this.conversations = {};
        this.currentChatId = null;
        this.nextId = 1;
        this.isProcessing = false;
        this.currentSlideIndex = 0;
        this.editorInstances = {};
    }

    getCurrentChat() {
        return this.conversations[this.currentChatId];
    }

    getChat(id) {
        return this.conversations[id];
    }

    getSlides(chat) {
        const slides = [];
        let i = 0;
        while (i < chat.messages.length) {
            const msg = chat.messages[i];
            if (msg.role === 'user') {
                const slide = { user: msg, assistant: null };
                if (i + 1 < chat.messages.length &&
                    (chat.messages[i + 1].role === 'assistant' || chat.messages[i + 1].role === 'code_editor')) {
                    slide.assistant = chat.messages[i + 1];
                    i += 2;
                } else {
                    i += 1;
                }
                slides.push(slide);
            } else {
                slides.push({ user: null, assistant: msg });
                i += 1;
            }
        }
        return slides;
    }

    getCodeEditorMessage(chatId) {
        const chat = this.getChat(chatId);
        if (!chat) return null;
        for (let msg of chat.messages) {
            if (msg.role === 'code_editor') {
                return msg;
            }
        }
        return null;
    }

    createInitialChat() {
        const id = 'chat1';
        const initialCode = `// 🚀 Welcome to the Code Editor!
// Write, run, and organize your code here.

function greet(name) {
  return \`Hello, \${name}!\`;
}

const user = "Developer";
console.log(greet(user));

// Try editing this code and press ▶ Run`;

        this.conversations[id] = {
            title: 'Code Playground',
            messages: [{
                role: 'code_editor',
                content: initialCode,
                versions: [initialCode],
                currentVersionIndex: 0,
                timestamp: Date.now(),
            }],
        };
        this.currentChatId = id;
        this.currentSlideIndex = 0;
    }
}

// Singleton instance
export const state = new State();