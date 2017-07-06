/**
 * Created by tania on 13.06.17.
 *
 *
 *
 *
 */


jQuery.fn.clickToggle = function(a,b) {
  function cb(){ [b,a][this._tog^=1].call(this); }
  return this.on("click", cb);
};

$( "img#white.post" ).clickToggle(function() {
    var post_id = $(this).attr("post_id");
    $(this).attr("src", 'static/image/blue_heart.png');

    $.ajax({
         type: 'POST',
         url: "/like_post",
         data: "id=" +post_id,
         success: function(data){
             $('#vote_countpost' + post_id).html(data);
         }
    });
}, function() {
    $(this).attr("src", 'static/image/white.png');

    var post_id = $(this).attr("post_id");
      $.ajax({
         type: 'POST',
         url: "/unlike_post",
         data: "id=" +post_id,
         success: function(data){
             $('#vote_countpost' + post_id).html(data);
         }
    });
});


$( "img#blue.post" ).clickToggle(function() {
    var post_id = $(this).attr("post_id");
    $(this).attr("src", 'static/image/white.png');

    $.ajax({
         type: 'POST',
         url: "/unlike_post",
         data: "id=" +post_id,
         success: function(data){

             $('#vote_countpost' + post_id).html(data);
         }
    });
}, function() {
    var post_id = $(this).attr("post_id");
        $(this).attr("src", 'static/image/blue_heart.png');

      $.ajax({
         type: 'POST',
         url: "/like_post",
         data: "id=" +post_id,
         success: function(data){
             $('#vote_countpost' + post_id).html(data);
         }
    });
});



$( "img#gold_star.post" ).clickToggle(function() {
    var post_id = $(this).attr("post_id");

    $(this).attr("src", 'static/image/white_star.png');

    $.ajax({
         type: 'GET',
         url: "{{ url_for('delete_post') }}",
         data: "post_id=" +post_id,
         success: function(data){

             $('.post#star_gold' + post_id).text("Add to saved");
         }
    });

}, function() {
    var post_id = $(this).attr("post_id");
        $(this).attr("src", 'static/image/gold_star.png');

      $.ajax({
         type: 'GET',
         url: "{{ url_for('save_post') }}",
         data: "post_id=" +post_id,
         success: function(data){
             $('.post#star_gold' + post_id).text("Delete_from_saved");
         }
    });
});

$( "img#white_star.post" ).clickToggle(function() {
    var post_id = $(this).attr("post_id");

    $(this).attr("src", 'static/image/gold_star.png');

    $.ajax({
         type: 'GET',
         url: "{{ url_for('save_post') }}",
         data: "post_id=" +post_id,

         success: function(data){
             $('.post#star_white' + post_id).text("Delete from saved");
         }
    });

}, function() {
    var post_id = $(this).attr("post_id");
        $(this).attr("src", 'static/image/white_star.png');

      $.ajax({
         type: 'GET',
         url: "{{ url_for('delete_post') }}",
         data: "post_id=" +post_id,
         success: function(data){
             $('.post#star_white' + post_id).text("Add to saved");
         }
    });
});



$(document).ready(function() {
    $('.anon_like').click(function() {
        $(".messages-container").fadeIn().delay(3000).fadeOut();
   });

});


function Comment_container(sort, contain, event) {
    event.preventDefault();
    $.ajax({
        type: "POST",
        url: "{{url_for('user_contain_comment' )}}",
        data: "user_id="+ "{{user.id}}" + "&sort=" + sort +  "&contain=" + contain,
        success: function (data) {
            $("#active_contain").html(data.com_container);
        },
        error: function (xhr, str) {
            alert('Mistake ' + xhr.responseCode);
        }
    });
};


function Product_container(sort, event) {
      event.preventDefault();

      $.ajax({
        type: "POST",
        url: "{{url_for('user_contain_product' )}}",
        data: "user_id="+ "{{user.id}}" + "&sort=" + sort,
        success: function (data) {
            $("#active_contain").html(data.prod_container);
        },
        error: function (xhr, str) {
            alert('Mistake ' + xhr.responseCode);
        }
    });
};

function Post_container(sort, event) {
    event.preventDefault();
    $.ajax({
        type: "POST",
        url: "{{url_for('user_contain_post' )}}",
        data: "user_id="+ "{{user.id}}" + "&sort=" + sort,
        success: function (data) {
            $("#active_contain").html(data.post_container);
        },
        error: function (xhr, str) {
            alert('Mistake ' + xhr.responseCode);
        }
    });
};


function Saved_container(sort, contain, event ) {
      event.preventDefault();

      $.ajax({
        type: "POST",
        url: "{{url_for('user_contain_saved' )}}",
        data: "user_id="+ "{{user.id}}" + "&sort=" + sort + "&contain=" + contain,
        success: function (data) {
            $("#active_contain").html(data.saved_container);
        },
        error: function (xhr, str) {
            alert('Mistake ' + xhr.responseCode);
        }
    });
};


jQuery.fn.clickToggle = function(a,b) {
  function cb(){ [b,a][this._tog^=1].call(this); }
  return this.on("click", cb);
};

$( "img#white.comment" ).clickToggle(function() {
    var comment_id = $(this).attr("comment_id");
    $(this).attr("src", '/static/image/blue_heart.png');

    $.ajax({
         type: 'POST',
         url: "/like_comment",
         data: "id=" +comment_id,
         success: function(data){
             $('#vote_countcomment' + comment_id).html(data);
         }
    });
}, function() {
    $(this).attr("src", '/static/image/white.png');

    var comment_id = $(this).attr("comment_id");
      $.ajax({
         type: 'POST',
         url: "/unlike_comment",
         data: "id=" +comment_id,
         success: function(data){
             $('#vote_countcomment' + comment_id).html(data);
         }
    });
});


$( "img#blue.comment" ).clickToggle(function() {
    var comment_id = $(this).attr("comment_id");
    $(this).attr("src", '/static/image/white.png');

    $.ajax({
         type: 'POST',
         url: "/unlike_comment",
         data: "id=" +comment_id,
         success: function(data){

             $('#vote_countcomment' + comment_id).html(data);
         }
    });
}, function() {
    var comment_id = $(this).attr("comment_id");
        $(this).attr("src", '/static/image/blue_heart.png');

      $.ajax({
         type: 'POST',
         url: "/like_comment",
         data: "id=" +comment_id,
         success: function(data){
             $('#vote_countcomment' + comment_id).html(data);
         }
    });
});


