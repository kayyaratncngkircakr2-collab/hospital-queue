# =========================================================
# CELL 2 — ระบบจองคิวออนไลน์
# โรงพยาบาลค่ายวชิราวุธ จังหวัดนครศรีธรรมราช
# โครงงานจำลองสำหรับการศึกษา
# =========================================================

from flask import Flask, request, render_template_string, jsonify, Response
import threading
import os

from PIL import Image, ImageDraw

app = Flask(__name__)

# =========================================================
# ข้อมูลโครงงาน
# =========================================================

HOSPITAL_NAME = "โรงพยาบาลค่ายวชิราวุธ"
PROVINCE = "จังหวัดนครศรีธรรมราช"

CREATORS = [
    "กัญญารัตน์ จงไกรจักร์",
    "ณัฐวรา ถ่องแท้"
]

CLASS_NAME = "ม.4/3"
PORT = 5000


# =========================================================
# รายชื่อแผนกและแพทย์
# หมายเหตุ: เป็นข้อมูลจำลองสำหรับโครงงาน
# =========================================================

DEPARTMENTS = {
    "อายุรกรรม": [
        "นพ. กิตติพงษ์ (จำลอง)",
        "พญ. พิมพ์ชนก (จำลอง)"
    ],

    "ศัลยกรรม": [
        "นพ. ธนกร (จำลอง)",
        "พญ. ชนากานต์ (จำลอง)"
    ],

    "กุมารเวชกรรม": [
        "พญ. ณัฐชา (จำลอง)",
        "นพ. ภูวดล (จำลอง)"
    ],

    "ทันตกรรม": [
        "ทพ. ศุภชัย (จำลอง)",
        "ทพญ. วราภรณ์ (จำลอง)"
    ],

    "หู คอ จมูก": [
        "นพ. ปกรณ์ (จำลอง)",
        "พญ. สุภัสสรา (จำลอง)"
    ]
}


TIMES = [
    "08:30",
    "09:00",
    "09:30",
    "10:00",
    "10:30",
    "11:00"
]


# =========================================================
# เก็บข้อมูลการจอง
# =========================================================

bookings = []
next_queue = 1


# =========================================================
# สร้างไอคอนแอป
# =========================================================

os.makedirs("static", exist_ok=True)

icon = Image.new("RGB", (512, 512), "white")
draw = ImageDraw.Draw(icon)

draw.ellipse(
    (50, 50, 462, 462),
    outline="#17365d",
    width=20
)

draw.rectangle(
    (236, 120, 276, 392),
    fill="#17365d"
)

draw.rectangle(
    (120, 236, 392, 276),
    fill="#17365d"
)

icon.save("static/icon.png")


# =========================================================
# หน้าเว็บไซต์
# =========================================================

