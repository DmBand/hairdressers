'use strict'


const loginBtn = document.querySelector(".login-name");
const profileBtns = document.querySelector(".profile-logout");

function addMenu() {
    profileBtns.classList.toggle("no-menu");
}

loginBtn.addEventListener('click', addMenu)