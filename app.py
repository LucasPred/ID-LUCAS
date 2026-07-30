import os
from flask import Flask, render_template_string, request, redirect, url_for
import google.generativeai as genai

app = Flask(__name__)

# Configuración de la API de Gemini con la clave de entorno
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# HTML + CSS completo con Bootstrap y diseño profesional
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulador de Análisis Granulométrico - GRAVAFILT</title>
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
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        }
    </style>
</head>
<body>

    <!-- Barra de Navegación -->
    <nav class="navbar navbar-dark bg-dark shadow-sm py-3">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-mountain me-2 text-warning"></i>GRAVAFILT S.A. | Simulador de Áridos
            </a>
        </div>
    </nav>

    <!-- Contenido Principal -->
    <div class="container my-5">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                
                <!-- Tarjeta del Formulario -->
                <div class="card p-4 p-md-5">
                    <h2 class="mb-3 text-dark fw-bold text-center">Análisis de Muestras por Inteligencia Artificial</h2>
                    <p class="text-muted text-center mb-4">Sube una fotografía de la muestra de arena o grava para evaluar granulometría, forma y características visuales.</p>

                    <form method="POST" enctype="multipart/form-data">
                        <div class="mb-4">
                            <label for="file" class="form-label fw-semibold text-secondary">Seleccionar imagen de la muestra:</label>
                            <input class="form-control form-control-lg" type="file" id="file" name="file" accept="image/*" required>
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-custom btn-lg text-white">
                                <i class="fas fa-microscope me-2"></i>Analizar Muestra
                            </button>
                        </div>
                    </form>

                    <!-- Sección de Resultados -->
                    {% if resultado %}
                    <div class="result-box mt-4">
                        <h4 class="text-dark fw-bold mb-3"><i class="fas fa-clipboard-check text-success me-2"></i>Informe de Resultados:</h4>
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

                    # Modelo activo y estable actualizados a gemini-1.5-flash
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = (
                        "Actúa como un experto en ingeniería de áridos, minería y control de calidad industrial. "
                        "Analiza detalladamente esta imagen de una muestra de arena o grava. Proporciona una estimación profesional "
                        "de la granulometría, forma de los cantos, limpieza, presencia de finos o impurezas, y una recomendación técnica general."
                    )

                    response = model.generate_content([prompt, image_part])
                    resultado = response.text

                except Exception as e:
                    error = f"Ocurrió un error al procesar la imagen con Gemini: {str(e)}"

    return render_template_string(HTML_TEMPLATE, resultado=resultado, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
