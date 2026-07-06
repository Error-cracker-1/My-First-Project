(function(){
  const runModified = document.getElementById('run-modified');
  const runAll = document.getElementById('run-all');
  const logCard = document.getElementById('log-card');
  const logEl = document.getElementById('log');
  const statusEl = document.getElementById('status');
  let pollInterval = null;

  function startPolling(){
    if(pollInterval) return;
    pollInterval = setInterval(fetchStatus, 1500);
    logCard.style.display = 'block';
  }
  function stopPolling(){
    if(pollInterval) { clearInterval(pollInterval); pollInterval = null; }
  }
  async function fetchStatus(){
    try{
      const res = await fetch('/status');
      if(!res.ok) return;
      const j = await res.json();
      const lines = j.log || [];
      logEl.innerHTML = lines.map(l => escapeHtml(l)).join('<br>');
      logEl.scrollTop = logEl.scrollHeight;
      const running = j.state && j.state.running;
      statusEl.textContent = running ? `Running (${j.state.mode || 'unknown'})` : 'Idle';
      if(!running){ stopPolling(); }
    }catch(e){
      console.error(e);
    }
  }
  function escapeHtml(s){
    return s.replace(/[&<>]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c]; });
  }

  async function run(mode){
    try{
      const res = await fetch('/run-review', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({mode})
      });
      if(res.status === 409){
        alert('A review is already running.');
        return;
      }
      if(!res.ok){ alert('Failed to start review'); return; }
      startPolling();
      fetchStatus();
    }catch(e){
      alert('Request failed');
    }
  }

  if(runModified) runModified.addEventListener('click', ()=>run('modified'));
  if(runAll) runAll.addEventListener('click', ()=>run('all'));

  // initial poll to show status if already running
  fetchStatus();
})();
