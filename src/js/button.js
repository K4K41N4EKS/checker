function handleDropdownChange(dropdown) {
    const selectedValue = dropdown.value;
    console.log(`Выбор ${selectedValue}`);
}

function hrefFuncSample(){
    window.location.href = 'index.html';
}

function hrefFuncNotSample(){
    window.location.href = 'settings.html';
}

function updateFileName() {
  const fileInput = document.getElementById('fileInput');
  const fileNameDisplay = document.getElementById('fileName');
  const fileName = fileInput.files.length > 0 ? fileInput.files[0].name : '';
  fileNameDisplay.textContent = `Ваш файл: ${fileName}`;
  console.log(fileName);
}

function handleFileUpload(event) {
  event.preventDefault();
  const fileInput = document.getElementById('fileInput');
  const filePath = fileInput.value;

  if (fileInput.files.length === 0) {
    alert("Для продолжения выберите файл");
    return;
  }

  // Проверка расширения файла
  const allowedExtensions = /(\.docx|\.doc)$/i;
  if (!allowedExtensions.exec(filePath)) {
      alert('Пожалуйста, загрузите файл формата .docx или .doc');
      return false;
  }

  window.location.href = 'settings.html';
}

function examinationFile() {
    window.location.href = 'downloadFile.html';
    return false;
}

function updateFileName() {
    const fileInput = document.getElementById('fileInput');
    const fileName = document.getElementById('fileName');
    fileName.textContent = `Ваш файл: ${fileInput.files[0].name}`;
}

var template_id = 0;
let operationId = null;

function handleFileUpload(event) {
    const formData = new FormData();
    const fileInput = document.getElementById('fileInput');
    const templateId = document.getElementById('templateId').value;
    const processingFile = document.getElementById('processing-file');
    

    formData.append('file', fileInput.files[0]);
    formData.append('template_id', templateId);
    
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const downloadContainer = document.getElementById('downloadContainer');

    progressContainer.style.display = 'block';
    progressBar.value = 0;
    progressText.textContent = '0%';
    processingFile.style.display = 'block';

    const xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://localhost:3000/files/upload', true);
    xhr.setRequestHeader('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXUyJ9.eyJleHAiOjE3NDgxOTEzOTAsImlzcyI6ImF1dGhfc2VydmlzIiwic3ViIjoiSGVybyIsInVzZXJuYW1lIjoiSGVybyJ9.IMQ9EXuF2Hu8_K-ami8Odm2SzKZIjBCMsBuISnUaAFc');

    xhr.upload.onprogress = function(event) {
        if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            progressBar.value = percentComplete;
            progressText.textContent = Math.round(percentComplete) + '%';
        }
    };

    xhr.onload = function() {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            operationId = response.operation_id;
            downloadContainer.style.display = 'block';
        } else {
            console.error('Ошибка при загрузке файла:', xhr.statusText);
        }
    };

    xhr.send(formData);
}

function downloadFile() {
    if (operationId) {
        const downloadUrl = `http://localhost:3000/files/download/${operationId}`;
        console.log('Download URL:', downloadUrl); // Выводим URL для отладки

        fetch(downloadUrl, {
            method: 'GET',
            headers: {
                'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXUyJ9.eyJleHAiOjE3NDgxOTEzOTAsImlzcyI6ImF1dGhfc2VydmlzIiwic3ViIjoiSGVybyIsInVzZXJuYW1lIjoiSGVybyJ9.IMQ9EXuF2Hu8_K-ami8Odm2SzKZIjBCMsBuISnUaAFc'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка при скачивании файла');
            }
            return response.blob(); // Получаем файл как Blob
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob); // Создаем URL для Blob
            const a = document.createElement('a'); // Создаем элемент <a>
            a.style.display = 'none';
            a.href = url;
            a.download = `downloaded_file_${operationId}.docx`; // Указываем имя файла
            document.body.appendChild(a); // Добавляем элемент в DOM
            a.click(); // Инициируем скачивание
            window.URL.revokeObjectURL(url); // Освобождаем память
            document.body.removeChild(a); // Удаляем элемент из DOM
        })
        .catch(error => {
            console.error('Ошибка при скачивании файла:', error);
        });
    } else {
        alert('Сначала загрузите файл.');
    }
}



