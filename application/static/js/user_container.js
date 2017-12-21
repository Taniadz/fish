
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
            alert(data.post_container);
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
    alert(444);
    AddClassActive("#product_block");
    var sort = $(this).attr('sort');
    var user = $(this).attr('user');
    $.ajax({
        type: "POST",
        url: $SCRIPT_ROOT +'/user_contain_product',
        data: "user_id=" + user + "&sort=" + sort,
        success: function (data) {
            alert(data.product_container);

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
    alert(1111);
    AddClassActive("#comment_block");
    var sort = $(this).attr('id');
    var contain = $(this).attr('rel_obj');
    alert(contain);
    var user = $(this).attr('user');
    $.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + '/user_contain_comment',
        data: "user_id=" + user + "&sort=" + sort + "&contain=" + contain,
        success: function (data) {
            alert("succes");
            alert(data.com_container);
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
    alert(555);
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
                    alert(data.favourite_container);
                },
                error: function (xhr, str) {
                    alert('Mistake ' + xhr.responseCode);
                }
            })

}

// $(document).ready(function() {
//
//
//     $("#post_block, a#post_block").on("click", UpdatePostContainer);
//     $(".user-activities li.comment, .user-activities li.prod_comment, a.comment, a.prod_comment").on("click", UpdateCommentContainer);
//     $("#product_block, a#product_block").on("click", UpdateProductContainer);
//     $(".user-activities li.post, .user-activities li.product, a.post, a.product").on("click", UpdateFavouriteContainer);
//
//
//
// });

//     $("button#post, button#post_in_user").click(function (event){

//
//         $('.user_but').removeClass("active");
//         $("#post").addClass("active");
//         var sort = $(this).attr('sort');
//         var user = "{{ user.id }}";
//         alert("new2");
//         alert(user);
//         alert(sort);
//             $.ajax({
//                 type: "POST",
//                 url: $SCRIPT_ROOT + '/user_contain_post',
//                 data: "user_id=" + user + "&sort=" + sort,
//                 success: function (data) {
//                     alert(data.post_container);
//                     $("#active_contain").html(data.post_container);
//                 },
//                 error: function (xhr, str) {
//                     alert('Mistake ' + xhr.responseCode);
//                 }
//             });
//         });
//
//
//     $("li.post#date, li.post#vote, li.product#vote,  li.product#date" ).click(function (event) {
//             event.preventDefault();
//             event.stopImmediatePropagation();
//
//             $('.user_but').removeClass("active");
//             $("#saved_block").addClass("active");
//             var sort = $(this).attr('id');
//             var contain = $(this).attr('class');
//             var user = $(this).attr('user');
//             $.ajax({
//                 type: "POST",
//                 url: $SCRIPT_ROOT + '/user_contain_saved',
//                 data: "user_id=" + user + "&sort=" + sort + "&contain=" + contain,
//                 success: function (data) {
//                     $("#active_contain").html(data.saved_container);
//                     alert(data.saved_container);
//                 },
//                 error: function (xhr, str) {
//                     alert('Mistake ' + xhr.responseCode);
//                 }
//             });
//         });
// });
//
//
//
