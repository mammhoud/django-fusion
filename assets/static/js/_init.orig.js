// # not used
/*===============================================
  Portfolio Masonry
===============================================*/
var pMasonry = document.querySelector(".portfolio-masonry");

if (pMasonry) {
  imagesLoaded(pMasonry, function () {
    var pWrapper = $(".portfolio-masonry").isotope({
      itemSelector: ".portfolio-item",
      transitionDuration: 250 // 0.25 second
    });
    var filter = $(".filter ul li");

    // Portfolio Filter //
    filter.on("click", function () {
      var filterValue = $(this).attr("data-filter");
      pWrapper.isotope({ filter: filterValue });

      filter.removeClass("active");
      $(this).addClass("active");
    });
  });
}
/*===============================================
  8. Portfolio Grid
===============================================*/
var pGrid = document.querySelector(".portfolio-grid");

if (pGrid) {
  var mixer = mixitup('.portfolio-grid', {
    selectors: {
      target: '.portfolio-item'
    },
    animation: {
      duration: 250
    }
  });
}
/*===============================================
   Slider
===============================================*/
var owlSlider = document.querySelector(".owl-carousel");

if (owlSlider) {
  $(".owl-carousel").each(function () {
    var $carousel = $(this);

    var $defaults = {
      rewind: true,
      navText: ["<i class='bi bi-arrow-left-short'></i>", "<i class='bi bi-arrow-right-short'></i>"],
      autoHeight: true,
      autoplayTimeout: 4000,
      autoplaySpeed: 400,
      autoplayHoverPause: true,
      navSpeed: 300,
      dotsSpeed: 300
    }

    var $options = {
      items: $carousel.data("owl-items"),
      margin: $carousel.data("owl-margin"),
      loop: $carousel.data("owl-loop"),
      center: $carousel.data("owl-center"),
      nav: $carousel.data("owl-nav"),
      rewind: $carousel.data("owl-rewind"),
      dots: $carousel.data("owl-dots"),
      autoplay: $carousel.data("owl-autoplay")
    }

    var $responsive = {
      responsive: {
        0: {
          items: $carousel.data("owl-xs")
        },
        576: {
          items: $carousel.data("owl-sm")
        },
        768: {
          items: $carousel.data("owl-md")
        },
        992: {
          items: $carousel.data("owl-lg")
        },
        1200: {
          items: $carousel.data("owl-xl")
        }
      }
    }

    $carousel.owlCarousel($.extend($defaults, $options, $responsive));
  });
}
/*===============================================
   Blog Masonry
===============================================*/
var blogMasonry = document.querySelector(".blog-masonry");

if (blogMasonry) {
  imagesLoaded(blogMasonry, function () {
    var $blogMasonry = $(blogMasonry);
    $blogMasonry.masonry({
      itemSelector: '.blog-post-box'
    });
  });
}
/*===============================================
   Masonry
===============================================*/
var masonryGrid = document.querySelector(".masonry");

if (masonryGrid) {
  imagesLoaded(masonryGrid, function () {
    var $masonryGrid = $(masonryGrid);
    $masonryGrid.masonry({
      itemSelector: '.masonry-item'
    });
  });
}
// Lightbox - Gallery //
//
var $gallery = $(".gallery-wrapper");
if ($gallery.length) {
  $gallery.each(function () {
    var $this = $(this);
    $this.magnificPopup({
      delegate: 'a',
      removalDelay: '200',
      type: 'image',
      fixedContentPos: false,
      gallery: {
        enabled: true
      },
      image: {
        titleSrc: 'data-gallery-title'
      }
    });
  });
}
/*===============================================
   Parallax
===============================================*/
if ($windowWidth > 1200) {
  var parallaxBg = $(".parallax");

  if (parallaxBg.length) {
    parallaxBg.each(function () {
      $(this).parallaxie({
        speed: 0.2
      });
    });
  }
}
/*===============================================
  Countdown
===============================================*/
$(".countdown").each(function () {
  var finalDate = $(this).attr('data-countdown');

  $(this).countdown(finalDate, function (event) {
    $(this).html(event.strftime('%D days %H:%M:%S'));
  });
});
/*===============================================
  Accordion
===============================================*/
var accordionTitles = document.querySelectorAll(".accordion-title");
accordionTitles.forEach(function (accordionTitle) {
  accordionTitle.addEventListener("click", function () {
    var accordionList = accordionTitle.parentElement;
    var accordionContent = accordionTitle.nextElementSibling;

    if (accordionList.classList.contains("active")) {
      accordionList.classList.remove("active");
      accordionContent.style.maxHeight = null;
    } else {
      accordionList.classList.add("active");
      if (accordionTitle.closest(".accordion").classList.contains("single-open")) {
        var accordionItems = accordionTitle.closest(".accordion").querySelectorAll("li");
        accordionItems.forEach(function (item) {
          item.classList.remove("active");
        });
        accordionList.classList.add("active");
        accordionTitle.closest(".single-open").querySelectorAll(".accordion-content").forEach(function (content) {
          content.style.maxHeight = "0";
        });
      }
      accordionContent.style.maxHeight = accordionContent.scrollHeight + "px";
    }
  });
  //
  // Give max-height to Accordion's active content //
  //
  var accordion = accordionTitle.parentElement.closest(".accordion");
  if (accordion.querySelector("li.active")) {
    var accordionActiveContent = accordion.querySelector("li.active .accordion-content");
    var accordionHeight = accordionActiveContent.scrollHeight;
    accordionActiveContent.style.maxHeight = accordionHeight + "px";
  }
});
/*===============================================
  Animated Progress bar
===============================================*/
$(".animated-progress div").each(function () {
  $(this).appear(function () {
    $(this).css("width", $(this).attr("data-progress") + "%");
  }, { accX: 0, accY: -10 })
});
/*===============================================
  Easy Pie Chart
===============================================*/
$(".pie-chart").appear(function () {

  $(this).each(function () {
    $(this).easyPieChart({
      lineCap: 'square',
      onStep: function (from, to, percent) {
        $(this.el).find('.percent').text(Math.round(percent));
      }
    });
  });

}, { accX: 0, accY: -10 });


