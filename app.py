import os
import base64
from datetime import datetime
from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
from google import genai
from google.genai import types

# ==========================================
# CONFIGURACIÓN GENERAL DE LA APLICACIÓN FLASK
# ==========================================
app = Flask(__name__)
app.secret_key = "gravafilt_secret_key_2026_secure"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Inicialización del cliente de Google GenAI con el SDK moderno y timeout extendido
api_key_val = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key_val, http_options={'timeout': 120000})


# ==========================================
# PLANTILLA HTML / CSS / JAVASCRIPT PRINCIPAL
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>GRAVAFILT S.A. | Dirección y Control de Calidad Geológica y Áridos</title>
    <!-- Bootstrap 5 CSS CDN -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- FontAwesome Icons CDN -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        /* Estilos generales y diseño corporativo de GRAVAFILT S.A. */
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

    <!-- Barra de Navegación Superior -->
    <nav class="navbar navbar-dark shadow-sm py-3 navbar-top">
        <div class="container d-flex justify-content-between align-items-center">
            <a class="navbar-brand fw-bold fs-6 fs-md-5 text-white" href="/">
                <i class="fas fa-mountain me-2 text-warning"></i>GRAVAFILT S.A. <span class="text-info fs-7 d-block d-md-inline">| Panel de Directorio y Control Técnico</span>
            </a>
            <div class="d-flex align-items-center gap-3">
                <span class="badge-corp d-none d-md-inline-block"><i class="fas fa-shield-alt me-1"></i> ACCESO DIRECTORIO: LSANTIAGO</span>
                <a href="/logout" class="btn btn-outline-light btn-sm rounded-pill px-3"><i class="fas fa-sign-out-alt me-1"></i> Salir</a>
            </div>
        </div>
    </nav>

    <!-- Contenedor Principal de la Interfaz -->
    <div class="container my-4 my-md-5">
        <div class="row justify-content-center">
            <div class="col-lg-11">
                
                <!-- Pestañas de Navegación del Panel -->
                <ul class="nav nav-pills mb-4 justify-content-center bg-white p-2 rounded-pill shadow-sm" id="pills-tab" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active rounded-pill px-4" id="pills-analizador-tab" data-bs-toggle="pill" data-bs-target="#pills-analizador" type="button" role="tab">
                            <i class="fas fa-microscope me-2"></i>Analizador de Muestras IA
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link rounded-pill px-4" id="pills-historial-tab" data-bs-toggle="pill" data-bs-target="#pills-historial" type="button" role="tab">
                            <i class="fas fa-history me-2"></i>Historial de Ensayos <span class="badge bg-primary ms-1" id="contadorHistorial">{{ historial|length if historial else 0 }}</span>
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link rounded-pill px-4" id="pills-trazabilidad-tab" data-bs-toggle="pill" data-bs-target="#pills-trazabilidad" type="button" role="tab">
                            <i class="fas fa-map-marked-alt me-2"></i>Trazabilidad y Origen
                        </button>
                    </li>
                </ul>

                <!-- Contenido de las Pestañas -->
                <div class="tab-content" id="pills-tabContent">
                    
                    <!-- TAB 1: ANALIZADOR DE MUESTRAS -->
                    <div class="tab-pane fade show active" id="pills-analizador" role="tabpanel">
                        <div class="card p-4 p-md-5">
                            
                            <!-- Overlay de carga asíncrona -->
                            <div id="loadingOverlay">
                                <div class="spinner-border text-primary mb-3" role="status" style="width: 3.5rem; height: 3.5rem;"></div>
                                <h5 class="text-dark fw-bold">Generando informe geológico exhaustivo...</h5>
                                <p class="text-muted small text-center px-3">Gemini IA está procesando la caracterización detallada y las tablas IRAM/ASTM en segundo plano sin cortes de Cloudflare.</p>
                            </div>

                            <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap">
                                <h2 class="text-dark fw-bold fs-3 fs-md-2 mb-2 mb-md-0">Laboratorio Geológico Automatizado</h2>
                                <span class="badge bg-success text-white px-3 py-2 rounded-pill"><i class="fas fa-check-circle me-1"></i> Sistema Blindado Anti-502</span>
                            </div>
                            <p class="text-muted mb-4 small">Capture la fotografía con su dispositivo móvil o cargue la muestra de árido para iniciar el protocolo técnico completo de GRAVAFILT S.A.</p>

                            <!-- Formulario de Análisis con AJAX -->
                            <form id="analisisForm" onsubmit="enviarAsync(event)">
                                <div class="mb-4 preview-container">
                                    <label for="fileInput" class="form-label fw-semibold text-secondary d-block mb-3">
                                        <i class="fas fa-camera-retro fa-2x text-primary mb-2 d-block"></i>
                                        Seleccionar Archivo o Capturar con Cámara:
                                    </label>
                                    <input class="form-control form-control-lg mx-auto" type="file" id="fileInput" accept="image/*" capture="environment" required style="max-width: 500px;">
                                    <div class="form-text text-muted mt-2">Formatos admitidos: JPG, PNG, WEBP (Optimización automática en cliente para evitar saturación).</div>
                                </div>
                                <div class="d-grid">
                                    <button type="submit" id="btnAnalizar" class="btn btn-custom btn-lg text-white">
                                        <i class="fas fa-atom me-2"></i>Ejecutar Diagnóstico Geológico Completo con Gemini
                                    </button>
                                </div>
                            </form>

                            <!-- Contenedor del Resultado del Informe -->
                            <div id="resultadoBox" class="result-box">
                                <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap border-bottom pb-2">
                                    <h4 class="text-dark fw-bold fs-5 fs-md-4 mb-2 mb-md-0"><i class="fas fa-file-invoice text-success me-2"></i>Informe Técnico Oficial de Laboratorio:</h4>
                                    <span class="text-muted small fw-semibold" id="timestampTexto"></span>
                                </div>
                                <div id="resultadoContenido" class="text-secondary" style="white-space: pre-line; line-height: 1.75; font-size: 0.95rem;"></div>
                            </div>

                            <!-- Contenedor de Errores -->
                            <div id="errorBox" class="alert alert-danger mt-4 rounded-3 shadow-sm small" style="display: none;" role="alert">
                                <i class="fas fa-exclamation-triangle me-2"></i><span id="errorTexto"></span>
                            </div>
                        </div>
                    </div>

                    <!-- TAB 2: HISTORIAL DE ENSAYOS -->
                    <div class="tab-pane fade" id="pills-historial" role="tabpanel">
                        <div class="card p-4 p-md-5">
                            <h3 class="text-dark fw-bold mb-3"><i class="fas fa-archive text-primary me-2"></i>Historial Resguardado de Ensayos</h3>
                            <p class="text-muted small mb-4">Registro cronológico detallado de los análisis geológicos ejecutados durante la sesión activa del Directorio.</p>
                            <div id="listaHistorial">
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
                                                    <div class="text-secondary" style="font-size: 0.9rem; max-height: 120px; overflow: hidden; text-overflow: ellipsis;">
                                                        {{ item.resumen[:350] }}...
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
                    </div>

                    <!-- TAB 3: TRAZABILIDAD Y ORIGEN -->
                    <div class="tab-pane fade" id="pills-trazabilidad" role="tabpanel">
                        <div class="card p-4 p-md-5">
                            <h3 class="text-dark fw-bold mb-3"><i class="fas fa-map-marked-alt text-primary me-2"></i>Origen, Trazabilidad y Marco Geológico</h3>
                            <p class="text-muted small mb-4">Información corporativa y de cuencas de extracción operadas por GRAVAFILT S.A.</p>
                            <div class="row g-4">
                                <div class="col-md-6">
                                    <div class="p-4 border rounded-3 bg-light h-100">
                                        <h5 class="text-dark fw-bold mb-3"><i class="fas fa-water text-info me-2"></i>Extracción y Cuencas</h5>
                                        <p class="text-secondary small">Materiales procesados por GRAVAFILT S.A. provenientes de extracciones fluviales controladas, asegurando granulometrías estables para la industria de la construcción y filtración.</p>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="p-4 border rounded-3 bg-light h-100">
                                        <h5 class="text-dark fw-bold mb-3"><i class="fas fa-certificate text-warning me-2"></i>Garantía de Directorio</h5>
                                        <p class="text-secondary small">Supervisado directamente por el Directorio ejecutivo (Usuario autorizado: <strong>lsantiago</strong>), garantizando trazabilidad y cumplimiento de estándares de calidad corporativos.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>

            </div>
        </div>
    </div>

    <!-- Script de comunicación asíncrona AJAX para evitar límite de Cloudflare -->
    <script>
        function enviarAsync(event) {
            event.preventDefault();
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            if (!file) return;

            document.getElementById('loadingOverlay').style.display = 'flex';
            document.getElementById('btnAnalizar').disabled = true;
            document.getElementById('errorBox').style.display = 'none';
            document.getElementById('resultadoBox').style.display = 'none';

            const reader = new FileReader();
            reader.onload = function(e) {
                const img = new Image();
                img.onload = function() {
                    const canvas = document.createElement('canvas');
                    let width = img.width;
                    let height = img.height;
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
                    
                    const base64Data = canvas.toDataURL('image/jpeg', 0.80).split(',')[1];

                    fetch('/analizar-ajax', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ image_base64: base64Data })
                    })
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('loadingOverlay').style.display = 'none';
                        document.getElementById('btnAnalizar').disabled = false;

                        if (data.error) {
                            document.getElementById('errorTexto').innerText = data.error;
                            document.getElementById('errorBox').style.display = 'block';
                        } else {
                            document.getElementById('resultadoContenido').innerText = data.resultado;
                            document.getElementById('timestampTexto').innerText = "Emitido: " + data.timestamp;
                            document.getElementById('resultadoBox').style.display = 'block';
                            if (data.contador) {
                                document.getElementById('contadorHistorial').innerText = data.contador;
                            }
                        }
                    })
                    .catch(err => {
                        document.getElementById('loadingOverlay').style.display = 'none';
                        document.getElementById('btnAnalizar').disabled = false;
                        document.getElementById('errorTexto').innerText = "Error de red asíncrona: " + err;
                        document.getElementById('errorBox').style.display = 'block';
                    });
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    </script>
    <!-- Bootstrap JS Bundle CDN -->
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
# RUTAS Y CONTROLADORES DE FLASK
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("username") == "lsantiago" and request.form.get("password") == "gravafil2026":
            session["authenticated"] = True
            if "historial" not in session: 
                session["historial"] = []
            return redirect(url_for("index"))
        else:
            error = "Credenciales incorrectas."
    return render_template_string(LOGIN_TEMPLATE, error=error)


