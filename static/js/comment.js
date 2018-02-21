function delete_comment(e, id, url) {

    bootbox.confirm({
    title: "Delete Comment?",
    message: "Do you want to activate the Deathstar now? This cannot be undone.",
    buttons: {
        cancel: {
            label: '<i class="fa fa-times"></i> Cancel'
        },
        confirm: {
            label: '<i class="fa fa-check"></i> Confirm'
        }
    },
    callback: function (result) {
        if (result){
           $.post( url, {id:id},function( data ) {
            $("#comment" + id).html(data.deleted);
             $("#edit" + id).text(data.nodelet);


        });
} else {
    // Do nothing!
    }
}
});
}

function edit_comment(event, id, url) {
    event.preventDefault();

    $.ajax({
        type: "GET",
        url: url + '/' + id,

        success: function (data) {
            $("#comment" + id).html(data.form);
            $("#edit" + id).text(data.noedit);

        },
        error: function (xhr, str) {
            alert('Mistake ' + xhr.responseCode);
        }
    });
}



    function RenderProductCommentForm(event) {
        event.preventDefault();

                event.stopImmediatePropagation();

        var id = $(this).attr('id');
        $(".answer#answer" + id).slideToggle();
        var user = $(this).attr('user');
        var product = $(this).attr('product_id');
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
    }

    function RenderPostCommentForm(event) {
        event.preventDefault();
        event.stopImmediatePropagation();

        var id = $(this).attr('id');
        $(".answer#answer" + id).slideToggle();
        var user = $(this).attr('user');
        var post = $(this).attr('post_id');
        $.ajax({
            type: "POST",
            url: '/comment_form',
            data: "parent_id=" + id + "&post_id=" + post,
            success: function (data) {
                $(".answer#answer" + id).html(data.com_form);
                $("textarea#text").val(user + ", ");
            },
            error: function (xhr, str) {
                alert('Mistake ' + xhr.responseCode);
            }
        });
        event.preventDefault();
    }

// $(document).ready(function() {
// // data send by ajax on server where render template with updated comment part
//
// $(".discussion.post-form.comment-login").on("click", RenderPostCommentForm);
// $(".discussion.product-form.comment-login").on("click", RenderProductCommentForm);
// });

