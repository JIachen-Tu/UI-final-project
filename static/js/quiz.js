$(document).ready(function () {
    const quizContainer = $("#quiz-container");
    const quizId = quizContainer.data("quiz-id");
    const nextQuestion = quizContainer.data("next-question");

    $(".option-btn").on("click", function () {
        const userAnswer = $(this).text();

        $.ajax({
            type: "POST",
            url: "/record_answer",
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({ quiz_id: String(quizId), user_answer: userAnswer }),
            success: function () {
                window.location.href = nextQuestion === "end"
                    ? "/results"
                    : "/quiz/" + nextQuestion;
            }
        });
    });
});