function createNewTemplate() {
    const templateMessage = document.getElementById('templateMessage');
    const createTemplateButton = document.getElementById('createTemplateButton');

    // Логика для создания нового шаблона
    templateMessage.textContent = "Создание нового шаблона...";
    createTemplateButton.style.display = 'none'; // Скрыть кнопку
}

function handleDropdownChange(selectElement, iter) {
    const selectedValue = selectElement.options[selectElement.selectedIndex].text;
    const selectId = selectElement.id;

    let title = '';
    let description = '';

    if ((selectId === 'font-name')||(selectId === 'font-name-table')||(selectId === 'font-name-figureCaption')||(selectId === 'font-name-list')) {
        title = 'Шрифт';
        description = `Шрифт определяет стиль текста, который используется в документе. Выбор шрифта может повлиять на читаемость и общее восприятие текста.`;
    } else if ((selectId === 'font-size')||(selectId === 'font-size-table')||(selectId === 'font-size-figureCaption')||(selectId === 'font-size-list')) {
        title = 'Размер шрифта';
        description = `Размер шрифта указывает, насколько крупным или мелким будет текст. Обычно размер шрифта измеряется в пунктах (pt).`;
    } else if ((selectId === 'line-spacing')||(selectId === 'line-spacing-table')||(selectId === 'line-spacing-figureCaption')||(selectId === 'line-spacing-list')) {
        title = 'Междустрочный интервал';
        description = `Междустрочный интервал определяет расстояние между строками текста.`;
    } else if ((selectId === 'first-line-indent')||(selectId === 'first-line-indent-table')||(selectId === 'first-line-indent-figureCaption')||(selectId === 'first-line-indent-listLevel1')||(selectId === 'first-line-indent-listLevel2')) {
        title = 'Абзацный отступ';
        description = `Абзацный отступ определяет расстояние между началом абзаца и левым краем страницы. Это помогает структурировать текст и делает его более удобным для восприятия.`;
    } else if ((selectId === 'alignment')||(selectId === 'alignment-table')||(selectId === 'alignment-figureCaption')||(selectId === 'alignment-list')) {
        title = 'Выравнивание';
        description = `Выравнивание текста определяет, как текст будет располагаться на странице. Возможные варианты включают выравнивание по левому краю, по центру, по правому краю и по ширине. Правильное выравнивание помогает создать аккуратный и профессиональный вид документа.`;
    } 
    if (iter === 0) {
        document.getElementById('selectedTitle').innerText = title;
        document.getElementById('description').innerText = description;
    } else if (iter === 1) {
        document.getElementById('selectedTitle-table').innerText = title;
        document.getElementById('description-table').innerText = description;
    } else if (iter === 2) {
        document.getElementById('selectedTitle-figureCaption').innerText = title;
        document.getElementById('description-figureCaption').innerText = description;
    } else if (iter === 3) {
        document.getElementById('selectedTitle-list').innerText = title;
        document.getElementById('description-list').innerText = description;
    }
    
}


function sendData() {
    const jsonData = {
        "name": document.getElementById('name-input').value,
        "filters": {
            "body_text": {
                "font_name": [document.getElementById('font-name').value],
                "font_size": [parseFloat(document.getElementById('font-size').value)],
                "alignment": [document.getElementById('alignment').value],
                "first_line_indent": parseFloat(document.getElementById('first-line-indent').value),
                "line_spacing": parseFloat(document.getElementById('line-spacing').value)
            },
            "table_caption": {
                "font_name": [document.getElementById('font-name-table').value],
                "font_size": [parseFloat(document.getElementById('font-size-table').value)],
                "alignment": [document.getElementById('alignment-table').value],
                "first_line_indent": parseFloat(document.getElementById('first-line-indent-table').value),
                "line_spacing": parseFloat(document.getElementById('line-spacing-table').value)
            },
            "figure_caption": {
                "font_name": [document.getElementById('font-name-figureCaption').value],
                "font_size": [parseFloat(document.getElementById('font-size-figureCaption').value)],
                "alignment": [document.getElementById('alignment-figureCaption').value],
                "first_line_indent": parseFloat(document.getElementById('first-line-indent-figureCaption').value),
                "line_spacing": parseFloat(document.getElementById('line-spacing-figureCaption').value)
            },
            "list_level_1": {
                "font_name": [document.getElementById('font-name-list').value],
                "font_size": [parseFloat(document.getElementById('font-size-list').value)],
                "alignment": [document.getElementById('alignment-list').value],
                "first_line_indent": parseFloat(document.getElementById('first-line-indent-listLevel1').value)
            },
            "list_level_2": {
                "font_name": [document.getElementById('font-name-list').value],
                "font_size": [parseFloat(document.getElementById('font-size-list').value)],
                "alignment": [document.getElementById('alignment-list').value],
                "first_line_indent": parseFloat(document.getElementById('first-line-indent-listLevel2').value)
            }
        }
    };

    fetch('http://localhost:3000/templates/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXUyJ9.eyJleHAiOjE3NDgxOTEzOTAsImlzcyI6ImF1dGhfc2VydmlzIiwic3ViIjoiSGVybyIsInVzZXJuYW1lIjoiSGVybyJ9.IMQ9EXuF2Hu8_K-ami8Odm2SzKZIjBCMsBuISnUaAFc'
        },
        body: JSON.stringify(jsonData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Гуд:', data);
    })
    .catch((error) => {
        console.error('Не гуд:', error);
    });
    
    window.alert("Ваш шаблон с именем «" + jsonData.name + "» создан");
    
    const data = response.json();
    template_id = data.id;
}

