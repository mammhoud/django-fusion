// ================================================================
//   MOCK API - Simulated LLM responses
// ================================================================

export class MockApi {
    getResponse(userMessage) {
        const lower = userMessage.toLowerCase();
        
        if (lower.includes('hello') || lower.includes('hi') || lower.includes('hey')) {
            return "Hello! 👋 I see you're using the code editor. Feel free to write, run, and organize your code right here.";
        } else if (lower.includes('code') || lower.includes('programming') || lower.includes('python') || lower.includes('javascript')) {
            return "Great! The code editor supports JavaScript with Monaco. You can format (Ctrl+F), copy, and run the code to see output below.";
        } else if (lower.includes('run') || lower.includes('execute')) {
            return "To run the code, click the ▶ **Run** button in the editor toolbar. The output will appear below the editor.";
        } else if (lower.includes('help')) {
            return "I'm here to help! You can ask me about the code editor, programming concepts, or just chat. The editor supports syntax highlighting, formatting, and execution.";
        } else if (lower.includes('bye')) {
            return "Goodbye! Keep coding and come back anytime. 🚀";
        } else {
            const responses = [
                "That's interesting! How does your code relate to that?",
                "I see. Would you like to try writing some code in the editor?",
                "Good question! The editor is fully integrated – you can edit, run, and iterate.",
                "Let's explore that. Try writing a function in the editor and run it!",
                "I'm here to assist with coding or general questions. What would you like to do?",
            ];
            return responses[Math.floor(Math.random() * responses.length)];
        }
    }
}