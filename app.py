import os
import time
import base64
from datetime import datetime
from flask import Flask, render_template_string, request, session, redirect, url_for
from google import genai
from google.genai import types

app = Flask(__name__)
app.secret_key = "gravafilt_secret_key_2026_secure"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

api_key_val = os.environ.get("GEMINI_API_KEY")

# Cliente configurado con timeout máximo
client = genai.Client(
    api_key=api_key_val,
    http_options={'timeout': 120000} 
)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>GRAVAFILT S.A. | Dirección y Control de Calidad Geológica y Áridos</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            background-color: #f1f5f9;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            -webkit-font-smoothing: antialiased;
        }
        .navbar-top {
            background: linear-gradient(135deg, #0f172a, #1e293b);
            border-bottom: 3px solid #3b82f6;
        }
        .card {
            border: none;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.06);
            position: relative;
            overflow: hidden;
            background: #ffffff;
        }
        .btn-custom {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            border: none;
            border-radius: 50px;
            padding: 14px 30px;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
        }
        .btn-custom:hover {
            background: linear-gradient(135deg, #1d4ed8, #1e40af);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
        }
        .badge-corp {
            background-color: #0f172a;
            color: #38bdf8;
            font-size: 0.75rem;
            letter-spacing: 1px;
            padding: 6px 12px;
            border-radius: 30px;
            font-weight: 700;
        }
        .result-box {
            background-color: #ffffff;
            border-left: 6px solid #2563eb;
            padding: 25px;
            border-radius: 12px;
            margin-top: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.04);
            overflow-x: auto;
        }
        .result-box table {
            width: 100%;
            margin-top: 15px;
            margin-bottom: 15px;
            border-collapse: collapse;
            display: block;
            overflow-x: auto;
            white-space: nowrap;
        }
        .result-box th, .result-box td {
            padding: 10px 14px;
            text-align: center;
            border: 1px solid #e2e8f0;
            font-size: 0.9rem;
        }
        .result-box th {
            background-color: #1e293b;
            color: #ffffff;
            font-weight: 600;
        }
        .result-box tr:nth-child(even) {
            background-color: #f8fafc;
        }
        #loadingOverlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.95);
            z-index: 1000;
            display: none;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            backdrop-filter: blur(3px);
        }
        .preview-container {
            border: 2px dashed #cbd5e1;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            background: #f8fafc;
            transition: all 0.3s;
        }
        .preview-container:hover {
            border-color: #2563eb;
            background: #f1f5f9;
        }
        .nav-pills .nav-link.active {
            background-color: #2563eb;
            font-weight: 600;
        }
        .nav-pills .nav-link {
            color: #475569;
            font-weight: 500;
        }
        .historial-img {
            width: 80px;
            height: 80px;
            object-fit: cover;
            border-radius: 8px;
            border: 1px solid #cbd5e1;
        }
    </style>
