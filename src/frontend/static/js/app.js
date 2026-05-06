/**
 * SpecSentinel Frontend Application
 * Handles API specification analysis via backend API
 */

// Configuration
// Use relative URLs to go through Flask proxy
const API_BASE_URL = '/api';

// State
let currentReport = null;
let currentFile = null;
let currentSeverityFilter = 'all';
let analyzedFileName = '';
let originalUploadTitle = 'Analyze Your API Specification';

// DOM Elements
const elements = {
    // Tabs
    tabBtns: document.querySelectorAll('.tab-btn'),
    tabContents: document.querySelectorAll('.tab-content'),

    // Upload
    uploadArea: document.getElementById('uploadArea'),
    fileInput: document.getElementById('fileInput'),
    selectedFile: document.getElementById('selectedFile'),
    fileName: document.getElementById('fileName'),
    removeFile: document.getElementById('removeFile'),

    // Paste
    specInput: document.getElementById('specInput'),
    specName: document.getElementById('specName'),

    // Actions
    analyzeBtn: document.getElementById('analyzeBtn'),
    clearBtn: document.getElementById('clearBtn'),

    // Loading
    loadingOverlay: document.getElementById('loadingOverlay'),

    // Results
    resultsSection: document.getElementById('resultsSection'),
    scoreNumber: document.getElementById('scoreNumber'),
    scoreRing: document.getElementById('scoreRing'),
    scoreBand: document.getElementById('scoreBand'),
    bandEmoji: document.getElementById('bandEmoji'),
    bandText: document.getElementById('bandText'),
    criticalCount: document.getElementById('criticalCount'),
    highCount: document.getElementById('highCount'),
    mediumCount: document.getElementById('mediumCount'),
    lowCount: document.getElementById('lowCount'),
    categoryBreakdown: document.getElementById('categoryBreakdown'),
    issuesFixesList: document.getElementById('issuesFixesList'),

    // Modal
    severityModal: document.getElementById('severityModal'),
    modalTitle: document.getElementById('modalTitle'),
    modalClose: document.getElementById('modalClose'),
    modalCloseBtn: document.getElementById('modalCloseBtn'),
    modalIssuesList: document.getElementById('modalIssuesList'),
    modalIssuesCount: document.getElementById('modalIssuesCount'),
    modalExportBtn: document.getElementById('modalExportBtn'),

    // Export
    exportJsonBtn: document.getElementById('exportJsonBtn'),
    exportTextBtn: document.getElementById('exportTextBtn'),
    analyzeNewBtn: document.getElementById('analyzeNewBtn'),

    // Action Panel
    actionPanel: document.getElementById('actionPanel'),

    // Error
    errorSection: document.getElementById('errorSection'),
    errorMessage: document.getElementById('errorMessage'),
    retryBtn: document.getElementById('retryBtn'),
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    checkBackendHealth();
    setupCollapsibleUploadSection();
});

/**
 * Initialize all event listeners
 */
function initializeEventListeners() {
    // Tab switching
    elements.tabBtns.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    // File upload
    elements.uploadArea.addEventListener('click', (e) => {
        // Don't trigger if clicking on the label (it already triggers the input)
        if (e.target.tagName !== 'LABEL' && !e.target.closest('label')) {
            elements.fileInput.click();
        }
    });
    elements.fileInput.addEventListener('change', handleFileSelect);
    elements.removeFile.addEventListener('click', (e) => {
        e.stopPropagation();
        clearFile();
    });

    // Drag and drop
    elements.uploadArea.addEventListener('dragover', handleDragOver);
    elements.uploadArea.addEventListener('dragleave', handleDragLeave);
    elements.uploadArea.addEventListener('drop', handleDrop);

    // Actions
    elements.analyzeBtn.addEventListener('click', analyzeSpec);
    elements.clearBtn.addEventListener('click', clearAll);

    // Modal
    elements.modalClose.addEventListener('click', closeModal);
    elements.modalCloseBtn.addEventListener('click', closeModal);
    elements.severityModal.addEventListener('click', (e) => {
        if (e.target === elements.severityModal) {
            closeModal();
        }
    });
    elements.modalExportBtn.addEventListener('click', exportModalData);

    // Export
    elements.exportJsonBtn.addEventListener('click', exportJson);
    elements.exportTextBtn.addEventListener('click', exportText);
    elements.analyzeNewBtn.addEventListener('click', resetToUpload);

    // Error
    elements.retryBtn.addEventListener('click', resetToUpload);
}

/**
 * Switch between tabs
/**
 * Setup collapsible upload section
 */
function setupCollapsibleUploadSection() {
    const uploadSection = document.querySelector('.upload-section');
    if (uploadSection) {
        // Get the h2 title element
        const titleElement = uploadSection.querySelector('h2');

        if (titleElement) {
            // Make title clickable to toggle collapse
            titleElement.style.cursor = 'pointer';
            titleElement.addEventListener('click', function (e) {
                e.stopPropagation();
                const wasCollapsed = uploadSection.classList.contains('collapsed');
                uploadSection.classList.toggle('collapsed');

                // Update title text based on state
                if (uploadSection.classList.contains('collapsed')) {
                    // Just collapsed - show filename
                    if (analyzedFileName) {
                        titleElement.textContent = `API specification analyzed for ${analyzedFileName}`;
                    }
                } else {
                    // Just expanded - restore original title
                    titleElement.textContent = originalUploadTitle;
                }
            });
        }

        // Also allow clicking on collapsed section to expand
        uploadSection.addEventListener('click', function (e) {
            if (this.classList.contains('collapsed')) {
                const isInteractive = e.target.closest('button, input, textarea, label, .tab-btn');
                if (!isInteractive) {
                    this.classList.remove('collapsed');
                    // Restore original title when expanding
                    if (titleElement) {
                        titleElement.textContent = originalUploadTitle;
                    }
                }
            }
        });
    }
}

