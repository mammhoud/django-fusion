// ================================================================
//   APP - Main Application Controller
// ================================================================

import { state } from '../config/state';
import { Dom } from '../ui/dom';
import { ChatRenderer } from '../chat/messages';
import { HistoryRenderer } from '../chat/history';
import { SlideNavigator } from '../ui/navigation';
import { InputHandler } from '../ui/input';
import { MonacoLoader } from './monaco-loader';
import { EditorManager } from '../editor/editor';
import { VersionManager } from '../editor/version';
import { MockApi } from '../utils/mock-api';

export class App {
    constructor() {
        this.dom = new Dom();
        this.state = state;
        this.chatRenderer = new ChatRenderer(this.dom, this.state);
        this.historyRenderer = new HistoryRenderer(this.dom, this.state);
        this.slideNavigator = new SlideNavigator(this.dom, this.state, this.chatRenderer);
        this.inputHandler = new InputHandler(this.dom, this.state, this.chatRenderer, this.historyRenderer);
        this.editorManager = new EditorManager(this.dom, this.state);
        this.versionManager = new VersionManager(this.dom, this.state, this.editorManager);
        this.monacoLoader = new MonacoLoader();
        this.mockApi = new MockApi();
    }

    init() {
        // Initialize state
        this.state.createInitialChat();

        // Setup DOM references
        this.dom.initialize();

        // Render initial UI
        this.historyRenderer.render();
        this.chatRenderer.render(this.state.currentChatId);

        // Setup event listeners
        this.setupEventListeners();

        // Focus input
        this.dom.userInput.focus();

        console.log('🚀 AI Chat + Code Editor ready!');
        console.log('💾 Click Apply to save versions, use arrows to navigate.');
    }

    setupEventListeners() {
        // Input handlers
        this.inputHandler.setup();

        // Navigation
        this.slideNavigator.setup();

        // New chat
        this.dom.newChatBtn.addEventListener('click', () => {
            this.createNewChat();
        });

        // Settings (demo)
        this.dom.settingsNav.addEventListener('click', () => {
            alert('⚙️ Settings panel (demo)');
        });

        // Logout (demo)
        this.dom.logoutNav.addEventListener('click', () => {
            if (confirm('Sign out?')) alert('Signed out (demo)');
        });
    }

    createNewChat() {
        const id = 'chat' + (this.state.nextId++);
        const defaultCode = `// 🚀 New code playground
// Write your JavaScript here.

const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);
console.log(doubled);`;

        this.state.conversations[id] = {
            title: `Chat ${this.state.nextId - 1}`,
            messages: [{
                role: 'code_editor',
                content: defaultCode,
                versions: [defaultCode],
                currentVersionIndex: 0,
                timestamp: Date.now(),
            }],
        };
        this.state.currentChatId = id;
        this.state.currentSlideIndex = 0;

        this.historyRenderer.render();
        this.chatRenderer.render(id);
        this.dom.userInput.focus();

        // Flash animation
        this.dom.newChatBtn.style.transform = 'scale(0.95)';
        setTimeout(() => {
            this.dom.newChatBtn.style.transform = 'scale(1)';
        }, 150);
    }
}