$(document).ready(function() {
    "use strict";

    /******************** NAVBAR ********************/
    var animationProp = $('.navbar-nemo'); //Navbar wraper

    if (matchMedia('only screen and (min-width: 768px)').matches && animationProp.hasClass('navbar-transparent')) {
        var scrollPos = $(this).scrollTop(),
            animationEndPos = 150, //At the point background add
            logo = animationProp.find('.navbar-brand img');

        //if visitor refresh on the middle of the document
        if (scrollPos > animationEndPos) {
            animationProp.removeClass('navbar-transparent');
            logo.attr('src', 'images/logo-alt.png');
        }

        //toggle existing class
        $(document).scroll(function() {
            scrollPos = $(this).scrollTop();

            if (scrollPos > animationEndPos) {
                animationProp.removeClass('navbar-transparent');

                //change logo into black
                logo.attr('src', 'images/logo-alt.png');
            } else {
                animationProp.addClass('navbar-transparent');

                //change logo into base
                logo.attr('src', 'images/logo.png');

            }
        });
    }

    /******************** BACKGROUND VIDEO ********************/
    var vidContainer1 = document.querySelector(".video-player");
    var vidContainer2 = document.querySelector(".the-video-2");

    if (vidContainer1 != null) {
        var vid = vidContainer1.querySelector("video");
        var pauseButton = vidContainer1.querySelector("button");

        vid.addEventListener('ended', function() {
            // only functional if "loop" is removed
            vid.pause();
            // to capture IE10
            // vidFade();
        });

        pauseButton.addEventListener("click", function() {
            if (vid.paused) {
                vid.play();
                $(pauseButton).animate({
                    'bottom': '50px',
                    'opacity': '0.5'
                });
                $(pauseButton).find('.play').removeClass('active');
                $(pauseButton).find('.pause').addClass('active');

            } else {
                vid.pause();
                $(pauseButton).animate({
                    'bottom': '50%',
                    'opacity': '1'
                });
                $(pauseButton).find('.pause').removeClass('active');
                $(pauseButton).find('.play').addClass('active');
            }
        });
    }

    if (vidContainer2 != null) {
        var vid = vidContainer2.querySelector("video");
        var pauseButton = vidContainer2.querySelector("button");

        vid.addEventListener('ended', function() {
            // only functional if "loop" is removed
            vid.pause();
            // to capture IE10
            // vidFade();
        });

        pauseButton.addEventListener("click", function() {
            if (vid.paused) {
                vid.play();
                $(vidContainer2).addClass('playing');
                $(pauseButton).find('.play').removeClass('active');
                $(pauseButton).find('.pause').addClass('active');

            } else {
                vid.pause();
                $(vidContainer2).removeClass('playing');
                $(pauseButton).animate({
                    'bottom': '50%',
                    'opacity': '1'
                });
                $(pauseButton).find('.pause').removeClass('active');
                $(pauseButton).find('.play').addClass('active');
            }
        });
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

    /******************** ENABLE LINK FOR NAVBAR LOGIN ********************/
    $(document).ready(function() {
        $('ul.nav > li > a').off("click");
    });
});