/**
 * Switch between tabs
 */
function switchTab(tabName) {
    elements.tabBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    elements.tabContents.forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });

    clearAll();
}

/**
 * Handle file selection
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        displaySelectedFile(file);
    }
}

/**
 * Handle drag over
 */
function handleDragOver(event) {
    event.preventDefault();
    elements.uploadArea.classList.add('drag-over');
}

/**
 * Handle drag leave
 */
function handleDragLeave(event) {
    event.preventDefault();
    elements.uploadArea.classList.remove('drag-over');
}

/**
 * Handle file drop
 */
function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    elements.uploadArea.classList.remove('drag-over');

    const file = event.dataTransfer.files[0];
    if (file) {
        // Update the file input as well
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        elements.fileInput.files = dataTransfer.files;
        displaySelectedFile(file);
    }
}

/**
 * Display selected file
 */
function displaySelectedFile(file) {
    currentFile = file;
    elements.fileName.textContent = file.name;
    elements.selectedFile.style.display = 'flex';
    elements.uploadArea.style.display = 'none';
}

/**
 * Clear selected file
 */
function clearFile() {
    currentFile = null;
    elements.fileInput.value = '';
    elements.selectedFile.style.display = 'none';
    elements.uploadArea.style.display = 'block';
}

/**
 * Clear all inputs
 */
function clearAll() {
    clearFile();
    elements.specInput.value = '';
    elements.specName.value = '';
}

/**
 * Analyze specification
 */
async function analyzeSpec() {
    const activeTab = document.querySelector('.tab-btn.active').dataset.tab;

    if (activeTab === 'upload') {
        if (!currentFile) {
            showError('Please select a file to analyze');
            return;
        }
        await analyzeFile(currentFile);
    } else {
        const specText = elements.specInput.value.trim();
        if (!specText) {
            showError('Please paste your API specification');
            return;
        }
        await analyzeText(specText, elements.specName.value || 'pasted_spec');
    }
}

/**
 * Show modal with findings and recommendations for a specific category
 */
function showCategoryModal(category, categoryName) {
    if (!currentReport) return;

    const categoryIcons = {
        'security': '🔒',
        'Security': '🔒',
        'design': '🎨',
        'Design': '🎨',
        'error_handling': '⚠️',
        'ErrorHandling': '⚠️',
        'documentation': '📝',
        'Documentation': '📝',
        'governance': '⚖️',
        'Governance': '⚖️',
    };

    const icon = categoryIcons[category] || '📋';

    // Set modal title
    elements.modalTitle.textContent = `${icon} ${categoryName} Issues`;

    // Filter findings by category (case-insensitive)
    const findings = (currentReport.findings || []).filter(f => {
        const fCategory = (f.category || '').toLowerCase().replace(/\s+/g, '');
        const searchCategory = category.toLowerCase().replace(/\s+/g, '');
        return fCategory === searchCategory;
    });

    // Get rule_ids from findings in this category
    const categoryRuleIds = new Set(findings.map(f => f.rule_id).filter(Boolean));

    // Filter recommendations by matching rule_ids from category findings
    const recommendations = (currentReport.recommendations || []).filter(rec => {
        if (typeof rec === 'object' && rec.rule_id) {
            return categoryRuleIds.has(rec.rule_id);
        }
        return false;
    });

    // Display merged issues and fixes in modal
    displayModalIssuesAndFixes(findings, recommendations, categoryName);

    // Show modal
    elements.severityModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

/**
 * Analyze file via API
 */
async function analyzeFile(file) {
    showLoading();
    showPipelineProgress();

    try {
        const formData = new FormData();
        formData.append('file', file);

        console.log('Sending file to backend with SSE:', file.name);

        // Use fetch to send the file and get streaming response
        const response = await fetch(`${API_BASE_URL}/analyze/stream`, {
            method: 'POST',
            body: formData,
        });

        console.log('Response status:', response.status);

        if (!response.ok) {
            let errorMessage = 'Analysis failed';
            try {
                const error = await response.json();
                errorMessage = error.detail || errorMessage;
            } catch (e) {
                errorMessage = await response.text() || errorMessage;
            }
            throw new Error(errorMessage);
        }

        // Process the streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let finalReport = null;

        while (true) {
            const { done, value } = await reader.read();

            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            // Process complete SSE messages
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line in buffer

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.substring(6));
                        console.log('SSE event:', data);

                        if (data.stage === 'COMPLETE') {
                            finalReport = data.result;
                        } else if (data.stage === 'ERROR') {
                            throw new Error(data.message || 'Analysis failed');
                        } else {
                            updatePipelineStage(data);
                        }
                    } catch (e) {
                        console.error('Error parsing SSE data:', e);
                    }
                }
            }
        }

        if (finalReport) {
            console.log('Received final report:', finalReport);
            displayResults(finalReport);
        } else {
            throw new Error('No report received from analysis');
        }
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Failed to analyze specification. Please check if the backend server is running.');
    } finally {
        hideLoading();
    }
}

