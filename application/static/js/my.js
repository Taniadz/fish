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


    // like/unlike in one click without using reraction
function ToggleLikeUnlike(){
    var url = $(this).attr("url");
    var id = $(this).attr("obj_id");
    var div_class = $(this).attr("class");
    if (div_class == "unliked") {
        $(this).attr("src", '/static/image/like_smile.png');
        $.ajax({
            type: 'POST',
            url: "/" + url,
            data: "id=" + id,
            success: function (data) {
                UpdateCount(data, url, id);
            }
        });
        $(this).attr("class", "liked");
    }
    else if (div_class == "liked") {
        var url = $(this).attr("url");
        var id = $(this).attr("obj_id");
            $(this).attr("src", '/static/image/gray.png');
            $.ajax({
                type: 'POST',
                url: "/un" + url,
                data: "id=" + id,
                success: function (data) {
                    UpdateCount(data, url, id);
                }
            });
            $(this).attr("class", "unliked");
        }
    }


$("img.unliked, img.liked").on("click", ToggleLikeUnlike);
$('.smile').on("click", AddReaction);
ShowReactionDiv() ;

function AddReaction() {
    var type=$(this).attr("type");
    var id = $(this).attr("obj_id");
    var url = $(this).attr("url");
    var prev_src = $(this).attr("src");
    //add to like under pop-up div class "liked" and clicked reaction's src
    $("img.liked[obj_id=" + id+"][url=" + url +"]").attr("src",prev_src );
    $("img.unliked[obj_id=" + id+"][url=" + url +"]").attr("src",prev_src );
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
}

//show pop-up div with reaction
function ShowReactionDiv() {
    $("img.liked, img.unliked, .popup-div").mouseenter(function() {
        var id = $(this).attr("obj_id");
        var url = $(this).attr("url");
        var $div2 = $(".popup-div[obj_id=" + id+"][url=" + url +"]");
        if ($div2.is(":visible")) { return; }
        $div2.show();
        setTimeout(function() {
            $div2.hide();
        }, 3000);
    });
}


