import streamlit as str

# Cấu hình giao diện Streamlit
str.set_page_config(page_title="Game Cá Lớn Nuốt Cá Bé 3D", page_icon="🦈", layout="centered")

str.title("🦈 Cá Lớn Nuốt Cá Bé 3D")
str.caption("Phiên bản đồ họa 3D không gian chiều sâu tích hợp mượt mà trên Streamlit!")

with str.sidebar:
    str.header("🎮 Cách Điều Khiển")
    str.markdown("""
    - **Di chuyển chuột**: Cá 3D của bạn sẽ bơi và uốn lượn theo con trỏ chuột trong không gian 3 chiều.
    - **Nguyên tắc**: Săn các con cá nhỏ hơn mình để lớn lên và né các quái vật đại dương to lớn!
    """)
    str.write("---")
    str.success("Game sử dụng đồ họa Three.js tăng tốc phần cứng nên cực kỳ mượt mà.")

# Mã HTML5, Three.js và JavaScript xử lý logic game 3D
game_3d_html = """
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
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow: hidden;
        }
        #canvasContainer {
            position: relative;
            width: 800px;
            height: 500px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        }
        /* UI Điểm số trên màn hình */
        #uiPanel {
            position: absolute;
            top: 20px;
            left: 20px;
            color: white;
            font-size: 18px;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
            pointer-events: none;
        }
        #gameOverScreen {
            display: none;
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(10, 25, 47, 0.85);
            color: white;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            z-index: 10;
        }
        #restartBtn {
            background: linear-gradient(45deg, #00f2fe, #4facfe);
            color: white;
            border: none;
            padding: 12px 28px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 25px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
            transition: 0.3s;
            margin-top: 15px;
        }
        #restartBtn:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(79, 172, 254, 0.6);
        }
    </style>
    <!-- Tích hợp thư viện Three.js bản stable qua CDN -->
    <script src="https://cloudflare.com"></script>
</head>
<body>

    <div id="canvasContainer">
        <div id="uiPanel">
            <div id="scoreLabel">Score: 0</div>
            <div id="sizeLabel">Size: 1.0m</div>
        </div>
        
        <div id="gameOverScreen">
            <h1 style="color: #ff4b4b; font-size: 40px; margin: 0 0 10px 0; text-shadow: 2px 2px 5px rgba(0,0,0,0.5);">GAME OVER</h1>
            <p style="font-size: 18px; margin-bottom: 5px;">Bạn đã bị quái vật đại dương nuốt chửng!</p>
            <h2 id="finalScore" style="color: #00f2fe; margin-top: 5px;">Điểm: 0</h2>
            <button id="restartBtn" onclick="resetGame()">Hồi Sinh Chơi Lại 🔄</button>
        </div>
    </div>

    <script>
        const container = document.getElementById('canvasContainer');
        const scoreLabel = document.getElementById('scoreLabel');
        const sizeLabel = document.getElementById('sizeLabel');
        const gameOverScreen = document.getElementById('gameOverScreen');
        const finalScore = document.getElementById('finalScore');

        let scene, camera, renderer;
        let playerFish, playerScale = 1.0, score = 0;
        let npcFishes = [];
        let mouseX = 0, mouseY = 0;
        let gameActive = true;
        let clock = new THREE.Clock();

        // Hàm tạo hình mô hình con cá 3D (Thân uốn, mắt, đuôi)
        function create3DFish(color, scaleSize, isPlayer = false) {
            const fishGroup = new THREE.Group();

            // 1. Thân cá (Hình elip 3D - Khối Capsule hoặc Sphere được co giãn)
            const bodyGeo = new THREE.SphereGeometry(1, 32, 16);
            bodyGeo.scale(2.0, 1.0, 0.5); // Kéo dài ra làm thân cá
            const bodyMat = new THREE.MeshStandardMaterial({ 
                color: color, 
                roughness: 0.3, 
                metalness: 0.1 
            });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            fishGroup.add(body);

            // 2. Đuôi cá (Hình nón dẹt)
            const tailGeo = new THREE.ConeGeometry(0.6, 1.2, 4);
            tailGeo.rotateZ(Math.PI / 2); // Xoay hướng nằm ngang
            tailGeo.scale(0.2, 1.5, 1.0);
            const tailMat = new THREE.MeshStandardMaterial({ color: color });
            const tail = new THREE.Mesh(tailGeo, tailMat);
            tail.position.x = -2.2; // Đặt ở phía sau thân
            tail.name = "tail"; // Đặt tên để tạo hiệu ứng vẫy đuôi
            fishGroup.add(tail);

            // 3. Mắt cá (2 bên trái phải)
            const eyeGeo = new THREE.SphereGeometry(0.2, 16, 16);
            const eyeMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
            const pupilMat = new THREE.MeshBasicMaterial({ color: 0x000000 });
            
            // Mắt trái
            const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
            eyeL.position.set(1.0, 0.3, 0.4);
            const pupilL = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 8), pupilMat);
            pupilL.position.set(1.1, 0.3, 0.5);
            fishGroup.add(eyeL, pupilL);

            // Mắt phải
            const eyeR = new THREE.Mesh(eyeGeo, eyeMat);
            eyeR.position.set(1.0, 0.3, -0.4);
            const pupilR = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 8), pupilMat);
            pupilR.position.set(1.1, 0.3, -0.5);
            fishGroup.add(eyeR, pupilR);

            // Thiết lập kích thước
            fishGroup.scale.set(scaleSize, scaleSize, scaleSize);
            
            // Lưu bán kính va chạm logic vào group
            fishGroup.userData = { radius: scaleSize * 1.2, baseColor: color };
            return fishGroup;
        }

        // Khởi tạo môi trường 3D
        function init() {
            scene = new THREE.Scene();
            // Đặt màu nền sương mù đại dương (Fog giúp tạo chiều sâu)
            scene.background = new THREE.Color(0x0a2342);
            scene.fog = new THREE.FogExp2(0x0a2342, 0.025);

            camera = new THREE.PerspectiveCamera(60, 800 / 500, 0.1, 1000);
            camera.position.z = 25; // Góc nhìn từ trên xuống bao quát không gian

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(800, 500);
            renderer.shadowMap.enabled = true;
            container.appendChild(renderer.domElement);

            // Thiết lập ánh sáng (Đèn mặt trời phía trên và ánh sáng môi trường đại dương)
            const ambientLight = new THREE.AmbientLight(0x336699, 1.5);
            scene.add(ambientLight);

            const dirLight = new THREE.DirectionLight(0xffffff, 1.2);
            dirLight.position.set(10, 20, 10);
            scene.add(dirLight);

            // Tạo cá người chơi (Màu xanh neon nổi bật)
            playerFish = create3DFish(0x00ffcc, playerScale, true);
            scene.add(playerFish);

            // Lắng nghe sự kiện chuột chuyển động trên container
            container.addEventListener('mousemove', onMouseMove);
            
            animate();
        }

        function onMouseMove(event) {
            const rect = container.getBoundingClientRect();
            // Chuẩn hóa tọa độ chuột từ -1 đến 1 để tương thích không gian 3D của Camera
            mouseX = ((event.clientX - rect.left) / 800) * 2 - 1;
            mouseY = -((event.clientY - rect.top) / 500) * 2 + 1;
        }

        // Hàm sinh ra các loại cá NPC ngẫu nhiên
        function spawnNPC() {
            if (!gameActive || npcFishes.length > 22) return;

            const fromLeft = Math.random() < 0.5;
            const posX = fromLeft ? -28 : 28;
            const posY = (Math.random() * 2 - 1) * 14;
            const posZ = (Math.random() * 2 - 1) * 3; // Dao động nhẹ ở trục sâu Z

            // Kích thước ngẫu nhiên đa dạng dựa trên kích thước người chơi
            const sizes = [0.4, 0.6, 0.8, 1.2, 1.6, 2.5, 3.5];
            const size = playerScale * sizes[Math.floor(Math.random() * sizes.length)];
            
            // Tạo màu sắc ngẫu nhiên rực rỡ cho sinh vật biển
            const colors = [0xff7675, 0xffeaa7, 0x9b59b6, 0xe67e22, 0x2ecc71, 0xe84393];
            const color = colors[Math.floor(Math.random() * colors.length)];

            const npc = create3DFish(color, size);
            npc.position.set(posX, posY, posZ);
            
            // Xác định vận tốc và hướng quay đầu của cá
            const speedX = fromLeft ? (Math.random() * 0.1 + 0.08) : -(Math.random() * 0.1 + 0.08);
            if (!fromLeft) {
                npc.rotation.y = Math.PI; // Quay mặt sang trái nếu xuất phát từ bên phải
            }

            npc.userData.speedX = speedX;
            scene.add(npc);
            npcFishes.push(npc);
        }

        // Hàm Khởi động lại Game khi thua
        function resetGame() {
            gameActive = true;
            score = 0;
            playerScale = 1.0;
            
            // Xóa cá cũ
            npcFishes.forEach(fish => scene.remove(fish));
            npcFishes = [];

            playerFish.scale.set(1, 1, 1);
            playerFish.userData.radius = 1.2;
            playerFish.position.set(0, 0, 0);

            scoreLabel.innerText = "Score: " + score;
            sizeLabel.innerText = "Size: 1.0m";
