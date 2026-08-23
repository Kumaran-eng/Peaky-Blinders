async function uploadDocument(file) {
  const body = new FormData(); body.append('file', file);
  const response = await fetch('/api/documents/upload', {method: 'POST', body});
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || 'Upload failed.');
  return payload;
}
