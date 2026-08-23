const form = document.querySelector('#chat-form');
const input = document.querySelector('#question');
const messages = document.querySelector('#messages');
const error = document.querySelector('#chat-error');

function cleanAnswer(content) {
  return String(content)
    .replace(/\s*[【\[][^】\]]*(?:†\s*L\d+|L\d+\s*[-–]\s*L?\d+)[^】\]]*[】\]]/g, '')
    .replace(/\*\*/g, '')
    .trim();
}

function addMessage(kind, content, sources = [], unknown = false) {
  const item = document.createElement('article');
  item.className = `message ${kind}${unknown ? ' unknown' : ''}`;
  const label = kind === 'user' ? 'You' : 'DocTrust AI';
  item.innerHTML = `<strong>${label}</strong><p></p>`;
  item.querySelector('p').textContent = kind === 'assistant' ? cleanAnswer(content) : content;

  if (sources.length) {
    const list = document.createElement('div');
    list.className = 'source-chips';
    const uniqueSources = sources.filter((source, index, all) =>
      index === all.findIndex(item => item.document === source.document && item.page === source.page)
    );
    uniqueSources.forEach(source => {
      const chip = document.createElement('a');
      chip.className = 'source-chip';
      const page = source.page == null ? '' : ` | Page ${source.page}`;
      chip.textContent = `${source.document}${page}`;
      chip.title = `Source relevance: ${Number(source.score).toFixed(2)}`;
      chip.href = `/api/documents/view/${encodeURIComponent(source.document)}`;
      chip.target = '_blank';
      chip.rel = 'noopener';
      list.append(chip);
    });
    item.append(list);
  }
  messages.append(item);
  messages.scrollTop = messages.scrollHeight;
  return item;
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  error.textContent = '';
  const question = input.value.trim();
  if (!question) { error.textContent = 'Please enter a question.'; return; }
  addMessage('user', question);
  input.value = '';
  const loading = addMessage('assistant', 'Searching the document evidence...');
  const button = form.querySelector('button');
  button.disabled = true;
  try {
    const response = await fetch('/api/chat/', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({question})});
    const payload = await response.json().catch(() => ({}));
    loading.remove();
    if (!response.ok) throw new Error(payload.detail || 'The server could not answer right now.');
    addMessage('assistant', payload.answer, payload.sources || [], !payload.answered);
    if (!payload.answered) error.textContent = 'This question was not found in the current knowledge base.';
  } catch (err) {
    loading.remove();
    error.textContent = err.message || 'Could not reach the backend.';
  } finally {
    button.disabled = false;
    input.focus();
  }
});

input.addEventListener('keydown', event => {
  if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); form.requestSubmit(); }
});
document.querySelector('#clear-chat').addEventListener('click', () => { messages.replaceChildren(); error.textContent = ''; });

const pendingQuestion = sessionStorage.getItem('doctrust_pending_question');
if (pendingQuestion) {
  sessionStorage.removeItem('doctrust_pending_question');
  input.value = pendingQuestion;
  form.requestSubmit();
}
