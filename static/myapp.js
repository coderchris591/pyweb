

// Open side navigation
function toggleMenu() {
    var nav = document.querySelector('.sideNav');
    nav.classList.toggle('active');
}


// Close the side navigation if clicked outside
document.addEventListener('click', function(event) {
    var nav = document.querySelector('.sideNav');
    var hamburger = document.querySelector('.hamburger');
    var isClickInsideNav = nav.contains(event.target);
    var isClickInsideHamburger = hamburger.contains(event.target);

    if (!isClickInsideNav && !isClickInsideHamburger) {
        nav.classList.remove('active');
    }
});