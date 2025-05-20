/**
 * 맛집 리뷰 랭킹 - 메인 JavaScript 파일
 */

// DOM 로드 완료 후 실행
document.addEventListener("DOMContentLoaded", function () {
  // 툴팁 초기화
  const tooltipTriggerList = document.querySelectorAll(
    '[data-bs-toggle="tooltip"]'
  );
  if (tooltipTriggerList.length > 0) {
    const tooltipList = [...tooltipTriggerList].map(
      (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl)
    );
  }

  // 별점 선택 기능 초기화
  initRatingStars();

  // 좋아요 버튼 이벤트 처리
  initLikeButtons();

  // 이미지 업로드 미리보기 초기화
  initImagePreview();

  // 온도 슬라이더 초기화
  initTemperatureSlider();

  // 검색 자동완성 초기화
  initSearchAutocomplete();

  // 스크롤 시 네비게이션바 그림자 효과
  initNavbarScrollEffect();
});

/**
 * 별점 선택 기능 초기화
 */
function initRatingStars() {
  const ratingStars = document.querySelector(".rating-stars");
  if (!ratingStars) return;

  const stars = ratingStars.querySelectorAll(".star");
  const ratingInput = document.getElementById("rating");

  // 별점 초기화 (수정 시)
  const initialRating = ratingInput.value;
  if (initialRating) {
    updateStars(initialRating);
  }

  stars.forEach((star) => {
    // 호버 효과
    star.addEventListener("mouseenter", function () {
      const value = this.getAttribute("data-value");
      updateStars(value, true);
    });

    // 클릭 이벤트
    star.addEventListener("click", function () {
      const value = this.getAttribute("data-value");
      ratingInput.value = value;
      updateStars(value);
    });
  });

  // 별점 영역에서 마우스 떠날 때
  ratingStars.addEventListener("mouseleave", function () {
    const currentRating = ratingInput.value || 0;
    updateStars(currentRating);
  });

  // 별점 UI 업데이트 함수
  function updateStars(value, isHover = false) {
    stars.forEach((star) => {
      const starValue = parseInt(star.getAttribute("data-value"));
      const icon = star.querySelector("i");

      if (starValue <= value) {
        icon.classList.remove("far");
        icon.classList.add("fas");
      } else {
        icon.classList.remove("fas");
        icon.classList.add("far");
      }
    });
  }
}

/**
 * 좋아요 버튼 이벤트 처리
 */
