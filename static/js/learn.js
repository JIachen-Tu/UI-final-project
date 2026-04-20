$(document).ready(function () {
    $("#next-btn").on("click", function () {
        const next = $(this).data("next");
        window.location.href = next === "quiz" ? "/quiz/1" : "/learn/" + next;
    });
});