/*===============================================
  19. Google Maps
===============================================*/
var mapCanvas = $(".gmap");

if (mapCanvas.length) {
  var m, divId, initLatitude, initLongitude, map;

  for (var i = 0; i < mapCanvas.length; i++) {
    m = mapCanvas[i];

    initLatitude = m.dataset["latitude"];
    initLongitude = m.dataset["longitude"];
    divId = "#" + m["id"];

    map = new GMaps({
      el: divId,
      lat: initLatitude,
      lng: initLongitude,
      zoom: 16,
      scrollwheel: false,
      styles: [
        /* style your map at https://snazzymaps.com/editor and paste JSON here */
      ]
    });

    map.addMarker({
      lat: initLatitude,
      lng: initLongitude
    });
  }
}
/*===============================================
   Contact Form
===============================================*/
$(function () {
  $('#contact-form').on('submit', function (e) {
    e.preventDefault();

    $.ajax({
      type: "POST",
      url: "assets/php/contact-form.php", // PHP file ka path
      data: $(this).serialize(),
      dataType: "json",
      success: function (response) {
        var alertClass = response.class; // alert-success ya alert-danger
        var message = response.message;

        var alertBox = '<div class="' + alertClass + '">' + message + '</div>';

        $('.messages').html(alertBox);

        if (response.class === 'alert alert-success') {
          $('#contact-form')[0].reset(); // form reset karo success par
        }
      }
    });
  });
});
/*===============================================
  Cursor
===============================================*/
var customCursor = document.getElementById("cursor");

if (customCursor) {
  var cursor = document.getElementById("cursor");
  document.addEventListener('mousemove', function (e) {
    cursor.style.left = e.pageX + 'px';
    cursor.style.top = e.pageY + 'px';
  });

  var mouseElms = document.querySelectorAll("a, button, input, textarea, .accordion-title, .filter li");

  mouseElms.forEach(function (mouseElm) {
    mouseElm.addEventListener("mouseenter", function () {
      cursor.classList.add("scale-cursor");
    });
    mouseElm.addEventListener("mouseleave", function () {
      cursor.classList.remove("scale-cursor");
    });
  });
}


/*===============================================
  Page Scroll Progress
===============================================*/
var pageProgress = $(".page-progress-container");
if (pageProgress.length) {
  window.onscroll = function () { pageScrollFunction() };
  function pageScrollFunction() {
    var winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    var height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    var scrolled = (winScroll / height) * 100;
    document.getElementById("pageProgress").style.width = scrolled + "%";
  }
}


/*===============================================
  wiper
===============================================*/
var swiper = new Swiper(".hero-portfolio-slider", {
  slidesPerView: 1,
  spaceBetween: 30,
  // Responsive breakpoints
  breakpoints: {
    // when window width is >= 768px
    768: {
      slidesPerView: 2,
      spaceBetween: 30
    },
    // when window width is >= 992px
    992: {
      slidesPerView: 2,
      spaceBetween: 40
    },
    // when window width is >= 1200px
    1200: {
      slidesPerView: 2,
      spaceBetween: 50
    }
  },
  centeredSlides: true,
  grabCursor: true,
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
  },
});

//
// Sliding Text //
//
var swiper = new Swiper(".sliding-text", {
  slidesPerView: "auto",
  spaceBetween: 70,
  speed: 30000,
  loop: true,
  allowTouchMove: false,
  autoplay: {
    delay: 0,
    clickable: false,
    pauseOnMouseEnter: false,
    disableOnInteraction: false,
  },
});

//
// Sliding Text - Reverse //
//
var swiper = new Swiper(".sliding-text-reverse", {
  slidesPerView: "auto",
  spaceBetween: 70,
  speed: 30000,
  loop: true,
  allowTouchMove: false,
  autoplay: {
    delay: 0,
    clickable: false,
    pauseOnMouseEnter: false,
    disableOnInteraction: false,
    reverseDirection: true,
  },
});

/*===============================================
  Counter
===============================================*/
$(".counter").appear(function () {

  $(this).each(function () {
    $(this).prop("Counter", 0).animate({
      Counter: $(this).text()
    }, {
      duration: 2500,
      easing: "swing",
      step: function (now) {
        $(this).text(Math.ceil(now));
      }
    });
  });

}, { accX: 0, accY: -10 });
