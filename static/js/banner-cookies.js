const buttonAcceptCookies = document.getElementById('btn-accept-cookies');
const backgroundCookies = document.getElementById('background-cookies');

dataLayer = [];

if(!localStorage.getItem('cookies-accepted')){
	backgroundCookies.classList.add('active');
} else {
	dataLayer.push({'event': 'cookies-accepted'});
}

buttonAcceptCookies.addEventListener('click', () => {
	backgroundCookies.classList.remove('active');

	localStorage.setItem('cookies-accepted', true);

	dataLayer.push({'event': 'cookies-accepted'});
});