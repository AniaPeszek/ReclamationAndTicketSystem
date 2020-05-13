$(document).ready(function () {
    $('.edit-note-pre').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget)
        var content = button.data('note_content')

        var modal = $(this)
        modal.find('.modal-body textarea').val(content)
    })

    $('.edit-note').click(function () {
        var note_id = $(this).val();
        var content = $('#note-text-'+ note_id).val();
        console.log(content);
        console.log(JSON.stringify({'note_text':content}));
        var edit_note = $.ajax({
            "url": "/edit_note/" + note_id,
            "type": "POST",
            data: JSON.stringify({'note_text':content}),
            contentType: "application/json; charset=utf-8",
            dataType: "json",

            success: function (response) {
                console.log(response);
                $('#note_content'+note_id).html(content);
            },
            error: function (error) {
                console.log(error);
            }
        })
    })

    $(".delete-note").click(function () {
        var note_id = $(this).val();
        $('.note' + note_id).hide();

        var deleteNote = $.ajax({
            "url": "/delete_note/" + note_id,
            "type": "DELETE",

            success: function (response) {
                console.log(response);
            },
            error: function (error) {
                console.log(error);
            }
        });
    })
})