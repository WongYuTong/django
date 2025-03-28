document.addEventListener("DOMContentLoaded", function () {
    // ✅ 載入導覽列
    fetch("nav.html")
        .then(response => response.text())
        .then(data => {
            document.getElementById("navbar-container").innerHTML = data;

            // ✅ 確保導覽列載入後綁定按鈕事件
            document.getElementById("homeBtn")?.addEventListener("click", function () {
                window.location.href = "index.html";
            });

            document.getElementById("appBtn")?.addEventListener("click", function () {
                alert("App 下載功能尚未開放！");
            });

            document.getElementById("loginBtn")?.addEventListener("click", function () {
                window.location.href = "login.html";
            });

            document.getElementById("exploreBtn")?.addEventListener("click", function () {
                window.location.href = "chat.html";
            });
        });

    // ✅ 聊天功能
    const chatBox = document.getElementById("chatBox");
    const userInput = document.getElementById("userInput");
    const sendBtn = document.getElementById("sendBtn");

    let isComposing = false; // 標記是否在輸入法組字中

    if (chatBox && userInput && sendBtn) {
        sendBtn.addEventListener("click", sendMessage);

        userInput.addEventListener("compositionstart", () => isComposing = true);
        userInput.addEventListener("compositionend", () => isComposing = false);

        userInput.addEventListener("keydown", function (event) {
            if (event.key === "Enter" && !isComposing) {
                event.preventDefault();
                sendMessage();
            }
        });
    }

    function sendMessage() {
        let userMessage = userInput.value.trim();
        if (userMessage === "") return;

        addMessage(userMessage, "user");
        userInput.value = "";
        userInput.focus();

        setTimeout(() => {
            addMessage("正在思考中...", "bot");

            setTimeout(() => {
                let response = getBotReply(userMessage);
                let botMessage = chatBox.querySelector(".ai-message:last-child");
                if (botMessage) {
                    botMessage.textContent = response;
                }
            }, 1000);
        }, 500);
    }

    function addMessage(text, sender) {
        let messageDiv = document.createElement("div");
        messageDiv.classList.add(sender === "user" ? "user-message" : "ai-message");
        messageDiv.textContent = text;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function getBotReply(message) {
        return "這是一個範例回應：「" + message + "」";
    }
});