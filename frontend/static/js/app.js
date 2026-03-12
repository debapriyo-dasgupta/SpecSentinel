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

    // Modal
    severityModal: document.getElementById('severityModal'),
    modalTitle: document.getElementById('modalTitle'),
    modalClose: document.getElementById('modalClose'),
    modalCloseBtn: document.getElementById('modalCloseBtn'),
    modalFindingsList: document.getElementById('modalFindingsList'),
    modalRecommendationsList: document.getElementById('modalRecommendationsList'),
    modalFindingsCount: document.getElementById('modalFindingsCount'),
    modalRecommendationsCount: document.getElementById('modalRecommendationsCount'),
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

    // Display findings in modal
    displayModalFindings(findings, categoryName);

    // Display recommendations in modal
    displayModalRecommendations(recommendations, categoryName);

    // Show modal
    elements.severityModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

/**
 * Analyze file via API
 */
async function analyzeFile(file) {
    showLoading();

    try {
        const formData = new FormData();
        formData.append('file', file);

        console.log('Sending file to backend:', file.name);

        const response = await fetch(`${API_BASE_URL}/analyze?format=json`, {
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
 * Display findings
 */
function displayFindings(findings) {
    elements.findingsList.innerHTML = '';

    if (!findings || findings.length === 0) {
        elements.findingsList.innerHTML = '<p class="text-center">No findings detected. Great job! ✅</p>';
        return;
    }

    findings.forEach(finding => {
        const item = createFindingElement(finding);
        elements.findingsList.appendChild(item);
    });
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
    console.log('Displaying recommendations:', recommendations);
    elements.recommendationsList.innerHTML = '';

    if (!recommendations || !Array.isArray(recommendations) || recommendations.length === 0) {
        console.log('No recommendations to display');
        elements.recommendationsList.innerHTML = '<p class="text-center">No priority recommendations at this time.</p>';
        return;
    }

    console.log(`Rendering ${recommendations.length} recommendations`);
    recommendations.forEach((rec, index) => {
        const item = document.createElement('div');
        item.className = 'recommendation-item';

        // Handle both string and object formats
        if (typeof rec === 'string') {
            // Simple string format
            item.innerHTML = `<strong>${index + 1}.</strong> ${escapeHtml(rec)}`;
        } else if (rec && typeof rec === 'object') {
            // Object format from backend
            const priority = rec.priority || 'High';
            const title = rec.title || 'Recommendation';
            const issue = rec.issue || '';
            const fix = rec.fix || '';
            const benchmark = rec.benchmark || '';

            let html = `<strong>${index + 1}. [${priority}]</strong> ${escapeHtml(title)}`;

            if (issue) {
                html += `<br><span style="color: var(--text-secondary); font-size: 0.9em;">Issue: ${escapeHtml(issue)}</span>`;
            }

            if (fix) {
                html += `<br><span style="color: var(--success-color); font-size: 0.9em;">💡 Fix: ${escapeHtml(fix)}</span>`;
            }

            if (benchmark) {
                html += `<br><span style="color: var(--text-tertiary); font-size: 0.85em;">📋 ${escapeHtml(benchmark)}</span>`;
            }

            item.innerHTML = html;
        } else {
            console.warn('Invalid recommendation format:', rec);
            return;
        }

        elements.recommendationsList.appendChild(item);
    });
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

    // Filter recommendations by severity (if they have severity field)
    const recommendations = (currentReport.recommendations || []).filter(rec => {
        if (typeof rec === 'object' && rec.priority) {
            return rec.priority.toLowerCase() === severity;
        }
        return false;
    });

    // Display findings in modal
    displayModalFindings(findings, severity);

    // Display recommendations in modal
    displayModalRecommendations(recommendations, severity);

    // Show modal
    elements.severityModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

/**
 * Display findings in modal
 */
function displayModalFindings(findings, severity) {
    elements.modalFindingsList.innerHTML = '';
    elements.modalFindingsCount.textContent = findings.length;

    if (findings.length === 0) {
        elements.modalFindingsList.innerHTML = `
            <p class="text-center" style="color: var(--text-secondary); padding: 2rem;">
                No ${severity} severity findings detected. ✅
            </p>
        `;
        return;
    }

    findings.forEach(finding => {
        const item = createFindingElement(finding);
        elements.modalFindingsList.appendChild(item);
    });
}

/**
 * Display recommendations in modal
 */
function displayModalRecommendations(recommendations, severity) {
    elements.modalRecommendationsList.innerHTML = '';
    elements.modalRecommendationsCount.textContent = recommendations.length;

    if (recommendations.length === 0) {
        elements.modalRecommendationsList.innerHTML = `
            <p class="text-center" style="color: var(--text-secondary); padding: 2rem;">
                No ${severity} priority recommendations at this time.
            </p>
        `;
        return;
    }

    recommendations.forEach((rec, index) => {
        const item = document.createElement('div');
        item.className = 'recommendation-item';

        if (typeof rec === 'object') {
            const priority = rec.priority || 'High';
            const title = rec.title || 'Recommendation';
            const issue = rec.issue || '';
            const fix = rec.fix || '';
            const benchmark = rec.benchmark || '';

            let html = `<strong>${index + 1}. [${priority}]</strong> ${escapeHtml(title)}`;

            if (issue) {
                html += `<br><span style="color: var(--text-secondary); font-size: 0.9em;">Issue: ${escapeHtml(issue)}</span>`;
            }

            if (fix) {
                html += `<br><span style="color: var(--success-color); font-size: 0.9em;">💡 Fix: ${escapeHtml(fix)}</span>`;
            }

            if (benchmark) {
                html += `<br><span style="color: var(--text-tertiary); font-size: 0.85em;">📋 ${escapeHtml(benchmark)}</span>`;
            }

            item.innerHTML = html;
        } else {
            item.innerHTML = `<strong>${index + 1}.</strong> ${escapeHtml(rec)}`;
        }

        elements.modalRecommendationsList.appendChild(item);
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
