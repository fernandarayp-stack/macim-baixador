from flask import Flask, request, jsonify, render_template_string, send_file
import yt_dlp
import os
import uuid
import time

app = Flask(__name__)

# --- O NOSSO SITE EM HTML ---
HTML_SITE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Macim Ferramentas - Baixador Universal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        .fade-in { animation: fadeIn 0.4s ease-in-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .loader { border: 3px solid #f3f3f3; border-top: 3px solid #ef4444; border-radius: 50%; width: 24px; height: 24px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 8px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #c1c1c1; border-radius: 8px; }
    </style>
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center p-4 font-sans text-gray-800">

    <main class="w-full max-w-xl bg-white rounded-3xl shadow-2xl overflow-hidden transition-all duration-300 flex flex-col">
        
        <div class="bg-gradient-to-r from-red-600 to-red-500 p-8 text-center relative shrink-0">
            <div class="absolute -right-10 -top-10 opacity-10 transform rotate-12">
                <i data-lucide="download-cloud" class="w-48 h-48 text-white"></i>
            </div>
            <div class="relative z-10 flex flex-col items-center">
                <div class="bg-white p-3 rounded-full shadow-md mb-3">
                    <i data-lucide="tool" class="w-8 h-8 text-red-600"></i>
                </div>
                <h1 class="text-2xl sm:text-3xl font-bold text-white tracking-tight">Macim ferramentas</h1>
                <p class="text-red-100 mt-2 text-sm font-medium">Baixador Universal de Alta Qualidade</p>
            </div>
        </div>

        <div class="p-6 sm:p-8 bg-gray-50 relative">
            <div class="mb-6 text-sm text-gray-600 bg-white border border-gray-200 p-4 rounded-xl flex gap-3 shadow-sm">
                <i data-lucide="info" class="w-5 h-5 text-red-500 shrink-0"></i>
                <p>Suporta YouTube, TikTok, Instagram (Reels), X/Twitter, Facebook, Kwai e centenas de outros sites. Basta colar o link abaixo!</p>
            </div>

            <!-- Formulário -->
            <form id="downloadForm" class="space-y-4">
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <i data-lucide="link" class="w-5 h-5 text-gray-400"></i>
                    </div>
                    <input type="url" id="urlInputBaixador" class="block w-full pl-11 pr-4 py-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 bg-white text-gray-900 shadow-sm transition-shadow hover:shadow-md" placeholder="Cole o link do vídeo aqui..." required>
                </div>
                <button type="submit" class="w-full bg-gray-900 hover:bg-black text-white font-bold py-4 px-4 rounded-xl transition-transform flex items-center justify-center gap-2 shadow-lg active:scale-95">
                    <span>Analisar e Preparar</span>
                    <i data-lucide="search" class="w-5 h-5"></i>
                </button>
            </form>

            <!-- Loading State da Busca -->
            <div id="loadingStateBaixador" class="hidden flex flex-col items-center justify-center py-10">
                <div class="loader mb-4"></div>
                <p class="text-gray-500 text-sm font-medium animate-pulse">A buscar informações do vídeo...</p>
            </div>

            <div id="resultAreaBaixador" class="hidden mt-8 pt-6 border-t border-gray-200 fade-in">
                <div class="flex flex-col gap-4 mb-6 bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
                    <div class="flex flex-col sm:flex-row gap-4 items-start">
                        <img id="videoThumbBaixador" src="" class="w-full sm:w-40 h-28 object-cover rounded-xl shadow-md bg-gray-200 shrink-0">
                        <div class="flex-1 min-w-0 w-full">
                            <h2 id="videoTitleBaixador" class="text-base font-bold text-gray-900 line-clamp-2 mb-2" title="Título do Vídeo">Título</h2>
                            
                            <!-- Descrição -->
                            <div class="bg-gray-50 p-3 rounded-lg border border-gray-200 text-xs text-gray-600 max-h-24 overflow-y-auto custom-scrollbar">
                                <span class="font-bold text-gray-800 block mb-1">Descrição:</span>
                                <p id="videoDescBaixador" class="whitespace-pre-wrap leading-relaxed">Carregando...</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="border-t border-gray-100 pt-4 mt-2">
                        <label class="block text-sm font-bold text-gray-800 mb-2 flex items-center gap-2">
                            <i data-lucide="settings" class="w-4 h-4 text-gray-500"></i> Escolha o Formato:
                        </label>
                        <select id="qualidadeBaixador" class="block w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-red-500 bg-gray-50 font-medium text-gray-900 cursor-pointer">
                            <option value="alta">🎥 Vídeo: Alta Qualidade (Máxima disponível)</option>
                            <option value="media">🎥 Vídeo: Qualidade Média (Mais leve)</option>
                            <option value="audio">🎵 Apenas Áudio (Formato MP3)</option>
                        </select>
                    </div>
                </div>
                
                <button onclick="iniciarDownloadSelecionado()" id="btnFazerDownload" class="w-full flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 text-white font-bold py-4 px-4 rounded-xl shadow-xl transition-all active:scale-95 text-lg">
                    <i data-lucide="download-cloud" class="w-6 h-6"></i> Iniciar Download
                </button>
            </div>
        </div>
    </main>

    <script>
        lucide.createIcons();
        
        let urlParaBaixar = '';
        let tituloParaBaixar = '';

        function linkValido(url) {
            return url.trim().startsWith('http://') || url.trim().startsWith('https://');
        }

        document.getElementById('downloadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const url = document.getElementById('urlInputBaixador').value.trim();
            
            if (!linkValido(url)) {
                return alert("Por favor, insira um link válido começando com http:// ou https://");
            }

            urlParaBaixar = url;
            document.getElementById('resultAreaBaixador').classList.add('hidden');
            document.getElementById('loadingStateBaixador').classList.remove('hidden');

            try {
                const response = await fetch('/api/info', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                const res = await response.json();
                
                if (res.sucesso) {
                    tituloParaBaixar = res.dados.titulo;
                    document.getElementById('videoTitleBaixador').textContent = res.dados.titulo;
                    
                    const thumb = document.getElementById('videoThumbBaixador');
                    if(res.dados.thumb) {
                         thumb.src = res.dados.thumb;
                    } else {
                         thumb.src = "https://via.placeholder.com/300x200.png?text=Sem+Capa";
                    }
                    
                    document.getElementById('videoDescBaixador').textContent = res.dados.descricao || "Nenhuma descrição disponível para este vídeo.";
                    
                    document.getElementById('loadingStateBaixador').classList.add('hidden');
                    document.getElementById('resultAreaBaixador').classList.remove('hidden');
                } else {
                    alert("Erro ao ler o vídeo. Verifique se o link está correto e se o vídeo é público.");
                    document.getElementById('loadingStateBaixador').classList.add('hidden');
                }
            } catch (e) {
                alert("Erro de conexão com o servidor.");
                document.getElementById('loadingStateBaixador').classList.add('hidden');
            }
        });

        async function iniciarDownloadSelecionado() {
            const qualidade = document.getElementById('qualidadeBaixador').value;
            const btn = document.getElementById('btnFazerDownload');
            
            btn.disabled = true;
            btn.innerHTML = '<div class="loader !border-t-white !w-6 !h-6 mr-2"></div> A baixar no servidor...';
            btn.classList.replace('bg-red-600', 'bg-gray-800');
            btn.classList.replace('hover:bg-red-700', 'hover:bg-gray-900');

            try {
                const response = await fetch('/api/download_video', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: urlParaBaixar, qualidade: qualidade })
                });
                const result = await response.json();
                
                if (result.sucesso) {
                    btn.innerHTML = '<i data-lucide="check-circle" class="w-6 h-6"></i> Pronto! A enviar ficheiro...';
                    btn.classList.replace('bg-gray-800', 'bg-green-600');
                    btn.classList.replace('hover:bg-gray-900', 'hover:bg-green-700');
                    
                    window.location.href = `/api/download_file?id=${result.id}&titulo=${encodeURIComponent(tituloParaBaixar)}&ext=${result.ext}`;
                    
                    setTimeout(() => {
                        btn.disabled = false;
                        btn.innerHTML = '<i data-lucide="download-cloud" class="w-6 h-6"></i> Iniciar Download';
                        btn.classList.replace('bg-green-600', 'bg-red-600');
                        btn.classList.replace('hover:bg-green-700', 'hover:bg-red-700');
                        document.getElementById('urlInputBaixador').value = '';
                        document.getElementById('resultAreaBaixador').classList.add('hidden');
                    }, 5000);
                } else {
                    alert("Erro ao baixar: " + result.erro);
                    restaurarBotaoErro(btn);
                }
            } catch (e) { 
                alert("Erro de conexão durante o download."); 
                restaurarBotaoErro(btn);
            }
            lucide.createIcons();
        }

        function restaurarBotaoErro(btn) {
            btn.disabled = false;
            btn.innerHTML = '<i data-lucide="refresh-cw" class="w-6 h-6"></i> Tentar Novamente';
            btn.classList.replace('bg-gray-800', 'bg-red-600');
            btn.classList.replace('hover:bg-gray-900', 'hover:bg-red-700');
        }
    </script>
