import streamlit as st

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="Game Cá Lớn Nuốt Cá Bé 3D", page_icon="🐠", layout="centered")

st.title("🐠 Cá Lớn Nuốt Cá Bé 3D (Premium)")
st.caption("Phiên bản đồ họa 3D uốn lượn sinh động tích hợp mượt mà trên Streamlit!")

with st.sidebar:
    st.header("🎮 Hướng dẫn")
    st.markdown("""
    - **Di chuyển chuột**: Cá của bạn sẽ bơi, uốn đuôi và nghiêng mình theo con trỏ chuột.
    - **Luật chơi**: Ăn các sinh vật nhỏ hơn để tiến hóa to lớn hơn. Né các quái vật khổng lồ!
    """)
    st.write("---")
    st.info("Game chạy bằng đồ họa WebGL tăng tốc phần cứng trực tiếp trên trình duyệt của bạn.")

# Mã HTML5, Three.js nâng cấp mô hình cá 3D
game_premium_3d_html = """
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
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        }
        #uiPanel {
            position: absolute;
            top: 20px;
            left: 20px;
            color: #ffffff;
            font-size: 18px;
            font-weight: bold;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.9);
            pointer-events: none;
            background: rgba(25, 42, 86, 0.4);
            padding: 10px 15px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        #gameOverScreen {
            display: none;
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(6, 18, 36, 0.9);
            color: white;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            z-index: 10;
        }
        #restartBtn {
            background: linear-gradient(45deg, #ff7675, #d63031);
            color: white;
            border: none;
            padding: 14px 32px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 30px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(214, 48, 49, 0.4);
            transition: 0.3s;
            margin-top: 20px;
        }
        #restartBtn:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(214, 48, 49, 0.6);
        }
    </style>
    <!-- Nhúng Three.js -->
    <script src="https://cloudflare.com"></script>
</head>
<body>

    <div id="canvasContainer">
        <div id="uiPanel">
            <div id="scoreLabel">✨ Điểm: 0</div>
            <div id="sizeLabel">📏 Kích thước: 1.0m</div>
        </div>
        
        <div id="gameOverScreen">
            <h1 style="color: #ff7675; font-size: 42px; margin: 0 0 10px 0; text-shadow: 2px 2px 5px rgba(0,0,0,0.5);">BẠN ĐÃ BỊ NUỐT CHỬNG!</h1>
            <p style="font-size: 18px; color: #a4b0be;">Hãy cẩn thận hơn với những bóng ma đại dương...</p>
            <h2 id="finalScore" style="color: #f5cd79; margin-top: 5px;">Điểm số đạt được: 0</h2>
            <button id="restartBtn" onclick="resetGame()">Hồi Sinh Ngay 🔄</button>
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

        // HÀM TẠO MÔ HÌNH CÁ 3D CAO CẤP VÀ ĐẸP MẮT (Hình dáng giống cá thật)
        function createPremiumFish(colorHex, scaleSize, isPlayer = false) {
            const fishGroup = new THREE.Group();

            // Chất liệu da cá có độ bóng và phản chiếu ánh sáng nước tốt hơn
            const fishMaterial = new THREE.MeshStandardMaterial({ 
                color: colorHex, 
                roughness: 0.2, 
                metalness: 0.3,
                flatShading: false
            });

            // 1. Thân cá dáng thon (Dùng khối Cylinder thon 2 đầu hoặc kết hợp Sphere biến dạng rộng)
            const bodyGeo = new THREE.SphereGeometry(1, 32, 32);
            bodyGeo.scale(2.4, 1.1, 0.4); // Kéo dài ngang, thu hẹp bề dày hai bên mặt cá
            const body = new THREE.Mesh(bodyGeo, fishMaterial);
            fishGroup.add(body);

            // 2. Vây lưng cá (Dạng vây cá mập/cá ngừ đẹp mắt)
            const dorsalFinGeo = new THREE.ConeGeometry(0.4, 1.0, 4);
            dorsalFinGeo.rotateZ(-Math.PI / 4); // Nghiêng vây về sau
            dorsalFinGeo.scale(1, 1, 0.2); // Làm dẹt vây
            const dorsalFin = new THREE.Mesh(dorsalFinGeo, fishMaterial);
            dorsalFin.position.set(-0.2, 0.9, 0);
            fishGroup.add(dorsalFin);

            // 3. Hai vây bơi bên hông (Vây ngực)
            const pectoralFinGeo = new THREE.ConeGeometry(0.3, 0.8, 4);
            pectoralFinGeo.rotateX(Math.PI / 3);
            pectoralFinGeo.scale(1, 1, 0.1);
            
            const finLeft = new THREE.Mesh(pectoralFinGeo, fishMaterial);
            finLeft.position.set(0.5, -0.3, 0.4);
            finLeft.name = "finLeft";
            fishGroup.add(finLeft);

            const finRight = finLeft.clone();
            finRight.position.z = -0.4;
            finRight.rotateX(-Math.PI * 2 / 3);
            finRight.name = "finRight";
            fishGroup.add(finRight);

            // 4. Khớp đuôi và Đuôi uốn lượn (Tách riêng để tạo chuyển động mềm mại)
            const tailGroup = new THREE.Group();
            tailGroup.position.x = -2.0; // Đặt tâm xoay khớp tại cuối đuôi
            tailGroup.name = "tailSegment";

            // Cánh đuôi lớn hình vầng trăng khuyết dẹt
            const finTailGeo = new THREE.ConeGeometry(0.8, 1.6, 4);
            finTailGeo.rotateZ(Math.PI / 2); 
            finTailGeo.scale(0.1, 1.4, 0.8);
            const finTail = new THREE.Mesh(finTailGeo, fishMaterial);
            finTail.position.x = -0.6;
            tailGroup.add(finTail);
            fishGroup.add(tailGroup);

            // 5. Mắt cá lồi bóng bẩy
            const eyeGeo = new THREE.SphereGeometry(0.18, 16, 16);
            const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.1 });
            const pupilMat = new THREE.MeshBasicMaterial({ color: 0x000000 });

            // Mắt trái
            const eyeL = new THREE.Mesh(eyeGeo, eyeMat); eyeL.position.set(1.4, 0.2, 0.3);
            const pupilL = new THREE.Mesh(new THREE.SphereGeometry(0.09, 8, 8), pupilMat); pupilL.position.set(1.5, 0.2, 0.38);
            fishGroup.add(eyeL, pupilL);

            // Mắt phải
            const eyeR = new THREE.Mesh(eyeGeo, eyeMat); eyeR.position.set(1.4, 0.2, -0.3);
            const pupilR = new THREE.Mesh(new THREE.SphereGeometry(0.09, 8, 8), pupilMat); pupilR.position.set(1.5, 0.2, -0.38);
            fishGroup.add(eyeR, pupilR);

            // Thiết lập tỉ lệ thu phóng tổng thể
            fishGroup.scale.set(scaleSize, scaleSize, scaleSize);
            
            // Lưu dữ liệu va chạm logic
            fishGroup.userData = { radius: scaleSize * 1.3, baseColor: colorHex };
            return fishGroup;
        }

        // Khởi tạo thế giới đại dương 3D
        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x112233); // Màu xanh thẳm của biển sâu
            scene.fog = new THREE.FogExp2(0x112233, 0.028); // Sương mù che các đối tượng ở xa cực đẹp

            camera = new THREE.PerspectiveCamera(55, 800 / 500, 0.1, 1000);
            camera.position.z = 24;

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(800, 500);
            container.appendChild(renderer.domElement);

            // Thêm các nguồn sáng nghệ thuật làm nổi bật khối 3D của cá
            const ambientLight = new THREE.AmbientLight(0x4477aa, 1.2);
            scene.add(ambientLight);

            const sunLight = new THREE.DirectionLight(0xffffff, 1.5);
            sunLight.position.set(5, 20, 10);
            scene.add(sunLight);

            // Đèn màu xanh ngọc chiếu từ dưới lên mô phỏng ánh sáng phản chiếu đại dương
            const rimLight = new THREE.DirectionLight(0x00a8ff, 0.6);
            rimLight.position.set(-5, -10, -5);
            scene.add(rimLight);

            // Cá của người chơi: Màu vàng cam cá vàng (Goldfish Neon) cực đẹp
            playerFish = createPremiumFish(0xff9f43, playerScale, true);
            scene.add(playerFish);

            container.addEventListener('mousemove', onMouseMove);
            animate();
        }

        function onMouseMove(event) {
            const rect = container.getBoundingClientRect();
            mouseX = ((event.clientX - rect.left) / 800) * 2 - 1;
            mouseY = -((event.clientY - rect.top) / 500) * 2 + 1;
        }

        // Sinh cá ngẫu nhiên bơi qua lại
        function spawnNPC() {
            if (!gameActive || npcFishes.length > 25) return;

            const fromLeft = Math.random() < 0.5;
            const posX = fromLeft ? -28 : 28;
            const posY = (Math.random() * 2 - 1) * 13;
            const posZ = (Math.random() * 2 - 1) * 2;

            // Đa dạng kích thước cá dựa theo người chơi
            const sizes = [0.3, 0.5, 0.7, 1.0, 1.4, 2.2, 3.8];
