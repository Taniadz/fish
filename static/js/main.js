
var $devicewidth = (window.innerWidth > 0) ? window.innerWidth : screen.width;
var $bodyel = jQuery("body");
var $navbarel = jQuery(".navbar");
var $deviceheight = (window.innerHeight > 0) ? window.innerHeight : screen.height;
$(document).ready(function () {

    "use strict";
    if(document.getElementById('ct-js-wrapper')){

        var snapper = new Snap({
            element: document.getElementById('ct-js-wrapper')

        });

        snapper.settings({
            disable: "left",
            addBodyClasses: true
        });
    }

    snapper.on('start', function(){
    });

 // Snap Navigation in Mobile // -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        if ($devicewidth > 767 && document.getElementById('ct-js-wrapper')) {
            snapper.disable();
        }



        var myToggleButton = document.getElementById('listener');

    myToggleButton.addEventListener('click', function(){


        if( snapper.state().state=="right" ){

            snapper.close();
        } else {

            snapper.open('right');
        }

    });


  // Snap.js -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    $(window).on('resize', function() {
        if ($(window).width() < 768) {
            snapper.enable();
        } else{
            snapper.disable();
        }
    });

     $(window).scroll(function(){
        var scroll = $(window).scrollTop();
        if (scroll > 600) {
            jQuery('.ct-js-btnScrollUp').addClass('is-active');
        } else {
            jQuery('.ct-js-btnScrollUp').removeClass('is-active');
        }

        // Navbar Height // -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        if (($bodyel.hasClass("ct-navbar--fixedTop")) || ($bodyel.hasClass("ct-js-navbarMakeSmaller"))) {

            if (scroll >= 100) {
                $(".ct-navbar--fixedTop .navbar").css("box-shadow","0 0 15px -6px #4c505e");



                if($bodyel.hasClass("ct-js-navbarMakeSmaller")){
                    $bodyel.addClass("ct-navbar--fixedTop--is-small");




                }
                if ($bodyel.hasClass("ct-navbar-isTransparent-toInverse") || $bodyel.hasClass("ct-navbar-isTransparent-toDefault")){
                    $navbarel.removeClass("ct-navbar--transparent");
                }
                if ($bodyel.hasClass("ct-navbar-isTransparent-toInverse")){
                    $navbarel.addClass("navbar-inverse");
                }
                if ($bodyel.hasClass("ct-navbar-isTransparent-toDefault")){
                    $navbarel.removeClass("navbar-transparent");
                    $navbarel.addClass("navbar-default");

                }
            } else {
                if($bodyel.hasClass("ct-js-navbarMakeSmaller")){
                    $bodyel.removeClass("ct-navbar--fixedTop--is-small");
                    $(".ct-navbar--fixedTop .navbar").css("box-shadow","none");



                }
                if ($bodyel.hasClass("ct-navbar-isTransparent-toDefault") || $bodyel.hasClass("ct-navbar-isTransparent-toInverse")){
                    $navbarel.removeClass("navbar-default");
                    $navbarel.removeClass("navbar-inverse");
                    $navbarel.addClass("navbar-transparent");

                }
            }
        }

        // fixed navbar

        if ($bodyel.is(".navbar-fixed.with-topbar")) {
            if (scroll >= 100) {
                $bodyel.addClass("hide-topbar");


                if (!($bodyel.is(".revert-to-transparent"))) {
                    $bodyel.addClass("navbar-with-shadow");
                }
            } else {
                $bodyel.removeClass("hide-topbar navbar-with-shadow");

            }
        }

    });
    //  $(document).ready(function () {
    //
    //     // Flexslider height ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    //
    //     var $mediaSection = $(".ct-mediaSection");
    //     if($mediaSection.length > 0)
    //     {
    //         $mediaSection.each(function()
    //         {
    //             if( $(this).attr("data-height") == "100%")
    //             {
    //                 $(this).find(".flexslider").css("height",  $deviceheight + "px");
    //             }
    //         });
    //     }
    //
    //
    //
    // });
    $(".favourite-not-login").on("click", function () {

         $(".alert.alert-danger.favourite-alert").show();

     })

    $(".comment-not-login").on("click", function () {

         $(".alert.alert-danger.comment-alert").show();

     })

    $(".like-not-login").on("click", function () {

         $(".alert.alert-danger.like-alert").show();

     })

    autosize($('textarea'));

var text = $('.text-line').text();
console.log(text);
text = text.replace(/\r?\n/g, '<br />');
$('.text-line').html(text);


$(".ct-iconBox-flash").delay(5000).hide(1);

$(".close-flash").on("click", function () {
    $(".ct-iconBox-flash").hide();
})

});