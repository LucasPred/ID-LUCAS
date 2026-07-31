import os
import base64
from datetime import datetime
from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
from google import genai
from google.genai import types

# ==========================================
# CONFIGURACIÓN GENERAL BLINDADA
# ==========================================
app = Flask(__name__)
app.secret_key = "gravafilt_secret_key_2026_production_modular"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

api_key_val = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key_val, http_options={'timeout': 300000})


# ==========================================
# PLANTILLA HTML / CSS / JAVASCRIPT MODULAR
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>GRAVAFILT S.A. | Directorio Geotécnico Modular</title>
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
        .btn-success-custom {
            background: linear-gradient(135deg, #059669, #047857);
            border: none;
            border-radius: 50px;
            padding: 14px 30px;
            font-weight: 600;
            color: white;
            transition: all 0.3s ease;
        }
        .btn-success-custom:hover {
            background: linear-gradient(135deg, #047857, #065f46);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(5, 150, 105, 0.3);
            color: white;
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
            display: none;
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
        .loading-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.96);
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
        }
        .nav-pills .nav-link.active {
            background-color: #2563eb;
            font-weight: 600;
        }
        .nav-pills .nav-link {
            color: #475569;
            font-weight: 500;
        }
        .thumb-muestra {
            max-height: 200px;
            border-radius: 10px;
            border: 1px solid #cbd5e1;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
    </style>
</head>
<body>

    <nav class="navbar navbar-dark shadow-sm py-3 navbar-top">
        <div class="container d-flex justify-content-between align-items-center">
            <a class="navbar-brand fw-bold fs-6 fs-md-5 text-white" href="/">
                <i class="fas fa-mountain me-2 text-warning"></i>GRAVAFILT S.A. <span class="text-info fs-7 d-block d-md-inline">| Micrositios Desacoplados</span>
            </a>
            <div class="d-flex align-items-center gap-3">
                <span class="badge-corp d-none d-md-inline-block"><i class="fas fa-shield-alt me-1"></i> DIRECTORIO: LSANTIAGO</span>
                <a href="/logout" class="btn btn-outline-light btn-sm rounded-pill px-3"><i class="fas fa-sign-out-alt me-1"></i> Salir</a>
            </div>
        </div>
    </nav>

    <div class="container my-4 my-md-5">
        <div class="row justify-content-center">
            <div class="col-lg-11">
                
                <ul class="nav nav-pills mb-4 justify-content-center bg-white p-2 rounded-pill shadow-sm" id="pills-tab" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active rounded-pill px-4" id="pills-modulo1-tab" data-bs-toggle="pill" data-bs-target="#pills-modulo1" type="button" role="tab">
                            <i class="fas fa-camera-retro me-2"></i>Micrositio 1: Captura y Granulometría
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link rounded-pill px-4" id="pills-modulo2-tab" data-bs-toggle="pill" data-bs-target="#pills-modulo2" type="button" role="tab">
                            <i class="fas fa-file-contract me-2"></i>Micrositio 2: Reporte Yacimiento & Geotecnia
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link rounded-pill px-4" id="pills-historial-tab" data-bs-toggle="pill" data-bs-target="#pills-historial" type="button" role="tab">
                            <i class="fas fa-history me-2"></i>Historial Ejecutivo
                        </button>
                    </li>
                </ul>

                <div class="tab-content" id="pills-tabContent">
                    
                    <!-- MICROSITIO 1: CAPTURA Y CUADRO GRANULOMETRICO -->
                    <div class="tab-pane fade show active" id="pills-modulo1" role="tabpanel">
                        <div class="card p-4 p-md-5">
                            
                            <div id="loadingOverlay1" class="loading-overlay">
                                <div class="spinner-border text-primary mb-3" role="status" style="width: 3.5rem; height: 3.5rem;"></div>
                                <h5 class="text-dark fw-bold">Procesando captura y cálculo granulométrico...</h5>
                                <p class="text-muted small text-center px-3">Gemini AI está ejecutando la lectura óptica inicial de la muestra.</p>
                            </div>

                            <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap">
                                <h2 class="text-dark fw-bold fs-3 fs-md-2 mb-2 mb-md-0">Micrositio 1: Carga de Muestra y Cuadro Granulométrico</h2>
                                <span class="badge bg-primary text-white px-3 py-2 rounded-pill"><i class="fas fa-layer-group me-1"></i> Fase 1 Activa</span>
                            </div>
                            <p class="text-muted mb-4 small">Suba o capture la fotografía de la muestra. El sistema generará el cuadro IRAM/ASTM y registrará la imagen localmente para el Micrositio 2.</p>

                            <form id="formModulo1" onsubmit="enviarModulo1(event)">
                                <div class="mb-4 preview-container">
                                    <label for="fileInput" class="form-label fw-semibold text-secondary d-block mb-3">
                                        <i class="fas fa-camera fa-2x text-primary mb-2 d-block"></i>
                                        Seleccione Archivo o Capture con Cámara:
                                    </label>
                                    <input class="form-control form-control-lg mx-auto" type="file" id="fileInput" accept="image/*" capture="environment" required style="max-width: 500px;">
                                    <div class="form-text text-muted mt-2">Reducción de escala integrada para máxima velocidad.</div>
                                </div>
                                <div class="d-grid">
                                    <button type="submit" id="btnModulo1" class="btn btn-custom btn-lg text-white">
                                        <i class="fas fa-calculator me-2"></i>Generar Cuadro Granulométrico y Memorizar Muestra
                                    </button>
                                </div>
                            </form>

                            <div id="resultadoBox1" class="result-box">
                                <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap border-bottom pb-2">
                                    <h4 class="text-dark fw-bold fs-5 fs-md-4 mb-2 mb-md-0"><i class="fas fa-table text-success me-2"></i>Cuadro Granulométrico IRAM / ASTM:</h4>
                                    <span class="text-muted small fw-semibold" id="timestampTexto1"></span>
                                </div>
                                <div class="text-center mb-3" id="previewContenedorImg"></div>
                                <div id="resultadoContenido1" class="text-secondary" style="white-space: pre-line; line-height: 1.75; font-size: 0.95rem;"></div>
                                
                                <div class="mt-4 p-3 bg-light rounded-3 border text-center">
                                    <p class="mb-2 fw-semibold text-dark small"><i class="fas fa-arrow-right text-primary me-1"></i> Muestra memorizada correctamente.</p>
                                    <button class="btn btn-sm btn-outline-primary rounded-pill px-4" onclick="irAModulo2()">Ir a Micrositio 2: Reporte Geotécnico Completo</button>
                                </div>
                            </div>

                            <div id="errorBox1" class="alert alert-danger mt-4 rounded-3 shadow-sm small" style="display: none;" role="alert">
                                <i class="fas fa-exclamation-triangle me-2"></i><span id="errorTexto1"></span>
                            </div>
                        </div>
                    </div>

                    <!-- MICROSITIO 2: REPORTE PROFESIONAL TECNICO GEOLOGICO Y GEOTECNICO -->
                    <div class="tab-pane fade" id="pills-modulo2" role="tabpanel">
                        <div class="card p-4 p-md-5">
                            
                            <div id="loadingOverlay2" class="loading-overlay">
                                <div class="spinner-border text-success mb-3" role="status" style="width: 3.5rem; height: 3.5rem;"></div>
                                <h5 class="text-dark fw-bold">Generando dictamen geotécnico y de yacimientos fluviales...</h5>
                                <p class="text-muted small text-center px-3">Gemini AI analizando propiedades físico-químicas, ubicación en lecho de río y comportamientos en destino.</p>
                            </div>

                            <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap">
                                <h2 class="text-dark fw-bold fs-3 fs-md-2 mb-2 mb-md-0">Micrositio 2: Reporte Profesional Técnico Geológico y Geotécnico</h2>
                                <span class="badge bg-success text-white px-3 py-2 rounded-pill"><i class="fas fa-search-location me-1"></i> Fase 2 Especializada</span>
                            </div>
                            <p class="text-muted mb-4 small">Active este botón para procesar la imagen almacenada y compilar el informe integral de propiedades físico-químicas, ubicación en yacimiento y comportamiento industrial.</p>

                            <div id="avisoSinMuestra" class="alert alert-warning rounded-3 shadow-sm">
                                <i class="fas fa-exclamation-circle me-2"></i><strong>Atención:</strong> No hay ninguna muestra activa registrada en el navegador. Por favor, suba una imagen en el <strong>Micrositio 1</strong> primero.
                            </div>

                            <div id="panelConMuestra" style="display: none;">
                                <div class="text-center mb-4">
                                    <img id="imagenActivaPreview" src="" alt="Muestra Activa" class="thumb-muestra mb-2">
                                    <div class="text-muted small">Muestra persistida en memoria local, lista para análisis avanzado.</div>
                                </div>
                                <div class="d-grid">
                                    <button type="button" id="btnModulo2" class="btn btn-success-custom btn-lg" onclick="enviarModulo2()">
                                        <i class="fas fa-file-medical-alt me-2"></i>Generar Reporte Técnico Geológico, Yacimiento y Comportamiento en Destino
                                    </button>
                                </div>
                            </div>

                            <div id="resultadoBox2" class="result-box" style="border-left-color: #059669;">
                                <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap border-bottom pb-2">
                                    <h4 class="text-dark fw-bold fs-5 fs-md-4 mb-2 mb-md-0"><i class="fas fa-certificate text-success me-2"></i>Dictamen Técnico Oficial de Yacimiento y Geotecnia:</h4>
                                    <span class="text-muted small fw-semibold" id="timestampTexto2"></span>
                                </div>
                                <div id="resultadoContenido2" class="text-secondary" style="white-space: pre-line; line-height: 1.75; font-size: 0.95rem;"></div>
                            </div>

                            <div id="errorBox2" class="alert alert-danger mt-4 rounded-3 shadow-sm small" style="display: none;" role="alert">
                                <i class="fas fa-exclamation-triangle me-2"></i><span id="errorTexto2"></span>
                            </div>
                        </div>
                    </div>

                    <!-- HISTORIAL -->
                    <div class="tab-pane fade" id="pills-historial" role="tabpanel">
                        <div class="card p-4 p-md-5">
                            <h3 class="text-dark fw-bold mb-3"><i class="fas fa-archive text-primary me-2"></i>Historial Ejecutivo de Ensayos</h3>
                            <p class="text-muted small mb-4">Registro cronológico local de auditorías de laboratorio.</p>
                            <div id="listaHistorial">
                                <div class="text-center py-5 text-muted">
                                    <i class="fas fa-folder-open fa-3x mb-3 text-secondary"></i>
                                    <p class="fw-semibold">Los ensayos completados aparecerán aquí en orden cronológico.</p>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>

            </div>
        </div>
    </div>

    <!-- Script de control con localStorage blindado -->
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            verificarMuestraLocal();
        });

        function verificarMuestraLocal() {
            const imgB64 = localStorage.getItem("gravafilt_current_image");
            if (imgB64) {
                document.getElementById('avisoSinMuestra').style.display = 'none';
                document.getElementById('panelConMuestra').style.display = 'block';
                document.getElementById('imagenActivaPreview').src = "data:image/jpeg;base64," + imgB64;
            } else {
                document.getElementById('avisoSinMuestra').style.display = 'block';
                document.getElementById('panelConMuestra').style.display = 'none';
            }
        }

        function irAModulo2() {
            const triggerTab = document.querySelector('#pills-modulo2-tab');
            const tabObj = new bootstrap.Tab(triggerTab);
            tabObj.show();
        }

        function enviarModulo1(event) {
            event.preventDefault();
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            if (!file) return;

            document.getElementById('loadingOverlay1').style.display = 'flex';
            document.getElementById('btnModulo1').disabled = true;
            document.getElementById('errorBox1').style.display = 'none';
            document.getElementById('resultadoBox1').style.display = 'none';

            const reader = new FileReader();
            reader.onload = function(e) {
                const img = new Image();
                img.onload = function() {
                    const canvas = document.createElement('canvas');
                    let width = img.width;
                    let height = img.height;
                    const MAX_DIM = 850; 
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
                    
                    const base64Data = canvas.toDataURL('image/jpeg', 0.72).split(',')[1];

                    // Guardar de forma ultra segura en localStorage del navegador
                    localStorage.setItem("gravafilt_current_image", base64Data);
                    verificarMuestraLocal();

                    fetch('/analizar-granulometria', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ image_base64: base64Data })
                    })
                    .then(async response => {
                        const textData = await response.text();
                        try {
                            return { ok: response.ok, data: JSON.parse(textData) };
                        } catch (err) {
                            throw new Error("El servidor excedió el tiempo límite (Timeout/502). Detalle: " + textData.substring(0, 100));
                        }
                    })
                    .then(resObj => {
                        document.getElementById('loadingOverlay1').style.display = 'none';
                        document.getElementById('btnModulo1').disabled = false;

                        if (!resObj.ok || resObj.data.error) {
                            document.getElementById('errorTexto1').innerText = resObj.data.error || "Error en servidor.";
                            document.getElementById('errorBox1').style.display = 'block';
                        } else {
                            document.getElementById('resultadoContenido1').innerText = resObj.data.resultado;
                            document.getElementById('timestampTexto1').innerText = "Emitido: " + resObj.data.timestamp;
                            document.getElementById('previewContenedorImg').innerHTML = `<img src="data:image/jpeg;base64,${base64Data}" alt="Muestra analizada" class="thumb-muestra">`;
                            document.getElementById('resultadoBox1').style.display = 'block';
                        }
                    })
                    .catch(err => {
                        document.getElementById('loadingOverlay1').style.display = 'none';
                        document.getElementById('btnModulo1').disabled = false;
                        document.getElementById('errorTexto1').innerText = err.message;
                        document.getElementById('errorBox1').style.display = 'block';
                    });
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }

        function enviarModulo2() {
            const imgB64 = localStorage.getItem("gravafilt_current_image");
            if (!imgB64) {
                alert("No hay imagen registrada. Suba una muestra en el Micrositio 1.");
                return;
            }

            document.getElementById('loadingOverlay2').style.display = 'flex';
            document.getElementById('btnModulo2').disabled = true;
            document.getElementById('errorBox2').style.display = 'none';

            fetch('/generar-reporte-geotecnico', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image_base64: imgB64 })
            })
            .then(async response => {
                const textData = await response.text();
                try {
                    return { ok: response.ok, data: JSON.parse(textData) };
                } catch (err) {
                    throw new Error("El servidor excedió el tiempo límite en reporte geotécnico (Timeout/502). Detalle: " + textData.substring(0, 100));
                }
            })
            .then(resObj => {
                document.getElementById('loadingOverlay2').style.display = 'none';
                document.getElementById('btnModulo2').disabled = false;

                if (!resObj.ok || resObj.data.error) {
                    document.getElementById('errorTexto2').innerText = resObj.data.error || "Error al procesar reporte geotécnico.";
                    document.getElementById('errorBox2').style.display = 'block';
                } else {
                    document.getElementById('resultadoContenido2').innerText = resObj.data.resultado;
                    document.getElementById('timestampTexto2').innerText = "Emitido: " + resObj.data.timestamp;
                    document.getElementById('resultadoBox2').style.display = 'block';

                    // Agregar al historial visual
                    const listaHistorial = document.getElementById('listaHistorial');
                    if (listaHistorial.innerHTML.includes("Aún no se han registrado")) {
                        listaHistorial.innerHTML = '<div class="list-group" id="grupoHistorial"></div>';
                    }
                    const grupo = document.getElementById('grupoHistorial') || listaHistorial;
                    const nuevoItem = `
                        <div class="list-group-item list-group-item-action flex-column align-items-start mb-3 rounded-3 shadow-sm border p-4">
                            <div class="d-flex w-100 justify-content-between align-items-center mb-3 flex-wrap">
                                <h5 class="mb-1 fw-bold text-dark"><i class="fas fa-clipboard-check text-success me-2"></i>Dictamen Geotécnico Oficial</h5>
                                <small class="text-muted fw-semibold"><i class="far fa-calendar-alt me-1"></i> ${resObj.data.timestamp}</small>
                            </div>
                            <div class="row align-items-center g-3">
                                <div class="col-auto">
                                    <img src="data:image/jpeg;base64,${imgB64}" alt="Muestra" style="width: 70px; height: 70px; object-fit: cover; border-radius: 6px;">
                                </div>
                                <div class="col">
                                    <div class="text-secondary small" style="max-height: 100px; overflow: hidden; text-overflow: ellipsis;">
                                        ${resObj.data.resultado.substring(0, 300)}...
                                    </div>
                                </div>
                            </div>
                        </div>`;
                    grupo.insertAdjacentHTML('afterbegin', nuevoItem);
                }
            })
            .catch(err => {
                document.getElementById('loadingOverlay2').style.display = 'none';
                document.getElementById('btnModulo2').disabled = false;
                document.getElementById('errorTexto2').innerText = err.message;
                document.getElementById('errorBox2').style.display = 'block';
            });
        }
    </script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""


