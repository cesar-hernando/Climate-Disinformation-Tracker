function makeMovable(el) {
    let offsetX = 0, offsetY = 0, isDragging = false;

    el.addEventListener("mousedown", (e) => {
        isDragging = true;
        offsetX = e.clientX - el.getBoundingClientRect().left;
        offsetY = e.clientY - el.getBoundingClientRect().top;
        el.style.transition = "none";
        el.style.cursor = "grabbing";
    });

    document.addEventListener("mousemove", (e) => {
        if (!isDragging) return;
        el.style.left = (e.clientX - offsetX) + "px";
        el.style.top = (e.clientY - offsetY) + "px";
        el.style.bottom = "auto";
        el.style.right = "auto";
    });

    document.addEventListener("mouseup", () => {
        isDragging = false;
        el.style.transition = "";
        el.style.cursor = "grab";
    });
}

// Observe DOM until element exists
const observer = new MutationObserver((mutations, obs) => {
    const el = document.querySelector(".alignment-filter");
    if (el) {
        makeMovable(el);
        obs.disconnect();
    }
});

observer.observe(document.body, { childList: true, subtree: true });