/**
 * Analyze text via API
 */
async function analyzeText(specText, specName) {
    showLoading();

    try {
        // Try to parse as JSON or YAML
        let spec;
        try {
            spec = JSON.parse(specText);
        } catch {
            // If not JSON, send as string (backend will parse YAML)
            spec = specText;
        }

        console.log('Sending spec to backend:', specName);

        const response = await fetch(`${API_BASE_URL}/analyze/text?format=json`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                spec: spec,
                name: specName,
            }),
        });

        console.log('Response status:', response.status);

        if (!response.ok) {
            let errorMessage = 'Analysis failed';
            try {
                const error = await response.json();
                errorMessage = error.detail || errorMessage;
            } catch (e) {
                errorMessage = await response.text() || errorMessage;
            }
            throw new Error(errorMessage);
        }

        const report = await response.json();
        console.log('Received report:', report);
        displayResults(report);
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Failed to analyze specification. Please check if the backend server is running.');
    } finally {
        hideLoading();
    }
}

/**
 * Display analysis results
 */
function displayResults(report) {
    currentReport = report;

    // Validate report structure
    if (!report || !report.health_score) {
        showError('Invalid report format received from server');
        console.error('Invalid report:', report);
        return;
    }

    // Hide error section
    elements.errorSection.style.display = 'none';

    // Get filename from report metadata or current file
    if (report.meta && report.meta.spec_name) {
        analyzedFileName = report.meta.spec_name;
    } else if (currentFile) {
        analyzedFileName = currentFile.name;
    } else if (elements.specName.value) {
        analyzedFileName = elements.specName.value;
    } else {
        analyzedFileName = 'pasted specification';
    }

    // Collapse upload section and update title
    const uploadSection = document.querySelector('.upload-section');
    const titleElement = uploadSection ? uploadSection.querySelector('h2') : null;

    if (uploadSection) {
        uploadSection.classList.add('collapsed');

        // Update title to show analyzed filename
        if (titleElement) {
            titleElement.textContent = `API specification analyzed for ${analyzedFileName}`;
        }
    }

    // Show results section and action panel
    elements.resultsSection.style.display = 'block';
    if (elements.actionPanel) {
        elements.actionPanel.style.display = 'block';
    }

    // Scroll to results
    elements.resultsSection.scrollIntoView({ behavior: 'smooth' });

    // Display health score
    displayHealthScore(report.health_score);

    // Display category breakdown
    // Backend returns category_breakdown at top level, not in health_score
    if (report.category_breakdown) {
        displayCategoryBreakdown(report.category_breakdown);
    } else if (report.health_score.category_scores) {
        // Fallback for alternative format
        displayCategoryBreakdown(report.health_score.category_scores);
    }

    // Add click handlers to severity stat items
    addSeverityClickHandlers();
}

/**
 * Display health score
 */
function displayHealthScore(healthScore) {
    if (!healthScore) {
        console.error('Health score is undefined');
        return;
    }

    const score = Math.round(healthScore.total || 0);
    const band = healthScore.band || 'Unknown';
    const counts = healthScore.finding_counts || {};

    // Animate score number
    animateNumber(elements.scoreNumber, 0, score, 1000);

    // Animate score ring
    const circumference = 534; // 2 * PI * 85
    const offset = circumference - (score / 100) * circumference;
    elements.scoreRing.style.strokeDashoffset = offset;

    // Set ring color based on band
    const colors = {
        'Excellent': '#24a148',
        'Good': '#0f62fe',
        'Moderate': '#f1c21b',
        'Poor': '#da1e28',
    };
    elements.scoreRing.style.stroke = colors[band] || '#0f62fe';

    // Set band
    const emojis = {
        'Excellent': '✅',
        'Good': '🟢',
        'Moderate': '🟡',
        'Poor': '🔴',
    };
    elements.bandEmoji.textContent = emojis[band] || '⏳';
    elements.bandText.textContent = band;
    elements.bandText.style.color = colors[band] || '#0f62fe';

    // Set counts with safe defaults
    elements.criticalCount.textContent = counts.critical || 0;
    elements.highCount.textContent = counts.high || 0;
    elements.mediumCount.textContent = counts.medium || 0;
    elements.lowCount.textContent = counts.low || 0;
}

/**
 * Display category breakdown
 */
