// ================================================================
//   NAVIGATION - Slide navigation UI (floating buttons)
// ================================================================

export class SlideNavigator {
    constructor(dom, state, chatRenderer) {
        this.dom = dom;
        this.state = state;
        this.chatRenderer = chatRenderer;
    }

    setup() {
        this.dom.prevBtn.addEventListener('click', () => this.goToPrev());
        this.dom.nextBtn.addEventListener('click', () => this.goToNext());
    }

    goToPrev() {
        if (this.state.currentSlideIndex > 0) {
            this.state.currentSlideIndex--;
            this.chatRenderer.render(this.state.currentChatId);
        }
    }

    goToNext() {
        const chat = this.state.getCurrentChat();
        if (!chat) return;
        const slides = this.state.getSlides(chat);
        if (this.state.currentSlideIndex < slides.length - 1) {
            this.state.currentSlideIndex++;
            this.chatRenderer.render(this.state.currentChatId);
        }
    }
}