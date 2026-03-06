const state = {
    sessionId: null,
    currentStep: 0,
    steps: [
        { key: 'upload', next: 'clean' },
        { key: 'clean', next: 'query' },
        { key: 'query', next: 'visualize' },
        { key: 'visualize', next: 'report' },
        { key: 'report', next: null },
    ],
    stepStatus: {
        upload: false,
        clean: false,
        query: false,
        visualize: false,
        report: false,
    },
};

const endpoints = {
    session: '/api/session',
    summary: '/api/summary',
    reset: '/api/reset',
    upload: '/api/upload',
    cleaningNeeds: '/api/cleaning/needs',
    clean: '/api/clean',
    query: '/api/query',
    history: '/api/history',
    autoViz: '/api/visualize/auto',
    customViz: '/api/visualize/custom',
    charts: '/api/charts',
    report: '/api/report',
};

async function ensureSession(forceNew = false) {
    if (!forceNew) {
        const stored = localStorage.getItem('ai-session');
        if (stored) {
            state.sessionId = stored;
            updateSessionBadge();
            return stored;
        }
    }

    const res = await fetch(endpoints.session, { method: 'POST' });
    const data = await res.json();
    state.sessionId = data.session_id;
    localStorage.setItem('ai-session', state.sessionId);
    updateSessionBadge();
    return state.sessionId;
}

function updateSessionBadge() {
    const badge = document.getElementById('session-status');
    if (badge && state.sessionId) {
        badge.textContent = `Session ${state.sessionId.slice(0, 8)}…`;
        badge.classList.add('ready');
    }
}

async function apiFetch(path, options = {}) {
    if (!state.sessionId) {
        await ensureSession();
    }
    const headers = options.headers || {};
    headers['X-Session-Id'] = state.sessionId;
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = headers['Content-Type'] || 'application/json';
    }
    const response = await fetch(path, { ...options, headers });
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unexpected error' }));
        throw new Error(error.detail || 'Request failed');
    }
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
        return response.json();
    }
    return response;
}

function showToast(message, variant = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.dataset.variant = variant;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3500);
}

function getPrevStepKey(stepKey) {
    const index = state.steps.findIndex((step) => step.key === stepKey);
    if (index <= 0) return null;
    return state.steps[index - 1].key;
}

function canNavigateTo() {
    return true;
}

function isStepUnlocked() {
    return true;
}

function showStepByKey(stepKey) {
    const index = state.steps.findIndex((step) => step.key === stepKey);
    if (index === -1) return;
    state.currentStep = index;
    state.steps.forEach((step, idx) => {
        const card = document.querySelector(`[data-step-card="${step.key}"]`);
        if (card) {
            card.classList.toggle('active-step', idx === index);
        }
        const tab = document.querySelector(`[data-step-tab="${step.key}"]`);
        if (tab) {
            tab.classList.toggle('active', idx === index);
        }
    });
    updateNextButtons();
    updateStageTabsState();
}

function updateNextButtons() {
    state.steps.forEach((step) => {
        const card = document.querySelector(`[data-step-card="${step.key}"]`);
        const nextBtn = card?.querySelector('.next-btn');
        if (nextBtn) {
            nextBtn.disabled = !state.stepStatus[step.key];
        }
    });
}

function updateStageTabsState() {
    state.steps.forEach((step) => {
        const tab = document.querySelector(`[data-step-tab="${step.key}"]`);
        if (!tab) return;
        tab.classList.toggle('complete', state.stepStatus[step.key]);
    });
}

function markStepComplete(stepKey) {
    if (!state.stepStatus[stepKey]) {
        state.stepStatus[stepKey] = true;
        updateNextButtons();
        updateStageTabsState();
    }
}

function resetStageProgress() {
    Object.keys(state.stepStatus).forEach((key) => {
        state.stepStatus[key] = false;
    });
    state.currentStep = 0;
    showStepByKey(state.steps[0].key);
}

