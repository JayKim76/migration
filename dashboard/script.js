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
    
    // Collect data from UI
    const prefix = type === 'src' ? 'src' : (type === 'source' ? 'src' : 'tgt');
    const data = {
        type: type,
        server_host: document.getElementById(`${prefix}-ssh-host`).value,
        ssh_user: document.getElementById(`${prefix}-ssh-user`).value,
        ssh_password: document.getElementById(`${prefix}-ssh-pass`).value,
        service_name: document.getElementById(`${prefix}-db-sid`).value,
        port: document.getElementById(`${prefix}-db-port`).value,
        username: document.getElementById(`${prefix}-db-user`).value,
        password: document.getElementById(`${prefix}-db-pass`).value
    };

    btn.disabled = true;
    const originalText = btn.innerText;
    btn.innerText = "Testing...";
    
    const result = await callApi('/api/connect', data, 'step-1-terminal');
    
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
    const ddlPath = document.getElementById('ddl-save-path').value;
    
    btn.disabled = true;
    btn.innerText = "Extracting...";
    
    const result = await callApi('/api/extract-ddl', { ddl_dir: ddlPath }, 'step-2-terminal');
    
    btn.disabled = false;
    btn.innerText = "Run Extraction";
    if (result.status === "success") nextStep(3);
}

