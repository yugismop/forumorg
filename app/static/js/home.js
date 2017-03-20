$(document).ready(function() {
    "use strict";

    /******************** NAVBAR ********************/
    var animationProp = $('.navbar-nemo'); //Navbar wraper
    var scrollPos = $(this).scrollTop(),
        animationEndPos = 150,
        logo = animationProp.find('.navbar-brand img');

    if (animationProp.hasClass('navbar-transparent') && matchMedia('only screen and (min-width: 769px)').matches) {
        //if visitor refresh on the middle of the document
        if (scrollPos > animationEndPos) {
            animationProp.removeClass('navbar-transparent');
            logo.attr('src', '/static/images/fo-base.png');
        }

        //toggle existing class
        $(document).scroll(function() {
            scrollPos = $(this).scrollTop();
            if (scrollPos > animationEndPos) {
                animationProp.removeClass('navbar-transparent');
                logo.attr('src', '/static/images/fo-base.png');
            } else {
                animationProp.addClass('navbar-transparent');
                logo.attr('src', '/static/images/fo-alt.png');
            }
        });
    } else {
        logo.attr('src', '/static/images/fo-base.png');
    }

    /******************** NAVBAR APPEAR ON SCROLL ********************/
    if (animationProp.hasClass('appear-onscroll')) {
        $(document).scroll(function() {
            var scrollPos = $(this).scrollTop();

            if (scrollPos > 150) {
                animationProp.removeClass('appear-onscroll');
            } else {
                animationProp.addClass('appear-onscroll');
            }
        });
    }

    /******************** ONE PAGE NAVIGATION ********************/
    $('.navbar-nav').onePageNav({
        currentClass: 'active',
        scrollOffset: 74
    });

    /******************** SCROLL HACK ********************/
    $(window).scroll(function() {
        if ($(this).scrollTop() > 50) {
            $('.navbar-nav').addClass('opaque');
        } else {
            $('.navbar-nav').removeClass('opaque');
        }
    });

});
