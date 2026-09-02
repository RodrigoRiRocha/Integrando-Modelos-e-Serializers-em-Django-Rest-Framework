const api = '/api/social/';
const token = () => localStorage.getItem('chirp-token');
const authHeaders = () => token() ? { 'Content-Type': 'application/json', Authorization: `Token ${token()}` } : {};
const escapeHtml = value => String(value).replace(/[&<>'"]/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[character]);

async function request(path, options = {}) {
  const response = await fetch(api + path, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || Object.values(data).flat().join(' ') || 'Não foi possível concluir a ação.');
  return data;
}

function setMessage(message) {
  const target = document.querySelector('.form-message') || document.querySelector('#timeline-title');
  if (target) target.textContent = message;
}

function showAuth(open) { document.querySelector('#auth-layer').hidden = !open; }

function postCard(post) {
  const actions = token() ? `<div class="post-actions"><button data-like="${post.id}">Curtir ${post.likes_count}</button><button data-toggle-comment="${post.id}">Comentar ${post.comments.length}</button></div>` : '';
  return `<article class="post"><div class="avatar post-avatar">${escapeHtml(post.author.charAt(0).toUpperCase())}</div><div><div class="post-meta"><a href="/api/social/profile/${encodeURIComponent(post.author)}/">${escapeHtml(post.author)}</a><span>@${escapeHtml(post.author)}</span></div><p class="post-content">${escapeHtml(post.content)}</p>${actions}</div><form class="comment-form" data-comment="${post.id}" hidden><input name="content" maxlength="280" placeholder="Escreva uma resposta" required><button>Responder</button></form></article>`;
}

async function loadTimeline() {
  const container = document.querySelector('#feed');
  if (!container) return;
  try {
    const path = token() ? 'posts/feed/' : 'posts/';
    const data = await request(path, { headers: authHeaders() });
    container.innerHTML = data.results.length ? data.results.map(postCard).join('') : '<p class="empty">Ainda não há postagens para mostrar.</p>';
    const title = document.querySelector('#timeline-title');
    if (title) title.textContent = token() ? 'Seu feed' : 'Timeline pública';
  } catch (error) { container.innerHTML = `<p class="empty">${escapeHtml(error.message)}</p>`; }
}

async function getProfiles() {
  let path = 'profiles/'; const profiles = [];
  while (path) { const data = await request(path, { headers: authHeaders() }); profiles.push(...data.results); path = data.next ? data.next.replace(location.origin + api, '') : null; }
  return profiles;
}

function profileRow(profile) {
  const follow = token() ? `<button data-follow="${profile.id}">Seguir</button>` : '';
  return `<article class="profile-row"><div class="avatar">${escapeHtml(profile.username.charAt(0).toUpperCase())}</div><div class="profile-copy"><a href="/api/social/profile/${encodeURIComponent(profile.username)}/">${escapeHtml(profile.username)}</a><p>${profile.followers_count} seguidores · ${profile.following_count} seguindo</p></div>${follow}</article>`;
}

async function loadExplore() {
  const container = document.querySelector('#profile-results');
  if (!container) return;
  const profiles = await getProfiles();
  const render = () => { const query = document.querySelector('#profile-search').value.trim().toLowerCase(); const matches = profiles.filter(profile => profile.username.toLowerCase().includes(query)); container.innerHTML = matches.length ? matches.map(profileRow).join('') : '<p class="empty">Nenhum perfil encontrado.</p>'; };
  document.querySelector('#profile-search').addEventListener('input', render); render();
}

async function loadProfilePage() {
  const hero = document.querySelector('.profile-hero');
  if (!hero) return;
  const username = hero.dataset.username;
  const profile = await request(`profiles/by-username/${encodeURIComponent(username)}/`, { headers: authHeaders() });
  document.querySelector('#profile-name').textContent = profile.first_name || profile.username;
  document.querySelector('#profile-handle').textContent = `@${profile.username}`;
  document.querySelector('#profile-avatar').textContent = profile.username.charAt(0).toUpperCase();
  document.querySelector('#profile-stats').innerHTML = `<button data-connections="following"><strong>${profile.following_count}</strong> seguindo</button><button data-connections="followers"><strong>${profile.followers_count}</strong> seguidores</button>`;
  if (token()) document.querySelector('#profile-actions').innerHTML = `<button data-follow="${profile.id}">Seguir</button>`;
  const posts = await request('posts/', { headers: authHeaders() });
  const mine = posts.results.filter(post => post.author === username);
  document.querySelector('#profile-posts').innerHTML = mine.length ? mine.map(postCard).join('') : '<p class="empty">Nenhuma postagem ainda.</p>';
}

async function loadSettings() {
  const form = document.querySelector('#profile-form');
  if (!form || !token()) return;
  document.querySelector('#settings-locked').hidden = true; form.hidden = false;
  const profile = await request('profiles/me/', { headers: authHeaders() });
  for (const [key, value] of Object.entries(profile)) { const field = form.elements.namedItem(key); if (field && typeof value === 'string') field.value = value; }
}

function updateAuthenticatedState() {
  document.querySelectorAll('[data-open-auth]').forEach(button => button.hidden = Boolean(token()));
  const composer = document.querySelector('#post-form'); const locked = document.querySelector('#composer-locked');
  if (composer) composer.hidden = !token(); if (locked) locked.hidden = Boolean(token());
  if (token()) { loadTimeline(); loadSettings(); }
}

document.addEventListener('click', async event => {
  const action = event.target;
  if (action.matches('[data-open-auth]')) showAuth(true);
  if (action.matches('[data-close-auth]')) showAuth(false);
  if (action.dataset.authTab) { document.querySelectorAll('.auth-tabs .tab').forEach(tab => tab.classList.toggle('is-active', tab === action)); document.querySelector('#login-form').hidden = action.dataset.authTab !== 'login'; document.querySelector('#register-form').hidden = action.dataset.authTab !== 'register'; }
  if (action.dataset.follow) { try { await request(`profiles/${action.dataset.follow}/follow/`, { method: 'POST', headers: authHeaders() }); action.textContent = 'Seguindo'; } catch (error) { setMessage(error.message); } }
  if (action.dataset.like) { try { await request(`posts/${action.dataset.like}/like/`, { method: 'POST', headers: authHeaders() }); loadTimeline(); } catch (error) { setMessage(error.message); } }
  if (action.dataset.toggleComment) { const form = document.querySelector(`form[data-comment="${action.dataset.toggleComment}"]`); form.hidden = !form.hidden; }
});

document.addEventListener('submit', async event => {
  const form = event.target; event.preventDefault();
  try {
    if (form.id === 'login-form' || form.id === 'register-form') { const endpoint = form.id === 'login-form' ? 'auth/login/' : 'auth/register/'; const data = await request(endpoint, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(Object.fromEntries(new FormData(form))) }); localStorage.setItem('chirp-token', data.token); showAuth(false); updateAuthenticatedState(); }
    if (form.id === 'post-form') { await request('posts/', { method: 'POST', headers: authHeaders(), body: JSON.stringify(Object.fromEntries(new FormData(form))) }); form.reset(); loadTimeline(); }
    if (form.matches('.comment-form')) { await request(`posts/${form.dataset.comment}/comments/`, { method: 'POST', headers: authHeaders(), body: JSON.stringify(Object.fromEntries(new FormData(form))) }); loadTimeline(); }
    if (form.id === 'profile-form') { const data = new FormData(form); if (!data.get('avatar').size) data.delete('avatar'); const response = await fetch(api + 'profiles/me/', {method: 'PATCH', headers: {Authorization: `Token ${token()}`}, body: data}); if (!response.ok) throw new Error('Não foi possível atualizar o perfil.'); document.querySelector('#profile-message').textContent = 'Perfil atualizado.'; }
  } catch (error) { const target = form.querySelector('.form-message') || document.querySelector('#auth-message'); if (target) target.textContent = error.message; }
});

document.querySelector('#refresh-feed')?.addEventListener('click', loadTimeline);
document.querySelector('#post-form textarea')?.addEventListener('input', event => { document.querySelector('#character-count').textContent = `${event.target.value.length} / 280`; });
updateAuthenticatedState();
if (document.body.dataset.page === 'home') loadTimeline();
if (document.body.dataset.page === 'explore') loadExplore().catch(error => setMessage(error.message));
if (document.body.dataset.page === 'profile') loadProfilePage().catch(error => setMessage(error.message));