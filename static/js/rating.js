// Select all stars
const stars = document.querySelectorAll(".star");

// Add event listeners to each star
stars.forEach((star) => {
  star.addEventListener("click", () => {
    // Get the rating value of the clicked star
    const ratingValue = parseInt(star.getAttribute("data-value"));

    // Highlight all stars up to the clicked one
    stars.forEach((s) => {
      const starValue = parseInt(s.getAttribute("data-value"));
      if (starValue <= ratingValue) {
        s.classList.add("active");
      } else {
        s.classList.remove("active");
      }
    });
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const stars = document.querySelectorAll(".star");
  const commentBox = document.querySelector(".comment-box");
  const submitBtn = document.querySelector(".submit-btn");
  let selectedRating = 0;

  // Handle star click to set rating
  stars.forEach((star) => {
    star.addEventListener("click", function () {
      selectedRating = parseInt(star.getAttribute("data-value"));
      stars.forEach((s, index) => {
        s.classList.toggle("selected", index < selectedRating);
      });
    });
  });

  // Handle submission
  submitBtn.addEventListener("click", async function () {
    const comment = commentBox.value.trim();
    if (selectedRating === 0 || !comment) {
      alert("يرجى اختيار تقييم وكتابة تعليق.");
      return;
    }

    try {
      const response = await fetch("/submit_review", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          stars_count: selectedRating,
          text: comment,
        }),
      });
      if (response.ok) {
        alert("تم إرسال تقييمك بنجاح! شكراً لك.");
        commentBox.value = "";
        stars.forEach((star) => star.classList.remove("selected"));
        selectedRating = 0;
      } else {
        alert("حدث خطأ، حاول مرة أخرى.");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("تعذر الاتصال بالخادم.");
    }
  });
});