# ==========================================
# PLANTILLA HTML DE LOGIN
# ==========================================
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acceso Restringido - GRAVAFILT S.A.</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #0f172a, #1e293b); height: 100vh; display: flex; align-items: center; justify-content: center; font-family: 'Segoe UI', sans-serif; }
        .login-card { border-radius: 16px; background: #ffffff; width: 100%; max-width: 420px; padding: 40px; box-shadow: 0 15px 35px rgba(0,0,0,0.3); }
        .btn-login { background: #2563eb; border: none; border-radius: 50px; padding: 12px; font-weight: 600; color: white; width: 100%; }
    </style>
</head>
<body>
    <div class="login-card text-center">
        <h3 class="fw-bold text-dark mb-3">GRAVAFILT S.A.</h3>
        <p class="text-muted small mb-4">Acceso exclusivo Directorio (lsantiago)</p>
        {% if error %}<div class="alert alert-danger py-2 small mb-3">{{ error }}</div>{% endif %}
        <form method="POST">
            <div class="mb-3 text-start"><input type="text" class="form-control" name="username" placeholder="Usuario" required autofocus></div>
            <div class="mb-4 text-start"><input type="password" class="form-control" name="password" placeholder="Contraseña" required></div>
            <button type="submit" class="btn btn-login">Ingresar</button>
        </form>
    </div>
</body>
</html>
"""


# ==========================================
# RUTAS Y CONTROLADORES MODULARES
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("username") == "lsantiago" and request.form.get("password") == "gravafil2026":
            session["authenticated"] = True
            session.permanent = True
            return redirect(url_for("index"))
        else:
            error = "Credenciales incorrectas."
    return render_template_string(LOGIN_TEMPLATE, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def index():
    if not session.get("authenticated"): 
        return redirect(url_for("login"))
    return render_template_string(HTML_TEMPLATE)


@app.route("/analizar-granulometria", methods=["POST"])
def analizar_granulometria():
    if not session.get("authenticated"):
        return jsonify({"error": "Su sesión ha caducado."}), 401

    data = request.get_json()
    if not data or 'image_base64' not in data:
        return jsonify({"error": "No se ha recibido la imagen."}), 400

    try:
        image_bytes = base64.b64decode(data.get('image_base64'))
        timestamp_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        prompt_fase1 = (
            "Actúa como Ingeniero de Laboratorio de GRAVAFILT S.A. "
            "Examina la imagen de la muestra de árido y genera estrictamente:\n\n"
            "1. **Clasificación Visual Preliminar de Partículas:** Morfología, esfericidad y estimación mineralógica principal.\n"
            "2. **Cuadro Granulométrico Oficial (Norma IRAM / ASTM):** Tabla en Markdown con columnas obligatorias: Tamiz (mm), % Retenido Parcial, % Retenido Acumulado y % Pasante Acumulado.\n"
            "3. **Parámetros Estadísticos:** Módulo de Finura (MF) y Tamaño Máximo Nominal (TMN)."
        )

        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=[types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"), prompt_fase1]
        )

        return jsonify({"resultado": response.text, "timestamp": timestamp_actual})

    except Exception as e:
        return jsonify({"error": f"Fallo al procesar granulometría: {str(e)}"}), 500


@app.route("/generar-reporte-geotecnico", methods=["POST"])
def generar_reporte_geotecnico():
    if not session.get("authenticated"):
        return jsonify({"error": "Su sesión ha caducado."}), 401

    data = request.get_json()
    img_b64 = data.get('image_base64') if data else None
    
    if not img_b64:
        return jsonify({"error": "No hay ninguna imagen cargada. Suba una muestra en el Micrositio 1 primero."}), 400

    try:
        image_bytes = base64.b64decode(img_b64)
        timestamp_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        prompt_fase2 = (
            "Actúa como Ingeniero Geotécnico Jefe y Director de Operaciones de Yacimientos de GRAVAFILT S.A. "
            "Basándote en la muestra provista en imagen, redacta un REPORTE TÉCNICO PROFESIONAL estructurado exactamente en los siguientes 5 puntos:\n\n"
            "1. **Propiedades Físico-Químicas de los Materiales:** Densidad, porosidad, absorción y resistencia a la abrasión.\n"
            "2. **Ubicación Aproximada de Extracción en Yacimientos Fluviales de Río:** Deducción experta: ¿Proviene de zonas de orilla/costa (banco marginal con limos/arenas finas) o del canal medio de corriente rápida (rodado limpio, mayor esfericidad)? Justifíquese técnicamente.\n"
            "3. **Cualidades Organolépticas y Limpieza:** Descripción de textura táctil y visual, ausencia o presencia de materia orgánica o arcillas.\n"
            "4. **Comportamiento en Actividades de Destino:** Desempeño y compatibilidad para hormigones, pavimentación o filtración.\n"
            "5. **Explicaciones Relativas al Entorno y Encuadrado Granulométrico Regional:** Contextualización geomorfológica dentro de cuencas sedimentarias fluviales."
        )

        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=[types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"), prompt_fase2]
        )

        return jsonify({"resultado": response.text, "timestamp": timestamp_actual})

    except Exception as e:
        return jsonify({"error": f"Fallo al generar reporte geotécnico: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
