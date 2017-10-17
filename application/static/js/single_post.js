
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
                 $('.post#star_gold' + post_id).text("Add to saved");
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
                 $('.post#star_gold' + post_id).text("Delete_from_saved");
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
        $('.post#star_white' + post_id).text("Delete from saved");
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
                 $('#star_white' + post_id).text("Add to saved");
             }
        });
    });
});


// show div wit login url for unlogin user when they try to like or comment
$(document).ready(function() {
    $('.anon_like').click(function() {
        $(".messages-container").fadeIn().delay(3000).fadeOut();
   });

    $('#anon_comment').click(function() {
            $(".messages-container").fadeIn().delay(3000).fadeOut();
       });
});


// sort comment by data or rating (work only for comment with parent id = 0)
function post_comment(post_id, sort, event) {
    $.ajax({
        type: "POST",
        url:  $SCRIPT_ROOT + '/post_contain_comment',
        data: "post_id="+ post_id + "&sort=" + sort,
        success: function (data) {
            $("#comment").html(data.comments);
        },
        error: function (xhr, str) {
            alert('Mistake ' + xhr.responseCode);
        }
    });
    event.preventDefault();

}


// show comment from field under the post
$(document).ready(function() {
    $('#button_comment1').click(function() {
        $("#hiden_form1").slideToggle(500);
    });
    $("textarea.my_textarea").val("Type your comment");

    $("textarea.my_textarea").focus(function(){$("textarea.my_textarea").val("");});





// send comment by ajax from form field under the post
$("#form1.comment_form").submit(function (event) {
    $("#hiden_form1").slideToggle();
    var formData = new FormData($(this)[0]);
       $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: formData,
            processData: false,
            contentType: false,
            success: function (data) {
                $("#comment").html(data.comments);
                $('textarea#text').val("");

            },
            error: function (xhr, str) {
                alert('Mistake ' + xhr.responseCode);
            }
        });
event.preventDefault();
});


// send comment by ajax from form field at the end of the page
$("#form2.comment_form").submit(function (event) {
    alert(123);

    var formData = new FormData($(this)[0]);
        $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: formData,
            processData: false,
            contentType: false,
            success: function (data) {
                alert(123);
                $("#comment").html(data.comments);
                $('textarea#text').val("");

            },
            error: function (xhr, str) {
                alert('Mistake ' + xhr.responseCode);
            }
        });
event.preventDefault();
});

});

// delete product and redirect
function delete_post(post_id, e) {
    alert(post_id),
    e.preventDefault()
    if (confirm('Are you sure you want to save this thing into the database?')) {


        $.post(  $SCRIPT_ROOT + '/delete_post', {id:post_id},function( data ) {
           window.location.href =  $SCRIPT_ROOT + '/last_posts';
        });
} else {
    // Do nothing!
}

}


