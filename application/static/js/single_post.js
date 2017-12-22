
// toggle function for add to favourite one post / delete from favourite one post

function TogglePostfavour(){
    alert("post");
    if ($(this).hasClass("fa-star")){
        $.post( $SCRIPT_ROOT + '/delete_fav_post', {post_id: this.id});
        alert(this.id);
        $(this).removeClass("fa-star");
        $(this).addClass("fa-star-o");
    }else{
        alert("else");
        $.post( $SCRIPT_ROOT + '/add_fav_post', {post_id: this.id});
        $(this).removeClass("fa-star-o");
        $(this).addClass("fa-star");
    }
}



// sort comment by data or rating (work only for comment with parent id = 0)
function post_comment(post_id, sort, event) {
    $.ajax({
        type: "POST",
        url:  $SCRIPT_ROOT + '/post_contain_comment',
        data: "post_id="+ post_id + "&sort=" + sort,
        success: function (data) {
            alert(data.comments);
            $("#comments").html(data.comments);
        },
        error: function (xhr, str) {
            alert('Mistake ' + xhr.responseCode);
        }
    });
    event.preventDefault();

}

function ShowCommentForm() {
    $("#hiden_form1.post-form").slideToggle(400);
    $("form#form1.comment_form textarea").val("Type your comment");
    $("form#form1.comment_form textarea").focus(function(){$("form#form1.comment_form textarea").val("");});


}
// show comment from field under the post
$(document).ready(function() {
    $("i.favourite.post-fav, i.not-favourite.post-fav").on('click', TogglePostfavour);

    $('#button_comment1.post-form').on("click", ShowCommentForm);
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


