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