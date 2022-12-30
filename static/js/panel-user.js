import {tablePaginator, buttonsPaginator} from './paginator.js'

/* Logica de botones de Modal para agregar la cuenta mt5 del usuario */
const modalAdd = document.getElementById("modal-add");
const modalButtonOpen = document.querySelector('.open-modal-add');
const modalButtonClose = document.querySelector('.close-modal-add');
const ButtonSendModal = document.querySelector('.button-send-modal');
/* Inputs a verificar para cargar el loader */
const modalLoader = document.querySelector('.box-loader');
const inputUser = document.getElementById('id_login');
const inputPassword = document.getElementById('id_password');
const inputServer = document.getElementById('id_server');

if (modalButtonOpen != null ) {
    modalButtonOpen.addEventListener("click", () => {
        modalAdd.showModal();
    })
    modalButtonClose.addEventListener("click", () => {
        modalAdd.close();
    })

    /* Desactivar el boton de "agregar" cuando le de el primer click para no enviar mas solicitudes. */
    ButtonSendModal.addEventListener("click", () => {
        if (inputUser.value.length > 0 && inputPassword.value.length > 0 && inputServer.value.length > 0) {
            modalAdd.close();
            modalLoader.style.display = 'flex';
        }
    });
}


/* Logica de botones de modal para avisar que los botones de agregar y borrar cuenta mt5 solo estan habilitados en tiempo 
        determinado */
const modalMessage = document.getElementById("modal-message");
const modalOpen = document.querySelector('.open-modal-message');
const modalClose = document.querySelector('.close-modal-message');


if (modalOpen != null ) {
    modalOpen.addEventListener("click", () => {
        modalMessage.showModal();
    })
    modalClose.addEventListener("click", () => {
        modalMessage.close();
    })
}


// recogemos los botones del paginador de la tabla "Ganancias Semanales"
let PaginatorButtons = document.querySelectorAll('.page');
PaginatorButtons.forEach(function (currentValue, currentIndex) {

    currentValue.addEventListener('click', () => {
        const url = window.location.href
        // Hacemos una petición GET al servidor para traer los datos de la tabla "ganancias semanales"
        // La info de url para las peticiones esta la app vps en en la vista PanelUserView en django
        fetch(url + "?page=" + currentValue.value)
            .then(response => response.json())
            .then(function (data) {
                // Tomamos los datos para actualizar la tabla
                const profits = data.profits;
                const total_pages = data.total_pages;
                //Tomamos las filas a modificar
                const row_list = document.querySelectorAll('.tr-profits');
                // Hacemos la paginación a la tabla de ganancias semanales con una funcion
                tablePaginator(profits, row_list);
                buttonsPaginator(PaginatorButtons, currentIndex, total_pages);
            });
    });
});


// recogemos los botones del paginador de la tabla "Historial de operaciones de la cuenta madre"
let PaginatorButtons2 = document.querySelectorAll('.page2');
PaginatorButtons2.forEach(function (currentValue, currentIndex) {

    currentValue.addEventListener('click', () => {
        const url = window.location.href
        // Hacemos una petición GET al servidor para traer los datos de la tabla "Historial de operaciones de la cuenta madre"
        // La info de url para las peticiones esta la app vps en en la vista PanelUserView en django
        fetch(url + "?page2=" + currentValue.value)
            .then(response => response.json())
            .then(function (data) {
                // Tomamos los datos para actualizar la tabla
                const operations = data.operations;
                const total_pages = data.total_pages;
                // Corrigiendo el formato de las fechas en las filas
                operations.forEach(function (currentValue) {
                    const open_time = currentValue['open_time']
                    currentValue['open_time'] = open_time.replace('T', ' ')
                    const time = currentValue['time']
                    currentValue['time'] = time.replace('T', ' ')
                })
                //Tomamos las filas a modificar
                const row_list2 = document.querySelectorAll('.tr-operation');
                // Hacemos la paginación a la tabla de Historial de cuenta madre con una funcion
                tablePaginator(operations, row_list2);
                buttonsPaginator(PaginatorButtons2, currentIndex, total_pages);
            });
    });
});


// recogemos los botones del paginador de la tabla "Operaciones de la cuenta mt5 del usuario"
let PaginatorButtons3 = document.querySelectorAll('.page3');
PaginatorButtons3.forEach(function (currentValue, currentIndex) {

    currentValue.addEventListener('click', () => {
        const url = window.location.href
        // Hacemos una petición GET al servidor para traer los datos de la tabla "Operaciones en la semana actual"
        // La info de url para las peticiones esta la app vps en en la vista PanelUserView en django
        fetch(url + "?page3=" + currentValue.value)
            .then(response => response.json())
            .then(function (data) {
                // Tomamos los datos para actualizar la tabla
                const operations = data.operations2;
                const total_pages = data.total_pages;
                console.log(operations);
                // Corrigiendo el formato de las fechas en las filas
                operations.forEach(function (currentValue) {
                    let open_time = currentValue['open_time']
                    open_time = open_time.replace('T', ' ')
                    currentValue['open_time'] = open_time.replace('Z', '')
                    let close_time = currentValue['close_time']
                    close_time = close_time.replace('T', ' ')
                    currentValue['close_time'] = close_time.replace('Z', ' ')
                })
                //Tomamos las filas a modificar
                const row_list3 = document.querySelectorAll('.tr-operation2');
                // Hacemos la paginación a la tabla de Historial de operaciones de la cuenta mt5 del usuario con una funcion.
                tablePaginator(operations, row_list3);
                buttonsPaginator(PaginatorButtons3, currentIndex, total_pages);
            });
    });
});