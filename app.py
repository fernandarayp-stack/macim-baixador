from flask import Flask, request, jsonify, render_template_string, send_file
import yt_dlp
import os
import uuid
import time

app = Flask(__name__)

HTML_SITE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Macim Download - Premium</title>
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    
    <style>
        :root {
            --primary: #8b5cf6; /* Violet */
            --secondary: #3b82f6; /* Blue */
        }
        body {
            font-family: 'Outfit', sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            overflow-x: hidden;
            min-height: 100vh;
        }
        
        /* Glassmorphism Classes */
        .glass-panel {
            background: rgba(30, 41, 59, 0.6);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        
        .glass-input {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
            transition: all 0.3s ease;
        }
        .glass-input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.15);
            outline: none;
        }

        /* Animated Blobs in Background */
        .blob {
            position: absolute;
            border-radius: 50%;
            filter: blur(80px);
            z-index: -1;
            animation: float 10s infinite ease-in-out alternate;
        }
        .blob-1 { top: -10%; left: -10%; width: 400px; height: 400px; background: rgba(139, 92, 246, 0.4); }
        .blob-2 { bottom: -10%; right: -10%; width: 500px; height: 500px; background: rgba(59, 130, 246, 0.3); animation-delay: -5s; }
        
        @keyframes float {
            0% { transform: translate(0, 0) scale(1); }
            100% { transform: translate(30px, 50px) scale(1.1); }
        }

        /* Loading Spinner Advanced */
        .loader-ring {
            width: 40px; height: 40px;
            border: 3px solid rgba(139, 92, 246, 0.2);
            border-radius: 50%;
            border-top-color: var(--primary);
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* General Animations */
        .fade-in-up { animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #475569; }

        /* Gradient Text */
        .text-gradient {
            background: linear-gradient(to right, #a78bfa, #60a5fa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    </style>
</head>
<body class="relative flex items-center justify-center p-4">

    <!-- Background Animated Blobs -->
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>

    <!-- Main Container -->
    <main class="w-full max-w-2xl glass-panel rounded-[2rem] overflow-hidden fade-in-up flex flex-col relative z-10">
        
        <!-- Premium Header -->
        <div class="p-8 pb-6 text-center relative border-b border-white/5">
            <div class="inline-flex items-center justify-center p-4 bg-white/5 rounded-2xl mb-4 border border-white/10 shadow-lg backdrop-blur-md relative group">
                <div class="absolute inset-0 bg-gradient-to-r from-violet-500 to-blue-500 opacity-20 group-hover:opacity-40 transition-opacity rounded-2xl blur-md"></div>
                <i data-lucide="zap" class="w-10 h-10 text-violet-400 relative z-10"></i>
            </div>
            <h1 class="text-4xl sm:text-5xl font-extrabold tracking-tight mb-2">
                Macim <span class="text-gradient">Download</span>
            </h1>
            <p class="text-slate-400 text-sm sm:text-base font-medium">A nova geração de downloads em Alta Qualidade.</p>
        </div>

        <div class="p-6 sm:p-10 pt-6">
            
            <!-- Plataformas Suportadas (Micro-UI) -->
            <div class="flex items-center justify-center gap-4 mb-8 text-slate-500">
                <i data-lucide="youtube" class="w-5 h-5 hover:text-white transition-colors" title="YouTube"></i>
                <i data-lucide="instagram" class="w-5 h-5 hover:text-white transition-colors" title="Instagram"></i>
                <i data-lucide="twitter" class="w-5 h-5 hover:text-white transition-colors" title="X/Twitter"></i>
                <i data-lucide="facebook" class="w-5 h-5 hover:text-white transition-colors" title="Facebook"></i>
                <span class="text-xs font-bold uppercase tracking-widest">+ TikTok & Mais</span>
            </div>

            <!-- Formulário -->
            <form id="downloadForm" class="space-y-5">
                <div class="relative group">
                    <div class="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
                        <i data-lucide="link-2" class="w-6 h-6 text-slate-400 group-focus-within:text-violet-400 transition-colors"></i>
                    </div>
                    <input type="url" id="urlInputBaixador" class="block w-full pl-14 pr-5 py-5 rounded-2xl glass-input text-lg font-medium placeholder-slate-500 shadow-inner" placeholder="Cole a ligação do vídeo aqui..." required autocomplete="off">
                </div>
                
                <button type="submit" class="w-full bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 text-white font-bold py-5 px-6 rounded-2xl transition-all duration-300 flex items-center justify-center gap-3 shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_30px_rgba(139,92,246,0.5)] active:scale-[0.98] text-lg border border-white/10">
                    <span>Processar Vídeo</span>
                    <i data-lucide="arrow-right" class="w-5 h-5"></i>
                </button>
            </form>

            <!-- Loading State -->
            <div id="loadingStateBaixador" class="hidden flex-col items-center justify-center py-12">
                <div class="loader-ring mb-6"></div>
                <p class="text-violet-300 text-sm font-semibold tracking-widest uppercase animate-pulse">A extrair dados neurais...</p>
            </div>

            <!-- Área de Resultados -->
            <div id="resultAreaBaixador" class="hidden mt-8 fade-in-up">
                
                <div class="glass-panel p-5 rounded-[1.5rem] mb-6 flex flex-col sm:flex-row gap-5 items-start">
                    <div class="relative w-full sm:w-48 shrink-0 overflow-hidden rounded-xl border border-white/10 group">
                        <div class="absolute inset-0 bg-black/20 group-hover:bg-transparent transition-colors z-10"></div>
                        <img id="videoThumbBaixador" src="" class="w-full h-32 object-cover transition-transform duration-700 group-hover:scale-110">
                        <div class="absolute bottom-2 right-2 bg-black/70 backdrop-blur-sm text-white text-[10px] font-bold px-2 py-1 rounded-md z-20 flex items-center gap-1">
                            <i data-lucide="check-circle" class="w-3 h-3 text-emerald-400"></i> Pronto
                        </div>
                    </div>
                    
                    <div class="flex-1 min-w-0 w-full flex flex-col justify-between h-full">
                        <div>
                            <h2 id="videoTitleBaixador" class="text-base sm:text-lg font-bold text-white line-clamp-2 leading-snug mb-2" title="Título do Vídeo">Título do Vídeo</h2>
                            <p class="text-xs text-slate-400 flex items-center gap-1 mb-3">
                                <i data-lucide="shield-check" class="w-3 h-3 text-violet-400"></i> Analisado com segurança
                            </p>
                        </div>
                        
                        <!-- Seletor de Qualidade -->
                        <div id="secaoQualidade" class="mt-auto">
                            <select id="qualidadeBaixador" class="block w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-violet-500 text-slate-200 font-medium cursor-pointer transition-colors hover:bg-slate-800">
                                <option value="alta">🎥 MP4 - Alta Qualidade</option>
                                <option value="media">🎥 MP4 - Qualidade Média</option>
                                <option value="audio">🎵 MP3 - Apenas Áudio</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <button onclick="iniciarDownloadSelecionado()" id="btnFazerDownload" class="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-extrabold py-5 px-6 rounded-2xl transition-all duration-300 flex items-center justify-center gap-3 shadow-[0_0_20px_rgba(16,185,129,0.2)] hover:shadow-[0_0_30px_rgba(16,185,129,0.4)] active:scale-[0.98] text-lg">
                    <i data-lucide="download" class="w-6 h-6"></i> <span>Descarregar Ficheiro</span>
                </button>
            </div>
        </div>
    </main>

    <div id="toast-container" class="fixed bottom-6 right-6 z-50 flex flex-col gap-3 pointer-events-none"></div>

    <script>
        lucide.createIcons();
        
        let urlParaBaixar = '';
        let tituloParaBaixar = '';
        let isYoutube = false;

        function mostrarNotificacao(mensagem, tipo = 'erro') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            
            let bgClass = tipo === 'erro' ? 'bg-rose-500/90' : 'bg-emerald-500/90';
            let iconName = tipo === 'erro' ? 'alert-triangle' : 'check-circle';
            
            toast.className = `flex items-center gap-3 px-5 py-4 rounded-2xl shadow-2xl text-white font-medium text-sm backdrop-blur-md border border-white/20 transform transition-all duration-500 translate-y-10 opacity-0 ${bgClass}`;
            toast.innerHTML = `<i data-lucide="${iconName}" class="w-5 h-5 shrink-0"></i> <span>${mensagem}</span>`;
            
            container.appendChild(toast);
            lucide.createIcons();
            
            requestAnimationFrame(() => {
                toast.classList.remove('translate-y-10', 'opacity-0');
            });
            
            setTimeout(() => {
                toast.classList.add('translate-y-10', 'opacity-0');
                setTimeout(() => toast.remove(), 500);
            }, 4000);
        }

        function linkValido(url) {
            return url.trim().startsWith('http://') || url.trim().startsWith('https://');
        }

        function extrairVideoId(url) {
            const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts|live)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/i;
            const match = url.match(regex);
            return match ? match[1] : null;
        }

        document.getElementById('downloadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const url = document.getElementById('urlInputBaixador').value.trim();
            
            if (!linkValido(url)) {
                return mostrarNotificacao("Por favor, insira uma ligação válida.", "erro");
            }

            urlParaBaixar = url;
            const videoId = extrairVideoId(url);
            isYoutube = videoId !== null;

            document.getElementById('resultAreaBaixador').classList.add('hidden');
            document.getElementById('loadingStateBaixador').classList.remove('hidden');
            document.getElementById('loadingStateBaixador').classList.add('flex');

            if (isYoutube) {
                // FLUXO DE REDIRECIONAMENTO (Apenas para o YouTube)
                document.getElementById('secaoQualidade').classList.add('hidden');
                
                try {
                    const response = await fetch(`https://noembed.com/embed?url=https://www.youtube.com/watch?v=${videoId}`);
                    const data = await response.json();
                    document.getElementById('videoTitleBaixador').textContent = data.title || "Vídeo do YouTube";
                    document.getElementById('videoThumbBaixador').src = `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
                    
                    document.getElementById('loadingStateBaixador').classList.remove('flex');
                    document.getElementById('loadingStateBaixador').classList.add('hidden');
                    document.getElementById('resultAreaBaixador').classList.remove('hidden');
                } catch (error) {
                    mostrarNotificacao("Erro ao ler o YouTube. O link está correto?");
                    document.getElementById('loadingStateBaixador').classList.remove('flex');
                    document.getElementById('loadingStateBaixador').classList.add('hidden');
                }
            } else {
                // FLUXO NORMAL (Instagram, TikTok, X processados DIRETAMENTE no Backend da tela)
                document.getElementById('secaoQualidade').classList.remove('hidden');
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
                        document.getElementById('videoThumbBaixador').src = res.dados.thumb || "https://via.placeholder.com/300x200/1e293b/8b5cf6.png?text=Vídeo+Encontrado";
                        
                        document.getElementById('loadingStateBaixador').classList.remove('flex');
                        document.getElementById('loadingStateBaixador').classList.add('hidden');
                        document.getElementById('resultAreaBaixador').classList.remove('hidden');
                        mostrarNotificacao("Vídeo identificado com sucesso!", "sucesso");
                    } else {
                        mostrarNotificacao("Erro ao ler o vídeo. Certifique-se que o link é público.");
                        document.getElementById('loadingStateBaixador').classList.remove('flex');
                        document.getElementById('loadingStateBaixador').classList.add('hidden');
                    }
                } catch (e) {
                    mostrarNotificacao("Falha de conexão com o servidor neural.");
                    document.getElementById('loadingStateBaixador').classList.remove('flex');
                    document.getElementById('loadingStateBaixador').classList.add('hidden');
                }
            }
        });

        async function iniciarDownloadSelecionado() {
            const btn = document.getElementById('btnFazerDownload');
            const spanTexto = btn.querySelector('span');
            
            if (isYoutube) {
                // REDIRECIONA APENAS O YOUTUBE
                const videoId = extrairVideoId(urlParaBaixar);
                const urlFinal = `https://www.youtube.com/watch?v=${videoId}`;
                const downloadUrl = `https://cobalt.tools/?v=${encodeURIComponent(urlFinal)}`;
                window.open(downloadUrl, '_blank');
                
                // Reset Interface
                document.getElementById('urlInputBaixador').value = '';
                document.getElementById('resultAreaBaixador').classList.add('hidden');
                mostrarNotificacao("A abrir túnel de download seguro...", "sucesso");
            } else {
                // PROCESSA INSTAGRAM, TIKTOK E OUTRAS REDES DIRETAMENTE AQUI NA TELA
                const qualidade = document.getElementById('qualidadeBaixador').value;
                
                btn.disabled = true;
                spanTexto.textContent = "A processar no servidor...";
                btn.classList.replace('bg-emerald-500', 'bg-slate-700');
                btn.classList.replace('hover:bg-emerald-400', 'hover:bg-slate-600');
                btn.classList.remove('text-slate-900');
                btn.classList.add('text-white');
                btn.innerHTML = '<div class="loader-ring !w-5 !h-5 !border-2 !border-t-white mr-2"></div> <span>' + spanTexto.textContent + '</span>';

                try {
                    const response = await fetch('/api/download_video', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url: urlParaBaixar, qualidade: qualidade })
                    });
                    const result = await response.json();
                    
                    if (result.sucesso) {
                        btn.innerHTML = '<i data-lucide="check-circle" class="w-6 h-6"></i> <span>A enviar ficheiro...</span>';
                        btn.classList.replace('bg-slate-700', 'bg-violet-600');
                        btn.classList.replace('hover:bg-slate-600', 'hover:bg-violet-500');
                        
                        // Executa Download para o PC/Telemóvel do utilizador
                        window.location.href = `/api/download_file?id=${result.id}&titulo=${encodeURIComponent(tituloParaBaixar)}&ext=${result.ext}`;
                        mostrarNotificacao("Download iniciado com sucesso!", "sucesso");
                        
                        setTimeout(() => {
                            btn.disabled = false;
                            btn.classList.replace('bg-violet-600', 'bg-emerald-500');
                            btn.classList.replace('hover:bg-violet-500', 'hover:bg-emerald-400');
                            btn.classList.remove('text-white');
                            btn.classList.add('text-slate-900');
                            btn.innerHTML = '<i data-lucide="download" class="w-6 h-6"></i> <span>Descarregar Ficheiro</span>';
                            
                            document.getElementById('urlInputBaixador').value = '';
                            document.getElementById('resultAreaBaixador').classList.add('hidden');
                        }, 5000);
                    } else {
                        mostrarNotificacao("Erro: " + result.erro, "erro");
                        restaurarBotaoErro(btn);
                    }
                } catch (e) { 
                    mostrarNotificacao("Perda de conexão durante o processamento.", "erro"); 
                    restaurarBotaoErro(btn);
                }
                lucide.createIcons();
            }
        }

        function restaurarBotaoErro(btn) {
            btn.disabled = false;
            btn.classList.replace('bg-slate-700', 'bg-emerald-500');
            btn.classList.replace('hover:bg-slate-600', 'hover:bg-emerald-400');
            btn.classList.remove('text-white');
            btn.classList.add('text-slate-900');
            btn.innerHTML = '<i data-lucide="refresh-cw" class="w-6 h-6"></i> <span>Tentar Novamente</span>';
        }
    </script>
</body>
</html>
"""

def limpar_arquivos_antigos():
    """Limpeza automática de ficheiros antigos para o servidor não lotar a memória"""
    pasta_destino = 'downloads'
    if not os.path.exists(pasta_destino):
        return
        
    agora = time.time()
    for f in os.listdir(pasta_destino):
        caminho = os.path.join(pasta_destino, f)
        if os.path.isfile(caminho):
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
                'descricao': info.get('description', '') 
            }
        return jsonify({'sucesso': True, 'dados': dados})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/download_video', methods=['POST'])
def download_video():
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
        titulo_limpo = "Macim_Download"
        
    caminho_arquivo = f'downloads/{file_id}.{ext}'
    return send_file(caminho_arquivo, as_attachment=True, download_name=f"{titulo_limpo}.{ext}")

if __name__ == '__main__':
    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta)
