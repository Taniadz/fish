
var $devicewidth = (window.innerWidth > 0) ? window.innerWidth : screen.width;
var $bodyel = jQuery("body");
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
    console.log("start");
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
});