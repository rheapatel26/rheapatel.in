const text = document.getElementById('typewriter').innerHTML;
document.getElementById('typewriter').innerHTML = '';

let i = 0;
function typeWriter() {
    if (i < text.length) {
        document.getElementById('typewriter').innerHTML += text.charAt(i);
        i++;
        setTimeout(typeWriter,20); // Adjust typing speed here (milliseconds)
    }
}

function resetTypewriter() {
    const typewriter = document.getElementById('typewriter');
    typewriter.style.animation = 'none';
    typewriter.offsetHeight; /* trigger reflow */
    typewriter.style.animation = null;
    setTimeout(() => {
        typewriter.style.animation = 'typing 3.5s steps(20, end) infinite, blink-caret .75s step-end infinite';
    }, 200); // Delay to reset animation
}

// Initial call to start the typewriter effect
setTimeout(typeWriter, 5000); // Start typewriter effect after 5 seconds
setInterval(resetTypewriter, 7000); // Restart animation every 7 seconds (5 seconds after animation completes)

document.addEventListener('DOMContentLoaded', function () {
    // Optionally add a delay to show the animation after a short delay
    setTimeout(function () {
        const navbar = document.querySelector('.side-navbar');
        navbar.style.animation = 'none'; // Disable animation
        void navbar.offsetWidth; // Trigger reflow
        navbar.style.animation = null; // Re-enable animation
    }, 100);
});

