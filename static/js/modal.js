const modalAdd = document.getElementById("modal-add");
const modalButtonOpen = document.querySelector('.open-modal-add');
const modalButtonClose = document.querySelector('.close-modal-add');

modalButtonOpen.addEventListener("click", ()=> {
    modalAdd.showModal();
})

modalButtonClose.addEventListener("click", ()=> {
    modalAdd.close();
})
