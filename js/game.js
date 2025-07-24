// Global variables
let currentSuburb = '';
let correctAddress = '';
let allWinners = [];

// Initialize the game when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎮 Game.js loaded successfully!');
    
    // Get suburb from URL path
    const path = window.location.pathname;
    const suburbMatch = path.match(/\/suburb\/(.+)/);
    if (suburbMatch) {
        currentSuburb = decodeURIComponent(suburbMatch[1]);
        console.log('🏠 Current suburb:', currentSuburb);
    }

    // Get the correct address from the page
    const addressElement = document.getElementById('correct-address');
    if (addressElement) {
        correctAddress = addressElement.textContent.trim();
        console.log('🏠 Correct address loaded:', correctAddress);
    }

    // Load and display winners
    loadWinners();
    
    // Set up guess form
    setupGuessForm();
});

// Handle address guessing
function setupGuessForm() {
    const guessForm = document.getElementById('guess-form');
    const guessInput = document.getElementById('address-guess');
    
    if (!guessForm || !guessInput) {
        console.log('⚠️ Guess form elements not found');
        return;
    }

    guessForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const userGuess = guessInput.value.trim();
        console.log('🎯 Your guess:', userGuess);
        console.log('🏠 Correct address:', correctAddress);
        
        if (checkAddressMatch(userGuess, correctAddress)) {
            console.log('🎉 WINNER! Showing modal and confetti...');
            showWinnerModal();
            triggerConfetti();
        } else {
            console.log('❌ Wrong address, try again!');
            showIncorrectMessage();
        }
    });
}

// Check if the guessed address matches the correct one
function checkAddressMatch(guess, correct) {
    // Normalize both addresses
    const normalizedGuess = normalizeAddress(guess);
    const normalizedCorrect = normalizeAddress(correct);
    
    console.log('🔄 Normalized guess:', normalizedGuess);
    console.log('🔄 Normalized correct:', normalizedCorrect);
    
    // Check for exact match first
    const exactMatch = normalizedGuess === normalizedCorrect;
    console.log('📏 Exact match?', exactMatch);
    
    // Check for flexible match (contains key components)
    const flexibleMatch = isFlexibleMatch(normalizedGuess, normalizedCorrect);
    console.log('📏 Flexible match?', flexibleMatch);
    
    return exactMatch || flexibleMatch;
}

// Normalize address for comparison
function normalizeAddress(address) {
    return address
        .toLowerCase()
        .replace(/\s+/g, ' ')  // Multiple spaces to single space
        .replace(/[.,]/g, '')  // Remove commas and periods
        .replace(/\b(street|st|road|rd|avenue|ave|drive|dr|court|ct|place|pl)\b/g, '$1')  // Normalize street types
        .replace(/\bqld\s+\d+/g, 'qld')  // Remove postcode
        .replace(/\baustralia\b/g, '')  // Remove Australia
        .trim();
}

// Flexible matching for slight variations
function isFlexibleMatch(guess, correct) {
    const guessWords = guess.split(' ').filter(word => word.length > 0);
    const correctWords = correct.split(' ').filter(word => word.length > 0);
    
    // Must have at least 3 words in common for large addresses
    const commonWords = guessWords.filter(word => correctWords.includes(word));
    return commonWords.length >= Math.min(3, correctWords.length - 1);
}

// Show winner modal
function showWinnerModal() {
    const modal = document.getElementById('winner-modal');
    if (modal) {
        modal.style.display = 'block';
        
        // Focus on name input
        const nameInput = document.getElementById('winner-name');
        if (nameInput) {
            nameInput.focus();
        }
        
        // Set up winner form submission
        setupWinnerForm();
    }
}

// Set up winner form submission
function setupWinnerForm() {
    const winnerForm = document.getElementById('winner-form');
    if (!winnerForm) return;
    
    // Remove existing listeners to prevent duplicates
    const newForm = winnerForm.cloneNode(true);
    winnerForm.parentNode.replaceChild(newForm, winnerForm);
    
    newForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(newForm);
        const winnerData = {
            name: formData.get('name'),
            email: formData.get('email'),
            phone: formData.get('phone'),
            suburb: currentSuburb
        };
        
        console.log('🏆 Submitting winner data:', winnerData);
        
        // Submit to backend
        fetch('/submit_winner', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(winnerData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('✅ Winner saved:', data);
            
            try {
                appendWinner(data);
                closeWinnerModal();
                advanceToNextHouse();
            } catch (error) {
                console.error('❌ Error saving winner:', error);
                // Still close modal and advance even if display fails
                closeWinnerModal();
                advanceToNextHouse();
            }
        })
        .catch(error => {
            console.error('❌ Error submitting winner:', error);
            // Still close modal - backend might have worked
            closeWinnerModal();
            advanceToNextHouse();
        });
    });
}

// Load and display winners
async function loadWinners() {
    try {
        const response = await fetch('/winners.json');
        allWinners = await response.json();
        console.log('📋 All winners:', allWinners);
        
        // Display winners for current suburb
        displayWinnersForSuburb();
    } catch (error) {
        console.error('❌ Error loading winners:', error);
        allWinners = [];
    }
}