function displayCategoryBreakdown(categoryData) {
    console.log('Displaying category breakdown:', categoryData);
    elements.categoryBreakdown.innerHTML = '';

    if (!categoryData) {
        console.error('No category data provided');
        elements.categoryBreakdown.innerHTML = '<p>Category breakdown not available</p>';
        return;
    }

    const categoryNames = {
        'security': 'Security',
        'design': 'Design',
        'error_handling': 'Error Handling',
        'documentation': 'Documentation',
        'governance': 'Governance',
    };

    // Handle array format (from backend's category_breakdown)
    if (Array.isArray(categoryData)) {
        console.log(`Rendering ${categoryData.length} categories from array`);
        categoryData.forEach(cat => {
            const name = categoryNames[cat.category] || cat.category;
            const score = cat.score || 0;
            const weight = cat.weight_pct || 0;

            const item = document.createElement('div');
            item.className = 'category-item clickable';
            item.dataset.category = cat.category;
            item.innerHTML = `
                <div class="category-header">
                    <span class="category-name">${escapeHtml(name)} (${weight}%)</span>
                    <span class="category-score">${Math.round(score)}/100</span>
                </div>
                <div class="category-bar">
                    <div class="category-bar-fill" style="width: ${score}%"></div>
                </div>
            `;
            item.addEventListener('click', () => showCategoryModal(cat.category, name));
            elements.categoryBreakdown.appendChild(item);
        });
    }
    // Handle object format (fallback for category_scores)
    else if (typeof categoryData === 'object') {
        console.log('Rendering categories from object');
        Object.entries(categoryData).forEach(([key, score]) => {
            const name = categoryNames[key] || key;
            const safeScore = typeof score === 'number' ? score : 0;

            const item = document.createElement('div');
            item.className = 'category-item clickable';
            item.dataset.category = key;
            item.innerHTML = `
                <div class="category-header">
                    <span class="category-name">${escapeHtml(name)}</span>
                    <span class="category-score">${Math.round(safeScore)}/100</span>
                </div>
                <div class="category-bar">
                    <div class="category-bar-fill" style="width: ${safeScore}%"></div>
                </div>
            `;
            item.addEventListener('click', () => showCategoryModal(key, name));
            elements.categoryBreakdown.appendChild(item);
        });
    } else {
        console.error('Invalid category data format:', typeof categoryData);
        elements.categoryBreakdown.innerHTML = '<p>Category breakdown format not recognized</p>';
    }
}

/**
 * Group findings or recommendations by title
 */
function groupByTitle(items) {
    const grouped = {};
    items.forEach(item => {
        const title = item.title || 'Other';
        if (!grouped[title]) {
            grouped[title] = [];
        }
        grouped[title].push(item);
    });
    return grouped;
}

/**
 * Create a collapsible group element for findings
 */
function createFindingGroupElement(title, items) {
    const groupDiv = document.createElement('div');
    groupDiv.className = 'finding-group';

    // Get benchmark/source from first item for tag
    const benchmark = items[0].benchmark || items[0].source || '';
    const category = items[0].category || '';

    // Category display info
    const categoryInfo = {
        'security': { name: 'Security', icon: '🔒', color: '#da1e28' },
        'design': { name: 'Design', icon: '🎨', color: '#0f62fe' },
        'error_handling': { name: 'Error Handling', icon: '⚠️', color: '#f1c21b' },
        'documentation': { name: 'Documentation', icon: '📝', color: '#0043ce' },
        'governance': { name: 'Governance', icon: '⚖️', color: '#8a3ffc' },
    };

    const catInfo = categoryInfo[category.toLowerCase()] || { name: category, icon: '📋', color: '#525252' };

    // Create header
    const header = document.createElement('div');
    header.className = 'finding-group-header';
    header.innerHTML = `
        <div class="finding-group-title">
            <span class="group-toggle-icon">▶</span>
            <span class="group-title-text">${escapeHtml(title)}</span>
            <span class="group-count">(${items.length})</span>
            ${benchmark ? `<span class="group-tag">${escapeHtml(benchmark)}</span>` : ''}
        </div>
    `;

    // Create content container
    const content = document.createElement('div');
    content.className = 'finding-group-content';
    content.style.display = 'none';

    // Add each finding to the group
    items.forEach(item => {
        const findingDiv = document.createElement('div');
        findingDiv.className = 'grouped-finding-item';

        const severity = item.severity.toLowerCase();

        let html = `
            <div class="grouped-finding-header">
                <span class="severity-badge ${severity}">${item.severity}</span>
            </div>
            <div class="grouped-finding-section">
                <strong>📍 Issue:</strong>
                <p>${escapeHtml(item.description)}</p>
            </div>
        `;

        if (item.fix_guidance) {
            html += `
                <div class="grouped-finding-section">
                    <strong>💡 Fix:</strong>
                    <pre>${escapeHtml(item.fix_guidance)}</pre>
                </div>
            `;
        }

        if (item.evidence) {
            html += `
                <div class="grouped-finding-section">
                    <strong>🔍 Evidence:</strong>
                    <pre>${escapeHtml(item.evidence)}</pre>
                </div>
            `;
        }

        findingDiv.innerHTML = html;
        content.appendChild(findingDiv);
    });

    // Add toggle functionality
    header.addEventListener('click', () => {
        const isExpanded = content.style.display !== 'none';
        content.style.display = isExpanded ? 'none' : 'block';
        const toggleIcon = header.querySelector('.group-toggle-icon');
        toggleIcon.textContent = isExpanded ? '▶' : '▼';
        groupDiv.classList.toggle('expanded', !isExpanded);
    });

    groupDiv.appendChild(header);
    groupDiv.appendChild(content);

    return groupDiv;
}

/**
 * Create a collapsible group element for recommendations
 */
