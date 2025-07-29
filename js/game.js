document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('address-input');
  const button = document.getElementById('submit-btn');
  const result = document.getElementById('result');
  const winnerModal = document.getElementById('winner-modal');
  const nameInput = document.getElementById('winner-name');
  const mobileInput = document.getElementById('winner-mobile');
  const ageCheckbox = document.getElementById('winner-age');
  const saveBtn = document.getElementById('save-winner');
  const winnerGrid = document.getElementById('winner-grid');

  const currentSuburb = document.title.split(' – ')[0];
  console.log("🏠 Current suburb:", currentSuburb);

  loadExistingWinners();

  function normalizeAddress(address) {
    return address
      .toLowerCase()
      .replace(/\s+/g, ' ')
      .replace(/\b(road|rd)\b/g, 'road')
      .replace(/\b(street|st)\b/g, 'street')
      .replace(/\b(avenue|ave)\b/g, 'avenue')
      .replace(/\s*,\s*/g, ', ')
      .replace(/\s*\d{4}\s*,?\s*/g, ', ')
      .replace(/,\s*australia\s*$/i, '')
      .replace(/,\s*qld\s*$/i, ', qld')
      .trim();
  }

  button.addEventListener('click', () => {
    const guess = input.value.trim();

    console.log("🎯 Your guess:", guess);
    console.log("🏠 Correct address:", correctAddress);

    const normalizedGuess = normalizeAddress(guess);
    const normalizedCorrect = normalizeAddress(correctAddress);

    console.log("🔄 Normalized guess:", normalizedGuess);
    console.log("🔄 Normalized correct:", normalizedCorrect);

    const exactMatch = guess === correctAddress;
    const flexibleMatch = normalizedGuess === normalizedCorrect;

    console.log("📏 Exact match?", exactMatch);
    console.log("📏 Flexible match?", flexibleMatch);

    if (exactMatch || flexibleMatch) {
      console.log("🎉 WINNER! Showing modal and confetti...");
      showWinnerModal();
      triggerConfetti();
      result.classList.add('hidden');
    } else {
      console.log("❌ No match. Showing error message...");
      result.textContent = "❌ Not quite. Try again!";
      result.classList.remove('hidden');
      result.style.color = 'red';

      setTimeout(() => {
        result.classList.add('hidden');
        input.value = '';
        input.focus();
        console.log("🔄 Auto-reset: Ready for next attempt");
      }, 3000);
    }
  });

  input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      button.click();
    }
  });

  saveBtn.addEventListener('click', () => {
    const name = nameInput.value.trim();
    const mobile = mobileInput.value.trim();
    const over18 = ageCheckbox.checked;

    if (!name || !mobile || !over18) {
      alert("Please complete all fields and confirm you're over 18.");
      return;
    }

    const data = {
      name: name,
      email: '',
      phone: mobile,
      suburb: currentSuburb,
      address: correctAddress,
      image: imagePath
    };

    console.log("🏆 Submitting winner data:", data);

    fetch('/submit_winner', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(res => res.json())
      .then(saved => {
        console.log("✅ Winner saved:", saved);

        if (saved.success) {
          const newWinner = {
            name: `Winner: ${data.name}`,
            address: data.address,
            image: data.image
          };
          appendWinner(newWinner);
          closeWinnerModal();

          result.textContent = "🎉 Congratulations! Prize details will be sent to your mobile.";
          result.style.color = 'green';
          result.classList.remove('hidden');

          setTimeout(() => {
            window.location.href = `/suburb/${encodeURIComponent(currentSuburb)}`;
          }, 3000);
        } else {
          console.error("❌ Error saving winner:", saved.error);
          alert("Error saving winner: " + saved.error);
        }
      })
      .catch(err => {
        console.error("❌ Error saving winner:", err);
        alert("Error saving winner. Please try again.");
      });
  });

  function loadExistingWinners() {
    fetch('/winners.json')
      .then(res => res.json())
      .then(winners => {
        console.log("📋 All winners:", winners);

        const suburbWinners = winners.filter(winner => {
          const suburbFromImage = getSuburbFromImagePath(winner.image);
          console.log(`🔍 Winner ${winner.name}: image=${winner.image}, suburb=${suburbFromImage}, current=${currentSuburb}`);
          return suburbFromImage === currentSuburb;
        });

        console.log(`🏆 ${currentSuburb} winners:`, suburbWinners);

        suburbWinners.forEach(winner => {
          appendWinner(winner);
        });
      })
      .catch(err => {
        console.log('No winners file found or error loading winners:', err);
      });
  }

  function getSuburbFromImagePath(imagePath) {
    if (!imagePath || !imagePath.includes('_houses/')) return null;

    const suburbFolder = imagePath.split('_houses/')[0];

    if (suburbFolder === "Ashgrove") return "Ashgrove";
    if (suburbFolder === "TheGap") return "The Gap";
    if (suburbFolder === "RedHill") return "Red Hill";
    if (suburbFolder === "Bardon") return "Bardon";
    if (suburbFolder === "Paddington") return "Paddington";
    if (suburbFolder === "Enoggera") return "Enoggera";
    if (suburbFolder === "Alderley") return "Alderley"; // ✅ FIXED: Added for Alderley

    return null;
  }

  function showWinnerModal() {
    console.log("🎊 Displaying winner modal...");
    winnerModal.classList.remove('hidden');
  }

  function closeWinnerModal() {
    winnerModal.classList.add('hidden');
    nameInput.value = '';
    mobileInput.value = '';
    ageCheckbox.checked = false;
  }

  function appendWinner(winner) {
    let displayName = winner.name || 'Anonymous';
    if (!displayName.startsWith('Winner: ')) {
      displayName = `Winner: ${displayName}`;
    }

    const card = document.createElement('div');
    card.className = 'winner-card';
    card.innerHTML = `
      <img src="/${winner.image}" alt="Winner's house" class="winner-house-img" />
      <p><strong>${displayName}</strong></p>
      <p>${winner.address}</p>
    `;
    winnerGrid.appendChild(card);

    const img = card.querySelector('.winner-house-img');
    img.addEventListener('click', () => {
      showImageModal(winner.image, displayName, winner.address);
    });

    img.style.cursor = 'pointer';
    img.title = 'Click to view full size';
  }

  function showImageModal(imageSrc, winnerName, address) {
    const modal = document.createElement('div');
    modal.className = 'image-modal';
    modal.innerHTML = `
      <div class="image-modal-content">
        <button class="image-modal-close">&times;</button>
        <img src="/${imageSrc}" alt="Full size house" class="modal-image" />
        <div class="image-modal-info">
          <p><strong>${winnerName}</strong></p>
          <p>${address}</p>
        </div>
      </div>
    `;

    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';

    function closeModal() {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
      if (document.body.contains(modal)) {
        document.body.removeChild(modal);
      }
      console.log("✅ Modal closed and cleaned up");
    }

    const closeBtn = modal.querySelector('.image-modal-close');
    closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      closeModal();
    });

    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeModal();
      }
    });

    const content = modal.querySelector('.image-modal-content');
    content.addEventListener('click', (e) => {
      e.stopPropagation();
    });

    function handleEscape(e) {
      if (e.key === 'Escape') {
        closeModal();
      }
    }
    document.addEventListener('keydown', handleEscape);

    console.log("✅ Modal opened successfully");
  }

  function triggerConfetti() {
    console.log("🎈 Triggering EPIC confetti celebration...");

    const balloonEmojis = ['🎈', '🎉', '🎊', '✨'];
    for (let i = 0; i < 30; i++) {
      const balloon = document.createElement('div');
      balloon.textContent = balloonEmojis[Math.floor(Math.random() * balloonEmojis.length)];
      balloon.className = 'mega-balloon';
      balloon.style.left = `${Math.random() * 100}%`;
      balloon.style.animationDelay = `${Math.random() * 2}s`;
      document.body.appendChild(balloon);
      setTimeout(() => balloon.remove(), 8000);
    }

    const confettiColors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3', '#54a0ff'];
    const confettiShapes = ['●', '■', '▲', '♦', '★', '♥', '♠'];

    for (let i = 0; i < 100; i++) {
      const confetti = document.createElement('div');
      confetti.textContent = confettiShapes[Math.floor(Math.random() * confettiShapes.length)];
      confetti.className = 'confetti-piece';
      confetti.style.left = `${Math.random() * 100}%`;
      confetti.style.color = confettiColors[Math.floor(Math.random() * confettiColors.length)];
      confetti.style.animationDelay = `${Math.random() * 3}s`;
      confetti.style.animationDuration = `${3 + Math.random() * 4}s`;
      document.body.appendChild(confetti);
      setTimeout(() => confetti.remove(), 7000);
    }

    for (let i = 0; i < 25; i++) {
      const star = document.createElement('div');
      star.textContent = '⭐';
      star.className = 'golden-star';
      star.style.left = `${Math.random() * 100}%`;
      star.style.animationDelay = `${Math.random() * 1}s`;
      document.body.appendChild(star);
      setTimeout(() => star.remove(), 6000);
    }

    const flash = document.createElement('div');
    flash.className = 'winner-flash';
    document.body.appendChild(flash);
    setTimeout(() => flash.remove(), 1000);

    const celebrationText = document.createElement('div');
    celebrationText.textContent = '🎊 WINNER! 🎊';
    celebrationText.className = 'celebration-text';
    document.body.appendChild(celebrationText);
    setTimeout(() => celebrationText.remove(), 4000);
  }
});