// Display winners for current suburb
function displayWinnersForSuburb() {
    if (!allWinners) return;
    
    // Log all winners for debugging
    allWinners.forEach(winner => {
        console.log(`🔍 Winner Winner: ${winner.name}: image=${winner.image || 'no-image'}, suburb=${winner.suburb}, current=${currentSuburb}`);
    });
    
    // Filter winners for current suburb
    const suburbWinners = allWinners.filter(winner => winner.suburb === currentSuburb);
    console.log('🏆 ' + currentSuburb + ' winners:', suburbWinners);
    
    const winnersContainer = document.getElementById('winners-list');
    if (!winnersContainer) return;
    
    winnersContainer.innerHTML = '';
    
    if (suburbWinners.length === 0) {
        winnersContainer.innerHTML = '<p class="no-winners">🎯 No winners yet! Be the first to guess correctly!</p>';
        return;
    }
    
    suburbWinners.forEach(winner => {
        const winnerElement = createWinnerElement(winner);
        winnersContainer.appendChild(winnerElement);
    });
}

// Create winner element
function createWinnerElement(winner) {
    const winnerDiv = document.createElement('div');
    winnerDiv.className = 'winner-item';
    
    // Safely get image path
    const imagePath = getWinnerImagePath(winner);
    
    winnerDiv.innerHTML = `
        <div class="winner-content">
            <div class="winner-image">
                <img src="${imagePath}" alt="Winner house" onerror="this.src='/assets/placeholder-house.png'">
            </div>
            <div class="winner-details">
                <h4>🏆 ${escapeHtml(winner.name || 'Anonymous')}</h4>
                <p>📧 ${escapeHtml(winner.email || 'No email')}</p>
                <p>📱 ${escapeHtml(winner.phone || 'No phone')}</p>
                <p class="winner-suburb">🏠 ${escapeHtml(winner.suburb || currentSuburb)}</p>
                <p class="winner-time">⏰ ${formatTime(winner.timestamp)}</p>
            </div>
        </div>
    `;
    
    return winnerDiv;
}

// Safely get winner image path (fixes the undefined.startsWith error)
function getWinnerImagePath(winner) {
    // Check if winner has image property
    if (winner.image && typeof winner.image === 'string') {
        // If image path starts with '/', it's already relative to root
        if (winner.image.startsWith('/')) {
            return winner.image;
        }
        // Otherwise prepend with '/'
        return '/' + winner.image;
    }
    
    // Fallback: generate image path based on suburb and assume first house
    const suburbImageMap = {
        'Ashgrove': 'Ashgrove_houses/Ash1.png',
        'The Gap': 'TheGap_houses/Gap1.png', 
        'Red Hill': 'RedHill_houses/RedHill1.png',
        'Bardon': 'Bardon_houses/Bard1.png',
        'Paddington': 'Paddington_houses/Padd1.png',
        'Enoggera': 'Enoggera_houses/Enog1.png'
    };
    
    const defaultImage = suburbImageMap[winner.suburb || currentSuburb];
    return defaultImage ? '/' + defaultImage : '/assets/placeholder-house.png';
}

// Append new winner to display (with safe error handling)
function appendWinner(data) {
    if (!data || !data.result || !data.result.winner) {
        console.log('⚠️ No winner data to append');
        return;
    }
    
    const winner = data.result.winner;
    console.log('➕ Appending winner:', winner);
    
    // Add to allWinners array
    allWinners.push(winner);
    
    // Update display
    displayWinnersForSuburb();
}

// Close winner modal
function closeWinnerModal() {
    const modal = document.getElementById('winner-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Advance to next house
function advanceToNextHouse() {
    console.log('🏠 Advancing to next house...');
    
    // Reload the page to show next house
    setTimeout(() => {
        window.location.reload();
    }, 2000);
}

// Show incorrect message
function showIncorrectMessage() {
    const messageDiv = document.getElementById('message');
    if (messageDiv) {
        messageDiv.innerHTML = '<p class="incorrect">❌ Incorrect address. Try again!</p>';
        messageDiv.style.display = 'block';
        
        // Hide message after 3 seconds
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 3000);
    }
}

// Trigger confetti animation
function triggerConfetti() {
    console.log('🎈 Triggering EPIC confetti celebration...');
    
    // Multiple confetti bursts
    for (let i = 0; i < 5; i++) {
        setTimeout(() => {
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 }
            });
        }, i * 300);
    }
    
    // Extra special burst
    setTimeout(() => {
        confetti({
            particleCount: 200,
            spread: 120,
            origin: { y: 0.4 }
        });
    }, 1500);
}

// Utility function to escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Format timestamp
function formatTime(timestamp) {
    if (!timestamp) return 'Unknown time';
    
    try {
        const date = new Date(timestamp);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch (error) {
        return 'Invalid time';
    }
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        normalizeAddress,
        checkAddressMatch,
        isFlexibleMatch
    };
}