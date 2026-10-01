(() => {
  const screens = [...document.querySelectorAll('.screen')];
  const backButton = document.querySelector('.back-button');
  const toast = document.querySelector('.toast');
  const flow = ['discover', 'import', 'review', 'adapt', 'template-preview'];
  let current = 'discover';
  let toastTimer;

  function showToast(message) {
    toast.textContent = message;
    toast.classList.add('visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('visible'), 2300);
  }

  function navigate(name) {
    if (!document.querySelector(`[data-screen="${name}"]`)) return;
    current = name;
    screens.forEach((screen) => screen.classList.toggle('active', screen.dataset.screen === name));
    backButton.hidden = name === 'discover' || name === 'library';
    document.querySelectorAll('.tab').forEach((tab) => {
      const selected = tab.dataset.tab === name || (name === 'import' && tab.dataset.tab === 'create');
      tab.classList.toggle('active', selected);
    });
    document.querySelector('.screen.active .screen-scroll')?.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function goBack() {
    const index = flow.indexOf(current);
    if (index > 0) navigate(flow[index - 1]);
    else navigate('discover');
  }

  function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.hidden = false;
  }
  function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.hidden = true;
  }

  document.addEventListener('click', (event) => {
    const go = event.target.closest('[data-go]');
    if (go) {
      event.preventDefault();
      navigate(go.dataset.go);
      return;
    }

    const message = event.target.closest('[data-toast]');
    if (message) {
      showToast(message.dataset.toast);
      return;
    }

    const decision = event.target.closest('.decision');
    if (decision) {
      const card = decision.closest('.moment-card');
      card.querySelectorAll('.decision').forEach((button) => button.classList.remove('selected', 'danger'));
      decision.classList.add('selected');
      if (decision.dataset.decision === 'exclude') decision.classList.add('danger');
      card.classList.toggle('is-excluded', decision.dataset.decision === 'exclude');
      updateIncludedSummary();
      return;
    }

    const mode = event.target.closest('.mode');
    if (mode) {
      document.querySelectorAll('.mode').forEach((button) => button.classList.toggle('active', button === mode));
      const preview = document.querySelector('.recipe-preview');
      const templateMode = mode.dataset.mode === 'template';
      preview.style.background = templateMode ? '#e4d8f8' : 'linear-gradient(160deg,#e9b0a1,#825a8f 78%)';
      document.querySelector('.preview-pill').textContent = templateMode ? 'YOUR TEMPLATE' : 'REFERENCE · EXAMPLE ONLY';
      document.querySelector('.recipe-frame > span').innerHTML = templateMode ? 'YOUR MOMENT<br>GOES HERE' : 'ORIGINAL<br>REFERENCE';
      return;
    }

    const option = event.target.closest('.profile-option');
    if (option) {
      document.querySelectorAll('.profile-option').forEach((button) => button.classList.toggle('selected', button === option));
      const label = option.textContent.trim().split(/\s+/).slice(0, -1).join(' ');
      document.querySelector('#profile-select b').textContent = `${label} · ${option.querySelector('span').textContent}`;
      return;
    }

    const tab = event.target.closest('[data-tab="profile"]');
    if (tab) {
      openModal('login-modal');
      return;
    }
  });

  backButton.addEventListener('click', goBack);
  document.querySelector('.wordmark').addEventListener('click', (event) => {
    event.preventDefault();
    navigate('discover');
  });
  document.querySelector('.avatar').addEventListener('click', () => openModal('login-modal'));
  document.querySelector('#open-account').addEventListener('click', () => openModal('login-modal'));

  document.querySelector('#choose-video').addEventListener('click', () => {
    document.querySelector('#analyze-button').disabled = false;
    document.querySelector('#choose-video').textContent = 'sample-reference.mp4 · 17 sec';
    document.querySelector('.upload-zone strong').textContent = 'Sample reference selected';
    document.querySelector('.upload-zone > span').textContent = 'Demo clip · 9:16 · sound included';
    document.querySelector('.upload-icon').textContent = '✓';
    showToast('Demo only: no video was opened or uploaded.');
  });
  document.querySelector('#analyze-button').addEventListener('click', () => {
    const button = document.querySelector('#analyze-button');
    button.disabled = true;
    button.textContent = 'Finding moments…';
    setTimeout(() => {
      button.disabled = false;
      button.innerHTML = 'Analyze video <span>→</span>';
      navigate('review');
    }, 650);
  });

  document.querySelector('#fine-tune').addEventListener('click', () => {
    const timeline = document.querySelector('#compact-timeline');
    timeline.classList.toggle('expanded');
    showToast(timeline.classList.contains('expanded') ? 'Timing view expanded · sample only.' : 'Compact timing view restored.');
  });
  document.querySelector('#add-moment').addEventListener('click', () => showToast('Moment splitting and merging are not interactive in this concept yet.'));
  document.querySelector('#use-idea').addEventListener('click', (event) => {
    event.currentTarget.textContent = 'Idea selected ✓';
    event.currentTarget.classList.remove('primary');
    event.currentTarget.classList.add('secondary');
    showToast('Shot prompt added to this moment.');
  });
  document.querySelector('#open-edit-tools').addEventListener('click', () => {
    const panel = document.querySelector('#mini-tools');
    panel.hidden = !panel.hidden;
    document.querySelector('#open-edit-tools').textContent = panel.hidden ? 'Edit →' : 'Done ✓';
  });
  document.querySelector('.toggle').addEventListener('click', (event) => event.currentTarget.classList.toggle('on'));
  document.querySelector('#profile-select').addEventListener('click', () => openModal('profile-modal'));
  document.querySelector('#close-profile-modal').addEventListener('click', () => closeModal('profile-modal'));
  document.querySelector('#close-login-modal').addEventListener('click', () => closeModal('login-modal'));
  document.querySelectorAll('.sheet-close').forEach((button) => button.addEventListener('click', () => {
    closeModal('profile-modal');
    closeModal('login-modal');
  }));
  document.querySelectorAll('.modal-backdrop').forEach((backdrop) => backdrop.addEventListener('click', (event) => {
    if (event.target === backdrop) backdrop.hidden = true;
  }));
  document.querySelector('#bookmark-recipe').addEventListener('click', (event) => {
    event.currentTarget.textContent = event.currentTarget.textContent === '♡' ? '♥' : '♡';
    showToast(event.currentTarget.textContent === '♥' ? 'Saved to your sample list.' : 'Removed from your sample list.');
  });
  document.querySelector('#save-recipe').addEventListener('click', () => {
    showToast('Concept only: your template was not saved.');
    setTimeout(() => navigate('library'), 900);
  });
  document.querySelector('.dismiss').addEventListener('click', () => document.querySelector('.local-note').remove());

  function updateIncludedSummary() {
    const cards = [...document.querySelectorAll('.moment-card')];
    const excluded = cards.filter((card) => card.classList.contains('is-excluded')).length;
    const included = cards.length - excluded;
    const seconds = cards.reduce((total, card) => {
      if (card.classList.contains('is-excluded')) return total;
      const duration = card.dataset.moment === '1' ? 3 : card.dataset.moment === '2' ? 5 : card.dataset.moment === '3' ? 5 : 4;
      return total + duration;
    }, 0);
    document.querySelector('#included-count').textContent = included;
    document.querySelector('#runtime-count').textContent = `${seconds} sec`;
  }
})();
