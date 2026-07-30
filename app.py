import os
from flask import Flask, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

HTML_CONTENT = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulador Industrial - GRAVAFILT S.A.</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 font-sans">
    <div class="max-w-4xl mx-auto p-6">
        <h1 class="text-2xl font-bold text-amber-400 mb-2">GRAVAFILT S.A. | Simulador Táctico</h1>
        <p class="text-xs text-slate-400 mb-6">Sistema de Evaluación Granulométrica e IA</p>
        
        <form id="formSim" class="bg-slate-800 p-6 rounded-xl border border-slate-700 space-y-4">
            <div>
                <label class="block text-xs font-medium mb-1">Módulo de Fineza (MF):</label>
                <input type="text" name="mf" placeholder="Ej. 2.65" class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-white">
            </div>
            <div>
                <label class="block text-xs font-medium mb-1">Fotografía del Material:</label>
                <input type="file" name="imagen" accept="image/*" class="w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-amber-500/10 file:text-amber-400">
            </div>
            <button type="submit" id="btn" class="w-full bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold py-2.5 rounded text-sm">
                Ejecutar Análisis
            </button>
        </form>

        <div id="res" class="mt-6 bg-slate-800/80 border border-slate-700 rounded-xl p-6 text-sm font-mono whitespace-pre-wrap text-slate-300">
            Esperando datos de ejecución...
        </div>
    </div>

    <script>
        const form = document.getElementById('formSim');
        const res = document.getElementById('res');
        const btn = document.getElementById('btn');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            btn.disabled = true;
            res.textContent = "Procesando análisis con Gemini...";
            
            try {
                const formData = new FormData(form);
                const response = await fetch('/analizar', { method: 'POST', body: formData });
                const data = await response.json();
                if (data.status === 'success') {
                    res.textContent = data.texto;
                } else {
                    res.textContent = "Error: " + data.message;
                }
            } catch (err) {
                res.textContent = "Error de conexión con el servidor.";
            } finally {
                btn.disabled = false;
            }
        });
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return HTML_CONTENT

@app.route('/analizar', methods=['POST'])
def analizar():
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return jsonify({"status": "error", "message": "Falta configurar la variable de entorno GEMINI_API_KEY en Render."}), 500
        
        # Inicializar el cliente bajo demanda dentro de la ruta para evitar errores de arranque
        client = genai.Client(api_key=api_key)
        
        mf = request.form.get('mf', 'No especificado')
        imagen = request.files.get('imagen')
        
        prompt = f"Actúa como ingeniero geólogo y analiza este material para áridos industriales. Módulo de fineza ingresado: {mf}."
        contents = [prompt]
        
        if imagen and imagen.filename != '':
            contents.append(types.Part.from_bytes(data=imagen.read(), mime_type=imagen.mimetype or 'image/jpeg'))
            
        response = client.models.generate_content(model='gemini-2.5-flash', contents=contents)
        return jsonify({"status": "success", "texto": response.text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
