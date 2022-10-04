/* Logica de botones de Modal para agregar la cuenta mt5 del usuario */
const modalAdd = document.getElementById("modal-add");
const modalButtonOpen = document.querySelector('.open-modal-add');
const modalButtonClose = document.querySelector('.close-modal-add');
const ButtonSendModal = document.querySelector('.button-send-modal');

if (modalButtonOpen != null) {
    modalButtonOpen.addEventListener("click", () => {
        modalAdd.showModal();
    })
}

modalButtonClose.addEventListener("click", () => {
    modalAdd.close();
})


/* Desactivar el boton de "agregar" cuando le de el primer click */
let is_disabled = false;
ButtonSendModal.addEventListener("click", () => {
    if (is_disabled === true) {
        ButtonSendModal.setAttribute("disabled", "");
    }
    else {
        is_disabled = true;
    }
});


/*Función para paginar las tablas de la pagina panel de usuario. La función recibe la clase de las filas de
las tablas a paginar tambien las clases de los botones de pagina siguiente o anterior y la lista de objetos
con los datos a actualizar en cada fila*/
function tablesPaginator(data, button_list, button_index, rows) {
    /*ACTUALIZAMOS LAS FILAS DE LA TABLA*/
    /* Verificamos si hay filas sobrantes para ocultarlas y agregar los datos a los no sobrantes */
    if (rows.length > data.length) {
        // Escondemos las filas sobrantes
        let leftover_rows = rows.length - data.length;
        for (let row = 0; row < leftover_rows; row++) {
            rows[row + data.length].setAttribute('hidden', 'true');
        };

        // Agregamos la nueva data a las celdas de las filas que estan visibles 
        for (let row2 = 0; row2 < data.length; row2++) {
            let childs = rows[row2].children;
            let keys = Object.keys(data[row2]);

            for (let i = 0; i < keys.length; i++) {
                let key = keys[i];
                childs[i].innerHTML = data[row2][key];
            };
        };
    }
    else {
        // En caso de que no hay filas sobrantes tomamos las filas que hay y agregamos los datos a cada celda
        counter_row = 0;
        rows.forEach(function (currentValue) {
            currentValue.removeAttribute('hidden')
            let childs = currentValue.children;
            let keys = Object.keys(data[counter_row]);//Tomamos las claves del objeto (dict en python)

            for (let i = 0; i < keys.length; i++) {
                let key = keys[i];
                childs[i].innerHTML = data[counter_row][key];
            };

            if (counter_row < data.length) {
                counter_row++;
            };
        })
    };

    /*YA QUE ACTUALIZAMOS LOS DATOS DE LA TABLA ACTUALIZAMOS LOS BOTONES DEL PAGINADOR*/
    //Limpiamos los botones del paginador quitando la clase de la pagina actual
    for (let button=0; button<button_list.length; button++) {
        button_list[button].classList.remove('link-page-current')
    }
    // Agregamos la clase al boton con la pagina actual en el paginador
    let button_value = button_list[button_index].value; // Guardamos en una variable el value del boton seleccionado
    if (button_value == button_list[button_index].innerHTML) {
        if (button_list[button_index].classList.contains('link-page-current')) {
            //PASS
        } else {
            button_list[button_index].classList.add('link-page-current');
        }
    } else {
        button_list[button_value].classList.add('link-page-current');
    }

    //Actualizamos el atributo value de los botones anterior y siguiente en el paginador
    let buttonPrevious = button_list[0]; //Tomamos el boton de pagina anterior
    let buttonNext = button_list[button_list.length - 1];//Tomamos el boton de pagina siguiente
    let last_page = button_list.length - 2; //sacamos la ultima pagina del paginador
    button_value = parseInt(button_value); //convertimos a entero el value del boton actual
    switch (button_value) {
        case 1:
            buttonPrevious.setAttribute('value', '1')
            buttonNext.setAttribute('value', parseInt(button_list[button_index].value) + 1);
            break;

        case last_page:
            buttonPrevious.setAttribute('value', parseInt(button_list[button_index].value) - 1);
            buttonNext.setAttribute('value', last_page);
            break;

        default:
            buttonNext.setAttribute('value', button_value + 1);
            buttonPrevious.setAttribute('value', button_value - 1);
            break;
    }
}


// recogemos los botones del paginador de la tabla "Ganancias Semanales"
let PaginatorButtons = document.querySelectorAll('.link-page');
PaginatorButtons.forEach(function (currentValue, currentIndex) {

    currentValue.addEventListener('click', () => {

        // Hacemos una petición GET al servidor para traer los datos de la tabla "ganancias semanales"
        // La info de url para las peticiones esta la app vps en en la vista PanelUserView en django
        fetch("http://127.0.0.1:8000/panel-user/?page=" + currentValue.value)
            .then(response => response.json())
            .then(function (data) {
                // Tomamos los datos para actualizar la tabla
                profits = data.profits;
                //Tomamos las filas a modificar
                const row_list = document.querySelectorAll('.tr-profits');
                // Hacemos la paginación a la tabla de ganancias semanales con una funcion
                tablesPaginator(profits, PaginatorButtons, currentIndex, row_list)
            });
    });
});


// recogemos los botones del paginador de la tabla "Ganancias Semanales"
let PaginatorButtons2 = document.querySelectorAll('.link-page2');
PaginatorButtons2.forEach(function (currentValue, currentIndex) {

    currentValue.addEventListener('click', () => {

        // Hacemos una petición GET al servidor para traer los datos de la tabla "ganancias semanales"
        // La info de url para las peticiones esta la app vps en en la vista PanelUserView en django
        fetch("http://127.0.0.1:8000/panel-user/?page2=" + currentValue.value)
            .then(response => response.json())
            .then(function (data) {
                // Tomamos los datos para actualizar la tabla
                operations = data.operations;
                console.log(operations)
                //Tomamos las filas a modificar
                const row_list2 = document.querySelectorAll('.tr-operation');
                // Hacemos la paginación a la tabla de ganancias semanales con una funcion
                tablesPaginator(operations, PaginatorButtons2, currentIndex, row_list2)
            });
    });
});