function createRecommendationGroupElement(title, items) {
    const groupDiv = document.createElement('div');
    groupDiv.className = 'recommendation-group';

    // Get benchmark/source from first item for tag
    const benchmark = items[0].benchmark || items[0].source || '';

    // Create header
    const header = document.createElement('div');
    header.className = 'recommendation-group-header';
    header.innerHTML = `
        <div class="recommendation-group-title">
            <span class="group-toggle-icon">▶</span>
            <span class="group-title-text">${escapeHtml(title)}</span>
            <span class="group-count">(${items.length})</span>
            ${benchmark ? `<span class="group-tag">${escapeHtml(benchmark)}</span>` : ''}
        </div>
    `;

    // Create content container
    const content = document.createElement('div');
    content.className = 'recommendation-group-content';
    content.style.display = 'none';

    // Add each recommendation to the group
    items.forEach((rec, index) => {
        const recDiv = document.createElement('div');
        recDiv.className = 'grouped-recommendation-item';

        let html = '';

        if (typeof rec === 'object') {
            const priority = rec.priority || 'High';

            html = `
                <div class="grouped-rec-header">
                    <span class="priority-badge priority-${priority.toLowerCase()}">${priority}</span>
                </div>
            `;

            if (rec.issue) {
                html += `
                    <div class="grouped-rec-section">
                        <strong>📍 Issue:</strong>
                        <p>${escapeHtml(rec.issue)}</p>
                    </div>
                `;
            }

            if (rec.fix) {
                html += `
                    <div class="grouped-rec-section">
                        <strong>💡 Fix:</strong>
                        <pre>${escapeHtml(rec.fix)}</pre>
                    </div>
                `;
            }

            if (rec.recommendation) {
                html += `
                    <div class="grouped-rec-section">
                        <strong>✅ Recommendation:</strong>
                        <p>${escapeHtml(rec.recommendation)}</p>
                    </div>
                `;
            }
        } else {
            html = `<p>${escapeHtml(rec)}</p>`;
        }

        recDiv.innerHTML = html;
        content.appendChild(recDiv);
    });

    // Add toggle functionality
    header.addEventListener('click', () => {
        const isExpanded = content.style.display !== 'none';
        content.style.display = isExpanded ? 'none' : 'block';
        const toggleIcon = header.querySelector('.group-toggle-icon');
        toggleIcon.textContent = isExpanded ? '▶' : '▼';
        groupDiv.classList.toggle('expanded', !isExpanded);
    });

    groupDiv.appendChild(header);
    groupDiv.appendChild(content);

    return groupDiv;
}

/**
 * Display merged issues and fixes (findings + recommendations)
 */
function displayIssuesAndFixes(findings, recommendations) {
    if (!elements.issuesFixesList) {
        console.warn('issuesFixesList element not found');
        return;
    }

    elements.issuesFixesList.innerHTML = '';

    if ((!findings || findings.length === 0) && (!recommendations || recommendations.length === 0)) {
        elements.issuesFixesList.innerHTML = '<p class="text-center">No issues detected. Great job! ✅</p>';
        return;
    }

    // Merge findings and recommendations by title
    const mergedData = mergeIssuesAndFixes(findings, recommendations);

    // Create collapsible groups
    Object.entries(mergedData).forEach(([title, data]) => {
        const groupElement = createIssueFixGroupElement(title, data);
        elements.issuesFixesList.appendChild(groupElement);
    });
}

/**
 * Merge findings and recommendations by title
 */
function mergeIssuesAndFixes(findings, recommendations) {
    const merged = {};

    // Add findings
    if (findings && findings.length > 0) {
        findings.forEach(finding => {
            const title = finding.title || 'Other';
            if (!merged[title]) {
                merged[title] = {
                    findings: [],
                    recommendations: [],
                    benchmark: finding.benchmark || finding.source || '',
                    category: finding.category || ''
                };
            }
            merged[title].findings.push(finding);
        });
    }

    // Add recommendations
    if (recommendations && recommendations.length > 0) {
        recommendations.forEach(rec => {
            const title = rec.title || 'Other';
            if (!merged[title]) {
                merged[title] = {
                    findings: [],
                    recommendations: [],
                    benchmark: rec.benchmark || rec.source || '',
                    category: rec.category || ''
                };
            }
            merged[title].recommendations.push(rec);
        });
    }

    return merged;
}

/**
 * Create a collapsible group element for merged issues and fixes
 */
