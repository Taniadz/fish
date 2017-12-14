
function AddClassActive(class_to_add) {
    $('.user_but').removeClass("active");
    $(class_to_add).addClass("active");

}

function UpdatePostContainer() {
    event.preventDefault();
    event.stopImmediatePropagation();
    AddClassActive("#comment_block");
    var sort = $(this).attr('id');
    var contain = $(this).attr('class');
    var user = "{{ user.id }}";
    $.ajax({
                type: "POST",
                url: $SCRIPT_ROOT + '/user_contain_comment',
                data: "user_id=" + user + "&sort=" + sort + "&contain=" + contain,
                success: function (data) {
                    alert(data.com_container);
                    $("#active_contain").html(data.com_container);
                },
                error: function (xhr, str) {
                    alert('Mistake ' + xhr.responseCode);
                }
            });
}

$(document).ready(function() {


    $("li.comment#date,  li.prod_comment#date, li.comment#vote, li.prod_comment#vote" ).on("click", UpdatePostContainer);


        $("button#product").click(function (event) {
            event.preventDefault();
            event.stopImmediatePropagation();

            $('.user_but').removeClass("active");
            $("#product").addClass("active");
            var sort = $(this).attr('sort');
            var user = $(this).attr('user');
            $.ajax({
                type: "POST",
                url: $SCRIPT_ROOT +'/user_contain_product',
                data: "user_id=" + user + "&sort=" + sort,
                success: function (data) {
                     alert(data.prod_container);
                    $("#active_contain").html(data.prod_container);
                },
                error: function (xhr, str) {
                    alert('Mistake ' + xhr.responseCode);
                }
            });
            event.preventDefault();
        });

    $("button#post, button#post_in_user").click(function (event){
        event.preventDefault();
        event.stopImmediatePropagation();

        $('.user_but').removeClass("active");
        $("#post").addClass("active");
        var sort = $(this).attr('sort');
        var user = $(this).attr('user');
        alert(user);
        alert(sort);
            $.ajax({
                type: "POST",
                url: $SCRIPT_ROOT + '/user_contain_post',
                data: "user_id=" + user + "&sort=" + sort,
                success: function (data) {
                    alert(data.post_container);
                    $("#active_contain").html(data.post_container);
                },
                error: function (xhr, str) {
                    alert('Mistake ' + xhr.responseCode);
                }
            });
        });


    $("li.post#date, li.post#vote, li.product#vote,  li.product#date" ).click(function (event) {
            event.preventDefault();
            event.stopImmediatePropagation();

            $('.user_but').removeClass("active");
            $("#saved_block").addClass("active");
            var sort = $(this).attr('id');
            var contain = $(this).attr('class');
            var user = $(this).attr('user');
            $.ajax({
                type: "POST",
                url: $SCRIPT_ROOT + '/user_contain_saved',
                data: "user_id=" + user + "&sort=" + sort + "&contain=" + contain,
                success: function (data) {
                    $("#active_contain").html(data.saved_container);
                    alert(data.saved_container);
                },
                error: function (xhr, str) {
                    alert('Mistake ' + xhr.responseCode);
                }
            });
        });
});



