// Minimal OpenAI-compatible mock server used by the Playwright suite to test
// the chat pipeline end-to-end without external services. Logs request shapes
// so tests can assert the system prompt was assembled from prompt + context.
import http from 'node:http';

const server = http.createServer((req, res) => {
  let body = '';
  req.on('data', (chunk) => { body += chunk; });
  req.on('end', () => {
    if (req.url.endsWith('/chat/completions')) {
      let parsed = {};
      try { parsed = JSON.parse(body || '{}'); } catch { /* ignore */ }
      const lastUser = [...(parsed.messages || [])].reverse().find((message) => message.role === 'user');
      const hasSystem = (parsed.messages || []).some((message) => message.role === 'system');
      const systemText = (parsed.messages || []).filter((message) => message.role === 'system').map((message) => message.content).join('\n');
      // Study prompts ask for JSON flashcards; a note containing the marker
      // gets garbage instead so tests can drive the retry/failure path.
      if (systemText.includes('flashcards') && !String(lastUser?.content || '').includes('MOCK_NO_JSON')) {
        const cards = JSON.stringify([
          { question: 'Mock question 1?', answer: 'Mock answer 1.' },
          { question: 'Mock question 2?', answer: 'Mock answer 2.' },
        ]);
        res.writeHead(200, { 'content-type': 'application/json' });
        res.end(JSON.stringify({
          id: 'chatcmpl-mock', object: 'chat.completion', model: parsed.model || 'mock-model',
          choices: [{ index: 0, finish_reason: 'stop', message: { role: 'assistant', content: cards } }],
          usage: { prompt_tokens: 12, completion_tokens: 34, total_tokens: 46 },
        }));
        return;
      }
      // Echo the context-block headers back so tests can prove the server
      // actually injected the attached files into the system message.
      const contextRefs = [...systemText.matchAll(/^--- (.+?) \((?:complete|truncated|pdf text, (?:complete|truncated)|pdf, no extractable text)\) ---$/gm)].map((match) => match[1]);
      const contextNote = contextRefs.length ? `; context:${contextRefs.join(',')}` : '';
      // Multimodal parts on the current turn are counted so tests can prove an
      // image reached the provider as an image_url part, not as text.
      const parts = (parsed.messages || []).flatMap((message) => (Array.isArray(message.content) ? message.content : []));
      const imageCount = parts.filter((part) => part.type === 'image_url').length;
      const imageNote = imageCount ? `; images:${imageCount}` : '';
      const payload = JSON.stringify({
        id: 'chatcmpl-mock', object: 'chat.completion', model: parsed.model || 'mock-model',
        choices: [{ index: 0, finish_reason: 'stop', message: { role: 'assistant', content: `Mock reply to "${lastUser ? lastUser.content : ''}" (system:${hasSystem ? 'yes' : 'no'}${contextNote}${imageNote})` } }],
        usage: { prompt_tokens: 1, completion_tokens: 1, total_tokens: 2 },
      });
      res.writeHead(200, { 'content-type': 'application/json' });
      res.end(payload);
      return;
    }
    if (req.url.endsWith('/models')) {
      res.writeHead(200, { 'content-type': 'application/json' });
      res.end(JSON.stringify({ object: 'list', data: [{ id: 'mock-model', object: 'model' }] }));
      return;
    }
    res.writeHead(404, { 'content-type': 'application/json' });
    res.end(JSON.stringify({ error: { message: 'not found' } }));
  });
});

const port = Number(process.env.MOCK_LLM_PORT || 11434);
server.listen(port, '127.0.0.1', () => console.log(`mock-llm listening on ${port}`));