function toggleExportOptions() {
    const method = document.querySelector('input[name="exportMethod"]:checked').value;
    const expdpOptions = document.querySelectorAll('.expdp-option');
    const expOptions = document.querySelectorAll('.exp-option');
    
    if (method === 'expdp') {
        expdpOptions.forEach(el => el.style.display = 'block');
        expOptions.forEach(el => el.style.display = 'none');
    } else {
        expdpOptions.forEach(el => el.style.display = 'none');
        expOptions.forEach(el => el.style.display = 'block');
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

function getExportPayload() {
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
        
        payload.estimate_only = document.getElementById('exp-estimate-only').checked;
        
        // Advanced Options
        const estimate = document.getElementById('exp-estimate').value;
        if (estimate) payload.estimate = estimate;
        
        const filesize = document.getElementById('exp-filesize').value;
        if (filesize) payload.filesize = filesize;
        
        const flashbackScn = document.getElementById('exp-flashback-scn').value;
        if (flashbackScn) payload.flashback_scn = flashbackScn;
        
        const flashbackTime = document.getElementById('exp-flashback-time').value;
        if (flashbackTime) payload.flashback_time = flashbackTime;
        
        const include = document.getElementById('exp-include').value;
        if (include) payload.include = include;
        
        const networkLink = document.getElementById('exp-network-link').value;
        if (networkLink) payload.network_link = networkLink;
        
        const query = document.getElementById('exp-query').value;
        if (query) payload.query = query;
        
        const remapData = document.getElementById('exp-remap-data').value;
        if (remapData) payload.remap_data = remapData;
        
        const sample = document.getElementById('exp-sample').value;
        if (sample) payload.sample = sample;
        
        const version = document.getElementById('exp-version').value;
        if (version) payload.version = version;
        
        const jobName = document.getElementById('exp-job-name').value;
        if (jobName) payload.job_name = jobName;
        
        payload.reuse_dumpfiles = document.getElementById('exp-reuse-dumpfiles').checked;
        payload.cluster = document.getElementById('exp-cluster').checked;
        
        const encryption = document.getElementById('exp-encryption').value;
        if (encryption) payload.encryption = encryption;
        
        const encryptionAlgo = document.getElementById('exp-encryption-algorithm').value;
        if (encryptionAlgo) payload.encryption_algorithm = encryptionAlgo;
        
        const encryptionMode = document.getElementById('exp-encryption-mode').value;
        if (encryptionMode) payload.encryption_mode = encryptionMode;
        
        const encryptionPass = document.getElementById('exp-encryption-password').value;
        if (encryptionPass) payload.encryption_password = encryptionPass;
        
    } else {
        // Traditional exp options
        payload.consistent      = document.getElementById('exp-consistent').checked;
        payload.grants          = document.getElementById('exp-grants').checked;
        payload.indexes         = document.getElementById('exp-indexes').checked;
        payload.rows            = document.getElementById('exp-rows').checked;
        payload.constraints     = document.getElementById('exp-constraints').checked;
        payload.triggers        = document.getElementById('exp-triggers').checked;
        payload.direct          = document.getElementById('exp-direct').checked;
        payload.record          = document.getElementById('exp-record').checked;
        payload.object_consistent = document.getElementById('exp-object-consistent').checked;
        payload.resumable       = document.getElementById('exp-resumable').checked;
        payload.tts_full_check  = document.getElementById('exp-tts-full-check').checked;
        payload.transport_tablespace = document.getElementById('exp-transport-tablespace').checked;

        const statistics = document.getElementById('exp-statistics').value;
        if (statistics) payload.statistics = statistics;

        const inctype = document.getElementById('exp-inctype').value;
        if (inctype) payload.inctype = inctype;

        const buffer = document.getElementById('exp-buffer').value;
        if (buffer) payload.buffer = parseInt(buffer, 10);

        const recordlength = document.getElementById('exp-recordlength').value;
        if (recordlength) payload.recordlength = parseInt(recordlength, 10);

        const filesizeLeg = document.getElementById('exp-filesize-leg').value;
        if (filesizeLeg) payload.filesize = filesizeLeg;

        const volsize = document.getElementById('exp-volsize').value;
        if (volsize) payload.volsize = volsize;

        const feedback = document.getElementById('exp-feedback').value;
        if (feedback !== '' && feedback !== '0') payload.feedback = parseInt(feedback, 10);

        const resumableTimeout = document.getElementById('exp-resumable-timeout').value;
        if (resumableTimeout) payload.resumable_timeout = parseInt(resumableTimeout, 10);

        const resumableName = document.getElementById('exp-resumable-name').value;
        if (resumableName) payload.resumable_name = resumableName;

        const queryLeg = document.getElementById('exp-query-leg').value;
        if (queryLeg) payload.query = queryLeg;

        const flashbackScnLeg = document.getElementById('exp-flashback-scn-leg').value;
        if (flashbackScnLeg) payload.flashback_scn = flashbackScnLeg;

        const flashbackTimeLeg = document.getElementById('exp-flashback-time-leg').value;
        if (flashbackTimeLeg) payload.flashback_time = flashbackTimeLeg;

        const template = document.getElementById('exp-template').value;
        if (template) payload.template = template;
    }
    return payload;
}

async function previewExport() {
    const payload = getExportPayload();
    const result = await callApi('/api/preview-export', payload);
    
    if (result.command) {
        document.getElementById('export-preview-container').style.display = 'block';
        document.getElementById('export-command-preview').innerText = result.command;
        document.getElementById('btn-run-export').style.display = 'block';
    }
}

async function runStep3() {
    const btn = document.getElementById('btn-run-export');
    btn.disabled = true;
    btn.innerText = "Exporting...";
    
    const container = document.getElementById('export-progress-container');
    const bar = document.getElementById('export-progress');
    const text = document.getElementById('export-progress-text');
    container.style.display = 'block';
    bar.style.width = '30%';
    text.innerText = "Starting export process...";
    
    const payload = getExportPayload();
    const result = await callApi('/api/export', payload, 'step-3-terminal');
    
    bar.style.width = '100%';
    text.innerText = result.status === "success" ? "Export completed!" : "Export failed.";
    btn.disabled = false;
    btn.innerText = "Continue to Target Setup";
    
    if (result.status === "success") {
        setTimeout(() => nextStep(4), 2000);
    }
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

function toggleImportOptions() {
    const method = document.querySelector('input[name="importMethod"]:checked').value;
    const impdpOptions = document.querySelectorAll('.impdp-option');
    const impOptions   = document.querySelectorAll('.imp-only-option');

    if (method === 'impdp') {
        impdpOptions.forEach(el => el.style.display = 'block');
        impOptions.forEach(el   => el.style.display = 'none');
    } else {
        impdpOptions.forEach(el => el.style.display = 'none');
        impOptions.forEach(el   => el.style.display = 'block');
    }
}

function toggleImportMode() {
    const mode = document.getElementById('imp-mode').value;
    const targetGroup = document.getElementById('imp-target-group');
    const targetLabel = document.getElementById('imp-targets-label');

    if (mode === 'full') {
        targetGroup.style.display = 'none';
    } else {
        targetGroup.style.display = 'flex';
        if (mode === 'schema')      targetLabel.innerText = 'Target Schemas';
        else if (mode === 'table')  targetLabel.innerText = 'Target Tables';
        else if (mode === 'tablespace') targetLabel.innerText = 'Target Tablespaces';
    }
}

function getImportPayload() {
    const method = document.querySelector('input[name="importMethod"]:checked').value;
    const mode   = document.getElementById('imp-mode').value;

    const payload = { method, mode };

    if (mode !== 'full') {
        payload.targets = document.getElementById('imp-targets').value;
    }

    if (method === 'impdp') {
        payload.directory         = document.getElementById('imp-directory').value;
        payload.dumpfile          = document.getElementById('imp-dumpfile').value;
        payload.logfile           = document.getElementById('imp-logfile').value;
        payload.parallel          = parseInt(document.getElementById('imp-parallel').value, 10);
        payload.table_exists_action = document.getElementById('imp-table-exists').value;

        const content = document.getElementById('imp-content').value;
        if (content) payload.content = content;

        const exclude = document.getElementById('imp-exclude').value;
        if (exclude) payload.exclude = exclude;

        const include = document.getElementById('imp-include').value;
        if (include) payload.include = include;

        const query = document.getElementById('imp-query').value;
        if (query) payload.query = query;

        const sqlfile = document.getElementById('imp-sqlfile').value;
        if (sqlfile) payload.sqlfile = sqlfile;

        const remapSchema = document.getElementById('imp-remap-schema').value;
        if (remapSchema) payload.remap_schema = remapSchema;

        const remapTs = document.getElementById('imp-remap-tablespace').value;
        if (remapTs) payload.remap_tablespace = remapTs;

        const remapDf = document.getElementById('imp-remap-datafile').value;
        if (remapDf) payload.remap_datafile = remapDf;

        const remapTable = document.getElementById('imp-remap-table').value;
        if (remapTable) payload.remap_table = remapTable;

        const remapData = document.getElementById('imp-remap-data').value;
        if (remapData) payload.remap_data = remapData;

        const netLink = document.getElementById('imp-network-link').value;
        if (netLink) payload.network_link = netLink;

        const fScn = document.getElementById('imp-flashback-scn').value;
        if (fScn) payload.flashback_scn = fScn;

        const fTime = document.getElementById('imp-flashback-time').value;
        if (fTime) payload.flashback_time = fTime;

        const version = document.getElementById('imp-version').value;
        if (version) payload.version = version;

        const jobName = document.getElementById('imp-job-name').value;
        if (jobName) payload.job_name = jobName;

        const transform = document.getElementById('imp-transform').value;
        if (transform) payload.transform = transform;

        const tranTs = document.getElementById('imp-transport-tablespaces').value;
        if (tranTs) payload.transport_tablespaces = tranTs;

        const tranDf = document.getElementById('imp-transport-datafiles').value;
        if (tranDf) payload.transport_datafiles = tranDf;

        const encPass = document.getElementById('imp-encryption-password').value;
        if (encPass) payload.encryption_password = encPass;

        const status = parseInt(document.getElementById('imp-status').value, 10);
        if (status > 0) payload.status = status;

        payload.cluster                = document.getElementById('imp-cluster').checked;
        payload.reuse_datafiles        = document.getElementById('imp-reuse-datafiles').checked;
        payload.skip_unusable_indexes  = document.getElementById('imp-skip-unusable-indexes').checked;
        payload.streams_configuration  = document.getElementById('imp-streams-configuration').checked;
        payload.transport_full_check   = document.getElementById('imp-transport-full-check').checked;
    }
    // Note: traditional imp options are passed inline to main.py via the same payload
    // (the backend will use them from imp_cfg when method=imp)
    return payload;
}

async function previewImport() {
    const payload = getImportPayload();
    const result  = await callApi('/api/preview-import', payload);

    if (result.command) {
        document.getElementById('import-preview-container').style.display = 'block';
        document.getElementById('import-command-preview').innerText = result.command;
        document.getElementById('btn-run-import').style.display = 'block';
    }
}

async function runStep5() {
    const btn = document.getElementById('btn-run-import');
    btn.disabled = true;
    btn.innerText = "Importing...";

    const payload = getImportPayload();
    const result  = await callApi('/api/import', payload, 'step-5-terminal');

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