@app.route("/logout")
def logout():
    session.pop("authenticated", None)
    return redirect(url_for("login"))


@app.route("/")
def index():
    if not session.get("authenticated"): 
        return redirect(url_for("login"))
    return render_template_string(HTML_TEMPLATE, historial=session.get("historial", []))


@app.route("/analizar-ajax", methods=["POST"])
def analizar_ajax():
    if not session.get("authenticated"):
        return jsonify({"error": "Sesión expirada"}), 401

    data = request.get_json()
    img_base64 = data.get('image_base64')
    if not img_base64:
        return jsonify({"error": "No se recibió la imagen."})

    try:
        image_bytes = base64.b64decode(img_base64)
        timestamp_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Prompt técnico completo, profundo y detallado de laboratorio geológico
        prompt = (
            "Actúa como Ingeniero Geotécnico Jefe de GRAVAFILT S.A. "
            "Analiza con rigurosidad técnica la imagen de la muestra de árido y emite un informe exhaustivo estructurado exactamente en los siguientes 6 puntos:\n\n"
            "1. **Caracterización Geológica, Mineralógica y Fisotécnica:** Clasificación visual precisa, morfología de las partículas (angulosas/subredondeadas), grado de esfericidad, estimación mineralógica principal (cuarzo, feldespatos) y detección de finos o arcillas superficiales.\n"
            "2. **Cualidades Organolépticas y Condiciones Físico-Químicas:** Textura, grado de limpieza, ausencia de materia orgánica y comportamiento esperado ante agentes externos.\n"
            "3. **Origen y Trazabilidad de Extracción:** Referencia analítica sobre el banco fluvial de río y su aptitud industrial para operaciones en planta.\n"
            "4. **Cuadro Granulométrico Oficial (Norma de Laboratorio IRAM / ASTM):** Tabla formal en Markdown que incluya obligatoriamente las columnas: Tamiz (mm), % Retenido Parcial, % Retenido Acumulado y % Pasante Acumulado.\n"
            "5. **Parámetros Estadísticos del Ensayo:** Cálculo técnico detallado del Módulo de Finura (MF) y del Tamaño Máximo Nominal (TMN).\n"
            "6. **Dictamen de Calidad, Operativa y Uso Industrial:** Conclusión formal del Directorio sobre su aplicación en hormigones, construcción o filtración, incluyendo sugerencias de ajuste en planta."
        )

        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=[types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"), prompt]
        )
        resultado = response.text

        # Almacenamiento seguro en el historial de la sesión
        nuevo_reporte = {"fecha": timestamp_actual, "resumen": resultado, "imagen": img_base64}
        hist = session.get("historial", [])
        hist.insert(0, nuevo_reporte)
        session["historial"] = hist
        session.modified = True

        return jsonify({
            "resultado": resultado,
            "timestamp": timestamp_actual,
            "contador": len(hist)
        })

    except Exception as e:
        return jsonify({"error": f"Error interno en servidor al consultar la IA: {str(e)}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
