document.addEventListener('DOMContentLoaded', function () {
    var mood = document.body.getAttribute('data-mood');
    if (mood) {
        document.body.classList.add('mood-' + mood.replace(/\s+/g, '-').toLowerCase());
    }
});
