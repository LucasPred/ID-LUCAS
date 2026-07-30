import os
from flask import Flask, render_template_string, request
from google import genai
from google.genai import types

app = Flask(__name__)

# Inicialización segura del cliente leyendo explícitamente la clave de entorno
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
        table {
            width: 100%;
            margin-top: 15px;
            margin-bottom: 15px;
        }
        th, td {
            padding: 10px;
            text-align: center;
            border: 1px solid #dee2e6;
        }
        th {
            background-color: #212529;
            color: #ffffff;
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
                    <h2 class="mb-3 text-dark fw-bold text-center">Laboratorio Automatizado de Áridos</h2>
                    <p class="text-muted text-center mb-4">Sube una fotografía de alta resolución de tu muestra de arena o grava para ejecutar el ensayo granulométrico técnico.</p>

                    <form method="POST" enctype="multipart/form-data" onsubmit="mostrarCarga()">
                        <div class="mb-4">
                            <label for="file" class="form-label fw-semibold text-secondary">Seleccionar imagen de la muestra:</label>
                            <input class="form-control form-control-lg" type="file" id="file" name="file" accept="image/*" required>
                        </div>
                        <div class="d-grid">
                            <button type="submit" id="btnAnalizar" class="btn btn-custom btn-lg text-white">
                                <i class="fas fa-microscope me-2"></i>Ejecutar Ensayo Técnico
                            </button>
                        </div>
                    </form>

                    <!-- Indicador de carga -->
                    <div id="loadingIndicator" class="text-center mt-4" style="display: none;">
                        <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                            <span class="visually-hidden">Procesando...</span>
                        </div>
                        <p class="text-primary fw-semibold mt-2">Analizando granulometría y calculando curva de tamices con IA...</p>
                    </div>

                    <!-- Sección de Resultados -->
                    {% if resultado %}
                    <div class="result-box mt-4">
                        <h4 class="text-dark fw-bold mb-3"><i class="fas fa-file-invoice text-success me-2"></i>Informe Técnico de Laboratorio:</h4>
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
            document.getElementById('btnAnalizar').innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Ensamblando Reporte...';
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
                    
                    prompt = (
                        "Actúa con rigor absoluto como Ingeniero Geotécnico y Jefe de Control de Calidad de plantas de áridos (GRAVAFILT S.A.). "
                        "Analiza con detalle la fotografía provista de la muestra de material (arena o grava). "
                        "Tu informe debe estructurarse estrictamente de la siguiente forma:\n\n"
                        "1. **Caracterización Fisotécnica:** Clasificación visual del árido, morfología de los cantos (angulosos, subredondeados), estimación de limpieza y presencia de impurezas o finos arcillosos.\n"
                        "2. **Cuadro Granulométrico Oficial (Norma de Laboratorio):** "
                        "Construye una tabla formateada en Markdown clara y detallada que contenga exactamente estas columnas:\n"
                        "   | Tamiz / Malla | Abertura (mm) | % Retenido Parcial | % Retenido Acumulado | % Pasante Acumulado |\n"
                        "   Utiliza la serie estándar completa correspondiente al material analizado (ej: 9.5 mm, 4.75 mm, 2.36 mm, 1.18 mm, 0.600 mm, 0.300 mm, 0.150 mm, Fondo).\n"
                        "3. **Parámetros Estadísticos:** Estimación técnica del Módulo de Finura (MF) y Tamaño Máximo Nominal (TMN).\n"
                        "4. **Dictamen de Calidad:** Conclusión técnica sobre la aptitud del material para uso industrial, hormigones o sistemas de filtración, indicando los ajustes operativos necesarios en planta."
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