function createIssueFixGroupElement(title, data) {
    const groupDiv = document.createElement('div');
    groupDiv.className = 'issue-fix-group';

    const totalCount = data.findings.length + data.recommendations.length;
    const benchmark = data.benchmark;

    // Create header
    const header = document.createElement('div');
    header.className = 'issue-fix-group-header';
    header.innerHTML = `
        <div class="issue-fix-group-title">
            <span class="group-toggle-icon">▶</span>
            <span class="group-title-text">${escapeHtml(title)}</span>
            <span class="group-count">(${totalCount})</span>
            ${benchmark ? `<span class="group-tag">${escapeHtml(benchmark)}</span>` : ''}
        </div>
    `;

    // Create content container
    const content = document.createElement('div');
    content.className = 'issue-fix-group-content';
    content.style.display = 'none';

    // Add findings and recommendations together
    const allItems = [...data.findings, ...data.recommendations];

    allItems.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'issue-fix-item';

        let html = '';

        // Header with severity/priority badge and category tag (right-aligned)
        html += '<div class="issue-fix-header">';

        // Category tag (always show, use default if not present)
        const categoryInfo = {
            'security': { name: 'Security', icon: '🔒', color: '#da1e28' },
            'design': { name: 'Design', icon: '🎨', color: '#0f62fe' },
            'error_handling': { name: 'Error Handling', icon: '⚠️', color: '#f1c21b' },
            'documentation': { name: 'Documentation', icon: '📝', color: '#0043ce' },
            'governance': { name: 'Governance', icon: '⚖️', color: '#8a3ffc' },
        };
        const category = item.category || 'General';
        const catInfo = categoryInfo[category.toLowerCase()] || { name: category, icon: '📋', color: '#525252' };
        html += `<span class="category-tag" style="background-color: ${catInfo.color}">${catInfo.icon} ${catInfo.name}</span>`;

        // Severity badge (for findings)
        if (item.severity) {
            const severity = item.severity.toLowerCase();
            html += `<span class="severity-badge ${severity}">${item.severity}</span>`;
        }

        // Priority badge (for recommendations)
        if (item.priority) {
            const priority = item.priority.toLowerCase();
            html += `<span class="priority-badge priority-${priority}">${item.priority}</span>`;
        }

        html += '</div>';

        // Issue Statement (title) - NEW
        if (item.title) {
            html += `
                <div class="issue-fix-section issue-statement">
                    <strong>📋 Issue Statement:</strong>
                    <p>${escapeHtml(item.title)}</p>
                </div>
            `;
        }

        // Issue Description
        if (item.description || item.issue) {
            html += `
                <div class="issue-fix-section">
                    <strong>📍 Issue:</strong>
                    <p>${escapeHtml(item.description || item.issue)}</p>
                </div>
            `;
        }

        // Evidence section
        if (item.evidence) {
            html += `
                <div class="issue-fix-section">
                    <strong>🔍 Evidence:</strong>
                    <pre class="evidence-code">${escapeHtml(item.evidence)}</pre>
                </div>
            `;
        }

        // AI-Generated Fix (priority - from WatsonX/LLM)
        if (item.ai_suggested_fix) {
            html += `
                <div class="issue-fix-section ai-fix-section">
                    <strong>🤖 AI-Recommended Fix:</strong>
                    <div class="ai-fix-content">${escapeHtml(item.ai_suggested_fix)}</div>
                </div>
            `;
        }

        // Fallback to standard fix guidance
        if (!item.ai_suggested_fix && (item.fix_guidance || item.fix)) {
            const fixContent = item.fix_guidance || item.fix;
            html += `
                <div class="issue-fix-section">
                    <strong>💡 Recommended Fix:</strong>
                    <pre class="fix-code">${escapeHtml(fixContent)}</pre>
                </div>
            `;
        }

        // Recommendation section (for recommendation items)
        if (item.recommendation) {
            html += `
                <div class="issue-fix-section">
                    <strong>✅ Recommendation:</strong>
                    <p>${escapeHtml(item.recommendation)}</p>
                </div>
            `;
        }

        itemDiv.innerHTML = html;
        content.appendChild(itemDiv);
    });

    // Add toggle functionality
    header.addEventListener('click', () => {
        const isExpanded = content.style.display !== 'none';
        content.style.display = isExpanded ? 'none' : 'block';
        const toggleIcon = header.querySelector('.group-toggle-icon');
        toggleIcon.textContent = isExpanded ? '▶' : '▼';
        groupDiv.classList.toggle('expanded', !isExpanded);
    });

    groupDiv.appendChild(header);
    groupDiv.appendChild(content);

    return groupDiv;
}

/**
 * Copy to clipboard function
 */
function copyToClipboard(button) {
    const content = button.getAttribute('data-content');
    navigator.clipboard.writeText(content).then(() => {
        const originalText = button.textContent;
        button.textContent = '✅ Copied!';
        button.classList.add('copied');
        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('copied');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        button.textContent = '❌ Failed';
        setTimeout(() => {
            button.textContent = '📋 Copy';
        }, 2000);
    });
}

// Keep old functions for backward compatibility but make them call the new merged function
function displayFindings(findings) {
    // This is now handled by displayIssuesAndFixes
    console.log('displayFindings called with', findings?.length, 'findings');
}

/**
 * Create finding element
 */
function createFindingElement(finding) {
    const severity = finding.severity.toLowerCase();
    const category = finding.category || '';

    // Category display names and icons
    const categoryInfo = {
        'security': { name: 'Security', icon: '🔒', color: '#da1e28' },
        'design': { name: 'Design', icon: '🎨', color: '#0f62fe' },
        'error_handling': { name: 'Error Handling', icon: '⚠️', color: '#f1c21b' },
        'documentation': { name: 'Documentation', icon: '📝', color: '#0043ce' },
        'governance': { name: 'Governance', icon: '⚖️', color: '#8a3ffc' },
    };

    const catInfo = categoryInfo[category] || { name: category, icon: '📋', color: '#525252' };

    const item = document.createElement('div');
    item.className = `finding-item ${severity}`;
    item.dataset.severity = severity;
    item.dataset.category = category;

    let html = `
        <div class="finding-header">
            <div class="finding-title">${escapeHtml(finding.title)}</div>
            <div class="finding-badges">
                <span class="category-badge" style="background-color: ${catInfo.color}20; color: ${catInfo.color}; border: 1px solid ${catInfo.color}40;">
                    ${catInfo.icon} ${catInfo.name}
                </span>
                <span class="severity-badge ${severity}">${finding.severity}</span>
            </div>
        </div>
        <div class="finding-description">${escapeHtml(finding.description)}</div>
    `;

    if (finding.evidence) {
        html += `<div class="finding-evidence">📍 ${escapeHtml(finding.evidence)}</div>`;
    }

    if (finding.fix_guidance) {
        html += `<div class="finding-fix"><strong>💡 Fix:</strong> ${escapeHtml(finding.fix_guidance)}</div>`;
    }

    if (finding.benchmark) {
        html += `<div class="finding-benchmark">📋 <em>${escapeHtml(finding.benchmark)}</em></div>`;
    }

    item.innerHTML = html;
    return item;
}

