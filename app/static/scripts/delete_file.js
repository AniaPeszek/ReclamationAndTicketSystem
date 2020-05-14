$(document).ready(function () {
    $(".del-file").click(function () {
        var path = $(this).val();
        $(this).closest('.file-div').hide();

        var deleteFile = $.ajax({
            "url": "/delete_file/"+path,
            "type": "DELETE",

            success: function (response) {
                console.log(response);
            },
            error: function(error){
                console.log(error);
            }
        });
    })
})
