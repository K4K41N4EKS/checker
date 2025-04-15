/*const button = document.querySelector('.button')
const menu = document.querySelector('.menu')
const menuLinks = document.querySelectorAll('.menu-link')

button.addEventListener('click', (e) => {
  button.classList.toggle('active')

  if (button.classList.contains('active')) {
    button.setAttribute('aria-expanded', 'true')
    menu.setAttribute('aria-hidden', 'false')
    menuLinks.forEach(link => link.setAttribute('tabindex', '0'))
  } else {
    button.setAttribute('aria-expanded', 'false')
    menu.setAttribute('aria-hidden', 'true')
    menuLinks.forEach(link => link.setAttribute('tabindex', '-1'))
  }
})*/

function handleDropdownChange(dropdown) {
    const selectedValue = dropdown.value;
    console.log(`Выбор ${selectedValue}`);
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

function handleDropdownChange(selectElement) {
    const selectedValue = selectElement.options[selectElement.selectedIndex].text;
    const selectId = selectElement.id;

    let title = '';
    let description = '';

    if (selectId === 'font-name') {
        title = 'Шрифт';
        description = `Описание`;
    } else if (selectId === 'font-size') {
        title = 'Размер шрифта';
        description = `Описание`;
    } else if (selectId === 'line-spacing') {
        title = 'Междустрочный интервал';
        description = `Описание`;
    } else if (selectId === 'first-line-indent') {
        title = 'Абзацный отступ';
        description = `Описание`;
    } else if (selectId === 'page-margins') {
        title = 'Поля страницы';
        description = `Описание`;
    } else if (selectId === 'formatting-headings') {
        title = 'Форматирование заголовков';
        description = `Описание`;
    } else if (selectId === 'heading-position') {
        title = 'Расположение заголовков';
        description = `Описание`;
    } else if (selectId === 'numbering-tables-figures') {
        title = 'Нумерация таблиц и рисунков';
        description = `Описание`;
    } else if (selectId === 'page-numbering-format') {
        title = 'Формат нумерации страниц';
        description = `Описание`;
    } else if (selectId === 'contents-design') {
        title = 'Оформление оглавления';
        description = `Описание`;
    } else if (selectId === 'types-headlines') {
        title = 'Типы заголовков';
        description = `Описание`;
    }

    document.getElementById('selectedTitle').innerText = title;
    document.getElementById('description').innerText = description;
}

function sendData() {
    const selectedValue = parseFloat(document.getElementById('page-margins').value);
    let margins = {
        top: 0,
        bottom: 0,
        left: 0,
        right: 0
    };

    switch (selectedValue) {
        case 1: // Стандартные
            margins = {
                top: 2,
                bottom: 2,
                left: 3,
                right: 1.5
            };
            break;
        case 2: // Узкие
            margins = {
                top: 1.5,
                bottom: 1.5,
                left: 2,
                right: 1.5
            };
            break;
        case 3: // Широкие
            margins = {
                top: 2,
                bottom: 2,
                left: 4,
                right: 2
            };
            break;
        default:
            break;
    }
    
    const jsonData = {
        name: "NEW VERSION",
        filters: {
            start_after_heading: "Введение",
            margins: margins,
            required_headings: [
                "Введение",
                "Глава 1. Обзор литературы",
                "Глава 2. Практическая часть",
                "Заключение"
            ],
            styles: {
                "Normal": {
                    font_name: [document.getElementById('font-name').value],
                    font_size: [parseFloat(document.getElementById('font-size').value)],
                    bold: false,
                    italic: false,
                    underline: false,
                    all_caps: false,
                    alignment: "JUSTIFY",
                    line_spacing: parseFloat(document.getElementById('line-spacing').value),
                    first_line_indent: parseFloat(document.getElementById('first-line-indent').value)
                },
                "ListParagraph": {
                    first_line_indent: 0,
                    alignment: "JUSTIFY"
                },
                "ListParagraphLevel2": {
                    first_line_indent: 0.75,
                    alignment: "JUSTIFY"
                }
            }
        }
    };

    fetch('http://localhost:3000/templates/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + sessionStorage.getItem('access-token')
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
}

