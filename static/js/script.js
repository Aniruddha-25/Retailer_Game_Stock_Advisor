// ==================== Global Variables ====================

let availableYears = [];

// ==================== Page Initialization ====================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded, initializing...');
});

// ==================== Train Model ====================

async function trainModel() {
    const trainBtn = document.getElementById('trainBtn');
    const trainStatus = document.getElementById('trainStatus');
    
    trainBtn.disabled = true;
    trainBtn.textContent = '🔄 Training...';
    trainStatus.textContent = 'Training model, please wait...';
    trainStatus.style.color = '#2563eb';
    
    try {
        const response = await fetch('/api/train-model', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            trainBtn.textContent = '✅ Model Trained';
            trainStatus.textContent = data.message;
            trainStatus.style.color = '#10b981';
        } else {
            trainBtn.textContent = '❌ Training Failed';
            trainStatus.textContent = `❌ Error: ${data.error}`;
            trainStatus.style.color = '#ef4444';
        }
    } catch (error) {
        console.error('Error training model:', error);
        trainBtn.textContent = '❌ Error';
        trainStatus.textContent = `❌ Error: ${error.message}`;
        trainStatus.style.color = '#ef4444';
    } finally {
        setTimeout(() => {
            trainBtn.disabled = false;
        }, 1000);
    }
}

// ==================== Load Years ====================

async function getPredictions() {
    const year = document.getElementById('yearInput').value;
    const maxGames = document.getElementById('maxGames').value;

    // Validation
    if (!year) {
        showError('Please enter a year');
        return;
    }

    if (!maxGames || maxGames < 1) {
        showError('Please enter a valid number of games');
        return;
    }

    // Show loading indicator
    showLoading(true);
    hideError();

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                year: parseInt(year),
                max_games: parseInt(maxGames)
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            showError(data.error || 'Failed to get predictions');
            showLoading(false);
            return;
        }

        // Display results
        displayResults(data);
        showLoading(false);

    } catch (error) {
        console.error('Error fetching predictions:', error);
        showError('An error occurred while fetching predictions: ' + error.message);
        showLoading(false);
    }
}

// ==================== Display Results ====================

function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsSummary = document.getElementById('resultsSummary');
    const gamesGrid = document.getElementById('gamesGrid');

    // Display summary with requested stock info
    const summaryHTML = `
        <p>📅 <strong>Year:</strong> ${data.year} | 
           📊 <strong>Total Games Analyzed:</strong> ${data.total_games} | 
           📦 <strong>Stocks Requested:</strong> ${data.requested_stock} | 
           ⭐ <strong>Top Recommendations:</strong> ${data.games.length}</p>
        <p style="color: #10b981; font-weight: 600; margin-top: 8px;">✅ ${data.message}</p>
    `;
    resultsSummary.innerHTML = summaryHTML;

    // Display game cards
    gamesGrid.innerHTML = '';
    data.games.forEach(game => {
        const gameCard = createGameCard(game);
        gamesGrid.appendChild(gameCard);
    });

    // Show results section
    resultsSection.classList.remove('hidden');

    // Scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }, 300);
}

function createGameCard(game) {
    const card = document.createElement('div');
    card.className = 'game-card';

    const rankBadge = `<div class="game-rank">#${game.rank}</div>`;

    const gameDetails = `
        <div class="game-name">${escapeHtml(game.name)}</div>
        <div class="game-details">
            <div class="game-detail">
                <span class="game-detail-label">Platform:</span>
                <span class="game-platform">${escapeHtml(game.platform)}</span>
            </div>
            <div class="game-detail">
                <span class="game-detail-label">Genre:</span>
                <span class="game-genre">${escapeHtml(game.genre)}</span>
            </div>
            <div class="game-detail">
                <span class="game-detail-label">Publisher:</span>
                <span class="game-detail-value">${escapeHtml(game.publisher)}</span>
            </div>
        </div>
    `;

    const salesInfo = `
        <div class="game-sales">
            <div class="sales-label">Predicted Global Sales</div>
            <div class="sales-value">${game.predicted_sales}M</div>
        </div>
    `;

    const regionalBreakdown = `
        <div class="regional-breakdown">
            <div class="regional-item">
                <div class="regional-label">NA</div>
                <div class="regional-value">${game.na_sales}M</div>
            </div>
            <div class="regional-item">
                <div class="regional-label">EU</div>
                <div class="regional-value">${game.eu_sales}M</div>
            </div>
            <div class="regional-item">
                <div class="regional-label">JP</div>
                <div class="regional-value">${game.jp_sales}M</div>
            </div>
            <div class="regional-item">
                <div class="regional-label">Other</div>
                <div class="regional-value">${game.other_sales}M</div>
            </div>
        </div>
    `;

    card.innerHTML = rankBadge + gameDetails + salesInfo + regionalBreakdown;
    return card;
}

// ==================== Helper Functions ====================

function showLoading(show) {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (show) {
        loadingIndicator.classList.remove('hidden');
    } else {
        loadingIndicator.classList.add('hidden');
    }
}

function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

function hideError() {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.classList.add('hidden');
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// ==================== Enter Key Support ====================

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('yearSelect').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') getPredictions();
    });

    document.getElementById('maxGames').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') getPredictions();
    });
});

// ==================== Console Logging ====================

console.log('Game Stock Advisor - JavaScript loaded successfully');
