$(document).ready(function () {
    $("#next-btn").on("click", function () {
        const next = $(this).data("next");
        const lessonId = $(this).data("lesson-id");

        //console.log("lesson_id: ",lessonId)

        if (next === "quiz") {
            $.ajax({
                type: "POST",
                url: "/learn/last_page",
                dataType: "json",
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({ id: lessonId }),
                success: function () {
                    window.location.href = "/quiz/1";
                },
                error: function () {
                    console.log("error:", xhr.status, xhr.responseText);
                    alert("save last page error");
                }
            });

            return;
        }

        window.location.href = next === "quiz" ? "/quiz/1" : "/learn/" + next;
    });
});
