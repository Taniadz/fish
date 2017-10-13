function delete_comment(e, id, url) {

    e.preventDefault()
    if (confirm('Are you sure you want to save this thing into the database?')) {

        $.post( url, {id:id},function( data ) {
            $(".one_comment#comment" + id).html(data.deleted);
             $("#edit" + id).text(data.nodelet);


        });
} else {
    // Do nothing!
}

}

function edit_comment(event, id, url) {
    event.preventDefault();

    $.ajax({
        type: "GET",
        url: url + '/' + id,

        success: function (data) {
            $(".one_comment#comment" + id).html(data.form);
            $("#edit" + id).text(data.noedit);

        },
        error: function (xhr, str) {
            alert('Mistake ' + xhr.responseCode);
        }
    });
};
