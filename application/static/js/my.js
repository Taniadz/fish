/**
 * Created by tania on 13.06.17.
 *
 *
 *
 *
 */


$(document).ready(function() {


    $( "img.unliked, img.liked").click(function() {
        alert(123);
        var id = $(this).attr("obj_id");
        var url = $(this).attr("url");
        var div_class = $(this).attr("class");
        if (div_class == "unliked") {
            alert(123);
            $(this).attr("src", '/static/image/like_smile.png');
            $.ajax({
                type: 'POST',
                url: "/" + url,
                data: "id=" + id,
                success: function (data) {

                    $('#' + 'like_count_' + url + '_' + id).html(data.like);
                    $('#' + 'unlike_count_' + url + '_' + id).html(data.unlike);
                    $('#' + 'funny_count_' + url + '_' + id).html(data.funny);
                    $('#' + 'angry_count_' + url + '_' + id).html(data.angry);
                }
            });
            $(this).attr("class", "liked");
        }
        else if (div_class == "liked") {
            alert(123);
            $(this).attr("src", '/static/image/gray.png');
            var url = $(this).attr("url");
            var id = $(this).attr("obj_id");
            $.ajax({
                type: 'POST',
                url: "/un" + url,
                data: "id=" + id,
                success: function (data) {
                    $('#' + 'like_count_' + url + '_' + id).html(data.like);
                    $('#' + 'unlike_count_' + url + '_' + id).html(data.unlike);
                    $('#' + 'funny_count_' + url + '_' + id).html(data.funny);
                    $('#' + 'angry_count_' + url + '_' + id).html(data.angry);
                }
            });
            $(this).attr("class", "unliked");
        }
    });









$(".discussion").click(function (event){
    var id = $(this).attr('id');
    $(".answer#answer" + id).slideToggle();
    var user = $(this).attr('user');
    var product = "{{product_id}}";
    $.ajax({
        type: "POST",
        url: '/product_comment_form',
        data: "parent_id=" + id + "&product_id=" + product,
        success: function (data) {
             $(".answer#answer" + id).html(data.com_form);

            $("textarea#text").val(user + ", ");

        },
        error: function (xhr, str) {
            alert('Mistake ' + xhr.responseCode);
        }
    });
    event.preventDefault();



});
});  //end of the document ready

 function delete_comment(e, id, url) {

    e.preventDefault()
    if (confirm('Are you sure you want to save this thing into the database?')) {

        $.post( url, {id:id},function( data ) {
            $(".one_comment#comment" + id).html(data.deleted);
             $("#edit" + id).text(data.nodelet);


        });
} else {
    // Do nothing!
}

}

function edit_comment(event, id, url) {
    event.preventDefault();

    $.ajax({
        type: "GET",
        url: url + '/' + id,

        success: function (data) {
            $(".one_comment#comment" + id).html(data.form);
            $("#edit" + id).text(data.noedit);

        },
        error: function (xhr, str) {
            alert('Mistake ' + xhr.responseCode);
        }
    });
};


$(document).ready(function() {
    $('.smile').click(function() {
        var type=$(this).attr("type");

        var id = $(this).attr("obj_id");
        var url = $(this).attr("url");
        var prev_src = $(this).attr("src");
        $("img.liked[obj_id=" + id+"][url=" + url +"]").attr("src",prev_src );
        $("img.unliked[obj_id=" + id+"][url=" + url +"]").attr("src",prev_src );
        $("img.unliked[obj_id=" + id+"][url=" + url +"]").attr("class","liked" );
        $(".popup-div").fadeOut();

    $.ajax({
         type: 'POST',
         url: "/" + url,
         data: "id=" +id + "&type=" + type,
         success: function(data){

             $('#' + 'like_count_' + url +'_' + id).html(data.like);
             $('#' + 'unlike_count_' + url +'_' + id).html(data.unlike);
             $('#' + 'funny_count_' + url +'_' + id).html(data.funny);
             $('#' + 'angry_count_' + url +'_' + id).html(data.angry);
         }
    });
  });
});

