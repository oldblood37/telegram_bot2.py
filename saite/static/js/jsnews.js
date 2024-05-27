        var lastScrollY = window.scrollY || window.pageYOffset;
        var ticking = false;

        function onScroll() {
            var header = document.querySelector('header');
            var heroText = document.getElementById('heroText');
            var image2 = document.getElementById('image2');
            var scrollY = window.scrollY || window.pageYOffset;
            var heroImageHeight = document.querySelector('.hero-image').offsetHeight;

            // Adjust these values as needed
            var startOffset = 20; // Starting offset from the top
            var endOffset = heroImageHeight - 20 - heroText.offsetHeight; // Ending offset from the bottom

            // Calculate new top position of hero text
            var newTop = startOffset + scrollY;
            if (newTop > endOffset) {
                newTop = endOffset;
            }

            heroText.style.top = newTop + 'px';

            // Apply opacity to the second image
            var image2Start = 50; // Start showing the second image after 50px of scrolling
            var image2End = 170; // Fully show the second image after 200px of scrolling
            var image2Opacity = (scrollY - image2Start) / (image2End - image2Start);
            image2Opacity = Math.min(Math.max(image2Opacity, 0), 1); // Ensure the value is between 0 and 1
            image2.style.opacity = image2Opacity;

            // Apply shadow to header
            if (scrollY > 0) {
                header.classList.add('shadow');
            } else {
                header.classList.remove('shadow');
            }

            lastScrollY = scrollY;
            ticking = false;
        }

        function requestTick() {
            if (!ticking) {
                requestAnimationFrame(onScroll);
                ticking = true;
            }
        }

        window.addEventListener('scroll', requestTick);
        document.addEventListener('DOMContentLoaded', onScroll);
        