</head>
<body>

    <nav class="navbar navbar-dark shadow-sm py-3 navbar-top">
        <div class="container d-flex justify-content-between align-items-center">
            <a class="navbar-brand fw-bold fs-6 fs-md-5 text-white text-wrap" href="/">
                <i class="fas fa-mountain me-2 text-warning"></i>GRAVAFILT S.A. <span class="text-info fs-7 d-block d-md-inline">| Panel de Directorio y Control Técnico</span>
            </a>
            <div class="d-flex align-items-center gap-3">
                <span class="badge-corp d-none d-md-inline-block"><i class="fas fa-shield-alt me-1"></i> ACCESO DIRECTORIO: LSANTIAGO</span>
                <a href="/logout" class="btn btn-outline-light btn-sm rounded-pill px-3"><i class="fas fa-sign-out-alt me-1"></i> Salir</a>
            </div>
        </div>
    </nav>

    <div class="container my-4 my-md-5">
        <div class="row justify-content-center">
            <div class="col-lg-11">
                
                <ul class="nav nav-pills mb-4 justify-content-center bg-white p-2 rounded-pill shadow-sm" id="pills-tab" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active rounded-pill px-4" id="pills-analizador-tab" data-bs-toggle="pill" data-bs-target="#pills-analizador" type="button" role="tab">
                            <i class="fas fa-microscope me-2"></i>Analizador de Muestras IA
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link rounded-pill px-4" id="pills-historial-tab" data-bs-toggle="pill" data-bs-target="#pills-historial" type="button" role="tab">
                            <i class="fas fa-history me-2"></i>Historial de Ensayos <span class="badge bg-primary ms-1">{{ historial|length if historial else 0 }}</span>
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link rounded-pill px-4" id="pills-trazabilidad-tab" data-bs-toggle="pill" data-bs-target="#pills-trazabilidad" type="button" role="tab">
                            <i class="fas fa-map-marked-alt me-2"></i>Trazabilidad y Origen
                        </button>
                    </li>
                </ul>

                <div class="tab-content" id="pills-tabContent">
                    
                    <div class="tab-pane fade show active" id="pills-analizador" role="tabpanel">
                        <div class="card p-4 p-md-5">
                            
                            <div id="loadingOverlay">
                                <div class="spinner-border text-primary mb-3" role="status" style="width: 3.5rem; height: 3.5rem;">
                                    <span class="visually-hidden">Procesando...</span>
                                </div>
                                <h5 class="text-dark fw-bold">Procesando muestra y generando informe...</h5>
                                <p class="text-muted small text-center px-3">Gemini IA está calculando granulometría y parámetros físico-químicos. Por favor, no recargue la página.</p>
                            </div>

                            <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap">
                                <h2 class="text-dark fw-bold fs-3 fs-md-2 mb-2 mb-md-0">Laboratorio Geológico Automatizado</h2>
                                <span class="badge bg-success text-white px-3 py-2 rounded-pill"><i class="fas fa-check-circle me-1"></i> Sistema Cloud Conectado</span>
                            </div>
                            <p class="text-muted mb-4 small fs-md-6">Suba una foto de la muestra o capture con la cámara de su dispositivo móvil.</p>

                            <form id="analisisForm" method="POST" enctype="multipart/form-data" onsubmit="procesarYEnviar(event)">
                                <div class="mb-4 preview-container">
                                    <label for="fileInput" class="form-label fw-semibold text-secondary d-block mb-3">
                                        <i class="fas fa-camera-retro fa-2x text-primary mb-2 d-block"></i>
                                        Seleccionar Archivo o Capturar con Cámara:
                                    </label>
                                    <input class="form-control form-control-lg mx-auto" type="file" id="fileInput" accept="image/*" capture="environment" required style="max-width: 500px;">
                                    <input type="hidden" id="image_base64" name="image_base64">
                                    <div class="form-text mt-2 text-muted small">Compresión automática integrada para evitar saturación de red.</div>
                                </div>
                                <div class="d-grid">
                                    <button type="submit" id="btnAnalizar" class="btn btn-custom btn-lg text-white">
                                        <i class="fas fa-atom me-2"></i>Ejecutar Diagnóstico Geológico con Gemini
                                    </button>
                                </div>
                            </form>

                            {% if resultado %}
                            <div class="result-box mt-4">
                                <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap">
                                    <h4 class="text-dark fw-bold fs-5 fs-md-4 mb-2 mb-md-0"><i class="fas fa-file-invoice text-success me-2"></i>Informe Técnico Oficial de Laboratorio:</h4>
                                    <span class="text-muted small"><i class="far fa-clock me-1"></i> Emitido: {{ timestamp_actual }}</span>
                                </div>
                                <div class="text-secondary" style="white-space: pre-line; line-height: 1.7; font-size: 0.95rem;">{{ resultado }}</div>
                            </div>
                            {% endif %}

                            {% if error %}
                            <div class="alert alert-danger mt-4 rounded-3 shadow-sm small" role="alert">
                                <i class="fas fa-exclamation-triangle me-2"></i>{{ error }}
                            </div>
                            {% endif %}
                        </div>
                    </div>

                    <div class="tab-pane fade" id="pills-historial" role="tabpanel">
                        <div class="card p-4 p-md-5">
                            <h3 class="text-dark fw-bold mb-3"><i class="fas fa-archive text-primary me-2"></i>Historial Resguardado de Ensayos</h3>
                            <p class="text-muted small mb-4">Registro cronológico permanente de los reportes procesados.</p>
                            
                            {% if historial and historial|length > 0 %}
                                <div class="list-group">
                                    {% for item in historial %}
                                    <div class="list-group-item list-group-item-action flex-column align-items-start mb-3 rounded-3 shadow-sm border p-4">
                                        <div class="d-flex w-100 justify-content-between align-items-center mb-3 flex-wrap">
                                            <h5 class="mb-1 fw-bold text-dark"><i class="fas fa-clipboard-check text-success me-2"></i>Ensayo ID: #{{ loop.revindex }}</h5>
                                            <small class="text-muted fw-semibold"><i class="far fa-calendar-alt me-1"></i> {{ item.fecha }}</small>
                                        </div>
                                        <div class="row align-items-center g-3">
                                            <div class="col-auto">
                                                {% if item.imagen %}
                                                    <img src="data:image/jpeg;base64,{{ item.imagen }}" alt="Muestra" class="historial-img shadow-sm">
                                                {% else %}
                                                    <div class="historial-img bg-light d-flex align-items-center justify-content-center text-muted small">Sin imagen</div>
                                                {% endif %}
                                            </div>
                                            <div class="col">
                                                <div class="text-secondary" style="font-size: 0.9rem; max-height: 100px; overflow: hidden; text-overflow: ellipsis;">
                                                    {{ item.resumen[:300] }}...
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    {% endfor %}
                                </div>
                            {% else %}
                                <div class="text-center py-5 text-muted">
                                    <i class="fas fa-folder-open fa-3x mb-3 text-secondary"></i>
                                    <p class="fw-semibold">Aún no se han registrado ensayos en esta sesión activa.</p>
                                </div>
                            {% endif %}
                        </div>
                    </div>

                    <div class="tab-pane fade" id="pills-trazabilidad" role="tabpanel">
                        <div class="card p-4 p-md-5">
                            <h3 class="text-dark fw-bold mb-3"><i class="fas fa-map-marked-alt text-primary me-2"></i>Origen, Trazabilidad y Marco Geológico</h3>
                            <p class="text-muted mb-4">Información institucional sobre la procedencia de los áridos extraídos en cuencas fluviales.</p>
                            
                            <div class="row g-4">
                                <div class="col-md-6">
                                    <div class="p-4 border rounded-3 bg-light h-100">
                                        <h5 class="text-dark fw-bold mb-3"><i class="fas fa-water text-info me-2"></i>Extracción y Cuencas</h5>
                                        <p class="text-secondary small" style="line-height: 1.6;">
                                            Materiales procesados por GRAVAFILT S.A. provenientes de extracciones fluviales controladas, bajo estrictas pautas de sustentabilidad ambiental y normativas provinciales.
                                        </p>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="p-4 border rounded-3 bg-light h-100">
                                        <h5 class="text-dark fw-bold mb-3"><i class="fas fa-certificate text-warning me-2"></i>Garantía de Accionistas</h5>
                                        <p class="text-secondary small" style="line-height: 1.6;">
                                            Supervisado directamente por el Directorio (Usuario <strong>lsantiago</strong>), garantizando doble capa de seguridad y respaldo técnico ante clientes corporativos.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>

            </div>
        </div>
    </div>

    <script>
        function procesarYEnviar(event) {
            event.preventDefault();
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            
            if (!file) return;

            document.getElementById('loadingOverlay').style.display = 'flex';
            document.getElementById('btnAnalizar').disabled = true;

            const reader = new FileReader();
            reader.onload = function(e) {
                const img = new Image();
                img.onload = function() {
                    const canvas = document.createElement('canvas');
                    let width = img.width;
                    let height = img.height;
                    
                    // Resolución optimizada para evitar sobrecarga y errores 502 de Cloudflare
                    const MAX_DIM = 1000;
                    if (width > height && width > MAX_DIM) {
                        height *= MAX_DIM / width;
                        width = MAX_DIM;
                    } else if (height > MAX_DIM) {
                        width *= MAX_DIM / height;
                        height = MAX_DIM;
                    }
                    
                    canvas.width = width;
                    canvas.height = height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, width, height);
                    
                    const dataUrl = canvas.toDataURL('image/jpeg', 0.80);
                    const base64Data = dataUrl.split(',')[1];
                    
                    document.getElementById('image_base64').value = base64Data;
                    document.getElementById('analisisForm').submit();
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    </script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acceso Restringido - GRAVAFILT S.A.</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            background: linear-gradient(135deg, #0f172a, #1e293b);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .login-card {
            border: none;
            border-radius: 16px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            background: #ffffff;
            width: 100%;
            max-width: 420px;
            padding: 40px;
        }
        .btn-login {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            border: none;
            border-radius: 50px;
            padding: 12px;
            font-weight: 600;
            color: white;
            transition: all 0.3s;
        }
        .btn-login:hover {
            background: linear-gradient(135deg, #1d4ed8, #1e40af);
            transform: translateY(-1px);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="login-card text-center">
                    <div class="mb-4">
                        <i class="fas fa-shield-alt fa-3x text-primary mb-3"></i>
                        <h3 class="fw-bold text-dark">GRAVAFILT S.A.</h3>
                        <p class="text-muted small">Acceso exclusivo para Directorio y Accionistas</p>
                    </div>

                    {% if error %}
                    <div class="alert alert-danger py-2 small mb-3" role="alert">
                        <i class="fas fa-exclamation-circle me-1"></i>{{ error }}
                    </div>
                    {% endif %}

                    <form method="POST">
                        <div class="mb-3 text-start">
                            <label class="form-label fw-semibold text-secondary small">Usuario Autorizado:</label>
                            <div class="input-group">
                                <span class="input-group-text bg-light"><i class="fas fa-user text-muted"></i></span>
                                <input type="text" class="form-control" name="username" placeholder="Ingrese usuario" required autofocus>
                            </div>
                        </div>
                        <div class="mb-4 text-start">
                            <label class="form-label fw-semibold text-secondary small">Contraseña de Seguridad:</label>
                            <div class="input-group">
                                <span class="input-group-text bg-light"><i class="fas fa-lock text-muted"></i></span>
                                <input type="password" class="form-control" name="password" placeholder="Ingrese contraseña" required>
                            </div>
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-login">Ingresar al Sistema</button>
                        </div>
                    </form>
                    <div class="mt-4 text-muted" style="font-size: 0.75rem;">
                        Sistema de Doble Seguridad Verificado | Repositorio ID-LUCAS
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "lsantiago" and password == "gravafil2026":
            session["authenticated"] = True
            if "historial" not in session:
                session["historial"] = []
            return redirect(url_for("index"))
        else:
            error = "Credenciales incorrectas. Verifique usuario y contraseña."
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route("/logout")
def logout():
    session.pop("authenticated", None)
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("authenticated"):
        return redirect(url_for("login"))

    resultado = None
    error = None
    timestamp_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    if "historial" not in session:
        session["historial"] = []

    if request.method == "POST":
        img_base64 = request.form.get('image_base64')
        if not img_base64:
            error = "No se pudo procesar la imagen desde el dispositivo móvil."
        else:
            try:
                image_bytes = base64.b64decode(img_base64)
                
                # Prompt optimizado para garantizar respuestas veloces y evitar bloqueos de pasarela
                prompt = (
                    "Actúa como Ingeniero Geotécnico Jefe de GRAVAFILT S.A. "
                    "Analiza la imagen de la muestra de árido y emite un informe técnico preciso y estructurado en:\n\n"
                    "1. **Caracterización Geológica y Mineralógica:** Clasificación del árido (origen fluvial), morfología de partículas (angulosas/subredondeadas), esfericidad y estimación mineralógica (cuarzo, feldespatos) o presencia de finos.\n"
                    "2. **Cualidades Físico-Químicas:** Textura superficial, limpieza y ausencia de materia orgánica.\n"
                    "3. **Origen y Trazabilidad:** Aptitud industrial para extracción fluvial.\n"
                    "4. **Cuadro Granulométrico (Norma IRAM / ASTM):** Tabla en Markdown con columnas: Tamiz (mm), % Retenido Parcial, % Retenido Acumulado y % Pasante Acumulado.\n"
                    "5. **Parámetros Estadísticos:** Módulo de Finura (MF) y Tamaño Máximo Nominal (TMN).\n"
                    "6. **Dictamen de Calidad y Uso Industrial:** Conclusión del Directorio para hormigones o filtración y sugerencias de planta."
                )

                max_intentos = 3
                for intento in range(max_intentos):
                    try:
                        response = client.models.generate_content(
                            model='gemini-3.6-flash',
                            contents=[
                                types.Part.from_bytes(
                                    data=image_bytes,
                                    mime_type="image/jpeg",
                                ),
                                prompt
                            ]
                        )
                        resultado = response.text
                        break
                    except Exception as api_err:
                        if intento < max_intentos - 1:
                            time.sleep(2)
                            continue
                        raise api_err

                if resultado:
                    nuevo_reporte = {
                        "fecha": timestamp_actual,
                        "resumen": resultado,
                        "imagen": img_base64
                    }
                    hist_actual = session.get("historial", [])
                    hist_actual.insert(0, nuevo_reporte)
                    session["historial"] = hist_actual
                    session.modified = True

            except Exception as e:
                error = f"La pasarela o el servidor agotaron el tiempo de espera por restricciones de red móvil (Error 502/Timeout). Intente con una foto ligeramente más liviana o reintente en unos segundos: {str(e)}"

    return render_template_string(
        HTML_TEMPLATE, 
        resultado=resultado, 
        error=error, 
        historial=session.get("historial", []),
        timestamp_actual=timestamp_actual
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
