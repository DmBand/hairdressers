'use strict'


// Кнопка очистки портфолио
const delPortf = document.querySelector(".del-photo-text");
const divYesNo = document.querySelector(".yes-no-container");
const btnYes = document.getElementById('yes-reset');

function confirmReset() {
    delPortf.classList.toggle('active');
    if (delPortf.classList.contains('active')) {
        delPortf.innerText = 'Удалить все фото?'
        btnYes.classList.add('yes-reset');
        btnYes.innerText = 'Да';

        const btnNo = document.createElement('div');
        btnNo.classList.add('no-reset');
        btnNo.innerText = 'Нет'
        divYesNo.append(btnYes);
        divYesNo.append(btnNo);

        btnNo.addEventListener('click', confirmReset);

    } else {
            const btnNo = document.querySelector('.no-reset');
            btnNo.remove();

            btnYes.classList.remove('yes-reset');
            btnYes.innerText = '';

            delPortf.innerText = 'Удалить все фото';
    }
}

delPortf.addEventListener('click', confirmReset)