PAGE = """
<!DOCTYPE html>

<html lang="th">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width,
      initial-scale=1.0,
      maximum-scale=1.0">

<title>ระบบจองคิว - โรงพยาบาลค่ายวชิราวุธ</title>

<link rel="manifest" href="/manifest.json">

<meta name="theme-color" content="#17365d">

<meta name="mobile-web-app-capable" content="yes">

<meta name="apple-mobile-web-app-capable"
      content="yes">

<meta name="apple-mobile-web-app-title"
      content="จองคิว รพ.">

<link rel="apple-touch-icon"
      href="/static/icon.png">


<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f2f6fb;
    color: #17365d;
}

.header {
    background: #17365d;
    color: white;
    padding: 22px 15px;
    text-align: center;
}

.header h1 {
    margin: 0;
    font-size: 24px;
}

.header p {
    margin: 8px 0 0;
}

.container {
    width: 92%;
    max-width: 650px;
    margin: 20px auto;
}

.card {
    background: white;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

h2 {
    margin-top: 0;
}

label {
    display: block;
    margin-top: 12px;
    margin-bottom: 6px;
    font-weight: bold;
}

input,
select,
button {
    width: 100%;
    padding: 13px;
    border-radius: 10px;
    border: 1px solid #ccc;
    font-size: 16px;
}

button {
    background: #17365d;
    color: white;
    border: none;
    margin-top: 18px;
    font-weight: bold;
}

button:active {
    transform: scale(0.98);
}

.menu {
    display: grid;
    gap: 12px;
}

.menu a {
    display: block;
    text-decoration: none;
    text-align: center;
    background: #17365d;
    color: white;
    padding: 15px;
    border-radius: 12px;
}

.success {
    background: #e8f7ed;
    border: 1px solid #8bc79b;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
}

.queue {
    font-size: 32px;
    font-weight: bold;
    text-align: center;
    margin: 10px;
}

.booking {
    border: 1px solid #ddd;
    border-radius: 12px;
    padding: 12px;
    margin-top: 10px;
}

.small {
    color: #666;
    font-size: 14px;
}

</style>

</head>


<body>

<div class="header">

<h1>🏥 ระบบจองคิวออนไลน์</h1>

<p>{{ hospital }}</p>
<p>{{ province }}</p>

</div>


<div class="container">

{{ content | safe }}

</div>


<script>

if ("serviceWorker" in navigator) {

    window.addEventListener("load", function() {

        navigator.serviceWorker.register(
            "/service-worker.js"
        );

    });

}


function loadDoctors() {

    const department =
        document.getElementById("department");

    const doctor =
        document.getElementById("doctor");

    if (!department || !doctor) {
        return;
    }

    doctor.innerHTML =
        '<option value="">กำลังโหลด...</option>';

    if (!department.value) {

        doctor.innerHTML =
            '<option value="">-- เลือกแผนกก่อน --</option>';

        return;
    }

    fetch(
        "/doctors/" +
        encodeURIComponent(department.value)
    )

    .then(response => response.json())

    .then(data => {

        doctor.innerHTML =
            '<option value="">-- เลือกแพทย์ --</option>';

        data.forEach(function(name) {

            const option =
                document.createElement("option");

            option.value = name;
            option.textContent = name;

            doctor.appendChild(option);

        });

    });

}

</script>

</body>

</html>
"""


# =========================================================
# Manifest สำหรับ PWA
# =========================================================

@app.route("/manifest.json")
def manifest():

    data = """
{
    "name": "ระบบจองคิว โรงพยาบาลค่ายวชิราวุธ",
    "short_name": "จองคิว รพ.",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#f2f6fb",
    "theme_color": "#17365d",
    "icons": [
        {
            "src": "/static/icon.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ]
}
"""

    return Response(
        data,
        mimetype="application/manifest+json"
    )


# =========================================================
# Service Worker
# =========================================================

@app.route("/service-worker.js")
def service_worker():

    js = """
const CACHE_NAME = "queue-hospital-v1";

self.addEventListener("install", event => {
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", event => {

    event.respondWith(

        fetch(event.request)
        .catch(() => caches.match(event.request))

    );

});
"""

    return Response(
        js,
        mimetype="application/javascript"
    )


# =========================================================
# หน้าแรก
# =========================================================

@app.route("/")
def home():

    content = f"""
    <div class="card">

        <h2>🏥 {HOSPITAL_NAME}</h2>

        <p>{PROVINCE}</p>

        <p>
        ระบบจองคิวออนไลน์
        <br>
        <span class="small">
        โครงงานจำลองสำหรับการศึกษา
        </span>
        </p>

    </div>


    <div class="card">

        <h2>เมนู</h2>

        <div class="menu">

            <a href="/booking">
                📅 จองคิว
            </a>

            <a href="/search">
                🔎 ค้นหาคิว
            </a>

            <a href="/bookings">
                📋 ดูรายการจอง
            </a>

            <a href="/info">
                ℹ️ ข้อมูลโครงงาน
            </a>

        </div>

    </div>
    """

    return render_template_string(
        PAGE,
        hospital=HOSPITAL_NAME,
        province=PROVINCE,
        content=content
    )


# =========================================================
# ส่งรายชื่อแพทย์ตามแผนก
# =========================================================

