import {buttonsPaginator} from './paginator.js';

const buttonAccordion = document.querySelector(".primary-details");
const buttonAccordion2 = document.querySelector(".primary-details-2");

/* Boton para desplegar el accordion de todas las facturas de Gestión de cuentas */
buttonAccordion.addEventListener("click", ()=> {
    const listaDetails = document.querySelectorAll(".details");

    const open = buttonAccordion.getAttribute('open');

    if (open == null) {
        listaDetails.forEach(function(currentValue, currentIndex, listObj) {
            currentValue.setAttribute("open", "true");
        })
    } else {
        listaDetails.forEach(function(currentValue) {
            currentValue.removeAttribute("open");
        })
    } 
});


/* Boton para desplegar el accordion todas las facturas vps y copytrading */
if (buttonAccordion2 != null) {
    buttonAccordion2.addEventListener("click", ()=> {
        const listaDetails = document.querySelectorAll(".details-2");
    
        const open = buttonAccordion2.getAttribute('open');
        
        if (open == null) {
            listaDetails.forEach(function(currentValue, currentIndex, listObj) {
                currentValue.setAttribute("open", "true");
            })
        } else {
            listaDetails.forEach(function(currentValue) {
                currentValue.removeAttribute("open");
            })
        } 
    });
}


export function detailPaginator(data, details, bloque, url_payment) {
    /*ACTUALIZAMOS LAS FILAS DE LA TABLA*/
    const clase = details[0].className; // guardamos la clase de la tabla details para saber cual tabla es.
    // Borramos los details para crear nuevos details con la nueva informacion recibida
    details.forEach(function (currentValue) {
        currentValue.remove();
    });
    
    for (let i=0; i<data.length; i++) {
        // creamos el detail
        let new_details = document.createElement('DETAILS');
        new_details.setAttribute('class', clase);

        // creamos los hijos directos de detail que son la etiqueta "summary" y "ul"
        let summary = document.createElement('SUMMARY');
        new_details.appendChild(summary);
        // creamos los hijos directos de la etiqueta summary
        let span = document.createElement('SPAN');
        span.innerHTML = data[i]['id'];
        summary.appendChild(span);
        
        if (data[i]['status'] === 'Pagar') {
            let enlace = document.createElement('A');
            enlace.setAttribute('class', 'btn-pay');
            enlace.setAttribute('href', url_payment + data[i]['id'] + '/');
            enlace.innerHTML = data[i]['status'];
            summary.appendChild(enlace);
        } else {
            let p = document.createElement('P');
            p.innerHTML = data[i]['status'];
            summary.appendChild(p);
        }

        let ul = document.createElement('UL');
        new_details.appendChild(ul);
        // creamos los hijos directos de la etiqueta ul
        for (let j=0; j<4; j++) {

            const li = document.createElement('LI');
            ul.appendChild(li);
            const h4 = document.createElement('H4');
            h4.setAttribute('class', 'title-celdas');
            li.appendChild(h4);
            const li_span = document.createElement('SPAN');
            li.appendChild(li_span);
            
            switch (j) {
                case 0:
                    h4.innerHTML = 'Fecha';
                    li_span.innerHTML = data[i]['created_date'];
                    break;
                case 1:
                    h4.innerHTML = 'Vencimiento';
                    li_span.innerHTML = data[i]['expiration'];
                    break;
                case 2:
                    if (data[i]['id_management_id']) {
                    h4.innerHTML = 'Id. Referencia';
                    li_span.innerHTML = data[i]['id_management_id'];
                    }
                    break;
                case 3:
                    h4.innerHTML = 'Total';
                    li_span.innerHTML = data[i]['total'];
                    break;
            }
        }

        bloque.appendChild(new_details);
        
    }
}


// recogemos los botones del paginador de la tabla en version mobile de "VPS + COPYTRADING"
let PaginatorButtons3 = document.querySelectorAll('.link-page3');
PaginatorButtons3.forEach(function (currentValue, currentIndex) {

    currentValue.addEventListener('click', () => {
        const origin = window.location.origin;
        const pathname = window.location.pathname;
        const url = origin + pathname;
        const url_payment = origin + '/renewal-payment/';
        // Hacemos una petición GET al servidor para traer los datos de la tabla "VPS + COPYTRADING" mobile
        fetch(url + "?page=" + currentValue.value)
            .then(response => response.json())
            .then(function (data) {
                // Tomamos los datos para actualizar la tabla
                const payments = data.vps_payments;
                const total_pages = data.total_pages;
                //Tomamos las filas a modificar
                const bloque = document.querySelector('.box-detail-2');
                const details_list = document.querySelectorAll('.details-2');
                // Hacemos la paginación a la tabla de ganancias semanales con una funcion
                detailPaginator(payments, details_list, bloque, url_payment);
                buttonsPaginator(PaginatorButtons3, currentIndex, total_pages);
            });
    });
});


// recogemos los botones del paginador de la tabla "GESTION DE CUENTAS MT5"
let PaginatorButtons4 = document.querySelectorAll('.link-page4');
PaginatorButtons4.forEach(function (currentValue, currentIndex) {

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
                const bloque = document.querySelector('.box-detail');
                const details_list = document.querySelectorAll('.details');
                // Hacemos la paginación a la tabla de ganancias semanales con una funcion
                detailPaginator(payments, details_list, bloque, url_payment);
                buttonsPaginator(PaginatorButtons4, currentIndex, total_pages);
            });
    });
});
