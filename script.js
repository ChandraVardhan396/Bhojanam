/**
 * Senior Animation Engineering - GSAP + ScrollTrigger Cinematic Model
 * Focuses on sequential, high-fidelity scroll entrance with smooth reverse.
 */

// Initialize GSAP & ScrollTrigger
gsap.registerPlugin(ScrollTrigger);

function updateMain(imagePath, isClover) {
  const mainImg = document.getElementById('mainImg');
  if (!mainImg) return;

  // Kill any existing floating animations on the image during swap
  gsap.killTweensOf(mainImg.parentNode);

  gsap.to(mainImg, {
    opacity: 0,
    duration: 0.3,
    onComplete: () => {
      mainImg.src = imagePath;
      if (isClover) {
        mainImg.classList.add('clover-center');
      } else {
        mainImg.classList.remove('clover-center');
      }
      gsap.to(mainImg, {
        opacity: 1,
        duration: 0.3,
        onComplete: () => {
          // Resume subtle floating after swap if settled
          if (document.querySelector('.hero-visual').classList.contains('settled')) {
            initAmbientFloating();
          }
        }
      });
    }
  });
}

function downloadFile() {
  const downloadLink = "https://drive.google.com/file/d/1M2y_OcSnpowhouPG2_cbJ7vtUzIROkDF/view?usp=drive_link";
  window.location.href = downloadLink;
}

// Store floating animations to manage them during scroll
let floatingTweens = [];

/**
 * GSAP CINEMATIC SCROLL TIMELINE
 */
function initCinematicScroll() {
  const mainImage = document.querySelector('.anim-main');
  const plates = document.querySelectorAll('.anim-plate');
  const downloadBtn = document.querySelector('.anim-download');
  const decorators = document.querySelectorAll('.anim-deco');
  const visualContainer = document.querySelector('.hero-visual');

  // Create Parent Timeline
  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: ".hero",
      scroller: ".glass-container",
      start: "top 75%",
      end: "bottom 25%",
      toggleActions: "play reverse play reverse",
      onEnter: () => visualContainer.classList.remove('settled'),
      onLeaveBack: () => {
        visualContainer.classList.remove('settled');
        stopAmbientFloating();
      },
      onComplete: () => {
        visualContainer.classList.add('settled');
        initAmbientFloating();
      }
    }
  });

  // Ensure items are technically visible to GSAP (removes visibility: hidden)
  gsap.set([mainImage, plates, downloadBtn, decorators], { autoAlpha: 1 });

  // --- PHASE 1: CENTER LOCK (FOCUS) ---
  // Main hero image moves from right-offset to its visual center
  tl.fromTo(mainImage,
    { x: 80, scale: 0.85, opacity: 0 },
    { x: 0, scale: 1, opacity: 1, duration: 1.2, ease: "power2.out" }
  );

  // --- PHASE 2: ORBITAL PLATE ARRANGEMENT ---
  // Plates gracefully move from outside inwards with a staggered curve
  tl.fromTo(plates,
    {
      scale: 0.6,
      opacity: 0,
      x: (i) => i === 0 ? -120 : 120, // Exploded horizontal
      y: (i) => i === 0 ? 100 : 150,   // Exploded vertical
    },
    {
      scale: 1,
      opacity: 1,
      x: 0,
      y: 0,
      duration: 1.2,
      stagger: 0.2,
      ease: "back.out(1.2)"
    },
    "-=0.7" // Staggered overlap with main image finish
  );

  // --- PHASE 3: CTA REVEAL ---
  // Button slides up from below the formed group
  tl.fromTo(downloadBtn,
    { y: 80, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.9, ease: "power4.out" },
    "-=0.4"
  );

  // --- PHASE 4: AMBIENT DECORATORS ---
  tl.fromTo(decorators,
    { scale: 0.5, opacity: 0 },
    {
      scale: 1,
      opacity: (i, el) => el.classList.contains('leaf') ? 0.45 : 0.7,
      duration: 1,
      stagger: 0.1,
      ease: "power2.out"
    },
    "-=0.8"
  );

  // --- DOWNLOAD SECTION TIMELINE ---
  const dlContainer = document.querySelector('.download-container');
  const dlVisuals = dlContainer.querySelectorAll('.anim-dl-visual');
  const dlText = dlContainer.querySelector('.anim-dl-text');
  const dlButton = dlContainer.querySelector('.anim-dl-button');
  const dlBox = dlContainer.querySelector('.anim-dl-box');
  const dlDecos = dlContainer.querySelectorAll('.anim-dl-deco');

  const dlTl = gsap.timeline({
    scrollTrigger: {
      trigger: ".download-section",
      scroller: ".glass-container",
      start: "top 70%",
      toggleActions: "play none none reverse"
    }
  });

  gsap.set([dlVisuals, dlText, dlButton, dlBox, dlDecos], { autoAlpha: 1 });

  dlTl.fromTo(dlVisuals,
    { scale: 0.7, x: -100, opacity: 0 },
    { scale: 1, x: 0, opacity: 1, duration: 1.2, stagger: 0.2, ease: "power2.out" }
  );

  dlTl.fromTo(dlText,
    { y: 50, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.8 },
    "-=0.8"
  );

  dlTl.fromTo(dlButton,
    { scale: 0.8, opacity: 0 },
    { scale: 1, opacity: 1, duration: 0.6, ease: "back.out(1.7)" },
    "-=0.4"
  );

  dlTl.fromTo(dlBox,
    { y: 30, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.8 },
    "-=0.4"
  );

  dlTl.fromTo(dlDecos,
    { scale: 0, opacity: 0 },
    { scale: 1, opacity: (i, el) => el.classList.contains('dl-leaf') ? 0.5 : 0.7, duration: 0.8, stagger: 0.2 },
    "-=1"
  );

  // --- FEATURES SECTION TIMELINE ---
  const featureCards = document.querySelectorAll('.anim-feature');
  const featuresHeader = document.querySelector('.features-header');

  const featuresTl = gsap.timeline({
    scrollTrigger: {
      trigger: ".features-section",
      scroller: ".glass-container",
      start: "top 60%",
      toggleActions: "play none none reverse"
    }
  });

  gsap.set([featureCards, featuresHeader], { autoAlpha: 1 });

  featuresTl.fromTo(featuresHeader,
    { y: 50, opacity: 0 },
    { y: 0, opacity: 1, duration: 1, ease: "power2.out" }
  );

  featuresTl.fromTo(featureCards,
    { y: 60, opacity: 0, scale: 0.9 },
    {
      y: 0,
      opacity: 1,
      scale: 1,
      duration: 1,
      stagger: 0.15,
      ease: "power3.out"
    },
    "-=0.6"
  );

  // --- HOW TO USE SECTION TIMELINE ---
  const howSteps = document.querySelectorAll('.anim-how');
  const howHeader = document.querySelector('.how-header');

  const howTl = gsap.timeline({
    scrollTrigger: {
      trigger: ".how-to-use-section",
      scroller: ".glass-container",
      start: "top 60%",
      toggleActions: "play none none reverse"
    }
  });

  gsap.set([howSteps, howHeader], { autoAlpha: 1 });

  howTl.fromTo(howHeader,
    { y: 50, opacity: 0 },
    { y: 0, opacity: 1, duration: 1, ease: "power2.out" }
  );

  howTl.fromTo(howSteps,
    { x: -50, opacity: 0 },
    {
      x: 0,
      opacity: 1,
      duration: 0.8,
      stagger: 0.2,
      ease: "power2.out"
    },
    "-=0.5"
  );
}

