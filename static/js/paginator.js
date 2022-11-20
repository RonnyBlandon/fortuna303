/*Función para paginar las tablas de la pagina panel de usuario y el resto de paginas que tenga tablas
a paginar.*/
export function tablePaginator(data, rows, url=null) {
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
        let counter_row = 0;
        rows.forEach(function (currentValue) {
            currentValue.removeAttribute('hidden')
            let childs = currentValue.children;
            let keys = Object.keys(data[counter_row]);//Tomamos las claves del objeto (dict en python)
            
            for (let i = 0; i < keys.length; i++) {
                let key = keys[i];
                if (data[counter_row][key] === 'Pagar') {
                    let enlace = document.createElement('A');
                    enlace.setAttribute('class', 'btn-pay');
                    enlace.setAttribute('href', url + data[counter_row]['id'] + '/');
                    enlace.innerHTML = 'Pagar';
                    childs[i].innerHTML = '';
                    childs[i].appendChild(enlace);
                } else {
                    childs[i].innerHTML = data[counter_row][key];
                }
            };

            if (counter_row < data.length) {
                counter_row++;
            };
        })
    };
}


export function buttonsPaginator (button_list, button_index, total_pages) {
    /*YA QUE ACTUALIZAMOS LOS DATOS DE LA TABLA ACTUALIZAMOS LOS BOTONES DEL PAGINADOR*/
    // Guardamos en un array los botones que no sean los "«", "‹", "›", "»"
    let array_buttons = Array.from(button_list);
    let list_pages = array_buttons.slice(2, button_list.length - 2);
    //Limpiamos los botones del paginador quitando la clase de la pagina actual
    for (let button=0; button<button_list.length; button++) {
        button_list[button].classList.remove('link-page-current');
    }
    // Actualizamos los botones con numero de pagina en el paginador
    let button_value = parseInt(button_list[button_index].value); // Guardamos el value del boton seleccionado
    let button_innerHTML = button_list[button_index].innerHTML; // Guardamos el innerHTML del boton seleccionado
    let first_value_page = parseInt(list_pages[0].value);// guardamos el value del primer boton con pagina
    let last_value_page = parseInt(list_pages.at(-1).value);// guardamos el value del ultimo boton con pagina
    let last_page = parseInt(total_pages); // Guardamos la ultima pagina del paginador 
    switch (button_innerHTML) {
        case "«":
        case "‹":
            if (button_value < first_value_page) {
                let new_innerHTML = button_value;
                for (let button=0; button<list_pages.length; button++) {
                    list_pages[button].value = new_innerHTML
                    list_pages[button].innerHTML = new_innerHTML;
                    new_innerHTML = new_innerHTML + 1;
                }
            }
            break;
        case "›":
        case "»":
            if (button_value > total_pages) {
                button_value = total_pages;
            }
            if (button_value > last_value_page) {
                let new_innerHTML = button_value - list_pages.length;
                for (let button=0; button<list_pages.length; button++) {
                    new_innerHTML = new_innerHTML + 1;
                    list_pages[button].value = new_innerHTML
                    list_pages[button].innerHTML = new_innerHTML;
                }
            }
            break;
    }
    // Resaltamos el boton con la pagina actual
    for (let button=0; button<button_list.length; button++) {
        if (button_value == button_list[button].innerHTML) {
            button_list[button].classList.add('link-page-current');
        }
    }

    //Actualizamos los value de los cuatros botones de avanzar y retroceder en el paginador
    let buttonFirst = button_list[0]; //Guardamos el primer boton del paginador (<<)
    let buttonPrevious = button_list[1]; //Guardamos el boton de pagina anterior (<)
    let buttonNext = button_list[button_list.length - 2];//Guardamos el boton de pagina siguiente (>)
    let buttonLast = button_list[button_list.length - 1]; //Guardamos el ultimo boton del paginador (>>)
    switch (button_value) {
        case 1:
            buttonFirst.setAttribute('value', '1');
            buttonPrevious.setAttribute('value', '1');
            buttonNext.setAttribute('value', button_value + 1);
            buttonLast.setAttribute('value', button_value + list_pages.length);
            break;

        case last_page:
            buttonFirst.setAttribute('value', button_value - list_pages.length);
            if (button_value === list_pages.length) {
                buttonFirst.setAttribute('value', '1');
            }
            buttonPrevious.setAttribute('value', button_value - 1);
            buttonNext.setAttribute('value', last_page);
            buttonLast.setAttribute('value', last_page);
            break;

        default:
            buttonPrevious.setAttribute('value', button_value - 1);
            buttonNext.setAttribute('value', button_value + 1);
            if ((button_value - list_pages.length) <= 0) {
                buttonFirst.setAttribute('value', '1');
            } else {
                buttonFirst.setAttribute('value', button_value - list_pages.length);
            }

            if ((button_value + list_pages.length) >= last_page) {
                buttonLast.setAttribute('value', last_page);
            } else {
                buttonLast.setAttribute('value', button_value + list_pages.length);
            }
            break;
    }
}