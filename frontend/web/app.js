// Nếu dùng <script type="module" src="app.js"> trong HTML
// thì app.js sẽ import Firebase modular như dưới:

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.0/firebase-app.js";
import {
  getDatabase,
  ref,
  onValue,
  query,
  limitToLast
} from "https://www.gstatic.com/firebasejs/10.13.0/firebase-database.js";

// ================== 1. Firebase config & init ==================
// TODO: thay config này bằng config thật của project bạn
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  databaseURL: "https://YOUR_PROJECT_ID-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "XXXXXXX",
  appId: "1:XXXXXXX:web:YYYYYYYY"
};

const app = initializeApp(firebaseConfig);
const db = getDatabase(app);

// ================== 2. Cấu hình thiết bị & ref ==================

// deviceId phải trùng với device_id mà ESP32/MQTT gửi lên backend
// và backend đang lưu ở đường dẫn: warehouse_data/{device_id}, alerts/{device_id}
const deviceId = "esp32_test_01"; // hoặc "sim_001" tùy bạn dùng cái nào

const sensorRef = ref(db, `warehouse_data/${deviceId}`);
const alertsRef = query(ref(db, `alerts/${deviceId}`), limitToLast(5));

// ================== 3. Setup biểu đồ nhiệt độ (Chart.js) ==================

const ctx = document.getElementById("tempChart").getContext("2d");
let chart = new Chart(ctx, {
  type: "line",
  data: {
    labels: [],
    datasets: [
      {
        label: "Temperature (°C)",
        data: [],
        borderColor: "rgb(255, 99, 132)",
        tension: 0.2,
        pointRadius: 2
      }
    ]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 0
        }
      }
    }
  }
});

// ================== 4. Realtime alerts ==================

const alertList = document.getElementById("alert-list");

onValue(alertsRef, snap => {
  const v = snap.val();
  alertList.innerHTML = "";
  if (!v) return;

  // v là object {pushId: {...}}, chuyển thành array giá trị
  const arr = Object.values(v);

  arr.forEach(a => {
    const li = document.createElement("li");
    const ts = a.ts || a.iso_ts || "";
    li.textContent = (ts ? `[${ts}] ` : "") + (a.message || "");
    alertList.appendChild(li);
  });
});

// ================== 5. Realtime dữ liệu cảm biến cho biểu đồ ==================

onValue(sensorRef, snapshot => {
  const data = snapshot.val();
  if (!data) return;

  const items = Object.values(data);

  // Nếu muốn sort theo thời gian (đề phòng dữ liệu bị đảo)
  items.sort((a, b) => {
    const ta = new Date(a.iso_ts || a.timestamp || 0).getTime();
    const tb = new Date(b.iso_ts || b.timestamp || 0).getTime();
    return ta - tb;
  });

  const labels = [];
  const tempList = [];

  items.forEach(item => {
    // Backend đang lưu "iso_ts" chứ không phải "timestamp"
    const label = item.iso_ts || item.timestamp || "";
    labels.push(label);
    tempList.push(item.temperature ?? 0);
  });

  chart.data.labels = labels;
  chart.data.datasets[0].data = tempList;
  chart.update();
});
