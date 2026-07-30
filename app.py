import os
from flask import Flask, render_template_string, request
import google.generativeai as genai

app = Flask(__name__)

# Configuración de la API con la variable de entorno de Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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
    <style>
        body {
            background-color: #f4f7f6;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .navbar-brand {
            font-weight: 700;
            letter-spacing: 0.5px;
        }
        .card {
            border: none;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }
        .btn-custom {
            background-color: #0d6efd;
            border-color: #0d6efd;
            border-radius: 50px;
            padding: 12px 30px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn-custom:hover {
            background-color: #0b5ed7;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(13, 110, 253, 0.3);
        }
        .result-box {
            background-color: #ffffff;
            border-left: 5px solid #0d6efd;
            padding: 25px;
            border-radius: 8px;
            margin-top: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        }
        table.table-lab th {
            background-color: #212529;
            color: #ffffff;
            text-align: center;
        }
        table.table-lab td {
            text-align: center;
            vertical-align: middle;
        }
    </style>
</head>
<body>

    <!-- Barra de Navegación -->
    <nav class="navbar navbar-dark bg-dark shadow-sm py-3">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-flask me-2 text-warning"></i>GRAVAFILT S.A. | Control de Calidad y Granulometría
            </a>
        </div>
    </nav>

    <!-- Contenido Principal -->
    <div class="container my-5">
        <div class="row justify-content-center">
            <div class="col-lg-10">
                
                <!-- Tarjeta del Formulario -->
                <div class="card p-4 p-md-5">
                    <h2 class="mb-3 text-dark fw-bold text-center">Simulador de Ensayo Granulométrico por Visión Artificial</h2>
                    <p class="text-muted text-center mb-4">Sube una fotografía técnica de la muestra de arena o grava para generar el reporte de laboratorio con cuadro de tamices, porcentajes retenidos y pasantes acumulados.</p>

                    <form method="POST" enctype="multipart/form-data" onsubmit="mostrarCarga()">
                        <div class="mb-4">
                            <label for="file" class="form-label fw-semibold text-secondary">Seleccionar imagen de la muestra de áridos:</label>
                            <input class="form-control form-control-lg" type="file" id="file" name="file" accept="image/*" required>
                        </div>
                        <div class="d-grid">
                            <button type="submit" id="btnAnalizar" class="btn btn-custom btn-lg text-white">
                                <i class="fas fa-microscope me-2"></i>Ejecutar Ensayo de Laboratorio
                            </button>
                        </div>
                    </form>

                    <!-- Indicador de carga visual -->
                    <div id="loadingIndicator" class="text-center mt-4" style="display: none;">
                        <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                            <span class="visually-hidden">Procesando...</span>
                        </div>
                        <p class="text-primary fw-semibold mt-2">Ejecutando análisis granulométrico y cálculo de mallas, por favor espere...</p>
                    </div>

                    <!-- Sección de Resultados -->
                    {% if resultado %}
                    <div class="result-box mt-4">
                        <h4 class="text-dark fw-bold mb-3"><i class="fas fa-file-invoice text-success me-2"></i>Reporte Técnico de Laboratorio:</h4>
                        <div class="text-secondary" style="white-space: pre-line; line-height: 1.6;">{{ resultado }}</div>
                    </div>
                    {% endif %}

                    {% if error %}
                    <div class="alert alert-danger mt-4 rounded-3 shadow-sm" role="alert">
                        <i class="fas fa-exclamation-triangle me-2"></i>{{ error }}
                    </div>
                    {% endif %}
                </div>

            </div>
        </div>
    </div>

    <!-- Script de animación -->
    <script>
        function mostrarCarga() {
            document.getElementById('btnAnalizar').disabled = true;
            document.getElementById('btnAnalizar').innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Calculando...';
            document.getElementById('loadingIndicator').style.display = 'block';
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
                    image_part = {
                        "mime_type": file.content_type,
                        "data": image_bytes
                    }

                    # Modelo estable oficial
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    # Prompt altamente técnico enfocado en ingeniería y normativas de áridos
                    prompt = (
                        "Actúa rigurosamente como un Ingeniero Geotécnico y Jefe de Control de Calidad en planta de procesamiento de áridos (GRAVAFILT S.A.). "
                        "Analiza con extrema precisión técnica la imagen provista de la muestra de áridos (arena/grava). "
                        "Debes generar un informe de laboratorio formal que contenga estrictamente lo siguiente:\n\n"
                        "1. **Identificación y Clasificación Geotécnica:** Tipo de árido (fino/grueso), forma de las partículas (angulosas, subangulosas, rodadas), estimación visual de limpieza y ausencia/presencia de material arcilloso o limoso (finos).\n"
                        "2. **Cuadro de Análisis Granulométrico por Tamices (Norma IRAM / ASTM aplicable):** "
                        "Construye una tabla formateada en Markdown que incluya las columnas:\n"
                        "   - Tamiz / Malla (ej: 9.5 mm (3/8\"), 4.75 mm (N° 4), 2.36 mm (N° 8), 1.18 mm (N° 16), 0.600 mm (N° 30), 0.300 mm (N° 50), 0.150 mm (N° 100), Fondo)\n"
                        "   - % Retenido Parcial (Estimación técnica basada en la granulometría visual)\n"
                        "   - % Retenido Acumulado\n"
                        "   - % Pasante Acumulado\n"
                        "3. **Parámetros Estadísticos Derivados:** Estimación del Módulo de Finura (MF) y Tamaño Máximo Nominal (TMN).\n"
                        "4. **Conclusión y Dictamen Técnico:** Dictamen sobre si la muestra cumple con los parámetros estándar para uso en construcción o filtración industrial, detallando observaciones correctivas para la línea de clasificación."
                    )

                    response = model.generate_content([prompt, image_part])
                    resultado = response.text

                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "Quota exceeded" in error_msg:
                        error = "Se ha superado temporalmente el límite de consultas gratuitas de la API. Por favor, aguarda unos segundos e intenta nuevamente."
                    else:
                        error = f"Ocurrió un error en el procesamiento técnico: {error_msg}"

    return render_template_string(HTML_TEMPLATE, resultado=resultado, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
