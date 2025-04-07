function downloadFile() {
            // Создаем временную ссылку
            const link = document.createElement('a');
            
            // Указываем путь к файлу (замените на ваш)
            link.href = '../../docs/test.docx';
            
            // Добавляем атрибут download с именем файла
            link.download = 'lol.docx'; // Называть как угодно
            
            // Добавляем ссылку в DOM
            document.body.appendChild(link);
            
            // Эмулируем клик по ссылке
            link.click();
            
            // Удаляем ссылку из DOM
            document.body.removeChild(link);
        }