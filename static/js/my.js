/**
 * Created by tania on 13.06.17.
 *
 *
 *
 *
 */

function UpdateCount(data, url, id){
    $('#' + 'like_count_' + url + '_' + id).html(data.like);
    $('#' + 'unlike_count_' + url + '_' + id).html(data.unlike);
    $('#' + 'funny_count_' + url + '_' + id).html(data.funny);
    $('#' + 'angry_count_' + url + '_' + id).html(data.angry);

}


    // like/unlike in one click without using reaction
function ToggleLikeUnlike(){

    var url = $(this).attr("url");
    var ids = $(this).attr("obj_id");
    var id = ids.replace(/[^A-Za-z0-9]/g, '');
    var div_class = $(this).attr("class");
    alert(div_class);
    if ($(this).hasClass("unliked")) {
        alert("unliked");
        $(this).attr("src", '/static/image/button-liked.png');
        $.ajax({
            type: 'POST',
            url: "/" + url,
            data: "id=" + id,
            success: function (data) {
                UpdateCount(data, url, id);
            }
        });
        $(this).attr("class", "liked");
         event.preventDefault();
    }
    else if ($(this).hasClass("liked")) {
        alert("liked");
        var url = $(this).attr("url");
        var id = $(this).attr("obj_id");
            $(this).attr("src", '/static/image/not-reaction.png');
            $.ajax({
                type: 'POST',
                url: "/un" + url,
                data: "id=" + id,
                success: function (data) {
                    UpdateCount(data, url, id);
                }
            });
            $(this).attr("class", "unliked");
             event.preventDefault();
        }
    }


function AddReaction(event) {
    event.preventDefault();
    event.stopImmediatePropagation();
    var type=$(this).attr("type");
    var ids = $(this).attr("obj_id");
    var id = ids.replace(/[^A-Za-z0-9]/g, '');
    console.log(id, 1);
    var url = $(this).attr("url");
    var prev_src = $(this).attr("src");
    //add to like under pop-up div class "liked" and clicked reaction's src
    $("img.liked[obj_id=" + id +"][url=" + url +"]").attr("src",prev_src );
    $("img.unliked[obj_id=" + id +"][url=" + url +"]").attr("src",prev_src );
    $("img.unliked[obj_id=" + id+"][url=" + url +"]").attr("class","liked" );

    $(".popup-div").fadeOut();
    $.ajax({
         type: 'POST',
         url: "/" + url,
         data: "id=" +id + "&type=" + type,
         success: function(data){
             UpdateCount(data, url, id);
         }
    });
     event.preventDefault();
}

//show pop-up div with reaction
function ShowReactionDiv() {
    $("img.liked, img.unliked, .popup-div").mouseenter(function() {
        var ids = $(this).attr("obj_id");

        var id = ids.replace(/[^A-Za-z0-9]/g, '');
        var url = $(this).attr("url");
        var $div2 = $(".popup-div[obj_id=" + id+"][url=" + url +"]");
        if ($div2.is(":visible")) { return; }
        $div2.show();
        setTimeout(function() {
            $div2.hide();
        }, 3000);
    });
}


// $(document).ready(function() {
//
//     $("img.unliked, img.liked").on("click", ToggleLikeUnlike);
//     $('.smile').on("click", AddReaction);
//     ShowReactionDiv();
//
// });