</body>
</html>
"""

def limpar_arquivos_antigos():
    """Para o servidor não ficar com disco cheio, apagamos os vídeos com mais de 1 hora"""
    pasta_destino = 'downloads'
    if not os.path.exists(pasta_destino):
        return
        
    agora = time.time()
    for f in os.listdir(pasta_destino):
        caminho = os.path.join(pasta_destino, f)
        if os.path.isfile(caminho):
            # Se o arquivo tem mais de 3600 segundos (1 hora), apaga-o
            if agora - os.path.getmtime(caminho) > 3600:
                try:
                    os.remove(caminho)
                except Exception:
                    pass

@app.route('/')
def home():
    return render_template_string(HTML_SITE)

@app.route('/api/info', methods=['POST'])
def info_video():
    url = request.json.get('url')
    opcoes_ydl = {'quiet': True, 'extract_flat': False, 'noplaylist': True}
    try:
        with yt_dlp.YoutubeDL(opcoes_ydl) as ydl:
            info = ydl.extract_info(url, download=False)
            dados = {
                'titulo': info.get('title', 'Vídeo Sem Título'),
                'canal': info.get('uploader', 'Autor Desconhecido'),
                'thumb': info.get('thumbnail', ''),
                'descricao': info.get('description', 'Nenhuma descrição disponível.') 
            }
        return jsonify({'sucesso': True, 'dados': dados})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/download_video', methods=['POST'])
def download_video():
    # Limpa o lixo antigo antes de baixar um novo
    limpar_arquivos_antigos()
    
    dados = request.json
    url = dados.get('url')
    qualidade = dados.get('qualidade', 'alta')
    
    pasta_destino = 'downloads'
    os.makedirs(pasta_destino, exist_ok=True)
    file_id = str(uuid.uuid4())
    
    if qualidade == 'audio':
        opcoes_ydl = {
            'format': 'bestaudio/best',
            'outtmpl': f'{pasta_destino}/{file_id}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True, 'noplaylist': True
        }
        ext_final = 'mp3'
    elif qualidade == 'media':
        opcoes_ydl = {
            'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'merge_output_format': 'mp4',
            'outtmpl': f'{pasta_destino}/{file_id}.%(ext)s',
            'quiet': True, 'noplaylist': True
        }
        ext_final = 'mp4'
    else: 
        opcoes_ydl = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{pasta_destino}/{file_id}.%(ext)s',
            'quiet': True, 'noplaylist': True
        }
        ext_final = 'mp4'

    try:
        with yt_dlp.YoutubeDL(opcoes_ydl) as ydl:
            ydl.download([url])
        return jsonify({"sucesso": True, "id": file_id, "ext": ext_final})
    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500

@app.route('/api/download_file')
def enviar_para_usuario():
    file_id = request.args.get('id')
    titulo = request.args.get('titulo', 'video_baixado')
    ext = request.args.get('ext', 'mp4')
    
    titulo_limpo = "".join([c for c in titulo if c.isalnum() or c in ' _-']).rstrip()
    if not titulo_limpo:
        titulo_limpo = "video_macim"
        
    caminho_arquivo = f'downloads/{file_id}.{ext}'
    
    return send_file(caminho_arquivo, as_attachment=True, download_name=f"{titulo_limpo}.{ext}")

if __name__ == '__main__':
    # Configuração para rodar no servidor web
    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta)