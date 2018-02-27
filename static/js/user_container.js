
function AddClassActive(class_to_add) {
    $('.user_but').removeClass("active");
    $(".panel-title").removeClass("active");
    $(class_to_add).addClass("active");
    $(class_to_add).parent().addClass("active");

}
function UpdatePostContainer() {
    event.preventDefault();
    event.stopImmediatePropagation();

    AddClassActive("#post_block");
    var sort = $(this).attr('sort');
    var user = $(this).attr('user');
    $.ajax({
        type: "POST",
        url: $SCRIPT_ROOT +'/user_contain_post',
        data: "user_id=" + user + "&sort=" + sort,
        success: function (data) {
            $("#active-container").html(data.post_container);
            $("li#post_block").removeClass("active");
            $("li#post_block[sort=" + sort + "]").addClass("active");


        },
        error: function (xhr, str) {
            alert('Mistake ' + xhr.responseCode);
        }
    });
    event.preventDefault();
}


function UpdateProductContainer() {
    event.preventDefault();
    event.stopImmediatePropagation();
    AddClassActive("#product_block");
    var sort = $(this).attr('sort');
    var user = $(this).attr('user');
    $.ajax({
        type: "POST",
        url: $SCRIPT_ROOT +'/user_contain_product',
        data: "user_id=" + user + "&sort=" + sort,
        success: function (data) {
            $("#active-container").html(data.product_container);
            $("li#product_block").removeClass("active");
            $("li#product_block[sort=" + sort + "]").addClass("active");

        },
        error: function (xhr, str) {
            alert('Mistake ' + xhr.responseCode);
        }
    });
    event.preventDefault();
}

function UpdateCommentContainer() {
    AddClassActive("#comment_block");
    var sort = $(this).attr('id');
    var contain = $(this).attr('rel_obj');
    var user = $(this).attr('user');
    $.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + '/user_contain_comment',
        data: "user_id=" + user + "&sort=" + sort + "&contain=" + contain,
        success: function (data) {
            $("#active-container").html(data.com_container);
            $("li.comment_block").removeClass("active");
            $("li.comment_block[id=" + sort + "]").addClass("active");
        },
        error: function (xhr, str) {
                    alert('Mistake ' + xhr.responseCode);
                }
            });
}

function UpdateFavouriteContainer() {
    event.preventDefault();
    event.stopImmediatePropagation();
    AddClassActive("#favourite_block");
    var sort = $(this).attr('id');
    var contain = $(this).attr('class');
    var user = $(this).attr('user');
    $.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + '/user_contain_favourite',
        data: "user_id=" + user + "&sort=" + sort + "&contain=" + contain,
        success: function (data) {
            $("#active-container").html(data.favourite_container);
            $("li.favourite_block").removeClass("active");
            $("li.favourite_block[id=" + sort + "]").addClass("active");
                },
                error: function (xhr, str) {
                    alert('Mistake ' + xhr.responseCode);
                }
            })

}

