document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form");
    const input = document.getElementById("chat-input");
    const windowEl = document.getElementById("chat-window");

    function appendBubble(text, type) {
        const div = document.createElement("div");
        div.className = `chat-bubble ${type}`;
        div.innerHTML = text;
        windowEl.appendChild(div);
        windowEl.scrollTop = windowEl.scrollHeight;
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const message = input.value.trim();
        if (!message) return;

        appendBubble(message, "user");
        input.value = "";

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({message})
            });
            const data = await res.json();
            appendBubble(data.reply, "bot");
        } catch (err) {
            appendBubble("Sorry, something went wrong. Please try again.", "bot");
        }
    });
});
