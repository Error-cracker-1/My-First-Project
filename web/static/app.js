(function(){
  // --- Main application elements ---
  const runModifiedBtn = document.getElementById('run-modified');
  const runAllBtn = document.getElementById('run-all');
  const logCard = document.getElementById('log-card');
  const logEl = document.getElementById('log');
  const statusEl = document.getElementById('status');
  const progressContainerEl = document.getElementById('progress-container');
  const copyLogsBtn = document.getElementById('copy-logs-btn');

  // --- Repo Stats elements ---
  const refreshStatsBtn = document.getElementById('refresh-stats');
  const branchEl = document.getElementById('branch');
  const filesDiscoveredEl = document.getElementById('files_discovered');
  const lastReviewEl = document.getElementById('last_review');
  const totalProjectsEl = document.getElementById('total_projects');
  const lastUpdatedEl = document.getElementById('last_updated');
  const repoHealthEl = document.getElementById('repo_health');
  const statusIndicatorEl = document.getElementById('status-indicator');

  // --- Model Switch elements ---
  const switchModelBtn = document.getElementById('switch-model-btn');
  const modelSelectorEl = document.getElementById('model-selector');

  // --- Theme Toggle elements ---
  const themeToggleBtn = document.getElementById('theme-toggle');

  // --- File Browser & Modal Popup elements ---
  const fileSearchInput = document.getElementById('file-search-input');
  const filesListContainer = document.getElementById('files-list-container');
  const fileModal = document.getElementById('file-modal');
  const modalFilename = document.getElementById('modal-filename');
  const modalCopyBtn = document.getElementById('modal-copy-btn');
  const modalCloseBtn = document.getElementById('modal-close-btn');
  const modalFilesize = document.getElementById('modal-filesize');
  const modalFilemodified = document.getElementById('modal-filemodified');
  const modalCodeBlock = document.getElementById('modal-code-block');

  let pollInterval = null;
  let allFiles = []; // For file browser

  // --- Utility Functions ---

  function escapeHtml(s){
    const map = {'&':'&amp;','<':'&lt;','>':'&gt;'};
    return s.replace(/[&<>]/g, c => map[c]);
  }

  const formatBytes = (bytes, decimals = 1) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
  };

  const setupCopyButton = (buttonElement, textSourceElement, feedbackDuration = 1500) => {
    if (!buttonElement || !textSourceElement) return;

    buttonElement.addEventListener('click', () => {
      const textToCopy = textSourceElement.textContent;
      navigator.clipboard.writeText(textToCopy).then(() => {
        const originalText = buttonElement.textContent;
        buttonElement.textContent = 'Copied!';
        setTimeout(() => {
          buttonElement.textContent = originalText;
        }, feedbackDuration);
      }).catch(err => {
        console.error('Failed to copy content: ', err);
        alert('Failed to copy content to clipboard.');
      });
    });
  };

  function formatIsoDate(isoStr) {
    if (!isoStr) return 'n/a';
    try {
      const d = new Date(isoStr);
      if (isNaN(d.getTime())) return isoStr;
      const pad = (n) => String(n).padStart(2, '0');
      const year = d.getFullYear();
      const month = pad(d.getMonth() + 1);
      const day = pad(d.getDate());
      const hours = pad(d.getHours());
      const minutes = pad(d.getMinutes());
      const seconds = pad(d.getSeconds());
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    } catch {
      return isoStr;
    }
  }

  // --- Polling & Status Functions ---
  function startPolling(){
    if(pollInterval) return;
    pollInterval = setInterval(fetchStatus, 1500);
    if (logCard) logCard.style.display = 'block';
  }

  function stopPolling(){
    if(pollInterval) { clearInterval(pollInterval); pollInterval = null; }
  }

  async function fetchStatus(){
    try{
      const res = await fetch('/status');
      if(!res.ok) {
          console.error('Failed to fetch status: ', res.status, res.statusText);
          return;
      }
      const j = await res.json();
      const lines = j.log || [];
      if (logEl) {
        logEl.innerHTML = lines.map(l => escapeHtml(l)).join('<br>');
        logEl.scrollTop = logEl.scrollHeight;
      }
      
      const running = j.state?.running;
      const progress = j.state?.progress || {};
      const pct = progress.percentage !== undefined ? progress.percentage : 0;
      const completed = progress.completed !== undefined ? progress.completed : 0;
      const total = progress.total !== undefined ? progress.total : 0;
      const mode = j.state?.mode || 'n/a';
      const startTime = j.state?.start_time;
      const endTime = j.state?.end_time;
      const cancelled = j.state?.cancelled;
      const exitCode = j.state?.exit_code;

      if (progressContainerEl) {
        progressContainerEl.style.display = running ? 'block' : 'none';
      }
      if (statusEl) {
        statusEl.textContent = running ? `Running (${j.state?.mode || 'unknown'})` : 'Idle';
      }

      // Update Live Review log progress info container
      const progressInfoEl = document.getElementById('progress-info-container');
      if (progressInfoEl) {
        progressInfoEl.style.display = running ? 'block' : 'none';
      }
      
      const progressBar = document.querySelector('#progress-container .progress-bar');
      if (progressBar) {
        progressBar.style.width = `${pct}%`;
      }

      const pctEl = document.getElementById('progress-percentage');
      if (pctEl) {
        pctEl.textContent = `${pct}%`;
      }

      const labelEl = document.getElementById('progress-label');
      if (labelEl) {
        if (total > 0) {
          labelEl.textContent = `Reviewing files: ${completed} of ${total}`;
        } else {
          labelEl.textContent = `Preparing AI review...`;
        }
      }

      // Update Review Manager card
      const mgrStatusEl = document.getElementById('mgr-status');
      if (mgrStatusEl) {
        mgrStatusEl.className = 'badge'; // Reset classes
        if (running) {
          mgrStatusEl.textContent = 'Running ⏳';
          mgrStatusEl.classList.add('badge-running');
        } else if (cancelled) {
          mgrStatusEl.textContent = 'Cancelled ❌';
          mgrStatusEl.classList.add('badge-cancelled');
        } else if (exitCode === 0) {
          mgrStatusEl.textContent = 'Success ✅';
          mgrStatusEl.classList.add('badge-success');
        } else if (exitCode !== null && exitCode !== undefined) {
          mgrStatusEl.textContent = `Failed ⚠️ (Exit: ${exitCode})`;
          mgrStatusEl.classList.add('badge-failed');
        } else {
          mgrStatusEl.textContent = 'Idle';
          mgrStatusEl.classList.add('badge-idle');
        }
      }

      const mgrModeEl = document.getElementById('mgr-mode');
      if (mgrModeEl) {
        mgrModeEl.textContent = mode === 'all' ? 'Full Repository' : (mode === 'modified' ? 'Modified Files Only' : mode);
      }

      const mgrStartedEl = document.getElementById('mgr-started');
      if (mgrStartedEl) {
        mgrStartedEl.textContent = formatIsoDate(startTime);
      }

      const mgrEndedGroup = document.getElementById('mgr-ended-group');
      if (mgrEndedGroup) {
        mgrEndedGroup.style.display = running ? 'none' : 'flex';
      }

      const mgrEndedEl = document.getElementById('mgr-ended');
      if (mgrEndedEl) {
        mgrEndedEl.textContent = formatIsoDate(endTime);
      }

      const mgrProgressEl = document.getElementById('mgr-progress');
      if (mgrProgressEl) {
        if (total > 0) {
          mgrProgressEl.textContent = `${pct}% (${completed}/${total})`;
        } else {
          mgrProgressEl.textContent = running ? 'Preparing...' : '0%';
        }
      }

      const cancelBtn = document.getElementById('cancel-review-btn');
      if (cancelBtn) {
        cancelBtn.style.display = running ? 'block' : 'none';
      }

      // Update Detailed File Changes container
      const fileChangesContainer = document.getElementById('file-changes-container');
      if (fileChangesContainer && j.file_changes) {
        if (j.file_changes.length > 0) {
          let rowsHtml = j.file_changes.map(fc => `
            <tr style="border-bottom: 1px solid var(--border); font-size: 0.9rem;">
              <td style="padding: 10px;"><code style="background: var(--accent-light, rgba(79, 70, 229, 0.1)); color: var(--accent); padding: 3px 8px; border-radius: 6px;">${escapeHtml(fc.file || '')}</code></td>
              <td style="padding: 10px;">${escapeHtml(fc.what || '')}</td>
              <td style="padding: 10px;">${escapeHtml(fc.why || '')}</td>
            </tr>
          `).join('');
          fileChangesContainer.innerHTML = `
            <div style="overflow-x: auto;">
              <table style="width: 100%; border-collapse: collapse;">
                <thead>
                  <tr style="border-bottom: 1px solid var(--border); text-align: left; font-size: 0.85rem; color: var(--muted);">
                    <th style="padding: 10px;">Which File</th>
                    <th style="padding: 10px;">What Changed</th>
                    <th style="padding: 10px;">Why Changed</th>
                  </tr>
                </thead>
                <tbody>
                  ${rowsHtml}
                </tbody>
              </table>
            </div>
          `;
        } else {
          fileChangesContainer.innerHTML = `<p style="color: var(--muted); padding: 8px 0; margin: 0;">No file change details recorded yet. Run a review to generate detailed file change explanations.</p>`;
        }
      }

      // Update Review History card container
      const reviewHistoryContainer = document.getElementById('review-history-container');
      if (reviewHistoryContainer && j.review_history) {
        if (j.review_history.length > 0) {
          let historyHtml = j.review_history.map(item => `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: var(--bg); border: 1px solid var(--border); border-radius: 10px;">
              <div style="display: flex; flex-direction: column; gap: 2px;">
                <span style="font-weight: 600; font-size: 0.92rem; color: var(--text);">${escapeHtml(item.timestamp || '')}</span>
                ${item.report_name ? `<span style="font-size: 0.8rem; color: var(--muted);">Report: ${escapeHtml(item.report_name)}</span>` : ''}
              </div>
              <span class="badge" style="background: var(--accent-light, rgba(79, 70, 229, 0.12)); color: var(--accent); font-weight: 700; padding: 6px 14px; border-radius: 20px; font-size: 0.88rem;">
                Health: ${escapeHtml(String(item.health || ''))}
              </span>
            </div>
          `).join('');
          reviewHistoryContainer.innerHTML = `<div style="display: flex; flex-direction: column; gap: 10px;">${historyHtml}</div>`;
        } else {
          reviewHistoryContainer.innerHTML = `<p style="color: var(--muted); padding: 8px 0; margin: 0;">No review history recorded yet.</p>`;
        }
      }

      if (running) {

        startPolling();
      } else {
        stopPolling();
      }
    }catch(e){
      console.error('Error fetching status:', e);
    }
  }

  // --- Review Run Functionality ---
  async function runReview(mode){
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
      console.error('Request to start review failed:', e);
      alert('Request failed');
    }
  }

  if(runModifiedBtn) runModifiedBtn.addEventListener('click', ()=>runReview('modified'));
  if(runAllBtn) runAllBtn.addEventListener('click', ()=>runReview('all'));

  // --- Repo Stats Functionality ---
  if(refreshStatsBtn) refreshStatsBtn.addEventListener('click', async () => {
    refreshStatsBtn.disabled = true;
    refreshStatsBtn.textContent = 'Refreshing...';
    try {
      const response = await fetch('/repo-stats');
      if (!response.ok) {
          console.error('Failed to fetch repo stats:', response.status, response.statusText);
          throw new Error('Failed to fetch repo stats');
      }
      const data = await response.json();
      
      if (branchEl) branchEl.textContent = data.branch || 'n/a';
      if (filesDiscoveredEl) filesDiscoveredEl.textContent = data.files_discovered || '0';
      if (lastReviewEl) lastReviewEl.textContent = data.last_review || 'never';
      
      if (totalProjectsEl && data.total_projects != null) {
        totalProjectsEl.textContent = data.total_projects;
      }
      if (lastUpdatedEl && data.last_updated != null) {
        lastUpdatedEl.textContent = data.last_updated;
      }
      
      function cleanHealthVal(val) {
        if (val == null) return '100%';
        let s = String(val).trim();
        if (s.endsWith('%')) {
          let num = parseFloat(s);
          if (isNaN(num)) return '100%';
          if (num > 100) return '100%';
          return Math.round(num) + '%';
        }
        let num = parseFloat(s);
        if (isNaN(num)) return '100%';
        if (num <= 1.0 && num > 0) return Math.round(num * 100) + '%';
        if (num > 100) return '100%';
        return Math.round(num) + '%';
      }

      if (repoHealthEl && data.repo_health != null) {
        let displayVal = cleanHealthVal(data.repo_health);
        repoHealthEl.textContent = displayVal;
        let numVal = parseFloat(displayVal);
        const isHealthy = isNaN(numVal) || numVal >= 70;
        if (statusIndicatorEl) {
          statusIndicatorEl.textContent = isHealthy ? '✅' : '❗';
          statusIndicatorEl.title = isHealthy ? 'Healthy' : 'Needs Attention';
          statusIndicatorEl.style.display = ''; // Ensure it's visible
        }
      } else if (repoHealthEl) {
        repoHealthEl.textContent = '100%';
        if (statusIndicatorEl) {
          statusIndicatorEl.textContent = '✅';
          statusIndicatorEl.title = 'Healthy';
          statusIndicatorEl.style.display = '';
        }
      }

      const reviewHistoryContainer = document.getElementById('review-history-container');
      if (reviewHistoryContainer && data.review_history) {
        if (data.review_history.length > 0) {
          let historyHtml = data.review_history.map(item => `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: var(--bg); border: 1px solid var(--border); border-radius: 10px;">
              <div style="display: flex; flex-direction: column; gap: 2px;">
                <span style="font-weight: 600; font-size: 0.92rem; color: var(--text);">${escapeHtml(item.timestamp || '')}</span>
                ${item.report_name ? `<span style="font-size: 0.8rem; color: var(--muted);">Report: ${escapeHtml(item.report_name)}</span>` : ''}
              </div>
              <span class="badge" style="background: var(--accent-light, rgba(79, 70, 229, 0.12)); color: var(--accent); font-weight: 700; padding: 6px 14px; border-radius: 20px; font-size: 0.88rem;">
                Health: ${escapeHtml(cleanHealthVal(item.health))}
              </span>
            </div>
          `).join('');
          reviewHistoryContainer.innerHTML = `<div style="display: flex; flex-direction: column; gap: 10px;">${historyHtml}</div>`;
        } else {
          reviewHistoryContainer.innerHTML = `<p style="color: var(--muted); padding: 8px 0; margin: 0;">No review history recorded yet.</p>`;
        }
      }
    } catch (e) {
      console.error('Failed to refresh stats:', e);
      alert('Failed to refresh repository statistics.');
    } finally {
      refreshStatsBtn.disabled = false;
      refreshStatsBtn.textContent = 'Refresh';
    }
  });

  // --- Model Switch Functionality ---
  if(switchModelBtn && modelSelectorEl) switchModelBtn.addEventListener('click', async () => {
    const model = modelSelectorEl.value;
    switchModelBtn.disabled = true;
    switchModelBtn.textContent = 'Switching...';
    try {
      const res = await fetch('/switch-model', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({model})
      });
      if (!res.ok) {
          const errorText = await res.text();
          throw new Error(`Failed to switch model: ${errorText}`);
      }
      alert('Model switched successfully');
    } catch (e) {
      console.error('Switch model error:', e);
      alert(`Failed to switch model: ${e.message || 'Unknown error'}`);
    } finally {
      switchModelBtn.disabled = false;
      switchModelBtn.textContent = 'Switch Model';
    }
  });

  // --- Theme Toggle Functionality ---
  const setTheme = (isDark) => {
    document.body.classList.toggle('dark-mode', isDark);
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
      themeIcon.textContent = isDark ? '☀️' : '🌙';
    }
  };

  if (themeToggleBtn) {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setTheme(savedTheme === 'dark');
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setTheme(true);
    } else {
      setTheme(false); // Default to light if no preference and no dark scheme detected
    }

    themeToggleBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const isDark = !document.body.classList.contains('dark-mode');
      setTheme(isDark);
    });
  }

  // --- Copy Logs Functionality ---
  setupCopyButton(copyLogsBtn, logEl, 2000);

  // --- File Browser & Modal Popup ---
  async function loadFileList() {
    if (!filesListContainer) return;
    try {
      const res = await fetch('/api/files');
      if (!res.ok) {
          console.error('Failed to fetch file list:', res.status, res.statusText);
          throw new Error('Failed to fetch files');
      }
      const data = await res.json();
      allFiles = data.files || [];
      renderFileList(allFiles);
    } catch (e) {
      console.error('Error loading file list:', e);
      if (filesListContainer) { // Defensive check
        filesListContainer.innerHTML = `<div style="color: var(--danger); text-align: center; padding: 12px;">Error loading file list.</div>`;
      }
    }
  }

  function renderFileList(files) {
    if (!filesListContainer) return;
    if (files.length === 0) {
      filesListContainer.innerHTML = `<div style="color: var(--muted); text-align: center; padding: 12px;">No matching files found.</div>`;
      return;
    }
    
    filesListContainer.innerHTML = files.map(file => {
      const escapedFile = escapeHtml(file);
      return `
        <div class="file-item" data-path="${escapedFile}">
          <span class="file-item-path">${escapedFile}</span>
          <span class="file-item-action">View &rarr;</span>
        </div>
      `;
    }).join('');

    filesListContainer.querySelectorAll('.file-item').forEach(item => {
      item.addEventListener('click', () => {
        const path = item.getAttribute('data-path');
        openFileModal(path);
      });
    });
  }

  if (fileSearchInput) {
    fileSearchInput.addEventListener('input', () => {
      const query = fileSearchInput.value.toLowerCase().trim();
      const filtered = allFiles.filter(file => file.toLowerCase().includes(query));
      renderFileList(filtered);
    });
  }

  async function openFileModal(path) {
    if (!fileModal || !modalFilename || !modalFilesize || !modalFilemodified || !modalCodeBlock) return;
    
    // Set loading state
    modalFilename.textContent = path;
    modalFilesize.textContent = 'Loading...';
    modalFilemodified.textContent = '';
    modalCodeBlock.textContent = 'Fetching file contents...';
    fileModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';

    try {
      const res = await fetch(`/api/file-content?path=${encodeURIComponent(path)}`);
      if (!res.ok) {
        const errorBody = await res.text();
        let errorMessage = 'Failed to fetch content';
        try {
          const errData = JSON.parse(errorBody);
          errorMessage = errData.error || errorMessage;
        } catch {
          errorMessage = errorBody || errorMessage;
        }
        throw new Error(errorMessage);
      }
      const data = await res.json();
      
      modalFilesize.textContent = formatBytes(data.size);
      modalFilemodified.textContent = `Last modified: ${data.last_modified || 'unknown'}`;
      modalCodeBlock.textContent = data.content;
    } catch (e) {
      console.error('Error opening file modal:', e);
      modalFilesize.textContent = 'Error';
      modalCodeBlock.textContent = `Error loading file: ${e.message}`;
    }
  }

  function closeFileModal() {
    if (fileModal) {
      fileModal.style.display = 'none';
      document.body.style.overflow = '';
    }
  }

  if (modalCloseBtn) {
    modalCloseBtn.addEventListener('click', closeFileModal);
  }

  if (fileModal) {
    fileModal.addEventListener('click', (e) => {
      if (e.target === fileModal) {
        closeFileModal();
      }
    });
  }

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && fileModal && fileModal.style.display === 'flex') {
      closeFileModal();
    }
  });

  setupCopyButton(modalCopyBtn, modalCodeBlock);

  // --- Cancel Review Handler ---
  const cancelBtnElement = document.getElementById('cancel-review-btn');
  if (cancelBtnElement) {
    cancelBtnElement.addEventListener('click', async () => {
      if (!confirm('Are you sure you want to stop/cancel the current review?')) {
        return;
      }
      cancelBtnElement.disabled = true;
      cancelBtnElement.textContent = 'Stopping...';
      try {
        const res = await fetch('/cancel-review', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        if (res.ok) {
          alert('Review cancellation requested.');
          fetchStatus();
        } else {
          const err = await res.json();
          alert('Error cancelling review: ' + (err.error || 'Unknown error'));
        }
      } catch (e) {
        console.error('Error stopping review:', e);
        alert('Failed to request review cancellation.');
      } finally {
        cancelBtnElement.disabled = false;
        cancelBtnElement.textContent = 'Stop Current Review';
      }
    });
  }

  // --- Initialize ---
  fetchStatus(); // initial poll to show status if already running
  loadFileList(); // Load files on page init

})();