@app.route("/doctors/<department>")
def doctors(department):

    return jsonify(
        DEPARTMENTS.get(department, [])
    )


# =========================================================
# หน้าจองคิว
# =========================================================

@app.route("/booking", methods=["GET", "POST"])
def booking():

    global next_queue

    message = ""

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        hn = request.form.get("hn", "").strip()
        department = request.form.get("department", "")
        doctor = request.form.get("doctor", "")
        date = request.form.get("date", "")
        time = request.form.get("time", "")


        # ตรวจสอบข้อมูล

        if not all([
            name,
            hn,
            department,
            doctor,
            date,
            time
        ]):

            message = """
            <div class="success">
            ❌ กรุณากรอกข้อมูลให้ครบทุกช่อง
            </div>
            """

        elif doctor not in DEPARTMENTS.get(
            department, []
        ):

            message = """
            <div class="success">
            ❌ กรุณาเลือกแพทย์ให้ตรงกับแผนก
            </div>
            """

        else:

            duplicate = any(

                b["doctor"] == doctor
                and b["date"] == date
                and b["time"] == time

                for b in bookings

            )

            if duplicate:

                message = """
                <div class="success">
                ❌ เวลานี้ถูกจองแล้ว
                กรุณาเลือกเวลาอื่น
                </div>
                """

            else:

                queue = f"MED-{next_queue:03d}"

                next_queue += 1

                bookings.append({

                    "queue": queue,
                    "name": name,
                    "hn": hn,
                    "department": department,
                    "doctor": doctor,
                    "date": date,
                    "time": time

                })

                message = f"""
                <div class="success">

                    <div>✅ จองคิวสำเร็จ</div>

                    <div class="queue">
                    {queue}
                    </div>

                    <b>ชื่อ:</b> {name}<br>
                    <b>HN:</b> {hn}<br>
                    <b>แผนก:</b> {department}<br>
                    <b>แพทย์:</b> {doctor}<br>
                    <b>วันที่:</b> {date}<br>
                    <b>เวลา:</b> {time}

                </div>
                """


    department_options = ""

    for department in DEPARTMENTS:

        department_options += f"""
        <option value="{department}">
        {department}
        </option>
        """


    time_options = ""

    for t in TIMES:

        time_options += f"""
        <option value="{t}">
        {t}
        </option>
        """


    content = f"""
    <div class="card">

        <h2>📅 จองคิว</h2>

        {message}

        <form method="POST">

            <label>ชื่อผู้จอง</label>

            <input
                type="text"
                name="name"
                placeholder="กรอกชื่อ-นามสกุล"
                required
            >


            <label>เลข HN</label>

            <input
                type="text"
                name="hn"
                placeholder="เช่น HN001"
                required
            >


            <label>แผนก</label>

            <select
                id="department"
                name="department"
                onchange="loadDoctors()"
                required
            >

                <option value="">
                -- เลือกแผนก --
                </option>

                {department_options}

            </select>


            <label>แพทย์</label>

            <select
                id="doctor"
                name="doctor"
                required
            >

                <option value="">
                -- เลือกแผนกก่อน --
                </option>

            </select>


            <label>วันที่</label>

            <input
                type="date"
                name="date"
                required
            >


            <label>เวลา</label>

            <select name="time" required>

                <option value="">
                -- เลือกเวลา --
                </option>

                {time_options}

            </select>


            <button type="submit">
                ✅ ยืนยันการจองคิว
            </button>

        </form>

    </div>


    <div class="card">

        <a href="/">
        ← กลับหน้าหลัก
        </a>

    </div>
    """


    return render_template_string(
        PAGE,
        hospital=HOSPITAL_NAME,
        province=PROVINCE,
        content=content
    )


# =========================================================
# ค้นหาคิว
# =========================================================