function renderMetrics(summary) {
    const container = document.getElementById('status-metrics');
    if (!container) return;
    const entries = [
        ['Data Loaded', summary.has_data ? 'Yes' : 'No'],
        ['Rows', summary.rows.toLocaleString()],
        ['Columns', summary.columns.toString()],
        ['Cleaning Ops', summary.cleaning_operations.toString()],
        ['Queries', summary.queries_executed.toString()],
        ['Charts', summary.charts_generated.toString()],
        ['Insights', summary.insights_count.toString()],
    ];
    container.innerHTML = entries
        .map(
            ([label, value]) => `
            <div class="metric-card">
                <span>${label}</span>
                <strong>${value}</strong>
            </div>`
        )
        .join('');
}

function renderPreview(metadata) {
    const preview = document.getElementById('dataset-preview');
    if (!preview) return;
    const columns = metadata.preview?.columns || [];
    const head = metadata.preview?.head || [];
    const issues = metadata.metadata?.issues || {};
    preview.innerHTML = `
        <h3>${metadata.metadata?.rows?.toLocaleString() || 0} rows • ${metadata.metadata?.columns || 0} columns</h3>
        <p class="muted">Memory: ${(metadata.metadata?.memory_usage || 0).toFixed(2)} MB</p>
        <div class="scroll-block">
            <strong>Columns</strong>
            <ul>${columns
                .map(
                    (col) => `
                        <li>
                            <span>${col.name}</span>
                            <small>${col.dtype}</small>
                        </li>`
                )
                .join('')}</ul>
        </div>
        <div class="scroll-block table-block">
            <strong>Sample Rows</strong>
            <table>
                <thead>
                    <tr>${Object.keys(head[0] || {})
                        .map((column) => `<th>${column}</th>`)
                        .join('')}</tr>
                </thead>
                <tbody>
                    ${head
                        .map(
                            (row) => `
                        <tr>
                            ${Object.values(row)
                                .map((value) => `<td>${value ?? ''}</td>`)
                                .join('')}
                        </tr>`
                        )
                        .join('')}
                </tbody>
            </table>
        </div>
        <div class="issues">
            <strong>Warnings</strong>
            <ul>${(issues.warnings || ['No critical issues detected'])
                .map((warning) => `<li>${warning}</li>`)
                .join('')}</ul>
        </div>
    `;
}

function renderCleaningNeeds(needs) {
    const container = document.getElementById('cleaning-needs');
    if (!container) return;
    if (!needs.has_data) {
        container.textContent = 'Load a dataset to detect issues.';
        return;
    }
    const missingEntries = Object.entries(needs.missing_by_column || {});
    container.innerHTML = `
        <p><strong>Missing columns:</strong> ${missingEntries.length}</p>
        <ul>
            ${missingEntries
                .map(([col, cnt]) => `<li>${col}: ${cnt} gaps</li>`)
                .join('')}
        </ul>
        <p><strong>Duplicate rows:</strong> ${needs.duplicate_count}</p>
    `;
}

function renderCleaningSummary(summary) {
    const box = document.getElementById('cleaning-summary');
    if (!box) return;
    const data = summary.summary || {};
    box.innerHTML = `
        <p><strong>Rows removed:</strong> ${data.rows_removed || 0}</p>
        <p><strong>Missing values:</strong> ${data.missing_before || 0} → ${data.missing_after || 0}</p>
        <p><strong>Final rows:</strong> ${data.final_rows || 0}</p>
    `;
}

function renderQueryResult(result) {
    const panel = document.getElementById('query-result');
    if (!panel) return;
    if (!result) {
        panel.textContent = 'No result.';
        return;
    }
    const { explanation, result: payload } = result;
    let body = `<p>${explanation}</p>`;
    if (payload.type === 'dataframe') {
        const columns = payload.columns || [];
        const rows = payload.data || [];
        body += `
            <div class="scroll-block table-block">
                <table>
                    <thead><tr>${columns.map((c) => `<th>${c}</th>`).join('')}</tr></thead>
                    <tbody>
                        ${rows
                            .map(
                                (row) => `
                                <tr>
                                    ${columns.map((col) => `<td>${row[col]}</td>`).join('')}
                                </tr>`
                            )
                            .join('')}
                    </tbody>
                </table>
            </div>`;
    } else if (payload.type === 'series') {
        body += `<ul>${Object.entries(payload.data || {})
            .map(([key, value]) => `<li>${key}: ${value}</li>`)
            .join('')}</ul>`;
    } else {
        body += `<p class="highlight">${payload.data}</p>`;
    }
    panel.innerHTML = body;
}

