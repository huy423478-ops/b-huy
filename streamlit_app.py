import streamlit as str

# Cấu hình trang giao diện Streamlit
str.set_page_config(page_title="Game Cá Lớn Nuốt Cá Bé", page_icon="🐟", layout="centered")

str.title("🐟 Game Cá Lớn Nuốt Cá Bé")
str.caption("Dự án game mini chạy mượt mà trực tiếp trên nền tảng Streamlit!")

# Thêm phần hướng dẫn chơi bằng Markdown của Streamlit
with str.sidebar:
    str.header("🎮 Hướng dẫn chơi")
    str.markdown("""
    1. **Di chuyển chuột** trên khung chơi game để điều khiển chú cá của bạn.
    2. Ăn những chú cá **nhỏ hơn** mình để tăng kích thước và điểm số.
    3. Tránh né những chú cá **to hơn** để không bị nuốt chửng.
    4. Nếu thua, hãy nhấn nút **Chơi lại** xuất hiện trên màn hình.
    """)
    str.write("---")
    str.info("Mẹo: Hãy kiên nhẫn ăn cá nhỏ trước khi chuyển sang săn cá vừa nhé!")

# Mã HTML5 và JavaScript xử lý logic game mượt mà trên trình duyệt
game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #f0f2f6;
            font-family: Arial, sans-serif;
        }
        canvas {
            background-color: #1e90ff;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            cursor: none; /* Ẩn con trỏ chuột thật */
        }
        #gameOverScreen {
            display: none;
            position: absolute;
            background: rgba(0, 0, 0, 0.75);
            color: white;
            text-align: center;
            padding: 30px;
            border-radius: 10px;
            width: 350px;
        }
        #restartBtn {
            background-color: #00ff7f;
            color: #000;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 15px;
        }
        #restartBtn:hover {
            background-color: #00cd63;
        }
    </style>
</head>
<body>

    <div style="position: relative;">
        <canvas id="gameCanvas" width="800" height="500"></canvas>
        <div id="gameOverScreen">
            <h2 style="color: #ff4b4b; margin-top:0;">GAME OVER</h2>
            <p>Bạn đã bị cá lớn nuốt chửng!</p>
            <h3 id="finalScore">Điểm số: 0</h3>
            <button id="restartBtn" onclick="resetGame()">Chơi Lại 🔄</button>
        </div>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const gameOverScreen = document.getElementById("gameOverScreen");
        const finalScoreText = document.getElementById("finalScore");

        // Khởi tạo thông số người chơi
        let player = {
            x: canvas.width / 2,
            y: canvas.height / 2,
            radius: 12,
            score: 0,
            color: "#00ff7f",
            isAlive: true
        };

        let npcList = [];
        let spawnTimer = 0;

        // Bắt sự kiện chuột di chuyển để lái cá
        canvas.addEventListener("mousemove", (e) => {
            if (!player.isAlive) return;
            const rect = canvas.getBoundingClientRect();
            player.x = e.clientX - rect.left;
            player.y = e.clientY - rect.top;
        });

        // Hàm tạo cá ngẫu nhiên bơi qua màn hình
        function spawnNPC() {
            const side = Math.random() < 0.5 ? "left" : "right";
            let x, speedX;
            if (side === "left") {
                x = -40;
                speedX = Math.random() * 3 + 1.5;
            } else {
                x = canvas.width + 40;
                speedX = -(Math.random() * 3 + 1.5);
            }

            const y = Math.random() * (canvas.height - 60) + 30;
            
            // Tỷ lệ kích thước ngẫu nhiên dựa theo cá người chơi hiện tại
            const sizeFactors = [0.5, 0.7, 0.9, 1.2, 1.5, 2.3];
            const chosenFactor = sizeFactors[Math.floor(Math.random() * sizeFactors.length)];
            const radius = Math.max(7, player.radius * chosenFactor);

            // Tạo màu sắc ngẫu nhiên rực rỡ
            const color = `hsl(${Math.random() * 360}, 85%, 55%)`;

            npcList.push({ x, y, radius, speedX, color });
        }

        // Hàm Reset trò chơi khi nhấn nút chơi lại
        function resetGame() {
            player = {
                x: canvas.width / 2,
                y: canvas.height / 2,
                radius: 12,
                score: 0,
                color: "#00ff7f",
                isAlive: true
            };
            npcList = [];
            spawnTimer = 0;
            gameOverScreen.style.display = "none";
            loop();
        }

        // Vòng lặp cập nhật Game chính
        function loop() {
            if (!player.isAlive) {
                finalScoreText.innerText = "Điểm số của bạn: " + player.score;
                // Định vị bảng thông báo giữa Canvas
                gameOverScreen.style.display = "block";
                gameOverScreen.style.top = (canvas.height / 2 - gameOverScreen.offsetHeight / 2) + "px";
                gameOverScreen.style.left = (canvas.width / 2 - gameOverScreen.offsetWidth / 2) + "px";
                return;
            }

            // Xóa màn hình cũ để vẽ khung hình mới
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Tạo cá định kỳ
            spawnTimer++;
            if (spawnTimer >= 35) {
                if (npcList.length < 20) spawnNPC();
                spawnTimer = 0;
            }

            // Cập nhật logic & Vẽ cá NPC
            for (let i = npcList.length - 1; i >= 0; i--) {
                let npc = npcList[i];
                npc.x += npc.speedX;

                // Xóa cá nếu bơi ra ngoài màn hình
                if (npc.x < -60 || npc.x > canvas.width + 60) {
                    npcList.splice(i, 1);
                    continue;
                }

                // Vẽ cá NPC (Hình tròn đại diện)
                ctx.beginPath();
                ctx.arc(npc.x, npc.y, npc.radius, 0, Math.PI * 2);
                ctx.fillStyle = npc.color;
                ctx.fill();
                ctx.closePath();

                // Tính va chạm giữa người chơi và cá NPC
                const dx = player.x - npc.x;
                const dy = player.y - npc.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < player.radius + npc.radius) {
                    if (player.radius >= npc.radius) {
                        // Cá lớn nuốt cá bé
                        player.radius += npc.radius * 0.12; // To lên
                        player.score += Math.floor(npc.radius); // Tăng điểm
                        npcList.splice(i, 1); // Xóa con cá bị ăn
                    } else {
                        // Người chơi bị ăn thịt
                        player.isAlive = false;
                    }
                }
            }

            // Vẽ Cá Người chơi
            ctx.beginPath();
            ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2);
            ctx.fillStyle = player.color;
            ctx.fill();
            ctx.closePath();

            // Vẽ mắt cá người chơi cho sống động
            ctx.beginPath();
            ctx.arc(player.x + player.radius/2, player.y - player.radius/3, player.radius/4, 0, Math.PI * 2);
            ctx.fillStyle = "#fff";
            ctx.fill();
            ctx.beginPath();
            ctx.arc(player.x + player.radius/2, player.y - player.radius/3, player.radius/8, 0, Math.PI * 2);
            ctx.fillStyle = "#000";
            ctx.fill();

            // Hiển thị Điểm số lên Canvas
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 18px Arial";
            ctx.fillText("Điểm số: " + player.score, 20, 35);
            ctx.fillText("Kích thước: " + Math.floor(player.radius), 20, 60);

            requestAnimationFrame(loop);
        }

        // Bắt đầu chạy game
        loop();
    </script>
</body>
</html>
"""

# Sử dụng component html của Streamlit để hiển thị game với chiều rộng và chiều cao phù hợp
str.components.v1.html(game_html, height=530, width=820)
