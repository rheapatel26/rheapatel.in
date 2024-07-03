        // JavaScript for typewriter effect
        const text = document.getElementById('typewritter').innerHTML;
        document.getElementById('typewritter').innerHTML = '';

        let i = 0;
        function typeWriter() {
            if (i < text.length) {
                document.getElementById('typewritter').innerHTML += text.charAt(i);
                i++;
                setTimeout(typeWriter, 25); // Adjust typing speed here (milliseconds)
            }
        }
        typeWriter();

        document.addEventListener('DOMContentLoaded', function() {
            // Optionally add a delay to show the animation after a short delay
            setTimeout(function() {
                const navbar = document.querySelector('.side-navbar');
                navbar.style.animation = 'none'; // Disable animation
                void navbar.offsetWidth; // Trigger reflow
                navbar.style.animation = null; // Re-enable animation
            }, 100);
        });
                
        