/**
 * Display recommendations
 */
function displayRecommendations(recommendations) {
    // This is now handled by displayIssuesAndFixes
    console.log('displayRecommendations called with', recommendations?.length, 'recommendations');
}

/**
 * Filter findings by severity
 */
function filterFindings(severity) {
    currentSeverityFilter = severity;

    // Update filter buttons
    elements.filterBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.severity === severity);
    });

    // Filter findings
    const findingItems = elements.findingsList.querySelectorAll('.finding-item');
    findingItems.forEach(item => {
        if (severity === 'all' || item.dataset.severity === severity) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

/**
 * Export report as JSON
 */
function exportJson() {
    if (!currentReport) return;

    const blob = new Blob([JSON.stringify(currentReport, null, 2)], { type: 'application/json' });
    downloadFile(blob, 'specsentinel-report.json');
}

/**
 * Export report as text
 */
async function exportText() {
    if (!currentReport) return;

    try {
        const activeTab = document.querySelector('.tab-btn.active').dataset.tab;
        let response;

        if (activeTab === 'upload' && currentFile) {
            const formData = new FormData();
            formData.append('file', currentFile);
            response = await fetch(`${API_BASE_URL}/analyze?format=text`, {
                method: 'POST',
                body: formData,
            });
        } else {
            const specText = elements.specInput.value.trim();
            let spec;
            try {
                spec = JSON.parse(specText);
            } catch {
                spec = specText;
            }

            response = await fetch(`${API_BASE_URL}/analyze/text?format=text`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    spec: spec,
                    name: elements.specName.value || 'pasted_spec',
                }),
            });
        }

        if (!response.ok) throw new Error('Failed to export text report');

        const text = await response.text();
        const blob = new Blob([text], { type: 'text/plain' });
        downloadFile(blob, 'specsentinel-report.txt');
    } catch (error) {
        console.error('Export error:', error);
        showError('Failed to export text report');
    }
}

/**
 * Download file
 */
function downloadFile(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Show pipeline progress indicator
 */
function showPipelineProgress() {
    const pipelineProgress = document.getElementById('pipelineProgress');
    const loadingSubtext = document.getElementById('loadingSubtext');
    if (pipelineProgress) {
        pipelineProgress.style.display = 'block';
        if (loadingSubtext) loadingSubtext.style.display = 'none';
        resetPipelineStages();
    }
}

/**
 * Hide pipeline progress indicator
 */
function hidePipelineProgress() {
    const pipelineProgress = document.getElementById('pipelineProgress');
    const loadingSubtext = document.getElementById('loadingSubtext');
    if (pipelineProgress) {
        pipelineProgress.style.display = 'none';
        if (loadingSubtext) loadingSubtext.style.display = 'block';
    }
}

/**
 * Reset all pipeline stages to initial state
 */
function resetPipelineStages() {
    const stages = document.querySelectorAll('.stage-item');
    stages.forEach(stage => {
        stage.classList.remove('active', 'completed', 'error');
        const icon = stage.querySelector('.stage-icon');
        const status = stage.querySelector('.stage-status');
        if (icon) icon.textContent = '⏳';
        if (status) status.textContent = '';
    });

    const progressFill = document.getElementById('progressFill');
    const progressMessage = document.getElementById('progressMessage');
    if (progressFill) progressFill.style.width = '0%';
    if (progressMessage) progressMessage.textContent = 'Initializing...';
}

/**
 * Update pipeline stage based on SSE event
 */
function updatePipelineStage(data) {
    const { stage, status, message, duration } = data;
    const stageElement = document.querySelector(`.stage-item[data-stage="${stage}"]`);
    const progressMessage = document.getElementById('progressMessage');
    const progressFill = document.getElementById('progressFill');

    if (!stageElement) return;

    const icon = stageElement.querySelector('.stage-icon');
    const statusText = stageElement.querySelector('.stage-status');

    if (status === 'started') {
        // Mark as active
        stageElement.classList.add('active');
        stageElement.classList.remove('completed', 'error');
        if (icon) icon.textContent = '🔄';
        if (statusText) statusText.textContent = '';
        if (progressMessage) progressMessage.textContent = message || `Processing ${stage}...`;

    } else if (status === 'completed') {
        // Mark as completed
        stageElement.classList.remove('active');
        stageElement.classList.add('completed');
        if (icon) icon.textContent = '✅';
        if (statusText && duration) {
            statusText.textContent = `${duration.toFixed(2)}s`;
        }

        // Update progress bar
        const stages = ['PLAN', 'ANALYZE', 'MATCH', 'SCORE', 'REPORT', 'AI-ENHANCE'];
        const completedIndex = stages.indexOf(stage);
        if (completedIndex >= 0 && progressFill) {
            const progress = ((completedIndex + 1) / stages.length) * 100;
            progressFill.style.width = `${progress}%`;
        }

    } else if (status === 'error') {
        // Mark as error
        stageElement.classList.remove('active', 'completed');
        stageElement.classList.add('error');
        if (icon) icon.textContent = '❌';
        if (progressMessage) progressMessage.textContent = message || 'Error occurred';

    } else if (status === 'skipped') {
        // Mark as skipped
        stageElement.classList.remove('active');
        stageElement.classList.add('completed');
        if (icon) icon.textContent = '⏭️';
        if (statusText) statusText.textContent = 'skipped';
    }
}

/**
 * Reset to upload screen
 */
function resetToUpload() {
    elements.resultsSection.style.display = 'none';
    elements.errorSection.style.display = 'none';

    // Hide action panel
    if (elements.actionPanel) {
        elements.actionPanel.style.display = 'none';
    }

    // Expand upload section and restore original title
    const uploadSection = document.querySelector('.upload-section');
    const titleElement = uploadSection ? uploadSection.querySelector('h2') : null;

    if (uploadSection) {
        uploadSection.classList.remove('collapsed');

        // Restore original title
        if (titleElement) {
            titleElement.textContent = originalUploadTitle;
        }
    }

    currentReport = null;
    analyzedFileName = '';
    clearAll();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Show loading overlay
 */
function showLoading() {
    elements.loadingOverlay.style.display = 'flex';
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    elements.loadingOverlay.style.display = 'none';
    hidePipelineProgress();
}

/**
 * Show error
 */
function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorSection.style.display = 'block';
    elements.resultsSection.style.display = 'none';
    elements.errorSection.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Check backend health
 */
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✅ Backend server is running');
        }
    } catch (error) {
        console.warn('⚠️ Backend server may not be running. Please start it with: python src/api/app.py');
    }
}

