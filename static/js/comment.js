function delete_comment(e, id, url) {

    bootbox.confirm({
    title: "Удалить комментарий?",
    message: "Вы дейстительно хотите удалить этот комментарий?",
    buttons: {
        cancel: {
            label: '<i class="fa fa-times"></i> Отменить'
        },
        confirm: {
            label: '<i class="fa fa-check"></i> Удалить'
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
    $(".answer-form").submit(function (event) {
        var formData = new FormData($(this)[0]);

        $.ajax({
            type: "POST",
            url: $(this).attr("action"),
            data: formData,
            processData: false,
            contentType: false,
            success: function (data) {
                $("#comments").html(data.comments);
                $("textarea#text").val("");
            },
            error: function (xhr, str) {
                alert('Mistake ' + xhr.responseCode);
            }
        });
        event.preventDefault();
    });

$(".edit_comment").submit(function(event) {
    var id = $(this).attr("id");
    var formData = new FormData($(this)[0]);
    $.ajax({
        type: "POST",
        url: $(this).attr('action'),
        data: formData,
        processData: false,
        contentType: false,

        success: function (data) {
            $("#comment" + id).html(data.comment);
            $("textarea#text").val("");

        },
        error: function (xhr, str) {
            alert('Mistake ' + xhr.responseCode);
        }
    });
    event.preventDefault();
});
$(document).ready(function() {
$('.comment-file').change(function() {
    $(this).next().html("<div class='uploaded'>Загружено</div>");
    $(this).next().next().html(" ");

});
});
// $(document).ready(function() {
// // data send by ajax on server where render template with updated comment part
//
// $(".discussion.post-form.comment-login").on("click", RenderPostCommentForm);
// $(".discussion.product-form.comment-login").on("click", RenderProductCommentForm);
// });

