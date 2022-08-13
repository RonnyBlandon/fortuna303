alert("Hola Mundo");

const menu_list = document.querySelector(".menu__list");
const botonMenuBars = document.querySelector(".menu__btn-bars");

botonMenuBars.addEventListener("click", ()=>{
    menu_list.classList.toggle("menu__list-toggle");
});