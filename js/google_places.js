// ✅ Make initAutocomplete available globally
window.initAutocomplete = function() {
  console.log("🚀 Google Places API callback fired!");
  
  const input = document.getElementById('address-input');
  if (!input) {
    console.error("❌ Address input element not found!");
    return;
  }

  console.log("✅ Address input found, creating autocomplete...");
  
  try {
    const autocomplete = new google.maps.places.Autocomplete(input, {
      types: ['address'],
      componentRestrictions: { country: 'au' },
      fields: ['formatted_address', 'geometry']
    });

    console.log("✅ Autocomplete created successfully!");

    // Optional: Listen for place selection
    autocomplete.addListener('place_changed', () => {
      const place = autocomplete.getPlace();
      console.log("📍 Selected place:", place.formatted_address);
      
      // Auto-populate the input with the selected address
      if (place.formatted_address) {
        input.value = place.formatted_address;
      }
    });

    console.log("✅ Place change listener added!");

  } catch (error) {
    console.error("❌ Error creating autocomplete:", error);
  }
};

// ✅ Fallback if script loads before DOM or callback doesn't fire
document.addEventListener('DOMContentLoaded', () => {
  console.log("🔄 DOM loaded, checking for Google API...");
  
  // If Google is already loaded but autocomplete wasn't initialized
  if (window.google && window.google.maps && window.google.maps.places) {
    console.log("🔄 Google API already loaded, initializing autocomplete...");
    window.initAutocomplete();
  } else {
    console.log("⏳ Waiting for Google API to load...");
  }
});