function attachChart(chart) {
    const gallery = document.getElementById('chart-gallery');
    if (!gallery) return;
    const wrapper = document.createElement('div');
    wrapper.className = 'chart-card';
    wrapper.innerHTML = `<h4>${chart.title}</h4><div class="plot" id="plot-${crypto.randomUUID()}"></div>`;
    gallery.prepend(wrapper);
    const plotDiv = wrapper.querySelector('.plot');
    Plotly.newPlot(plotDiv, chart.figure.data, chart.figure.layout || {}, { displayModeBar: false });
}

function renderHistory(items) {
    const list = document.getElementById('history-list');
    if (!list) return;
    list.innerHTML = items
        .map(
            (item) => `
            <li>
                <strong>${item.query}</strong>
                <p>${item.explanation}</p>
                <small>${item.result_summary.type}</small>
            </li>`
        )
        .join('');
}

async function refreshSummary() {
    try {
        const summary = await apiFetch(endpoints.summary);
        renderMetrics(summary);
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function refreshHistory() {
    try {
        const history = await apiFetch(endpoints.history);
        renderHistory(history);
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function parseColumns(value) {
    if (!value) return [];
    return value
        .split(',')
        .map((col) => col.trim())
        .filter(Boolean);
}

function bindStepNavigation() {
    const tabs = document.querySelectorAll('[data-step-tab]');
    tabs.forEach((tab) => {
        tab.addEventListener('click', () => {
            const target = tab.getAttribute('data-step-tab');
            showStepByKey(target);
        });
    });

    const nextButtons = document.querySelectorAll('.next-btn');
    nextButtons.forEach((btn) => {
        btn.addEventListener('click', () => {
            const currentCard = btn.closest('[data-step-card]');
            const currentKey = currentCard?.getAttribute('data-step-card');
            const nextKey = btn.getAttribute('data-next-step');
            if (!currentKey || !nextKey) return;
            if (!state.stepStatus[currentKey]) {
                showToast('Finish this step to continue', 'warning');
                return;
            }
            showStepByKey(nextKey);
        });
    });
}

function bindUpload() {
    const form = document.getElementById('upload-form');
    const input = document.getElementById('data-file');
    const indicator = document.getElementById('selected-file');
    const indicatorDefault = indicator ? (indicator.dataset.placeholder || indicator.textContent || 'No file selected yet.') : 'No file selected yet.';

    if (indicator && !indicator.dataset.placeholder) {
        indicator.dataset.placeholder = indicatorDefault;
    }

    const updateIndicator = (file) => {
        if (!indicator) return;
        if (!file) {
            indicator.textContent = indicator.dataset.placeholder || indicatorDefault;
            return;
        }
        const sizeMb = file.size ? ` • ${(file.size / (1024 * 1024)).toFixed(2)} MB` : '';
        indicator.textContent = `${file.name}${sizeMb}`;
    };

    updateIndicator(null);

    input?.addEventListener('change', () => {
        const file = input.files?.[0];
        updateIndicator(file || null);
    });

    if (!form) return;
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        if (!input?.files?.length) {
            showToast('Select a file first', 'warning');
            return;
        }
        const fd = new FormData();
        fd.append('file', input.files[0]);
        try {
            const result = await apiFetch(endpoints.upload, { method: 'POST', body: fd });
            renderPreview(result);
            await refreshSummary();
            const needs = await apiFetch(endpoints.cleaningNeeds);
            renderCleaningNeeds(needs);
            updateIndicator(input.files[0]);
            markStepComplete('upload');
            showToast('Dataset profiled successfully', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    });
}

function bindCleaning() {
    const form = document.getElementById('clean-form');
    if (!form) return;
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const payload = {
            clean_missing: true,
            missing_strategy: document.getElementById('missing-strategy').value,
            missing_columns: parseColumns(document.getElementById('missing-columns').value),
            clean_duplicates: document.getElementById('handle-duplicates').checked,
            duplicate_strategy: document.getElementById('handle-duplicates').checked ? 'drop' : 'keep',
        };
        try {
            const result = await apiFetch(endpoints.clean, {
                method: 'POST',
                body: JSON.stringify(payload),
            });
            renderCleaningSummary(result);
            await refreshSummary();
            markStepComplete('clean');
            showToast(result.message, 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    });
}

function bindQuery() {
    const form = document.getElementById('query-form');
    if (!form) return;
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const query = document.getElementById('query-input').value.trim();
        if (!query) {
            showToast('Ask something first', 'warning');
            return;
        }
        try {
            const result = await apiFetch(endpoints.query, {
                method: 'POST',
                body: JSON.stringify({ query }),
            });
            renderQueryResult(result);
            await Promise.all([refreshSummary(), refreshHistory()]);
            markStepComplete('query');
            showToast('Query executed', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    });
}

function bindViz() {
    const autoButton = document.getElementById('auto-viz');
    if (autoButton) {
        autoButton.addEventListener('click', async (event) => {
            event.preventDefault();
            try {
                const result = await apiFetch(endpoints.autoViz, { method: 'POST' });
                (result.charts || []).forEach(attachChart);
                await refreshSummary();
                if ((result.charts || []).length) {
                    markStepComplete('visualize');
                }
                showToast(result.message, 'success');
            } catch (err) {
                showToast(err.message, 'error');
            }
        });
    }

    const customForm = document.getElementById('custom-viz-form');
    if (customForm) {
        customForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const payload = {
                chart_type: document.getElementById('chart-type').value,
                x_col: document.getElementById('x-col').value.trim(),
                y_col: document.getElementById('y-col').value.trim() || null,
            };
            if (!payload.x_col) {
                showToast('Provide an X column', 'warning');
                return;
            }
            try {
                const result = await apiFetch(endpoints.customViz, {
                    method: 'POST',
                    body: JSON.stringify(payload),
                });
                (result.charts || []).forEach(attachChart);
                await refreshSummary();
                if ((result.charts || []).length) {
                    markStepComplete('visualize');
                }
                showToast(result.message, 'success');
            } catch (err) {
                showToast(err.message, 'error');
            }
        });
    }
}

function bindReport() {
    const button = document.getElementById('generate-report');
    if (!button) return;
    button.addEventListener('click', async (event) => {
        event.preventDefault();
        try {
            const result = await apiFetch(endpoints.report, { method: 'POST' });
            const status = document.getElementById('report-status');
            if (status) {
                const fname = result.report_path.split('/').pop();
                status.innerHTML = `
                    <p>Report ready:</p>
                    <a href="/api/reports/${fname}" target="_blank">Download ${fname}</a>`;
            }
            markStepComplete('report');
            showToast('Report generated', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    });
}

function bindControls() {
    document.getElementById('primary-action')?.addEventListener('click', async (event) => {
        event.preventDefault();
        await ensureSession(true);
        await refreshSummary();
        showToast('Session refreshed', 'success');
    });

    document.getElementById('reset-session')?.addEventListener('click', async () => {
        try {
            await apiFetch(endpoints.reset, { method: 'POST' });
            document.getElementById('dataset-preview')?.innerHTML = '';
            document.getElementById('cleaning-summary')?.innerHTML = '';
            document.getElementById('query-result')?.innerHTML = '';
            document.getElementById('chart-gallery')?.innerHTML = '';
            document.getElementById('history-list')?.innerHTML = '';
            const fileIndicator = document.getElementById('selected-file');
            if (fileIndicator) {
                fileIndicator.textContent = fileIndicator.dataset.placeholder || 'No file selected yet.';
            }
            const fileInput = document.getElementById('data-file');
            if (fileInput) {
                fileInput.value = '';
            }
            resetStageProgress();
            await refreshSummary();
            showToast('Session cleared', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    });

    document.getElementById('refresh-history')?.addEventListener('click', refreshHistory);
}

async function bootstrap() {
    bindStepNavigation();
    bindUpload();
    bindCleaning();
    bindQuery();
    bindViz();
    bindReport();
    bindControls();
    resetStageProgress();
    try {
        await ensureSession();
        await refreshSummary();
        await refreshHistory();
        const needs = await apiFetch(endpoints.cleaningNeeds);
        renderCleaningNeeds(needs);
    } catch (err) {
        console.warn('Initialization issue:', err);
        showToast(err.message || 'Unable to connect to backend', 'error');
    }
}

bootstrap();
