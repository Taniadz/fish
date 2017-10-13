
// toggle function for add to favourite one post / delete from favourite one post


jQuery.fn.clickToggle = function (a, b) {
    function cb() {
        [b, a][this._tog ^= 1].call(this);
    }

    return this.on("click", cb);
};
$(document).ready(function () {


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

// delete product and redirect
function delete_product(product_id, e) {

    alert(product_id);
    e.preventDefault()
    if (confirm('Are you sure you want to save this thing into the database?')) {
        $.post("{{ url_for('delete_product')}}", {id: product_id}, function (data) {
            window.location.href = "{{ url_for('popular_product') }}";
        });
    } else {
        // Do nothing!
    }

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
            $("#comment").html(data.comments);
        },
        error: function (xhr, str) {
            alert('Mistake ' + xhr.responseCode);
        }
    });
    event.preventDefault();

};


// show comment from field under the product
$(document).ready(function () {
    $('#button_comment1').click(function () {
        $("#hiden_form1").slideToggle(500);
    });
    $("textarea.my_textarea").val("Type your comment");

    $("textarea.my_textarea").focus(function () {
        $("textarea.my_textarea").val("");
    });


// send comment by ajax from form field under the product
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
    var formData = new FormData($(this)[0]);

    $.ajax({
        type: "POST",
        url: $(this).attr('action'),
        data: formData,
        processData: false,
        contentType: false,
        success: function (data) {
            alert(123)
            $("#comment").html(data.comments);
            $('textarea#text').val("");

        },
        error: function (xhr, str) {
            alert('Mistake ' + xhr.responseCode);
        }
    });
    event.preventDefault();
});







// if user not the comments'author, user can discuss other comment
// data send by ajax on server where render template with updated comment part
$(".discussion").click(function (event){
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
    event.preventDefault();
});
});

