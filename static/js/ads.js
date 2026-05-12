document.querySelectorAll(".ad-slider").forEach(function (slider) {
  let images = JSON.parse(slider.dataset.adImages || "[]");
  let adImage = slider.querySelector("img");
  let index = 0;

  if (!adImage || images.length === 0) {
    return;
  }

  adImage.src = images[index];

  if (images.length === 1) {
    return;
  }

  setInterval(function () {
    adImage.classList.add("ad-slide-out");

    setTimeout(function () {
      index = (index + 1) % images.length;
      adImage.src = images[index];
      adImage.classList.remove("ad-slide-out");
      adImage.classList.add("ad-slide-in");

      setTimeout(function () {
        adImage.classList.remove("ad-slide-in");
      }, 650);
    }, 650);
  }, 4000);
});
