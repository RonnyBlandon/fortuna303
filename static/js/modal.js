/* Modal para agregar la cuenta mt5 del usuario */
const modalAdd = document.getElementById("modal-add");
const modalButtonOpen = document.querySelector('.open-modal-add');
const modalButtonClose = document.querySelector('.close-modal-add');
const ButtonSendModal = document.querySelector('.button-send-modal');


modalButtonOpen.addEventListener("click", ()=> {
    modalAdd.showModal();
})
    
modalButtonClose.addEventListener("click", ()=> {
    modalAdd.close();
})


let is_disabled = false;
ButtonSendModal.addEventListener("click", ()=> {
    if (is_disabled === true) {
        ButtonSendModal.setAttribute("disabled", "");
    }
    else {
        is_disabled = true;
    }
});
