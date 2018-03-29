
// toggle function for add to favourite one post / delete from favourite one post

function TogglePostfavour(){

    if ($(this).hasClass("fa-star")){
        $.post( $SCRIPT_ROOT + '/delete_fav_post', {post_id: this.id});
        $(this).removeClass("fa-star");
        $(this).addClass("fa-star-o");
        $(this).attr("title", "Добавить в избранное");

    }else{
        $.post( $SCRIPT_ROOT + '/add_fav_post', {post_id: this.id});
        $(this).removeClass("fa-star-o");
        $(this).addClass("fa-star");
        $(this).attr("title", "Убрать с избранного");

    }
}



// sort comment by data or rating (work only for comment with parent id = 0)
function post_comment(post_id, sort, event) {
    $.ajax({
        type: "POST",
        url:  $SCRIPT_ROOT + '/post_contain_comment',
        data: "post_id="+ post_id + "&sort=" + sort,
        success: function (data) {
            $("#comments").html(data.comments);
        },
        error: function (xhr, str) {
            alert('Mistake ' + xhr.responseCode);
        }
    });
    event.preventDefault();

}

function ShowCommentForm() {
    $("#hiden_form1.post-form").slideToggle(200);
}

// delete post and redirect
function delete_post(post_id, e) {

    bootbox.confirm({
        message: "Вы действительно хотите удалить этот пост?",
        callback: function (result) { /* result is a boolean; true = OK, false = Cancel*/

        if(result){
        $.post($SCRIPT_ROOT + '/delete_post', {id: post_id}, function (data) {
            window.location.href =  $SCRIPT_ROOT + '/last_posts';
        });

    }
else
    {
        console.log("no changes")
    }
}
    })
}

// show comment from field under the post
$(document).ready(function() {
    $("i.favourite.post-fav, i.not-favourite.post-fav").on('click', TogglePostfavour);

    $('#button_comment1.post-form.comment-login').on("click", ShowCommentForm);
});


