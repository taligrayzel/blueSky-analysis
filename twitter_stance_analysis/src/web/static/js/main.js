// Show loading spinner
function showLoading() {
    document.getElementById('loading').style.display = 'flex';
}

// Hide loading spinner
function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// Format percentage
function formatPercentage(value) {
    return (value * 100).toFixed(1) + '%';
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Display user information
function displayUserInfo(userInfo) {
    const userInfoDiv = document.getElementById('userInfo');
    userInfoDiv.innerHTML = `
        <div class="user-stat">
            <span>Display Name:</span>
            <strong>${userInfo.display_name || 'N/A'}</strong>
        </div>
        <div class="user-stat">
            <span>Followers:</span>
            <strong>${formatNumber(userInfo.followers_count)}</strong>
        </div>
        <div class="user-stat">
            <span>Following:</span>
            <strong>${formatNumber(userInfo.following_count)}</strong>
        </div>
        <div class="user-stat">
            <span>Posts:</span>
            <strong>${formatNumber(userInfo.posts_count)}</strong>
        </div>
        <div class="user-stat">
            <span>Description:</span>
            <strong>${userInfo.description || 'N/A'}</strong>
        </div>
    `;
}

// Display analysis results
function displayAnalysisResults(analysis) {
    const resultsDiv = document.getElementById('analysisResults');
    
    // Create stance badge
    const stanceClass = analysis.stance.toLowerCase().replace('/', '-');
    const stanceBadge = `<span class="stance-badge stance-${stanceClass}">${analysis.stance}</span>`;
    
    resultsDiv.innerHTML = `
        <div class="mb-4">
            <h6>Overall Stance</h6>
            ${stanceBadge}
        </div>
        <div class="mb-4">
            <h6>Confidence</h6>
            <div class="progress">
                <div class="progress-bar" role="progressbar" 
                     style="width: ${analysis.confidence * 100}%" 
                     aria-valuenow="${analysis.confidence * 100}" 
                     aria-valuemin="0" 
                     aria-valuemax="100">
                    ${formatPercentage(analysis.confidence)}
                </div>
            </div>
        </div>
        <div class="mb-4">
            <h6>Average Score</h6>
            <div class="progress">
                <div class="progress-bar ${analysis.average_score > 0 ? 'bg-primary' : 'bg-danger'}" 
                     role="progressbar" 
                     style="width: ${Math.abs(analysis.average_score * 100)}%" 
                     aria-valuenow="${Math.abs(analysis.average_score * 100)}" 
                     aria-valuemin="0" 
                     aria-valuemax="100">
                    ${analysis.average_score.toFixed(2)}
                </div>
            </div>
        </div>
        <div>
            <h6>Stance Distribution</h6>
            <div class="row">
                ${Object.entries(analysis.stance_distribution).map(([stance, percentage]) => `
                    <div class="col-md-4 mb-2">
                        <div class="card">
                            <div class="card-body text-center">
                                <h6>${stance}</h6>
                                <h4>${formatPercentage(percentage)}</h4>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Display visualization
function displayVisualization(username) {
    const vizImage = document.getElementById('vizImage');
    vizImage.src = `/visualization/${username}?t=${new Date().getTime()}`;
}

// Analyze a user
async function analyzeUser() {
    const username = document.getElementById('username').value.trim();
    if (!username) {
        alert('Please enter a username');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('results').style.display = 'flex';
            displayUserInfo(data.user_info);
            displayAnalysisResults(data.analysis);
            displayVisualization(username);
        } else {
            alert(data.error || 'Error analyzing user');
        }
    } catch (error) {
        alert('Error analyzing user: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Compare users
async function compareUsers() {
    const usernames = document.getElementById('compareUsernames').value
        .split(',')
        .map(u => u.trim())
        .filter(u => u);
        
    if (usernames.length < 2) {
        alert('Please enter at least two usernames separated by commas');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/compare', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ usernames }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayComparisonResults(data);
        } else {
            alert(data.error || 'Error comparing users');
        }
    } catch (error) {
        alert('Error comparing users: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Display comparison results
function displayComparisonResults(comparison) {
    const resultsDiv = document.getElementById('comparisonResults');
    
    // Create comparison chart
    const ctx = document.createElement('canvas');
    resultsDiv.innerHTML = '';
    resultsDiv.appendChild(ctx);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(comparison),
            datasets: [{
                label: 'Stance Score',
                data: Object.values(comparison).map(a => a.average_score),
                backgroundColor: Object.values(comparison).map(a => 
                    a.average_score > 0 ? '#3498db' : '#e74c3c'
                ),
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Load analysis history
async function loadHistory() {
    try {
        const response = await fetch('/history');
        const data = await response.json();
        
        if (response.ok) {
            displayHistoryResults(data);
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Display history results
function displayHistoryResults(history) {
    const resultsDiv = document.getElementById('historyResults');
    
    resultsDiv.innerHTML = Object.entries(history).map(([username, analysis]) => `
        <div class="history-item">
            <h6>@${username}</h6>
            <div class="d-flex justify-content-between align-items-center">
                <span class="stance-badge stance-${analysis.stance.toLowerCase().replace('/', '-')}">
                    ${analysis.stance}
                </span>
                <small>Confidence: ${formatPercentage(analysis.confidence)}</small>
            </div>
        </div>
    `).join('');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Load history on page load
    loadHistory();
    
    // Add enter key support for search
    document.getElementById('username').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            analyzeUser();
        }
    });
    
    // Add enter key support for comparison
    document.getElementById('compareUsernames').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            compareUsers();
        }
    });
}); 