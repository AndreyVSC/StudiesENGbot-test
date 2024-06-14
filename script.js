document.addEventListener("DOMContentLoaded", function() {
    const buttons = document.querySelectorAll('.btn');

    buttons.forEach(button => {
        button.addEventListener('click', function() {
            const nextScreenId = this.getAttribute('data-next');
            if (nextScreenId) {
                document.querySelector('.screen.active').classList.remove('active');
                document.getElementById(nextScreenId).classList.add('active');
            }
        });
    });

    // Initially show the first screen
    document.getElementById('screen1').classList.add('active');
});
