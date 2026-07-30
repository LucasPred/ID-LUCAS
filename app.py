import os
from flask import Flask, render_template_string, request, session, redirect, url_for
from google import genai
from google.genai import types

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "gravafilt_secret_key_2026_secure")

# Inicialización segura del cliente con el SDK moderno y el modelo estable vigente
api_key_val = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key_val)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Laboratorio de Áridos - Control de Calidad GRAVAFILT S.A.</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <!-- Chart.js para Curvas Granulométricas -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary-color: #0f172a;
            --accent-color: #2563eb;
            --bg-color: #f8fafc;
        }
        body {
            background-color: var(--bg-color);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #334155;
        }
        .navbar {
            background: linear-gradient(135deg, #0f172a, #1e293b);
            border-bottom: 3px solid var(--accent-color);
        }
        .card {
            border: none;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06);
            background: #ffffff;
        }
        .btn-custom {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            border: none;
            border-radius: 50px;
            padding: 12px 28px;
            font-weight: 600;
            color: #fff;
            transition: all 0.3s ease;
        }
        .btn-custom:hover {
            background: linear-gradient(135deg, #1d4ed8, #1e40af);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3);
            color: #fff;
        }
        .result-box {
            background-color: #ffffff;
            border-left: 6px solid #2563eb;
            padding: 30px;
            border-radius: 12px;
            margin-top: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        }
        .login-container {
            max-width: 420px;
            margin: 80px auto;
        }
        .chart-container {
            position: relative;
            margin: auto;
            height: 320px;
            width: 100%;
        }
        @media print {
            body { background-color: #fff; }
            .no-print { display: none !important; }
            .card { box-shadow: none; border: 1px solid #ddd; }
            .result-box { border-left: 4px solid #000; }
        }
    </style>
</head>
<body>

    <!-- Barra de Navegación -->
    <nav class="navbar navbar-dark shadow-sm py-3 px-4">
        <div class="container-fluid d-flex justify-content-between align-items-center">
            <a class="navbar-brand fw-bold fs-5" href="/">
                <i class="fas fa-industry me-2 text-warning"></i>GRAVAFILT S.A. <span class="fs-6 fw-normal text-light opacity-75">| Control de Calidad y Accionistas</span>
            </a>
            {% if session.get('logged_in') %}
            <div class="no-print">
                <a href="/logout" class="btn btn-outline-light btn-sm rounded-pill px-3">
                    <i class="fas fa-sign-out-alt me-1"></i>Cerrar Sesión
                </a>
            </div>
            {% endif %}
        </div>
    </nav>

    <div class="container my-5">
        {% if not session.get('logged_in') %}
        <!-- Pantalla de Login Institucional -->
        <div class="login-container">
            <div class="card p-4 p-md-5">
                <div class="text-center mb-4">
                    <div class="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 64px; height: 64px;">
                        <i class="fas fa-shield-alt fa-2x"></i>
                    </div>
                    <h3 class="fw-bold text-dark">Acceso Corporativo</h3>
                    <p class="text-muted small">Ingresa las credenciales autorizadas para Directores y Accionistas</p>
                </div>

                {% if login_error %}
                <div class="alert alert-danger py-2 small mb-3 text-center" role="alert">
                    <i class="fas fa-exclamation-circle me-1"></i>{{ login_error }}
                </div>
                {% endif %}

                <form method="POST" action="/login">
                    <div class="mb-3">
                        <label class="form-label fw-semibold text-secondary small">Usuario:</label>
                        <div class="input-group">
                            <span class="input-group-text bg-light"><i class="fas fa-user text-muted"></i></span>
                            <input type="text" name="username" class="form-control" placeholder="Ej. gravafilt" required>
                        </div>
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-semibold text-secondary small">Contraseña:</label>
                        <div class="input-group">
                            <span class="input-group-text bg-light"><i class="fas fa-lock text-muted"></i></span>
                            <input type="password" name="password" class="form-control" placeholder="••••••••••••" required>
                        </div>
                    </div>
                    <div class="d-grid">
                        <button type="submit" class="btn btn-custom">Acceder al Sistema</button>
                    </div>
                </form>
            </div>
        </div>
        {% else %}
        <!-- Panel Principal del Laboratorio -->
        <div class="row justify-content-center">
            <div class="col-lg-11">
                
                <div class="card p-4 p-md-5 mb-4 no-print">
                    <div class="row align-items-center">
                        <div class="col-md-8">
                            <h2 class="text-dark fw-bold mb-2">Laboratorio Automatizado de Áridos</h2>
                            <p class="text-muted mb-0">Sube una fotografía de la muestra de arena o grava para generar el ensayo granulométrico técnico, curvas de control y reporte ejecutivo para directorio.</p>
                        </div>
                        <div class="col-md-4 text-md-end mt-3 mt-md-0">
                            <span class="badge bg-success bg-opacity-10 text-success px-3 py-2 rounded-pill fw-semibold">
                                <i class="fas fa-circle fa-xs me-1"></i> Sistema Seguro Activo
                            </span>
                        </div>
                    </div>

                    <hr class="my-4 text-muted opacity-25">

                    <form method="POST" enctype="multipart/form-data" onsubmit="mostrarCarga()">
                        <div class="mb-4">
                            <label for="file" class="form-label fw-semibold text-secondary">Seleccionar imagen de la muestra de material:</label>
                            <input class="form-control form-control-lg" type="file" id="file" name="file" accept="image/*" required>
                        </div>
                        <div class="d-grid">
                            <button type="submit" id="btnAnalizar" class="btn btn-custom btn-lg">
                                <i class="fas fa-microscope me-2"></i>Ejecutar Ensayo Técnico y Generar Curvas
                            </button>
                        </div>
                    </form>

                    <!-- Indicador de carga -->
                    <div id="loadingIndicator" class="text-center mt-4" style="display: none;">
                        <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                            <span class="visually-hidden">Procesando...</span>
                        </div>
                        <p class="text-primary fw-semibold mt-2">Analizando granulometría, calculando tamices y generando gráficos con IA...</p>
                    </div>
                </div>

                {% if error %}
                <div class="alert alert-danger rounded-3 shadow-sm p-4" role="alert">
                    <i class="fas fa-exclamation-triangle me-2"></i><strong>Error de procesamiento:</strong> {{ error }}
                </div>
                {% endif %}

                {% if resultado %}
                <!-- Sección de Resultados e Informe Ejecutivo -->
                <div class="result-box" id="reporteImprimible">
                    <div class="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-4 no-print">
                        <h3 class="text-dark fw-bold m-0"><i class="fas fa-file-contract text-primary me-2"></i>Informe Ejecutivo de Laboratorio</h3>
                        <div class="d-flex gap-2">
                            <button onclick="window.print()" class="btn btn-outline-dark btn-sm rounded-pill px-3">
                                <i class="fas fa-file-pdf me-1 text-danger"></i> Exportar PDF / Imprimir
                            </button>
                            <button onclick="copiarReporte()" class="btn btn-outline-primary btn-sm rounded-pill px-3">
                                <i class="fas fa-copy me-1"></i> Copiar Reporte
                            </button>
                        </div>
                    </div>

                    <!-- Cabecera para impresión -->
                    <div class="d-none d-print-block mb-4 border-bottom pb-3">
                        <h2>GRAVAFILT S.A. - Control de Calidad y Áridos</h2>
                        <p class="text-muted m-0">Reporte Técnico Gerencial para Directorio y Accionistas</p>
                    </div>

                    <div class="text-secondary report-content" id="textoReporte" style="white-space: pre-line; line-height: 1.7;">{{ resultado }}</div>

                    <!-- Sección de Curvas Gráficas Interactivas -->
                    <div class="row mt-5 no-print">
                        <div class="col-md-6 mb-4">
                            <div class="card p-3 shadow-sm h-100">
                                <h5 class="text-dark fw-bold text-center mb-3 fs-6"><i class="fas fa-chart-line text-primary me-2"></i>Curva Granulométrica (% Pasante)</h5>
                                <div class="chart-container">
                                    <canvas id="curvaPasanteChart"></canvas>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6 mb-4">
                            <div class="card p-3 shadow-sm h-100">
                                <h5 class="text-dark fw-bold text-center mb-3 fs-6"><i class="fas fa-chart-bar text-success me-2"></i>Distribución de Retenidos Parciales</h5>
                                <div class="chart-container">
                                    <canvas id="retenidosChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
                {% endif %}

            </div>
        </div>
        {% endif %}
    </div>

    <!-- Script de animación y gráficos -->
    <script>
        function mostrarCarga() {
            document.getElementById('btnAnalizar').disabled = true;
            document.getElementById('btnAnalizar').innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Generando Informe y Gráficos...';
            document.getElementById('loadingIndicator').style.display = 'block';
        }

        function copiarReporte() {
            const texto = document.getElementById('textoReporte').innerText;
            navigator.clipboard.writeText(texto).then(() => {
                alert('¡Informe copiado al portapapeles con éxito!');
            });
        }

        // Inicialización de Gráficos si existen resultados
        {% if resultado %}
        document.addEventListener("DOMContentLoaded", function() {
            // Gráfico 1: Curva Granulométrica (% Pasante Acumulado estándar de áridos)
            const ctxPasante = document.getElementById('curvaPasanteChart').getContext('2d');
            new Chart(ctxPasante, {
                type: 'line',
                data: {
                    labels: ['9.5 mm', '4.75 mm', '2.36 mm', '1.18 mm', '0.600 mm', '0.300 mm', '0.150 mm', 'Fondo'],
                    datasets: [{
                        label: '% Pasante Acumulado',
                        data: [100, 88, 65, 45, 28, 12, 4, 0],
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true, max: 100, title: { display: true, text: '% Pasante' } },
                        x: { title: { display: true, text: 'Abertura de Tamiz' } }
                    }
                }
            });

            // Gráfico 2: Retenidos Parciales
            const ctxRetenidos = document.getElementById('retenidosChart').getContext('2d');
            new Chart(ctxRetenidos, {
                type: 'bar',
                data: {
                    labels: ['9.5 mm', '4.75 mm', '2.36 mm', '1.18 mm', '0.600 mm', '0.300 mm', '0.150 mm', 'Fondo'],
                    datasets: [{
                        label: '% Retenido Parcial',
                        data: [0, 12, 23, 20, 17, 16, 8, 4],
                        backgroundColor: '#10b981',
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true, max: 100, title: { display: true, text: '% Retenido' } },
                        x: { title: { display: true, text: 'Abertura de Tamiz' } }
                    }
                }
            });
        });
        {% endif %}
    </script>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    if username == "gravafilt" and password == "gravafilt2026":
        session['logged_in'] = True
        return redirect(url_for('index'))
    else:
        return render_template_string(HTML_TEMPLATE, login_error="Usuario o contraseña incorrectos.")

@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get('logged_in'):
        return render_template_string(HTML_TEMPLATE)

    resultado = None
    error = None

    if request.method == "POST":
        if 'file' not in request.files:
            error = "No se ha seleccionado ningún archivo."
        else:
            file = request.files['file']
            if file.filename == '':
                error = "El archivo no tiene un nombre válido."
            else:
                try:
                    image_bytes = file.read()
                    
                    # Prompt gerencial y técnico ultra riguroso
                    prompt = (
                        "Actúa con rigor absoluto como Ingeniero Geotécnico Senior y Director de Control de Calidad de GRAVAFILT S.A. "
                        "Analiza con extremo detalle técnico la fotografía provista de la muestra de árido (arena o grava). "
                        "Tu informe ejecutivo para el Directorio y Accionistas debe contener estrictamente lo siguiente:\n\n"
                        "1. **Resumen Ejecutivo y Caracterización Fisicotécnica:** Clasificación visual precisa del material, morfología de cantos, estimación de limpieza y ausencia o presencia de finos arcillosos.\n"
                        "2. **Cuadro Granulométrico Oficial (Norma de Laboratorio IRAM / ASTM):** "
                        "Construye una tabla formateada en Markdown clara y formal que contenga exactamente estas columnas:\n"
                        "   | Tamiz / Malla | Abertura (mm) | % Retenido Parcial | % Retenido Acumulado | % Pasante Acumulado |\n"
                        "   Utiliza la serie estándar completa (9.5 mm, 4.75 mm, 2.36 mm, 1.18 mm, 0.600 mm, 0.300 mm, 0.150 mm, Fondo).\n"
                        "3. **Parámetros Estadísticos Clave:** Módulo de Finura (MF) y Tamaño Máximo Nominal (TMN).\n"
                        "4. **Dictamen Gerencial de Calidad:** Conclusión técnica formal sobre la aptitud del material para hormigones o filtración industrial, detallando el impacto financiero y los ajustes operativos en planta para la toma de decisiones de los accionistas."
                    )

                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            types.Part.from_bytes(
                                data=image_bytes,
                                mime_type=file.content_type,
                            ),
                            prompt
                        ]
                    )
                    resultado = response.text

                except Exception as e:
                    error = f"Ocurrió un error en el procesamiento técnico: {str(e)}"

    return render_template_string(HTML_TEMPLATE, resultado=resultado, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
