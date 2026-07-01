/** PGxRx — Clinical Pharmacogenomics Decision Support UI */

/* ── Config ──────────────────────────────────────────── */
const API = window.location.origin; // same-origin calls

/* ── State ───────────────────────────────────────────── */
let genesData   = [];   // [{ gene, alleles: [...] }]
let drugsData   = [];   // [{ drug, genes: [...] }]
let selectedDrugs = []; // [{ drug, genes }]

/* ── DOM refs ────────────────────────────────────────── */
const $ = (s) => document.querySelector(s);

const geneSelect    = $('#geneSelect');
const allele1Select = $('#allele1Select');
const allele2Select = $('#allele2Select');
const drugInput     = $('#drugInput');
const drugDropdown  = $('#drugDropdown');
const drugTags      = $('#drugTags');
const drugContainer = $('#drugContainer');
const annotateBtn   = $('#annotateBtn');
const resetBtn      = $('#resetBtn');
const statusDot     = $('#statusDot');
const statusText    = $('#statusText');
const resultsPanel  = $('#resultsPanel');
const errorPanel    = $('#errorPanel');
const errorMessage  = $('#errorMessage');
const loader        = $('#loader');

/* ── Init ────────────────────────────────────────────── */
(async function init() {
    try {
        // Load genes & drugs in parallel
        const [genesRes, drugsRes] = await Promise.all([
            fetch(`${API}/genes`),
            fetch(`${API}/drugs`)
        ]);

        if (!genesRes.ok || !drugsRes.ok) throw new Error('API unreachable');

        genesData = await genesRes.json();
        drugsData = await drugsRes.json();

        populateGenes();
        renderDrugTags();

        statusDot.classList.add('connected');
        statusText.textContent = 'Connected';

        setupEvents();
    } catch (err) {
        statusDot.classList.add('error');
        statusText.textContent = 'Offline';
        showError('Could not connect to PGxRx server. Make sure the API is running.');
    }
})();

/* ── Gene Dropdown ───────────────────────────────────── */
function populateGenes() {
    genesData.sort((a, b) => a.gene.localeCompare(b.gene));
    geneSelect.innerHTML = '<option value="">— Select gene —</option>';
    for (const { gene, alleles } of genesData) {
        const opt = document.createElement('option');
        opt.value = gene;
        opt.textContent = `${gene} (${alleles.length} alleles)`;
        geneSelect.appendChild(opt);
    }
}

/* ── Allele Dropdowns ────────────────────────────────── */
function populateAlleles() {
    const gene = geneSelect.value;
    const info = genesData.find(g => g.gene === gene);

    [allele1Select, allele2Select].forEach(sel => {
        sel.innerHTML = '<option value="">— Select allele —</option>';
        sel.disabled = !gene;
    });

    if (!info) return;

    const sorted = [...info.alleles].sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
    for (const al of sorted) {
        const opt1 = new Option(al, al);
        const opt2 = new Option(al, al);
        allele1Select.appendChild(opt1);
        allele2Select.appendChild(opt2);
    }

    annotateBtn.disabled = true;
    hideResults();
}

/* ── Drug Autocomplete & Tagging ─────────────────────── */
function setupDrugAutocomplete() {
    drugInput.addEventListener('input', () => {
        const q = drugInput.value.trim().toLowerCase();
        if (q.length < 1) { drugDropdown.hidden = true; return; }

        const matches = drugsData
            .filter(d => d.drug.toLowerCase().includes(q) && !selectedDrugs.some(s => s.drug === d.drug))
            .slice(0, 8);

        if (!matches.length) { drugDropdown.hidden = true; return; }

        drugDropdown.hidden = false;
        drugDropdown.innerHTML = matches.map(d =>
            `<div class="ac-item" data-drug="${d.drug}">
                <span>${d.drug}</span>
                <span class="ac-genes">${d.genes.join(', ')}</span>
             </div>`
        ).join('');

        drugDropdown.querySelectorAll('.ac-item').forEach(el => {
            el.addEventListener('click', () => {
                const drug = el.dataset.drug;
                const info = drugsData.find(d => d.drug === drug);
                if (info) {
                    selectedDrugs.push({ drug: info.drug, genes: info.genes });
                    renderDrugTags();
                    drugInput.value = '';
                    drugDropdown.hidden = true;
                }
            });
        });
    });

    drugInput.addEventListener('focus', () => {
        if (drugInput.value.trim().length > 0) drugInput.dispatchEvent(new Event('input'));
    });

    // Close dropdown on outside click
    document.addEventListener('click', e => {
        if (!drugContainer.contains(e.target)) drugDropdown.hidden = true;
    });
}

