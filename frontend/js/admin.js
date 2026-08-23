const metricLabels = [['total_documents', 'Documents'], ['total_questions', 'Questions'], ['answered_questions', 'Answered'], ['unanswered_questions', 'Unanswered'], ['total_knowledge_gaps', 'Knowledge gaps'], ['average_rating', 'Average rating']];
const api = (path, options) => fetch(path, options).then(async response => {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || 'Request failed.');
  return body;
});
const date = value => value ? new Date(value).toLocaleString() : '—';
const loginView = document.querySelector('#admin-login');
const dashboardView = document.querySelector('#admin-dashboard');

function showLogin(message = '') {
  dashboardView.hidden = true;
  loginView.hidden = false;
  document.querySelector('#login-error').textContent = message;
}

function showDashboard() {
  loginView.hidden = true;
  dashboardView.hidden = false;
}

async function loadDashboard() {
  const error = document.querySelector('#admin-error');
  error.textContent = '';
  try {
    const [analytics, documents, gaps, questions] = await Promise.all([
      api('/api/admin/analytics'), api('/api/admin/documents'),
      api('/api/admin/knowledge-gaps'), api('/api/admin/questions'),
    ]);
    const metrics = document.querySelector('#metrics');
    metrics.replaceChildren();
    metricLabels.forEach(([key, label]) => {
      const el = document.createElement('article');
      el.className = 'metric';
      el.innerHTML = `<b>${analytics[key]}</b><span>${label}</span>`;
      metrics.append(el);
    });
    const rows = document.querySelector('#documents');
    rows.replaceChildren();
    documents.forEach(doc => {
      const row = document.createElement('tr');
      row.innerHTML = `<td>${doc.filename}</td><td>${doc.file_type || '—'}</td><td><span class="badge ${doc.status === 'failed' ? 'failed' : ''}">${doc.status}</span></td><td>${date(doc.created_at)}</td><td><button class="text-button">Delete</button></td>`;
      row.querySelector('button').onclick = () => deleteDocument(doc.id);
      rows.append(row);
    });
    const gapList = document.querySelector('#gaps');
    gapList.replaceChildren();
    gaps.forEach(gap => { const item = document.createElement('li'); item.textContent = gap.question; gapList.append(item); });
    if (!gaps.length) gapList.innerHTML = '<li>No gaps recorded yet.</li>';
    const questionList = document.querySelector('#questions');
    questionList.replaceChildren();
    questions.forEach(item => {
      const row = document.createElement('li');
      row.innerHTML = `${item.question}<small>${item.answered ? 'Answered' : 'Unanswered'} · ${date(item.created_at)}</small>`;
      questionList.append(row);
    });
    if (!questions.length) questionList.innerHTML = '<li>No questions yet.</li>';
  } catch (err) {
    if (err.message === 'Admin sign-in is required.') return showLogin();
    error.textContent = err.message || 'Could not load dashboard data.';
  }
}

async function deleteDocument(id) {
  if (!confirm('Remove this document record? Its indexed vectors will remain.')) return;
  try { await api(`/api/admin/documents/${id}`, { method: 'DELETE' }); await loadDashboard(); }
  catch (err) { document.querySelector('#admin-error').textContent = err.message; }
}

document.querySelector('#login-form').addEventListener('submit', async event => {
  event.preventDefault();
  const password = document.querySelector('#admin-password').value;
  try {
    await api('/api/admin/login', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({password}) });
    event.target.reset(); showDashboard(); await loadDashboard();
  } catch (err) { document.querySelector('#login-error').textContent = err.message || 'Unable to sign in.'; }
});
document.querySelector('#upload-form').addEventListener('submit', async event => {
  event.preventDefault();
  const file = document.querySelector('#document-file').files[0];
  const status = document.querySelector('#upload-status');
  if (!file) return;
  status.textContent = 'Uploading and indexing...';
  try { await uploadDocument(file); status.textContent = 'Completed.'; event.target.reset(); await loadDashboard(); }
  catch (err) { status.textContent = err.message || 'Upload failed.'; }
});
document.querySelector('#refresh').addEventListener('click', loadDashboard);
document.querySelector('#logout').addEventListener('click', async () => { await api('/api/admin/logout', {method: 'POST'}); showLogin(); });

(async () => {
  try {
    const session = await api('/api/admin/session');
    if (session.authenticated) { showDashboard(); await loadDashboard(); }
    else showLogin();
  } catch (err) { showLogin(err.message || 'Unable to check admin access.'); }
})();
