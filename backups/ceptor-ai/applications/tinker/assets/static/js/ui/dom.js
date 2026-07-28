// ================================================================
//   DOM - Centralized DOM references
// ================================================================

export class Dom {
    constructor() {
        this.messagesContainer = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.chatTitle = document.getElementById('chatTitle');
        this.chatHistoryEl = document.getElementById('chatHistory');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.settingsNav = document.getElementById('settingsNav');
        this.logoutNav = document.getElementById('logoutNav');
        this.sideNav = document.getElementById('sideNav');
        this.chatMain = document.getElementById('chatMain');
    }

    initialize() {
        // Any additional DOM setup
    }
}