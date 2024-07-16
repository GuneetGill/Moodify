// scripts.js

//button to redirect to playlists
document.addEventListener('DOMContentLoaded', function() {
    var analyzeButton = document.getElementById('analyze-button');
    analyzeButton.addEventListener('click', function() {
        window.location.href = '/get_playlists';
    });
});

//deals with loading animation
document.addEventListener("DOMContentLoaded", function() {
    const overlay = document.getElementById('overlay');
    const loadingSpinner = document.getElementById('loading-spinner');

    // Debugging: Ensure elements are correctly selected
    console.log('Page loaded. Hiding spinner and overlay.');
    overlay.style.display = 'none';
    loadingSpinner.style.display = 'none';

    // Set up click event listeners for playlist links
    document.querySelectorAll('a[href^="/analyze_playlist/"]').forEach(function(link) {
        link.addEventListener('click', function(event) {
            console.log('Link clicked:', this.href);  // Debugging link click
            overlay.style.display = 'block';
            loadingSpinner.style.display = 'block';

        });
    });

    // Ensure spinner is hidden when navigating back to the page
    window.addEventListener('pageshow', function(event) {
        // Check if the event is triggered from the back/forward cache
        if (event.persisted || (window.performance && window.performance.navigation.type === 2)) {
            console.log('Page loaded from cache. Hiding spinner.');
            overlay.style.display = 'none';
            loadingSpinner.style.display = 'none';
        }
    });
});

