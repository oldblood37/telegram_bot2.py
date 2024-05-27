    window.addEventListener('scroll', function() {
        var header = document.querySelector('header');
        var image2 = document.getElementById('image2');
        var heroText = document.querySelector('.hero-text');
        var scrollY = window.scrollY || window.pageYOffset;

        // Assuming you want the text fully invisible by the time the user scrolls 100px down
        var fadeOutHeight = 100; // Adjust this value as needed
        var opacity = 1 - (scrollY / fadeOutHeight);
        opacity = opacity < 0 ? 0 : opacity; // Ensure opacity doesn't go below 0

        // Apply calculated opacity to hero text
        heroText.style.opacity = opacity;

        // Image and header shadow logic remains the same
        if (scrollY > 0) {
            header.classList.add('shadow');
            image2.style.opacity = 1; // Reveals the second image
        } else {
            header.classList.remove('shadow');
            image2.style.opacity = 0; // Shows the first image
        }
    });

    document.addEventListener("DOMContentLoaded", function() {
        const steps = document.querySelectorAll('.step');
        const windowHeight = window.innerHeight;

        function checkVisibility() {
            for (let step of steps) {
                const rect = step.getBoundingClientRect();
                if (rect.top <= windowHeight * 0.8) { // Если элемент в пределах 80% высоты окна
                    step.classList.add('visible');
                }
            }
        }

        window.addEventListener('scroll', checkVisibility);
        checkVisibility(); // Проверка при загрузке страницы
    });