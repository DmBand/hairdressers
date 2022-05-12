'use strict'


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


