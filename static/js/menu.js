// Funcion para el boton de menu responsivo 

const menu_list = document.querySelector(".menu__list");
const botonMenuBars = document.querySelector(".menu__btn-bars");

botonMenuBars.addEventListener("click", ()=>{
    menu_list.classList.toggle("menu__list-toggle");
});

// Funcion de menu de usuario para dispositvios moviles
const menu_user = document.querySelector(".menu__user");
const botonMenuUser = document.querySelector(".menu__btn-profile");

botonMenuUser.addEventListener("click", ()=>{
    menu_user.classList.toggle("menu__list-toggle");
});