function choiceSample(){
    window.location.href = 'sample.html';
}

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM полностью загружен");
    fetchTemplates();
});

async function fetchTemplates() {
    
    console.log("fetchTemplates вызвана");
    try {
        const response = await fetch('http://localhost:3000/templates/', {
            method: 'GET',
            headers: {
                'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXUyJ9.eyJleHAiOjE3NDgxOTEzOTAsImlzcyI6ImF1dGhfc2VydmlzIiwic3ViIjoiSGVybyIsInVzZXJuYW1lIjoiSGVybyJ9.IMQ9EXuF2Hu8_K-ami8Odm2SzKZIjBCMsBuISnUaAFc'
            }
        });

        if (!response.ok) {
            throw new Error('Ошибка при получении шаблонов');
        }

        const templates = await response.json();
        console.log('Полученные шаблоны:', templates);
        displayTemplates(templates);
    } catch (error) {
        console.error('Не удалось получить шаблоны:', error);
    }
}




async function deleteFile(templateId) {
    if (confirm('Вы уверены, что хотите удалить этот файл?')) {
        try {
            const response = await fetch(`http://localhost:3000/templates/${templateId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXUyJ9.eyJleHAiOjE3NDgxOTEzOTAsImlzcyI6ImF1dGhfc2VydmlzIiwic3ViIjoiSGVybyIsInVzZXJuYW1lIjoiSGVybyJ9.IMQ9EXuF2Hu8_K-ami8Odm2SzKZIjBCMsBuISnUaAFc'
                }
            });

            if (!response.ok) {
                throw new Error('Ошибка при удалении файла');
            }

            const data = await response.json();
            console.log('Файл удален:', data);
            alert('Файл успешно удален!');
            location.reload();
            // Здесь можно обновить интерфейс, чтобы удалить элемент из DOM
        } catch (error) {
            console.error('Ошибка при удалении файла:', error);
            alert('Не удалось удалить файл.');
        }
    }
}

function displayTemplates(templates) {
    const container = document.getElementById('button-new');
    //container.innerHTML = ''; // Очищаем контейнер перед добавлением новых блоков

    templates.forEach(template => {
        // Контейнер для кнопок
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'template-display__button-container';

        // Кнопка для шаблона
        const button = document.createElement('button');
        button.className = 'button-new';
        button.textContent = template.name;
        button.onclick = () => {
            hrefFuncSample(template.id);
            console.log(`Вы выбрали шаблон с ID: ${template.id}`);
        };

        // Дополнительные кнопки
        const updateButton = document.createElement('button');
        updateButton.className = 'button-update button-container';
        updateButton.innerHTML = '&#9997;';

        const deleteButton = document.createElement('button');
        deleteButton.className = 'button-delete button-container';
        deleteButton.setAttribute('data-template-id', template.id); // Устанавливаем правильный template_id
        deleteButton.onclick = function() {
            deleteFile(template.id); // Передаем template_id в функцию
        };
        deleteButton.innerHTML = '&#128465;';

        // Добавление кнопок в контейнер
        buttonContainer.appendChild(button);
        buttonContainer.appendChild(updateButton);
        buttonContainer.appendChild(deleteButton);

        // Добавление контейнера с кнопками в основной контейнер
        container.appendChild(buttonContainer);
    });
}




