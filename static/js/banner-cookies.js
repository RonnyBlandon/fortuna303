const buttonAcceptCookies = document.getElementById('btn-accept-cookies');
const backgroundCookies = document.getElementById('background-cookies');
const bannerCookies = document.getElementById('banner-cookies');
const arrowHide = document.querySelector('.arrow-hide');

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


// Hide the content of the cookie notice for better visibility on the page
arrowHide.addEventListener('click', () => {
	if (bannerCookies.classList.contains('hidden')) {
		bannerCookies.childNodes.forEach(function (currentValue) {
			// since some nodeChilds do not have the style attribute we use an if
			if (currentValue.style) {
				// Only the images are visible, the rest is hidden
				if (currentValue.tagName != 'IMG') {
					currentValue.style.display = 'block';
				};
				if (currentValue.classList.contains('arrow-hide')) {
					currentValue.style.rotate = '0deg';
				};
			};
		});
		bannerCookies.style.padding = '1.2em';
		bannerCookies.style.paddingTop = '3.75em';
		bannerCookies.classList.remove('hidden');
		
	} else {
		bannerCookies.childNodes.forEach(function (currentValue) {
			// since some nodeChilds do not have the style attribute we use an if
			if (currentValue.style) {
				// Only the images are visible, the rest is hidden
				if (currentValue.tagName != 'IMG') {
					currentValue.style.display = 'none';
				};
				if (currentValue.classList.contains('arrow-hide')) {
					currentValue.style.rotate = '180deg';
				};
			};
		});
		bannerCookies.style.padding = '1em';
		bannerCookies.classList.add('hidden');
	}
});	
