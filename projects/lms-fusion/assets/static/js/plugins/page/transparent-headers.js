export class TransparentHeadersHandler {
    constructor() {
        console.log('✨ Transparent headers handler created');
    }

    init() {
        // Initialize transparent-light headers
        if (document.querySelector(".transparent-light")) {
            window.addEventListener("scroll", () => {
                const headers = document.querySelectorAll(".header.sticky-autohide, .header.sticky");
                headers.forEach(header => {
                    header.classList.toggle("transparent-light", window.pageYOffset <= 10);
                });
            });
        }
        
        // Initialize transparent-dark headers
        if (document.querySelector(".transparent-dark")) {
            window.addEventListener("scroll", () => {
                const headers = document.querySelectorAll(".header.sticky-autohide, .header.sticky");
                headers.forEach(header => {
                    header.classList.toggle("transparent-dark", window.pageYOffset <= 10);
                });
            });
        }
    }
}