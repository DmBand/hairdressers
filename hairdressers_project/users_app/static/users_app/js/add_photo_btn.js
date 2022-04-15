'use strict'


// Кнопка добавления файлов в портфолио
const submitBtn = document.querySelector('.portf-btn-sumbit');
const btnWrapper = document.querySelector('.input__file-button');
const text = document.querySelector('.input__file-button-text');


let inputs = document.querySelectorAll('.input__file');
        Array.prototype.forEach.call(inputs, function (input) {
            let label = input.nextElementSibling,
            labelVal = label.querySelector('.input__file-button-text').innerText;

            input.addEventListener('change', function (e) {
                let countFiles = '';
                if (this.files && this.files.length >= 1)
                    countFiles = this.files.length;

                if (countFiles) {
                    if (countFiles > 20) {
                        text.classList.add('red-text');
                        label.querySelector('.input__file-button-text').innerText = 'Не более 20 файлов за раз (' + countFiles + ')' ;
                        submitBtn.classList.add('none-class');
                        btnWrapper.classList.add('add-width')
                    } else {
                        label.querySelector('.input__file-button-text').innerText = 'Выбрано файлов: ' + countFiles;
                        if (submitBtn.classList.contains('none-class')) {
                            submitBtn.classList.remove('none-class');
                            text.classList.remove('red-text');
                            btnWrapper.classList.remove('add-width')
                        }
                    }
                }
                else
                    label.querySelector('.input__file-button-text').innerText = labelVal;
            });
        });


