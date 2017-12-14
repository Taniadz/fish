
// toggle function for add to favourite one post / delete from favourite one post

function TogglePostfavour(){
    if (this.className == "favourite"){
        $.post( $SCRIPT_ROOT + '/delete_fav_post', {post_id: this.id});
        alert(this.id);
        $(this).attr("src", '/static/image/white_star.png');
    }else{
        $.post( $SCRIPT_ROOT + '/add_fav_post', {post_id: this.id});
        $(this).attr("src", '/static/image/gold_star.png');
    }
}
$("img.favourite, img.not-favourite").on('click', TogglePostfavour);


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

function ShowCommentForm() {
    $("#hiden_form1").slideToggle(400);
    $("textarea.my_textarea").val("Type your comment");
    $("textarea.my_textarea").focus(function(){$("textarea.my_textarea").val("");});

}
// show comment from field under the post
$(document).ready(function() {

$('#button_comment1').on("click", ShowCommentForm);
});
$(document).ready(function() {
    $("#form1.comment_form, #form2.comment_form").submit(function (event) {
        var formData = new FormData($(this)[0]);
           $.ajax({
                type: "POST",
                url: $(this).attr('action'),
                data: formData,
                processData: false,
                contentType: false,
                success: function (data) {
                    $("#comments").html(data.comments);
                    $('textarea#text').val("");
                },
                error: function (xhr, str) {
                    alert('Mistake ' + xhr.responseCode);
                }
            });
    event.preventDefault();
    });
});

// delete post and redirect
function delete_post(post_id, e) {
    e.preventDefault();
    if (confirm('Are you sure you want to save this thing into the database?')) {
        $.post(  $SCRIPT_ROOT + '/delete_post', {id:post_id},function( data ) {
           window.location.href =  $SCRIPT_ROOT + '/last_posts';
        });
} else {
    // Do nothing!
}
}


