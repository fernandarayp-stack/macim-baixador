from flask import Flask, request, jsonify, render_template_string, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

# --- O NOSSO SITE EM HTML (Apenas o Baixador) ---
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
                    <i data-lucide="video" class="w-8 h-8 text-red-600"></i>
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
                        </div>
                    </div>
                </div>
                
                <button onclick="iniciarDownloadCompleto()" id="btnFazerDownload" class="w-full flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 text-white font-bold py-4 px-4 rounded-xl shadow-xl transition-all active:scale-95 text-lg">
                    <i data-lucide="download-cloud" class="w-6 h-6"></i> Iniciar Download
                </button>
            </div>
        </div>
    </main>

    <script>
        lucide.createIcons();
        
        let urlParaBaixar = '';

        function linkValido(url) {
            return url.trim().startsWith('http://') || url.trim().startsWith('https://');
        }
        
        // Função para extrair ID do YouTube caso seja um link do Youtube
        function extrairVideoId(url) {
            const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts|live)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/i;
            const match = url.match(regex);
            return match ? match[1] : null;
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
                // Fetch info via noembed (which usually still works for basic info)
                let videoId = extrairVideoId(url);
                if (videoId) {
                    const response = await fetch(`https://noembed.com/embed?url=https://www.youtube.com/watch?v=${videoId}`);
                    const data = await response.json();
                    document.getElementById('videoTitleBaixador').textContent = data.title;
                    document.getElementById('videoThumbBaixador').src = `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
                } else {
                     // Para outros sites, apenas exibe um título genérico por enquanto
                     document.getElementById('videoTitleBaixador').textContent = "Vídeo Pronto para Download";
                     document.getElementById('videoThumbBaixador').src = "https://via.placeholder.com/300x200.png?text=Vídeo";
                }
                
                document.getElementById('loadingStateBaixador').classList.add('hidden');
                document.getElementById('resultAreaBaixador').classList.remove('hidden');
            } catch (e) {
                document.getElementById('loadingStateBaixador').classList.add('hidden');
                alert("Erro ao obter as informações do vídeo. Verifique se o link está correto.");
            }
        });

        async function iniciarDownloadCompleto() {
            // Em vez de baixar no servidor Render (que está bloqueado pelo Youtube), 
            // redirecionamos o usuário para um site de download limpo e gratuito.
            
            // Verifica se é link do YouTube
            let videoId = extrairVideoId(urlParaBaixar);
            
            if (videoId) {
                 // Redireciona para o Cobalt (um downloader open-source e sem anúncios)
                 const downloadUrl = `https://cobalt.tools/?v=https://www.youtube.com/watch?v=${videoId}`;
                 window.open(downloadUrl, '_blank');
            } else {
                 // Se for tiktok, instagram, etc. o Cobalt também aceita
                 const downloadUrl = `https://cobalt.tools/?v=${encodeURIComponent(urlParaBaixar)}`;
                 window.open(downloadUrl, '_blank');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    # Renderiza o site HTML
    return render_template_string(HTML_SITE)

if __name__ == '__main__':
    # Configuração para rodar no servidor web
    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta)
