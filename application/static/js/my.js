/**
 * Created by tania on 13.06.17.
 *
 *
 *
 *
 */


$(document).ready(function() {
    // send data to sever to create reaction object and change count (in object and in html)
    $( "img.unliked, img.liked").click(function() {
        var id = $(this).attr("obj_id");
        var url = $(this).attr("url");
        var div_class = $(this).attr("class");
        if (div_class == "unliked") {
            $(this).attr("src", '/static/image/like_smile.png');
            $.ajax({
                type: 'POST',
                url: "/" + url,
                data: "id=" + id,
                success: function (data) {
                    $('#' + 'like_count_' + url + '_' + id).html(data.like);
                    $('#' + 'unlike_count_' + url + '_' + id).html(data.unlike);
                    $('#' + 'funny_count_' + url + '_' + id).html(data.funny);
                    $('#' + 'angry_count_' + url + '_' + id).html(data.angry);
                }
            });
            $(this).attr("class", "liked");
        }
        else if (div_class == "liked") {
            $(this).attr("src", '/static/image/gray.png');
            var url = $(this).attr("url");
            var id = $(this).attr("obj_id");
            $.ajax({
                type: 'POST',
                url: "/un" + url,
                data: "id=" + id,
                success: function (data) {
                    $('#' + 'like_count_' + url + '_' + id).html(data.like);
                    $('#' + 'unlike_count_' + url + '_' + id).html(data.unlike);
                    $('#' + 'funny_count_' + url + '_' + id).html(data.funny);
                    $('#' + 'angry_count_' + url + '_' + id).html(data.angry);
                }
            });
            $(this).attr("class", "unliked");
        }
    });


});  //end of the document ready



//change reaction image after clicking in one big smile
$(document).ready(function() {
    $('.smile').click(function() {
        var type=$(this).attr("type");

        var id = $(this).attr("obj_id");
        var url = $(this).attr("url");
        var prev_src = $(this).attr("src");
        $("img.liked[obj_id=" + id+"][url=" + url +"]").attr("src",prev_src );
        $("img.unliked[obj_id=" + id+"][url=" + url +"]").attr("src",prev_src );
        $("img.unliked[obj_id=" + id+"][url=" + url +"]").attr("class","liked" );
        $(".popup-div").fadeOut();

    $.ajax({
         type: 'POST',
         url: "/" + url,
         data: "id=" +id + "&type=" + type,
         success: function(data){

             $('#' + 'like_count_' + url +'_' + id).html(data.like);
             $('#' + 'unlike_count_' + url +'_' + id).html(data.unlike);
             $('#' + 'funny_count_' + url +'_' + id).html(data.funny);
             $('#' + 'angry_count_' + url +'_' + id).html(data.angry);
         }
    });
  });
});

//show div with smiles
$(document).ready(function() {
    $("img.liked, img.unliked, .popup-div").hover(function(){
        var id = $(this).attr("obj_id");

        var url = $(this).attr("url");


        $(".popup-div[obj_id=" + id+"][url=" + url +"]").show();
    }, function() {
        var id = $(this).attr("obj_id");
        var url = $(this).attr("url");
        $("#popup-div_" + url + "_" + id).hide();
    });

});


