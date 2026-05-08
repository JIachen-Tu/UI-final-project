$(document).ready(function () {
    $("#next-btn").on("click", function () {
        const nextUrl = $(this).data("next-url");
        const lessonId = $(this).data("lesson-id");

        $.ajax({
            type: "POST",
            url: "/learn/last_page",
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({ id: lessonId }),
            complete: function () {
                window.location.href = nextUrl;
            }
        });
    });
});
