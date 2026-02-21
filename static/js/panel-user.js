import {tablePaginator, buttonsPaginator} from './paginator.js'

const modalAdd = document.getElementById("modal-add");
const modalButtonOpen = document.querySelector('.open-modal-add');
const modalButtonClose = document.querySelector('.close-modal-add');
const buttonSendModal = document.querySelector('.button-send-modal');
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

    buttonSendModal.addEventListener("click", () => {
        if (inputUser.value.length > 0 && inputPassword.value.length > 0 && inputServer.value.length > 0) {
            modalAdd.close();
            modalLoader.style.display = 'flex';
        }
    });
}


const btnLoaderReconnect = document.querySelector('.btn-reconnect');
if (btnLoaderReconnect) {
    btnLoaderReconnect.addEventListener("click", () => {
        modalLoader.style.display = 'flex';
    });
}


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


let PaginatorButtons = document.querySelectorAll('.page');
PaginatorButtons.forEach(function (currentValue, currentIndex) {

    currentValue.addEventListener('click', () => {
        const origin = window.location.origin;
        const pathname = window.location.pathname;
        const url = origin + pathname;
        
        fetch(url + "?page=" + currentValue.value)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error de red: ' + response.status);
                }
                return response.json();
            })
            .then(function (data) {
                const profits = data.profits;
                const total_pages = data.total_pages;
                const row_list = document.querySelectorAll('.tr-profits');
                tablePaginator(profits, row_list);
                buttonsPaginator(PaginatorButtons, currentIndex, total_pages);
            })
            .catch(function(error) {
                console.error('Error en paginador Ganancias Semanales:', error);
            });
    });
});


let PaginatorButtons2 = document.querySelectorAll('.page2');
PaginatorButtons2.forEach(function (currentValue, currentIndex) {

    currentValue.addEventListener('click', () => {
        const origin = window.location.origin;
        const pathname = window.location.pathname;
        const url = origin + pathname;
        
        fetch(url + "?page2=" + currentValue.value)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error de red: ' + response.status);
                }
                return response.json();
            })
            .then(function (data) {
                const operations = data.operations;
                const total_pages = data.total_pages;
                
                if (operations && operations.length > 0) {
                    operations.forEach(function (currentValue) {
                        const open_time = currentValue['open_time'];
                        if (open_time) {
                            currentValue['open_time'] = open_time.replace('T', ' ');
                        }
                        const time = currentValue['time'];
                        if (time) {
                            currentValue['time'] = time.replace('T', ' ');
                        }
                    });
                }
                
                const row_list2 = document.querySelectorAll('.tr-operation');
                tablePaginator(operations, row_list2);
                buttonsPaginator(PaginatorButtons2, currentIndex, total_pages);
            })
            .catch(function(error) {
                console.error('Error en paginador Historial Cuenta Madre:', error);
            });
    });
});


let PaginatorButtons3 = document.querySelectorAll('.page3');
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
                const operations = data.operations2;
                const total_pages = data.total_pages;
                
                if (operations && operations.length > 0) {
                    operations.forEach(function (currentValue) {
                        let open_time = currentValue['open_time'];
                        if (open_time) {
                            open_time = open_time.replace('T', ' ');
                            currentValue['open_time'] = open_time.replace('Z', '');
                        }
                        let close_time = currentValue['close_time'];
                        if (close_time) {
                            close_time = close_time.replace('T', ' ');
                            currentValue['close_time'] = close_time.replace('Z', '');
                        }
                    });
                }
                
                const row_list3 = document.querySelectorAll('.tr-operation2');
                tablePaginator(operations, row_list3);
                buttonsPaginator(PaginatorButtons3, currentIndex, total_pages);
            })
            .catch(function(error) {
                console.error('Error en paginador Operaciones Cuenta MT5:', error);
            });
    });
});