@app.route("/search", methods=["GET", "POST"])
def search():

    result = ""

    if request.method == "POST":

        keyword = request.form.get(
            "keyword", ""
        ).strip().lower()

        found = [

            b for b in bookings

            if keyword in b["hn"].lower()
            or keyword in b["queue"].lower()

        ]

        if found:

            for b in found:

                result += f"""
                <div class="booking">

                    <b>คิว:</b> {b["queue"]}<br>
                    <b>ชื่อ:</b> {b["name"]}<br>
                    <b>HN:</b> {b["hn"]}<br>
                    <b>แผนก:</b> {b["department"]}<br>
                    <b>แพทย์:</b> {b["doctor"]}<br>
                    <b>วันที่:</b> {b["date"]}<br>
                    <b>เวลา:</b> {b["time"]}

                </div>
                """

        else:

            result = """
            <div class="success">
            ❌ ไม่พบข้อมูลคิว
            </div>
            """


    content = f"""
    <div class="card">

        <h2>🔎 ค้นหาคิว</h2>

        <form method="POST">

            <label>
            HN หรือหมายเลขคิว
            </label>

            <input
                type="text"
                name="keyword"
                placeholder="เช่น HN001 หรือ MED-001"
                required
            >

            <button type="submit">
            🔎 ค้นหา
            </button>

        </form>

        {result}

    </div>


    <div class="card">

        <a href="/">
        ← กลับหน้าหลัก
        </a>

    </div>
    """

    return render_template_string(
        PAGE,
        hospital=HOSPITAL_NAME,
        province=PROVINCE,
        content=content
    )


# =========================================================
# ดูรายการจอง
# =========================================================

@app.route("/bookings")
def all_bookings():

    result = ""

    if not bookings:

        result = """
        <p>ยังไม่มีรายการจองคิว</p>
        """

    else:

        for b in bookings:

            result += f"""
            <div class="booking">

                <b>คิว:</b> {b["queue"]}<br>
                <b>ชื่อ:</b> {b["name"]}<br>
                <b>HN:</b> {b["hn"]}<br>
                <b>แผนก:</b> {b["department"]}<br>
                <b>แพทย์:</b> {b["doctor"]}<br>
                <b>วันที่:</b> {b["date"]}<br>
                <b>เวลา:</b> {b["time"]}

            </div>
            """


    content = f"""
    <div class="card">

        <h2>📋 รายการจองคิว</h2>

        {result}

    </div>


    <div class="card">

        <a href="/">
        ← กลับหน้าหลัก
        </a>

    </div>
    """

    return render_template_string(
        PAGE,
        hospital=HOSPITAL_NAME,
        province=PROVINCE,
        content=content
    )


# =========================================================
# ข้อมูลโครงงาน
# =========================================================

@app.route("/info")
def info():

    content = f"""
    <div class="card">

        <h2>ℹ️ ข้อมูลโครงงาน</h2>

        <p>
        <b>ชื่อระบบ:</b>
        ระบบจองคิวออนไลน์
        </p>

        <p>
        <b>โรงพยาบาล:</b>
        {HOSPITAL_NAME}
        </p>

        <p>
        <b>จังหวัด:</b>
        {PROVINCE}
        </p>

        <p>
        <b>ผู้จัดทำ:</b><br>
        {CREATORS[0]}<br>
        {CREATORS[1]}
        </p>

        <p>
        <b>ชั้น:</b> {CLASS_NAME}
        </p>

        <hr>

        <p class="small">
        ระบบนี้จัดทำขึ้นเพื่อเป็นโครงงานจำลอง
        สำหรับการศึกษา ไม่ใช่ระบบจองคิวจริง
        ของโรงพยาบาล
        </p>

    </div>


    <div class="card">

        <a href="/">
        ← กลับหน้าหลัก
        </a>

    </div>
    """

    return render_template_string(
        PAGE,
        hospital=HOSPITAL_NAME,
        province=PROVINCE,
        content=content
    )


# =========================================================
# เปิด Flask
# =========================================================

def start_server():

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        use_reloader=False
    )


server_thread = threading.Thread(
    target=start_server,
    daemon=True
)

server_thread.start()

print("==========================================")
print("✅ ระบบจองคิวเริ่มทำงานแล้ว")
print("🏥", HOSPITAL_NAME)
print("🌐 Port:", PORT)
print("==========================================")