$(document).ready(function() {
    $("img.liked, img.unliked, .popup-div").hover(function(){
        alert(123);
        var id = $(this).attr("obj_id");
        var url = $(this).attr("url");


        $(".popup-div[obj_id=" + id+"][url=" + url +"]").show();
    }, function() {
        var id = $(this).attr("obj_id");
        var url = $(this).attr("url");
        $("#popup-div_" + url + "_" + id).hide();
    });

});


// toggle function for add to favourite one post / delete from favourite one post
$(document).ready(function() {
       jQuery.fn.clickToggle = function(a,b) {
      function cb(){ [b,a][this._tog^=1].call(this); }
      return this.on("click", cb);
    };
    $("img#gold_star.post").clickToggle(function() {
        var post_id = $(this).attr("post_id");

        $(this).attr("src", '/static/image/white_star.png');

        $.ajax({
             type: 'GET',

             url: $SCRIPT_ROOT + '/delete_fav_post',
             data: "post_id=" +post_id,
             success: function(data){
                 alert(123);
                 // $('.post#star_gold' + post_id).text("Add to saved");
             }
        });

    }, function() {
        var post_id = $(this).attr("post_id");
            $(this).attr("src", '/static/image/gold_star.png');

          $.ajax({
             type: 'GET',
             url: $SCRIPT_ROOT + '/add_fav_post',
             data: "post_id=" +post_id,
             success: function(data){
                 // $('.post#star_gold' + post_id).text("Delete_from_saved");
             }
        });
    });

    $( "img#white_star.post" ).clickToggle(function() {
        var post_id = $(this).attr("post_id");
        alert(2);

        $(this).attr("src", '/static/image/gold_star.png');

        $.getJSON($SCRIPT_ROOT + '/add_fav_post', {
        post_id: post_id
      }, function(data) {
            alert(123);
        // $('.post#star_white' + post_id).text("Delete from saved");
      });


    }, function() {
        var post_id = $(this).attr("post_id");
            $(this).attr("src", '/static/image/white_star.png');

          $.ajax({
             type: 'GET',
             url: $SCRIPT_ROOT + '/delete_fav_post',
             data: "post_id=" +post_id,
             success: function(data){
                 alert(123);
                 // $('#star_white' + post_id).text("Add to saved");
             }
        });
    });
});





$(document).ready(function() {
    $("img#gold_star.product").clickToggle(function () {
        var product_id = $(this).attr("product_id");

        $(this).attr("src", '/static/image/white_star.png');

        $.ajax({
            type: 'GET',
             url: $SCRIPT_ROOT + '/delete_fav_product',
            data: "product_id=" + product_id,
            success: function (data) {

                $('.product#star_gold' + product_id).text("Add to saved");
            }
        });

    }, function () {
        var product_id = $(this).attr("product_id");
        $(this).attr("src", '/static/image/gold_star.png');

        $.ajax({
            type: 'GET',
             url: $SCRIPT_ROOT + '/add_fav_product',
            data: "product_id=" + product_id,
            success: function (data) {
                $('.product#star_gold' + product_id).text("Delete_from_saved");
            }
        });
    });

    $("img#white_star.product").clickToggle(function () {
        var product_id = $(this).attr("product_id");

        $(this).attr("src", '/static/image/gold_star.png');

        $.ajax({
            type: 'GET',
             url: $SCRIPT_ROOT + '/add_fav_product',
            data: "product_id=" + product_id,

            success: function (data) {
                $('.product#star_white' + product_id).text("Delete from saved");
            }
        });

    }, function () {
        var product_id = $(this).attr("product_id");
        $(this).attr("src", '/static/image/white_star.png');

        $.ajax({
            type: 'GET',
             url: $SCRIPT_ROOT + '/delete_fav_product',
            data: "product_id=" + product_id,
            success: function (data) {
                $('.product#star_white' + product_id).text("Add to saved");
            }
        });
    });
});