/**
 * Animate number
 */
function animateNumber(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.round(current);
    }, 16);
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Made with Bob

/**
 * Add click handlers to severity stat items
 */
function addSeverityClickHandlers() {
    const statItems = document.querySelectorAll('.stat-item.clickable');
    statItems.forEach(item => {
        item.addEventListener('click', () => {
            const severity = item.dataset.severity;
            showSeverityModal(severity);
        });
    });
}

/**
 * Show modal with findings and recommendations for a specific severity
 */
function showSeverityModal(severity) {
    if (!currentReport) return;

    const severityNames = {
        'critical': 'Critical',
        'high': 'High',
        'medium': 'Medium',
        'low': 'Low'
    };

    const severityEmojis = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🔵'
    };

    // Set modal title
    elements.modalTitle.textContent = `${severityEmojis[severity]} ${severityNames[severity]} Severity Issues`;

    // Filter findings by severity
    const findings = (currentReport.findings || []).filter(f =>
        f.severity.toLowerCase() === severity
    );

    // For severity modal, only show findings (not recommendations)
    // Recommendations are priority-based, not severity-based
    const recommendations = [];

    // Display merged issues and fixes in modal
    displayModalIssuesAndFixes(findings, recommendations, severity);

    // Show modal
    elements.severityModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

/**
 * Display findings in modal
 */
function displayModalFindings(findings, severity) {
    // This is now handled by displayModalIssuesAndFixes
    console.log('displayModalFindings called - redirecting to merged view');
}

/**
 * Display recommendations in modal
 */
function displayModalRecommendations(recommendations, severity) {
    // This is now handled by displayModalIssuesAndFixes
    console.log('displayModalRecommendations called - redirecting to merged view');
}

/**
 * Display merged issues and fixes in modal
 */
function displayModalIssuesAndFixes(findings, recommendations, severity) {
    if (!elements.modalIssuesList) {
        console.warn('modalIssuesList element not found');
        return;
    }

    elements.modalIssuesList.innerHTML = '';
    const totalCount = (findings?.length || 0) + (recommendations?.length || 0);
    elements.modalIssuesCount.textContent = totalCount;

    if (totalCount === 0) {
        elements.modalIssuesList.innerHTML = `
            <p class="text-center" style="color: var(--text-secondary); padding: 2rem;">
                No ${severity} issues detected. ✅
            </p>
        `;
        return;
    }

    // Merge findings and recommendations by title
    const mergedData = mergeIssuesAndFixes(findings, recommendations);

    // Create collapsible groups
    Object.entries(mergedData).forEach(([title, data]) => {
        const groupElement = createIssueFixGroupElement(title, data);
        elements.modalIssuesList.appendChild(groupElement);
    });
}

/**
 * Close modal
 */
function closeModal() {
    elements.severityModal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

/**
 * Export modal data (findings and recommendations for current severity)
 */
function exportModalData() {
    const modalTitle = elements.modalTitle.textContent;
    const findings = Array.from(elements.modalFindingsList.querySelectorAll('.finding-item'));
    const recommendations = Array.from(elements.modalRecommendationsList.querySelectorAll('.recommendation-item'));

    let text = `${modalTitle}\n`;
    text += '='.repeat(modalTitle.length) + '\n\n';

    text += `FINDINGS (${findings.length})\n`;
    text += '-'.repeat(50) + '\n';
    findings.forEach((item, index) => {
        const title = item.querySelector('.finding-title')?.textContent || '';
        const description = item.querySelector('.finding-description')?.textContent || '';
        text += `${index + 1}. ${title}\n   ${description}\n\n`;
    });

    text += `\nRECOMMENDATIONS (${recommendations.length})\n`;
    text += '-'.repeat(50) + '\n';
    recommendations.forEach((item, index) => {
        text += `${item.textContent.trim()}\n\n`;
    });

    const blob = new Blob([text], { type: 'text/plain' });
    const severity = modalTitle.toLowerCase().split(' ')[1]; // Extract severity from title
    downloadFile(blob, `specsentinel-${severity}-report.txt`);
}