function renderDrugTags() {
    drugTags.innerHTML = selectedDrugs.map((d, i) =>
        `<span class="tag">${d.drug} <button data-i="${i}">&times;</button></span>`
    ).join('');

    drugTags.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
            selectedDrugs.splice(+btn.dataset.i, 1);
            renderDrugTags();
        });
    });
}

/* ── Analyze ─────────────────────────────────────────── */
async function analyze() {
    const gene    = geneSelect.value;
    const allele1 = allele1Select.value;
    const allele2 = allele2Select.value;

    if (!gene || !allele1 || !allele2) {
        showError('Please select a gene and both alleles.');
        return;
    }

    showLoader(true);
    hideResults();
    hideError();

    try {
        const payload = {
            gene,
            allele1,
            allele2,
            drugs: selectedDrugs.map(d => d.drug),
            sample_id: 'UI-INTERACTIVE'
        };

        const res  = await fetch(`${API}/annotate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();
        renderResults(data);
    } catch (err) {
        showError(err.message);
    } finally {
        showLoader(false);
    }
}

/* ── Render Results ──────────────────────────────────── */
function renderResults(data) {
    const panel = resultsPanel;
    panel.hidden = false;

    // Phenotype
    $('#phenotypeValue').textContent = data.phenotype || 'Unknown';
    const phCol = phenotypeColor(data.phenotype);
    $('#phenotypeValue').style.color = phCol;

    // Meta
    $('#diplotypeMeta').textContent = `Diplotype: ${data.diplotype || '—'}`;
    $('#confidenceMeta').textContent = `Confidence: ${data.confidence || '—'}`;

    // Activity score
    const score = data.activity_score ?? null;
    $('#activityScoreValue').textContent = score !== null ? score.toFixed(2) : '—';
    const pct = score !== null ? Math.min(100, (score / 2.0) * 100) : 0;
    $('#scoreBar').style.width = pct + '%';

    // Dosing
    const dosingSection = $('#dosingSection');
    const noDosingMsg   = $('#noDosingMsg');
    const dosingCards   = $('#dosingCards');

    if (data.dosing && data.dosing.length) {
        dosingSection.style.display = '';
        noDosingMsg.hidden = true;
        dosingCards.innerHTML = data.dosing.map(d => `
            <div class="dose-card">
                <div class="dose-drug">${d.drug}</div>
                <div class="dose-reco">${d.recommendation || 'No recommendation available'}</div>
                <div class="dose-evidence">Evidence: ${d.evidence_level || '—'}</div>
            </div>
        `).join('');
    } else if (selectedDrugs.length > 0) {
        // Drugs were requested but no guidelines matched
        dosingSection.style.display = 'none';
        noDosingMsg.hidden = false;
    } else {
        dosingSection.style.display = 'none';
        noDosingMsg.hidden = false;
    }

    // Scroll into view
    panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function phenotypeColor(p) {
    if (!p) return '#fff';
    const s = p.toLowerCase();
    if (s.includes('poor')) return '#f87171';
    if (s.includes('intermediate')) return '#fbbf24';
    if (s.includes('normal') || s.includes('extensive')) return '#34d399';
    if (s.includes('ultra')) return '#38bdf8';
    return '#fff';
}

/* ── UI helpers ──────────────────────────────────────── */
function showLoader(show) {
    loader.hidden = !show;
}

function hideResults() {
    resultsPanel.hidden = true;
}

function showError(msg) {
    errorMessage.textContent = msg;
    errorPanel.hidden = false;
    errorPanel.scrollIntoView({ behavior: 'smooth' });
}

function hideError() {
    errorPanel.hidden = true;
    errorMessage.textContent = '';
}

/* ── Events ──────────────────────────────────────────── */
function setupEvents() {
    geneSelect.addEventListener('change', populateAlleles);

    // Re-check analyze button when alleles change
    [allele1Select, allele2Select].forEach(sel => {
        sel.addEventListener('change', () => {
            annotateBtn.disabled = !(allele1Select.value && allele2Select.value);
            hideResults();
            hideError();
        });
    });

    annotateBtn.addEventListener('click', analyze);

    resetBtn.addEventListener('click', () => {
        geneSelect.value = '';
        [allele1Select, allele2Select].forEach(s => {
            s.innerHTML = '<option value="">— Select gene first —</option>';
            s.disabled = true;
        });
        selectedDrugs = [];
        renderDrugTags();
        drugInput.value = '';
        annotateBtn.disabled = true;
        hideResults();
        hideError();
    });

    setupDrugAutocomplete();
}