/**
 * AMBIENT FLOATING ANIMATIONS
 * Adds a high-fidelity "alive" feel after the entrance sequence.
 */
function initAmbientFloating() {
  stopAmbientFloating(); // Clean start

  // Hero Section
  floatingTweens.push(
    gsap.to(".main-portrait-circle", {
      y: -15,
      duration: 5,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut"
    })
  );

  floatingTweens.push(
    gsap.to(".plate-1", {
      y: -12,
      x: -5,
      duration: 4,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut",
      delay: 0.2
    })
  );

  floatingTweens.push(
    gsap.to(".plate-2", {
      y: -10,
      x: 5,
      duration: 6,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut",
      delay: 0.5
    })
  );

  // Download Section
  floatingTweens.push(
    gsap.to(".large-plate-wrapper", { y: -10, duration: 5, repeat: -1, yoyo: true, ease: "sine.inOut" })
  );
  floatingTweens.push(
    gsap.to(".small-plate-wrapper", { y: 10, x: 5, duration: 4, repeat: -1, yoyo: true, ease: "sine.inOut" })
  );
}

function stopAmbientFloating() {
  floatingTweens.forEach(tween => tween.kill());
  floatingTweens = [];
}

document.addEventListener("DOMContentLoaded", () => {
  // Bind standard download buttons
  const legacyDownload = document.getElementById("downloadBtn");
  if (legacyDownload) legacyDownload.addEventListener("click", downloadFile);

  // Start Cinematic Entrance
  initCinematicScroll();
});
