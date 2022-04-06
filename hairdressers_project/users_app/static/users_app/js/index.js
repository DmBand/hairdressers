'use strict'

// Кнопка добавления файлов в портфолио

let inputs = document.querySelectorAll('.input__file');
        Array.prototype.forEach.call(inputs, function (input) {
            let label = input.nextElementSibling,
            labelVal = label.querySelector('.input__file-button-text').innerText;

            input.addEventListener('change', function (e) {
                let countFiles = '';
                if (this.files && this.files.length >= 1)
                    countFiles = this.files.length;

                if (countFiles)
                    label.querySelector('.input__file-button-text').innerText = 'Выбрано файлов: ' + countFiles;
                else
                    label.querySelector('.input__file-button-text').innerText = labelVal;
            });
        });

// Кнопка загрузки аватара
const upload = document.querySelector('#input__file2');
const result = document.querySelector('#result');

upload.addEventListener("change", (e) => {
    previewFunc(e.target.files[0]);
});

function previewFunc(file) {
    if (!file.type.match(/image.*/)) return false;
    const reader = new FileReader();

    reader.addEventListener("load", (e) => {
        const img = document.createElement('img');
        img.src = e.target.result;
        img.classList.add('result-avatar');
        result.innerHTML = '';
        result.append(img);
    });
    reader.readAsDataURL(file);
}