// this fuction for Header

$(function() {
    $(window).on("scroll ", function() {
        if ($(window).scrollTop() > 40) {
            $(".header ").addClass("header-fixed ");
        } else {
            //remove the background property so it comes transparent again (defined in your css)
            $(".header ").removeClass("header-fixed");
        }
    });
});

$(function() {
    $(window).on("scroll ", function() {
        if ($(window).scrollTop() > 40) {
            $(".btn-whatsapp-pulse-border ").addClass("btn-whatsapp-pulse-border-new");
        } else {
            //remove the background property so it comes transparent again (defined in your css)
            $(".btn-whatsapp-pulse-border").removeClass("btn-whatsapp-pulse-border-new");
        }
    });
});





// this fuction for toggle
let menutoggle = document.querySelector('.toggle');
menutoggle.onclick = function() {
    menutoggle.classList.toggle('active')
}



$('.hero-img').load(
    function() {
        $(".hero-img").removeClass('.hero-img');
    }
);

console.log('"this is javascript"')
var year = 26
var name = ('darshan')
console.log("'this is single quote'")

$(document).load(function() {
    $('.hero-banner').addClass('hero-banner-new');
});