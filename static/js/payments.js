import {tablePaginator, buttonsPaginator} from './paginator.js';

// recogemos los botones del paginador de la tabla "VPS + COPYTRADING"
let PaginatorButtons = document.querySelectorAll('.link-page');
PaginatorButtons.forEach(function (currentValue, currentIndex) {

    currentValue.addEventListener('click', () => {
        const origin = window.location.origin;
        const pathname = window.location.pathname;
        const url = origin + pathname;
        const url_payment = origin + '/renewal-payment/';
        // Hacemos una petición GET al servidor para traer los datos de la tabla "VPS + COPYTRADING"
        fetch(url + "?page=" + currentValue.value)
            .then(response => response.json())
            .then(function (data) {
                // Tomamos los datos para actualizar la tabla
                const payments = data.vps_payments;
                const total_pages = data.total_pages;
                //Tomamos las filas a modificar
                const row_list = document.querySelectorAll('.rows-vps-payment');
                // Hacemos la paginación a la tabla de ganancias semanales con una funcion
                tablePaginator(payments, row_list, url_payment);
                buttonsPaginator(PaginatorButtons, currentIndex, total_pages);
            });
    });
});


// recogemos los botones del paginador de la tabla "GESTION DE CUENTAS MT5"
let PaginatorButtons2 = document.querySelectorAll('.link-page2');
PaginatorButtons2.forEach(function (currentValue, currentIndex) {

    currentValue.addEventListener('click', () => {
        const origin = window.location.origin;
        const pathname = window.location.pathname;
        const url = origin + pathname;
        const url_payment = origin + '/trader-payment/';
        // Hacemos una petición GET al servidor para traer los datos de la tabla "GESTION DE CUENTAS MT5"
        fetch(url + "?page2=" + currentValue.value)
            .then(response => response.json())
            .then(function (data) {
                // Tomamos los datos para actualizar la tabla
                const payments = data.trader_payments;
                const total_pages = data.total_pages;
                //Tomamos las filas a modificar
                const row_list = document.querySelectorAll('.rows-trader-payment');
                // Hacemos la paginación a la tabla de ganancias semanales con una funcion
                tablePaginator(payments, row_list, url_payment);
                buttonsPaginator(PaginatorButtons2, currentIndex, total_pages);
            });
    });
});