function initLikeButtons() {
  const likeButtons = document.querySelectorAll(".like-button");

  likeButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const reviewId = this.getAttribute("data-review-id");
      const isLiked = this.getAttribute("data-liked") === "true";
      const likeCount = this.querySelector(".like-count");
      const likeIcon = this.querySelector("i");

      // CSRF 토큰 가져오기
      const csrfToken = document.querySelector(
        'input[name="csrf_token"]'
      )?.value;

      fetch(`/review/like/${reviewId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        credentials: "same-origin",
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            if (data.liked) {
              likeIcon.classList.remove("far");
              likeIcon.classList.add("fas");
              likeCount.textContent = parseInt(likeCount.textContent) + 1;
              this.setAttribute("data-liked", "true");
            } else {
              likeIcon.classList.remove("fas");
              likeIcon.classList.add("far");
              likeCount.textContent = parseInt(likeCount.textContent) - 1;
              this.setAttribute("data-liked", "false");
            }
          } else {
            alert(data.message || "좋아요 처리 중 오류가 발생했습니다.");
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          alert("요청 처리 중 오류가 발생했습니다.");
        });
    });
  });
}

/**
 * 이미지 업로드 미리보기 초기화
 */
function initImagePreview() {
  const imageInput = document.getElementById("images");
  if (!imageInput) return;

  const imagePreviewContainer = document.getElementById(
    "image-preview-container"
  );

  imageInput.addEventListener("change", function () {
    imagePreviewContainer.innerHTML = "";

    if (this.files.length > 5) {
      alert("이미지는 최대 5장까지 업로드 가능합니다.");
      this.value = "";
      return;
    }

    Array.from(this.files).forEach((file, index) => {
      const reader = new FileReader();

      reader.onload = function (e) {
        const previewDiv = document.createElement("div");
        previewDiv.className = "col-auto image-preview";
        previewDiv.innerHTML = `
                    <img src="${e.target.result}" alt="미리보기 ${
          index + 1
        }" class="img-thumbnail">
                    <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 remove-image" data-index="${index}">
                        <i class="fas fa-times"></i>
                    </button>
                `;
        imagePreviewContainer.appendChild(previewDiv);

        // 이미지 삭제 버튼 이벤트
        previewDiv
          .querySelector(".remove-image")
          .addEventListener("click", function () {
            // FileList는 직접 수정할 수 없으므로, 새 input을 생성하여 처리
            const dt = new DataTransfer();
            const files = imageInput.files;
            const removeIndex = parseInt(this.getAttribute("data-index"));

            for (let i = 0; i < files.length; i++) {
              if (i !== removeIndex) {
                dt.items.add(files[i]);
              }
            }

            imageInput.files = dt.files;
            previewDiv.remove();

            // 남은 이미지들의 인덱스 업데이트
            document.querySelectorAll(".remove-image").forEach((btn, idx) => {
              btn.setAttribute("data-index", idx);
            });
          });
      };

      reader.readAsDataURL(file);
    });
  });

  // 영수증 이미지 미리보기
  const receiptInput = document.getElementById("receipt_image");
  if (!receiptInput) return;

  const receiptPreviewBox = document.querySelector(".receipt-preview-box");
  const receiptPreview = document.getElementById("receipt-preview");

  receiptInput.addEventListener("change", function () {
    if (this.files && this.files[0]) {
      const reader = new FileReader();

      reader.onload = function (e) {
        receiptPreview.src = e.target.result;
        receiptPreviewBox.classList.remove("d-none");
      };

      reader.readAsDataURL(this.files[0]);
    } else {
      receiptPreviewBox.classList.add("d-none");
    }
  });

  // 영수증 이미지 삭제 버튼
  const removeReceiptBtn = document.querySelector(".remove-receipt");
  if (removeReceiptBtn) {
    removeReceiptBtn.addEventListener("click", function () {
      receiptInput.value = "";
      receiptPreviewBox.classList.add("d-none");
    });
  }
}

/**
 * 온도 슬라이더 초기화
 */
function initTemperatureSlider() {
  const temperatureSlider = document.getElementById("temperatureSlider");
  if (!temperatureSlider) return;

  const temperatureValue = document.getElementById("temperatureValue");

  temperatureSlider.addEventListener("input", function () {
    temperatureValue.textContent = this.value + "℃";
  });

  // 온도 평가 제출 버튼
  const submitRatingBtn = document.getElementById("submitRating");
  if (!submitRatingBtn) return;

  submitRatingBtn.addEventListener("click", function () {
    const temperature = temperatureSlider.value;
    const feedback = document.getElementById("reviewerFeedback").value;
    const reviewerId = this.getAttribute("data-reviewer-id");

    // CSRF 토큰 가져오기
    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;

    // AJAX로 온도 평가 제출
    fetch(`/review/rate_reviewer/${reviewerId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({
        temperature: temperature,
        feedback: feedback,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // 모달 닫기
          const modal = bootstrap.Modal.getInstance(
            document.getElementById("rateReviewerModal")
          );
          modal.hide();

          // 성공 메시지 표시
          alert("리뷰어 평가가 성공적으로 제출되었습니다.");

          // 페이지 새로고침 (온도 반영)
          location.reload();
        } else {
          alert(data.message || "평가 제출 중 오류가 발생했습니다.");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("요청 처리 중 오류가 발생했습니다.");
      });
  });
}

/**
 * 검색 자동완성 초기화
 */
function initSearchAutocomplete() {
  const searchInput = document.querySelector('input[name="query"]');
  if (!searchInput) return;

  // 검색어 입력 시 실시간 추천 검색어 목록 표시
  searchInput.addEventListener(
    "input",
    debounce(function () {
      const query = this.value.trim();
      if (query.length < 2) return; // 2글자 이상 입력 시에만 작동

      fetch(`/api/search/autocomplete?query=${encodeURIComponent(query)}`)
        .then((response) => response.json())
        .then((data) => {
          // 자동완성 목록 UI 업데이트 로직...
        })
        .catch((error) => console.error("Error:", error));
    }, 300)
  );
}

/**
 * 스크롤 시 네비게이션바 그림자 효과
 */
function initNavbarScrollEffect() {
  const navbar = document.querySelector(".navbar");
  if (!navbar) return;

  window.addEventListener("scroll", function () {
    if (window.scrollY > 10) {
      navbar.classList.add("shadow");
    } else {
      navbar.classList.remove("shadow");
    }
  });
}

/**
 * 디바운스 함수 - 연속적인 이벤트 발생 시 마지막 이벤트만 처리
 */
function debounce(func, delay) {
  let timeout;
  return function () {
    const context = this;
    const args = arguments;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), delay);
  };
}

/**
 * 플래시 메시지 자동 숨김
 */
(function () {
  const flashMessages = document.querySelectorAll(".alert-dismissible");
  flashMessages.forEach((message) => {
    setTimeout(function () {
      const alert = new bootstrap.Alert(message);
      alert.close();
    }, 5000);
  });
})();
