
function ToggleProductFavour(){
    if ($(this).hasClass("fa-star")){
        $.post( $SCRIPT_ROOT + '/delete_fav_product', {product_id: this.id});
        $(this).removeClass("fa-star");
        $(this).addClass("fa-star-o");
    }else{
        $.post( $SCRIPT_ROOT + '/add_fav_product', {product_id: this.id});
        $(this).removeClass("fa-star-o");
        $(this).addClass("fa-star");
    }
}
// delete product and redirect
function delete_product(product_id, e) {
    bootbox.confirm({
        message: "Do you want to delete product?",
        callback: function (result) { /* result is a boolean; true = OK, false = Cancel*/

        if(result){
        $.post($SCRIPT_ROOT + '/delete_product', {id: product_id}, function (data) {
            window.location.href =  $SCRIPT_ROOT + '/popular_product';
        });

    }
else
    {
        console.log("no changes")

    }
}
    })
    // e.preventDefault();
    // if (confirm('Are you sure you want to save this thing into the database?')) {
    //     $.post("{{ url_for('delete_product')}}", {id: product_id}, function (data) {
    //         window.location.href = "{{ url_for('popular_product') }}";
    //     });
    // } else {
    //     // Do nothing!
    // }

}

// show div wit login url for unlogin user when they try to like or comment
$(document).ready(function () {
    $('.anon_like').click(function () {
        $(".messages-container").fadeIn().delay(3000).fadeOut();
    });

    $('#anon_comment').click(function () {
        $(".messages-container").fadeIn().delay(3000).fadeOut();
    });
});


// sort comment by data or rating (work only for comment with parent id = 0)
function product_comment(product_id, sort, event) {
     $.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + '/product_contain_comment',
        data: "product_id=" + product_id + "&sort=" + sort,
        success: function (data) {
            $("#comments").html(data.comments);
        },
        error: function (xhr, str) {
            alert('Mistake ' + xhr.responseCode);
        }
    });
    event.preventDefault();

}

function ShowProdCommentForm() {
    $("#hiden_form1.product-form").slideToggle(400);
    $("form#form1.comment_form textarea").val("Type your comment");
    $("form#form1.comment_form textarea").focus(function(){$("form#form1.comment_form textarea").val("");});

}

// show comment from field under the product
$(document).ready(function () {
    $('.product-form#button_comment1.comment-login').on("click", ShowProdCommentForm);

    $("i.favourite.product-fav, i.not-favourite.product-fav").on('click', ToggleProductFavour);




// send comment by ajax from form field under the product
$("#form1.comment_form").submit(function (event) {
    event.preventDefault();
    $("#hiden_form1").slideToggle();
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


// send comment by ajax from form field at the end of the page
$("#form2.comment_form").submit(function (event) {
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




});

