document.addEventListener('DOMContentLoaded', () => {
  const select = document.getElementById('suburb-select');
  const button = document.getElementById('start-btn');
  let isNavigating = false; // Prevent multiple clicks

  // Load suburbs from backend
  fetch('/load_suburbs')
    .then(res => res.json())
    .then(data => {
      data.suburbs.forEach(suburb => {
        const option = document.createElement('option');
        option.value = suburb;
        option.textContent = suburb;
        select.appendChild(option);
      });
      
      // ✅ Enable button once suburbs are loaded
      button.disabled = false;
      button.textContent = 'Start';
    })
    .catch(err => {
      console.error('Error loading suburbs:', err);
      button.textContent = 'Error - Refresh';
    });

  // ✅ Initially disable button until suburbs load
  button.disabled = true;
  button.textContent = 'Loading...';

  // ✅ Update button state when suburb changes
  select.addEventListener('change', () => {
    if (select.value && !isNavigating) {
      button.disabled = false;
      button.classList.remove('btn-disabled');
      button.classList.add('btn-ready');
    } else {
      button.disabled = true;
      button.classList.add('btn-disabled');
      button.classList.remove('btn-ready');
    }
  });

  // ✅ Super responsive button click
  button.addEventListener('click', (e) => {
    e.preventDefault(); // Prevent any default behavior
    
    const suburb = select.value.trim();
    console.log("Button clicked, suburb:", suburb);
    
    // ✅ Validate selection
    if (!suburb) {
      button.textContent = 'Please select suburb';
      button.style.backgroundColor = '#ff6b6b';
      setTimeout(() => {
        button.textContent = 'Start';
        button.style.backgroundColor = '';
      }, 1500);
      return;
    }

    // ✅ Prevent multiple clicks
    if (isNavigating) {
      console.log("Already navigating, ignoring click");
      return;
    }

    // ✅ Immediate visual feedback
    isNavigating = true;
    button.disabled = true;
    button.textContent = 'Loading...';
    button.classList.add('btn-loading');

    console.log("Navigating to:", suburb);

    // ✅ Navigate immediately (no delay)
    const safeSuburb = encodeURIComponent(suburb);
    window.location.href = `/suburb/${safeSuburb}`;
  });

  // ✅ Also handle Enter key on select
  select.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      button.click();
    }
  });
});