import {tablePaginator, buttonsPaginator} from './paginator.js';

let PaginatorButtons = document.querySelectorAll('.link-page');
PaginatorButtons.forEach(function (currentValue, currentIndex) {
    currentValue.addEventListener('click', () => {
        const origin = window.location.origin;
        const pathname = window.location.pathname;
        const url = origin + pathname;
        const url_payment = origin + '/payment/renewal-vps/';
        
        fetch(url + "?page=" + currentValue.value)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error de red: ' + response.status);
                }
                return response.json();
            })
            .then(function (data) {
                const payments = data.vps_payments;
                const total_pages = data.total_pages;
                const row_list = document.querySelectorAll('.rows-vps-payment');
                tablePaginator(payments, row_list, url_payment);
                buttonsPaginator(PaginatorButtons, currentIndex, total_pages);
            })
            .catch(function(error) {
                console.error('Error en paginador VPS:', error);
            });
    });
});


let PaginatorButtons2 = document.querySelectorAll('.link-page2');
PaginatorButtons2.forEach(function (currentValue, currentIndex) {
    currentValue.addEventListener('click', () => {
        const origin = window.location.origin;
        const pathname = window.location.pathname;
        const url = origin + pathname;
        const url_payment = origin + '/payment/renewal-trader/';
        
        fetch(url + "?page2=" + currentValue.value)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error de red: ' + response.status);
                }
                return response.json();
            })
            .then(function (data) {
                const payments = data.trader_payments;
                const total_pages = data.total_pages;
                const row_list = document.querySelectorAll('.rows-trader-payment');
                tablePaginator(payments, row_list, url_payment);
                buttonsPaginator(PaginatorButtons2, currentIndex, total_pages);
            })
            .catch(function(error) {
                console.error('Error en paginador Gestion MT5:', error);
            });
    });
});


function tablePaginatorAdditional(data, rows) {
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
            childs[0].innerHTML = data[index]['id'];
            childs[1].innerHTML = data[index]['plan_type'];
            childs[2].innerHTML = data[index]['created_date'];
            childs[3].innerHTML = data[index]['expiration'];
            childs[4].innerHTML = '$' + data[index]['total'];
            
            if (data[index]['status'] === 'Pagar') {
                let paymentType = data[index]['payment_type'];
                let paymentId = data[index]['id'];
                let link = document.createElement('a');
                link.setAttribute('class', 'btn-pay');
                link.setAttribute('href', window.location.origin + '/payment/renewal-' + paymentType + '/' + paymentId + '/');
                link.innerHTML = 'Pagar';
                childs[5].innerHTML = '';
                childs[5].appendChild(link);
            } else {
                childs[5].innerHTML = data[index]['status'];
            }
        } else {
            currentValue.setAttribute('hidden', 'true');
        }
    });
}

let PaginatorButtons3 = document.querySelectorAll('.link-page6');
PaginatorButtons3.forEach(function (currentValue, currentIndex) {
    currentValue.addEventListener('click', () => {
        const origin = window.location.origin;
        const pathname = window.location.pathname;
        const url = origin + pathname;
        
        fetch(url + "?page3=" + currentValue.value)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error de red: ' + response.status);
                }
                return response.json();
            })
            .then(function (data) {
                const payments = data.additional_payments;
                const total_pages = data.total_pages;
                const row_list = document.querySelectorAll('.rows-additional-payment');
                tablePaginatorAdditional(payments, row_list);
                buttonsPaginator(PaginatorButtons3, currentIndex, total_pages);
            })
            .catch(function(error) {
                console.error('Error en paginador Planes Adicionales:', error);
            });
    });
});
