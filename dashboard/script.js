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

// Action Functions for Steps
async function runStep1() {
    const btn = document.querySelector('#step-1 .btn');
    btn.disabled = true;
    btn.innerText = "Testing...";
    
    // Test Source
    await callApi('/api/connect', { type: 'source' });
    // Test Target
    await callApi('/api/connect', { type: 'target' });
    
    btn.disabled = false;
    btn.innerText = "Test Connection & Proceed";
    nextStep(2);
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

async function runStep3() {
    const btn = document.querySelector('#step-3 .btn');
    btn.disabled = true;
    btn.innerText = "Exporting...";
    
    const bar = document.getElementById('export-progress');
    bar.style.width = '30%';
    
    const result = await callApi('/api/export', {}, 'step-3-terminal');
    
    bar.style.width = '100%';
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
