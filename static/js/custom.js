var swiper = new Swiper('.swiper-container', {
    spaceBetween: 10,
    slidesPerView: 1,
    autoplay: {
        delay: 3000,
    },
    loop: true,
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },
    pagination: {
        el: '.swiper-pagination',
        clickable: true,
    },
});
