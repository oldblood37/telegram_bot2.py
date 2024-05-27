function showLoader() {
        document.getElementById('loader').style.visibility = 'visible';
    }

    document.addEventListener('DOMContentLoaded', function() {
        var loader = document.getElementById('loader');

        // Функция для показа загрузчика
        function showLoader() {
            loader.style.visibility = 'visible';
        }

        // Повесить обработчики на все ссылки
        document.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', function(event) {
                // Проверяем, удерживает ли пользователь клавишу Ctrl, Shift или Meta (Cmd)
                if (!event.ctrlKey && !event.shiftKey && !event.metaKey && !link.target) {
                    showLoader(); // Показать загрузчик при клике
                }
            });
        });

        // Скрыть загрузчик после полной загрузки страницы
        window.addEventListener('load', function() {
            loader.style.visibility = 'hidden';
        });
    });