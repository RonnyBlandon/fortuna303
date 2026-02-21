export function tablePaginator(data, rows, url=null) {
    if (!data || data.length === 0) {
        rows.forEach(function(row) {
            row.setAttribute('hidden', 'true');
        });
        return;
    }

    rows.forEach(function (currentValue, index) {
        if (index < data.length) {
            currentValue.removeAttribute('hidden');
            let childs = currentValue.children;
            let keys = Object.keys(data[index]);
            
            for (let i = 0; i < keys.length && i < childs.length; i++) {
                let key = keys[i];
                if (data[index][key] === 'Pagar' && url) {
                    let enlace = document.createElement('A');
                    enlace.setAttribute('class', 'btn-pay');
                    enlace.setAttribute('href', url + data[index]['id'] + '/');
                    enlace.innerHTML = 'Pagar';
                    childs[i].innerHTML = '';
                    childs[i].appendChild(enlace);
                } else {
                    childs[i].innerHTML = data[index][key];
                }
            }
        } else {
            currentValue.setAttribute('hidden', 'true');
        }
    });
}


export function buttonsPaginator (button_list, button_index, total_pages) {
    if (!button_list || button_list.length === 0) {
        return;
    }

    let array_buttons = Array.from(button_list);
    let list_pages = array_buttons.slice(2, button_list.length - 2);
    
    if (list_pages.length === 0) {
        return;
    }

    for (let button = 0; button < button_list.length; button++) {
        button_list[button].classList.remove('link-page-current');
    }

    let button_value = parseInt(button_list[button_index].value);
    let button_innerHTML = button_list[button_index].innerHTML;
    let first_value_page = parseInt(list_pages[0].value);
    let last_value_page = parseInt(list_pages.at(-1).value);
    let last_page = parseInt(total_pages);

    if (isNaN(button_value)) {
        button_value = 1;
    }
    if (isNaN(last_page) || last_page < 1) {
        last_page = 1;
    }

    switch (button_innerHTML) {
        case "\u00AB":
        case "\u2039":
            if (button_value < first_value_page) {
                let new_innerHTML = button_value;
                for (let button = 0; button < list_pages.length; button++) {
                    list_pages[button].value = new_innerHTML;
                    list_pages[button].innerHTML = new_innerHTML;
                    new_innerHTML = new_innerHTML + 1;
                }
            }
            break;
        case "\u203A":
        case "\u00BB":
            if (button_value > total_pages) {
                button_value = total_pages;
            }
            if (button_value > last_value_page) {
                let new_innerHTML = button_value - list_pages.length + 1;
                for (let button = 0; button < list_pages.length; button++) {
                    list_pages[button].value = new_innerHTML;
                    list_pages[button].innerHTML = new_innerHTML;
                    new_innerHTML = new_innerHTML + 1;
                }
            }
            break;
    }

    for (let button = 0; button < button_list.length; button++) {
        if (button_value == button_list[button].innerHTML) {
            button_list[button].classList.add('link-page-current');
        }
    }

    let buttonFirst = button_list[0];
    let buttonPrevious = button_list[1];
    let buttonNext = button_list[button_list.length - 2];
    let buttonLast = button_list[button_list.length - 1];

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
