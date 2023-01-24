const InputRadioPaypal = document.getElementById('paypal');
const InputsRadioStripe = document.getElementById('stripe');
const LabelRadioPaypal = document.querySelector('.label-radio-paypal');
const LabelRadioStripe = document.querySelector('.label-radio-stripe');

//resaltar el metodo de pago de Paypal si esta seleccionado.
LabelRadioPaypal.addEventListener("click", ()=> {
    if (InputRadioPaypal.checked) {
        LabelRadioPaypal.classList.add('input-radio-checked');

        let stripe_checked = LabelRadioStripe.classList.contains('input-radio-checked')
        if (stripe_checked) {
            LabelRadioStripe.classList.remove('input-radio-checked');
        };
    };
});

//resaltar el metodo de pago de Stripe si esta seleccionado.
LabelRadioStripe.addEventListener("click", ()=> {
    if (InputsRadioStripe.checked) {
        LabelRadioStripe.classList.add('input-radio-checked');

        let paypal_checked = LabelRadioStripe.classList.contains('input-radio-checked')
        if (paypal_checked) {
            LabelRadioPaypal.classList.remove('input-radio-checked');
        };
    };
});
