import os
import time
from flask import Flask, render_template_string, request
from google import genai
from google.genai import types

app = Flask(__name__)

# Inicialización segura del cliente con el SDK moderno
api_key_val = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key_val)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Laboratorio de Áridos - Control de Calidad GRAVAFILT S.A.</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            -webkit-font-smoothing: antialiased;
        }
        .navbar {
            background: linear-gradient(135deg, #1e293b, #0f172a);
        }
        .card {
            border: none;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            position: relative;
            overflow: hidden;
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
        .result-box {
            background-color: #ffffff;
            border-left: 6px solid #2563eb;
            padding: 20px;
            border-radius: 12px;
            margin-top: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            overflow-x: auto; /* Evita desbordes en celulares */
        }
        /* Contenedor responsivo para tablas generadas en Markdown */
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
            padding: 10px 12px;
            text-align: center;
            border: 1px solid #e2e8f0;
        }
        .result-box th {
            background-color: #1e293b;
            color: #ffffff;
            font-weight: 600;
        }
        .result-box tr:nth-child(even) {
            background-color: #f8fafc;
        }
        /* Capa de carga elegante y fluida (Evita pantallas negras o parpadeos bruscos) */
        #loadingOverlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.92);
            z-index: 1000;
            display: none;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            backdrop-filter: blur(2px);
        }
    </style>
</head>
<body>

    <!-- Barra de Navegación -->
    <nav class="navbar navbar-dark shadow-sm py-3">
        <div class="container">
            <a class="navbar-brand fw-bold fs-6 fs-md-5 text-white text-wrap" href="/">
                <i class="fas fa-flask me-2 text-warning"></i>GRAVAFILT S.A. | Control de Calidad
            </a>
        </div>
    </nav>

    <!-- Contenido Principal -->
    <div class="container my-4 my-md-5">
        <div class="row justify-content-center">
            <div class="col-lg-10">
                
                <!-- Tarjeta del Formulario -->
                <div class="card p-3 p-md-5">
                    
                    <!-- Capa de Carga Interna (Fluida y sin apagar pantalla) -->
                    <div id="loadingOverlay">
                        <div class="spinner-border text-primary mb-3" role="status" style="width: 3.5rem; height: 3.5rem;">
                            <span class="visually-hidden">Procesando...</span>
                        </div>
                        <h5 class="text-dark fw-bold">Analizando muestra en laboratorio...</h5>
                        <p class="text-muted small text-center px-3">Calculando granulometría y parámetros técnicos con IA. Esto puede tomar unos segundos.</p>
                    </div>

                    <h2 class="mb-3 text-dark fw-bold text-center fs-3 fs-md-2">Laboratorio Automatizado de Áridos</h2>
                    <p class="text-muted text-center mb-4 small fs-md-6">Sube una fotografía de alta resolución de tu muestra de arena o grava para generar de manera instantánea el ensayo granulométrico técnico y cuadro oficial de tamices.</p>

                    <form method="POST" enctype="multipart/form-data" onsubmit="mostrarCarga(event)">
                        <div class="mb-4">
                            <label for="file" class="form-label fw-semibold text-secondary">Seleccionar imagen de la muestra:</label>
                            <input class="form-control form-control-lg" type="file" id="file" name="file" accept="image/*" required>
                        </div>
                        <div class="d-grid">
                            <button type="submit" id="btnAnalizar" class="btn btn-custom btn-lg text-white">
                                <i class="fas fa-microscope me-2"></i>Ejecutar Ensayo de Laboratorio
                            </button>
                        </div>
                    </form>

                    <!-- Sección de Resultados -->
                    {% if resultado %}
                    <div class="result-box mt-4">
                        <h4 class="text-dark fw-bold mb-3 fs-5 fs-md-4"><i class="fas fa-file-invoice text-success me-2"></i>Informe Técnico de Laboratorio:</h4>
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
        </div>
    </div>

    <!-- Script de animación fluida (Evita parpadeos y pantallas negras) -->
    <script>
        function mostrarCarga(event) {
            // Muestra la capa de carga suave sobre la tarjeta
            document.getElementById('loadingOverlay').style.display = 'flex';
            document.getElementById('btnAnalizar').disabled = true;
        }
    </script>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
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
                    
                    prompt = (
                        "Actúa con rigor absoluto como Ingeniero Geotécnico y Jefe de Control de Calidad de plantas de áridos (GRAVAFILT S.A.). "
                        "Analiza con extremo detalle técnico la fotografía provista de la muestra de material (arena o grava). "
                        "Tu informe de laboratorio debe contener estrictamente lo siguiente:\n\n"
                        "1. **Caracterización Fisotécnica:** Clasificación visual precisa del árido, morfología de las partículas (angulosas, subredondeadas, esfericidad), estimación de limpieza y ausencia o presencia de material limoso/arcilloso (finos).\n"
                        "2. **Cuadro Granulométrico Oficial (Norma de Laboratorio IRAM / ASTM):** "
                        "Construye una tabla formateada en Markdown clara y rigurosa que contenga exactamente estas columnas:\n"
                        "   | Tamiz / Malla | Abertura (mm) | % Retenido Parcial | % Retenido Acumulado | % Pasante Acumulado |\n"
                        "   Utiliza la serie estándar completa correspondiente al material analizado (ej: 9.5 mm, 4.75 mm, 2.36 mm, 1.18 mm, 0.600 mm, 0.300 mm, 0.150 mm, Fondo).\n"
                        "3. **Parámetros Estadísticos del Ensayo:** Estimación técnica del Módulo de Finura (MF) y Tamaño Máximo Nominal (TMN).\n"
                        "4. **Dictamen de Calidad y Operativa:** Conclusión técnica formal sobre la aptitud del material para hormigones, construcción o filtración industrial, detallando las acciones correctivas o ajustes necesarios en la línea de clasificación de la planta."
                    )

                    # Sistema de reintentos ante picos de tráfico en Render / API
                    max_intentos = 3
                    for intento in range(max_intentos):
                        try:
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
                            break
                        except Exception as api_err:
                            if "503" in str(api_err) and intento < max_intentos - 1:
                                time.sleep(2 * (intento + 1))
                                continue
                            raise api_err

                except Exception as e:
                    error = f"Ocurrió un error en el procesamiento técnico (servidores ocupados, intenta de nuevo en unos segundos): {str(e)}"

    return render_template_string(HTML_TEMPLATE, resultado=resultado, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
