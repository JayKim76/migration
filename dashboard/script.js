const stepData = {
    1: { title: "Database Connectivity", subtitle: "Source and Target environment link verification." },
    2: { title: "DDL Extraction", subtitle: "Extracting metadata and schema structures." },
    3: { title: "Data Export", subtitle: "Packaging data into portable dump files." },
    4: { title: "Target Setup", subtitle: "Preparing the destination environment." },
    5: { title: "Data Ingestion", subtitle: "Injecting data into the target database." },
    6: { title: "Validation & Report", subtitle: "Ensuring data integrity and consistency." }
};

const API_BASE = ""; // Relative to the server

async function callApi(endpoint, data = {}, terminalId = null) {
    const terminal = terminalId ? document.getElementById(terminalId) : null;
    if (terminal) {
        terminal.innerHTML += `[API] Calling ${endpoint}...<br>`;
        terminal.scrollTop = terminal.scrollHeight;
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        
        if (terminal) {
            terminal.innerHTML += `<pre style="color: #fff; white-space: pre-wrap;">${result.output}</pre>`;
            terminal.innerHTML += `[STATUS] ${result.status.toUpperCase()}<br>`;
            terminal.scrollTop = terminal.scrollHeight;
        }
        return result;
    } catch (error) {
        if (terminal) {
            terminal.innerHTML += `<span style="color: #ff4d4d;">[ERROR] ${error.message}</span><br>`;
        }
        return { status: "error", output: error.message };
    }
}

async function showStep(stepNumber) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-step') == stepNumber) {
            item.classList.add('active');
        }
    });

    // Update content
    document.querySelectorAll('.step-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`step-${stepNumber}`).classList.add('active');

    // Update header
    document.getElementById('step-title').innerText = stepData[stepNumber].title;
    document.getElementById('step-subtitle').innerText = stepData[stepNumber].subtitle;
}

async function nextStep(stepNumber) {
    showStep(stepNumber);
    document.querySelector('main').scrollTo({ top: 0, behavior: 'smooth' });
}

// Track connection status
let sourceConnected = false;
let targetConnected = false;

async function testConnection(type) {
    const btnId = type === 'source' ? 'btn-test-source' : 'btn-test-target';
    const btn = document.getElementById(btnId);
    
    btn.disabled = true;
    const originalText = btn.innerText;
    btn.innerText = "Testing...";
    
    const result = await callApi('/api/connect', { type: type }, 'step-1-terminal');
    
    btn.disabled = false;
    btn.innerText = originalText;

    if (result.status === "success") {
        if (type === 'source') {
            sourceConnected = true;
            btn.style.background = 'var(--accent-green)';
            btn.innerText = "Source Verified ✓";
        } else {
            targetConnected = true;
            btn.style.background = 'var(--accent-green)';
            btn.innerText = "Target Verified ✓";
        }

        // If both are connected, automatically proceed or show a message
        if (sourceConnected && targetConnected) {
            setTimeout(() => nextStep(2), 1000);
        }
    } else {
        btn.style.background = '#ff4d4d';
        btn.innerText = "Test Failed ✗";
        setTimeout(() => {
            btn.style.background = '';
            btn.innerText = originalText;
        }, 3000);
    }
}

async function runStep1() {
    // This is now handled by testConnection, but kept for compatibility if needed
    await testConnection('source');
    if (sourceConnected) await testConnection('target');
}

async function runStep2() {
    const btn = document.querySelector('#step-2 .btn');
    btn.disabled = true;
    btn.innerText = "Extracting...";
    
    const result = await callApi('/api/extract-ddl', {}, 'step-2-terminal');
    
    btn.disabled = false;
    btn.innerText = "Run Extraction";
    if (result.status === "success") nextStep(3);
}

function toggleExportOptions() {
    const method = document.querySelector('input[name="exportMethod"]:checked').value;
    const expdpOptions = document.querySelectorAll('.expdp-option');
    const expOptions = document.querySelectorAll('.exp-option');
    
    if (method === 'expdp') {
        expdpOptions.forEach(el => el.style.display = 'flex');
        expOptions.forEach(el => el.style.display = 'none');
    } else {
        expdpOptions.forEach(el => el.style.display = 'none');
        expOptions.forEach(el => el.style.display = 'flex');
    }
}

function toggleExportMode() {
    const mode = document.getElementById('exp-mode').value;
    const targetGroup = document.getElementById('target-objects-group');
    const targetLabel = document.getElementById('exp-targets-label');
    
    if (mode === 'full') {
        targetGroup.style.display = 'none';
    } else {
        targetGroup.style.display = 'flex';
        if (mode === 'schema') targetLabel.innerText = "Target Schemas";
        else if (mode === 'table') targetLabel.innerText = "Target Tables";
        else if (mode === 'tablespace') targetLabel.innerText = "Target Tablespaces";
    }
}

async function runStep3() {
    const btn = document.querySelector('#step-3 .btn');
    btn.disabled = true;
    btn.innerText = "Exporting...";
    
    const container = document.getElementById('export-progress-container');
    const bar = document.getElementById('export-progress');
    const text = document.getElementById('export-progress-text');
    container.style.display = 'block';
    bar.style.width = '30%';
    text.innerText = "Starting export process...";
    
    // Gather payload
    const method = document.querySelector('input[name="exportMethod"]:checked').value;
    const mode = document.getElementById('exp-mode').value;
    
    const payload = {
        method: method,
        mode: mode,
        directory: document.getElementById('exp-directory').value,
        dumpfile: document.getElementById('exp-dumpfile').value,
        logfile: document.getElementById('exp-logfile').value
    };
    
    if (mode !== 'full') {
        payload.targets = document.getElementById('exp-targets').value;
    }
    
    if (method === 'expdp') {
        payload.parallel = parseInt(document.getElementById('exp-parallel').value, 10);
        payload.compression = document.getElementById('exp-compression').value;
        const content = document.getElementById('exp-content').value;
        if (content) payload.content = content;
        
        const exclude = document.getElementById('exp-exclude').value;
        if (exclude) payload.exclude = exclude;
        
        payload.estimate_only = document.getElementById('exp-estimate').checked;
    } else {
        payload.consistent = document.getElementById('exp-consistent').checked;
    }
    
    const result = await callApi('/api/export', payload, 'step-3-terminal');
    
    bar.style.width = '100%';
    text.innerText = result.status === "success" ? "Export completed!" : "Export failed.";
    btn.disabled = false;
    btn.innerText = "Continue to Target Setup";
    
    if (result.status === "success") nextStep(4);
}

async function runStep4() {
    const btn = document.querySelector('#step-4 .btn');
    btn.disabled = true;
    btn.innerText = "Setting up...";
    
    const result = await callApi('/api/setup-target', {}, 'step-4-terminal');
    
    btn.disabled = false;
    btn.innerText = "Start Ingestion";
    if (result.status === "success") nextStep(5);
}

async function runStep5() {
    const btn = document.querySelector('#step-5 .btn');
    btn.disabled = true;
    btn.innerText = "Importing...";
    
    const result = await callApi('/api/import', {}, 'step-5-terminal');
    
    btn.disabled = false;
    btn.innerText = "Finalize & Compare";
    if (result.status === "success") nextStep(6);
}

async function runStep6() {
    await callApi('/api/compare', {}, 'step-6-terminal');
}

// Initial state
document.addEventListener('DOMContentLoaded', () => {
    showStep(1);
});
