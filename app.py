import os
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Laboratorio de Áridos - Control de Calidad GRAVAFILT S.A.</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .navbar {
            background: linear-gradient(135deg, #1e293b, #0f172a);
        }
        .card {
            border: none;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
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
            padding: 30px;
            border-radius: 12px;
            margin-top: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        }
        table {
            width: 100%;
            margin-top: 20px;
            margin-bottom: 20px;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px 15px;
            text-align: center;
            border: 1px solid #e2e8f0;
        }
        th {
            background-color: #1e293b;
            color: #ffffff;
            font-weight: 600;
        }
        tr:nth-child(even) {
            background-color: #f8fafc;
        }
    </style>
</head>
<body>

    <!-- Barra de Navegación -->
    <nav class="navbar navbar-dark shadow-sm py-3">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">
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
                    <p class="text-muted text-center mb-4">Sube una fotografía de alta resolución de tu muestra de arena o grava para generar de manera instantánea el ensayo granulométrico técnico y cuadro oficial de tamices.</p>

                    <form method="POST" enctype="multipart/form-data" onsubmit="mostrarCarga()">
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
                        <div class="text-secondary" style="white-space: pre-line; line-height: 1.7;">{{ resultado }}</div>
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
            document.getElementById('btnAnalizar').innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Generando Reporte...';
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
                    
                    # Prompt ultra técnico enfocado estrictamente en normas de laboratorio para áridos
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

                    # Llamada utilizando el modelo actual y vigente en el SDK moderno
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
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
