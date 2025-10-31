from flask import Flask, jsonify, request, send_file
from pytubefix import YouTube
from flask_cors import CORS
import re
import io
import os
app = Flask(__name__)
CORS(app) 

@app.route('/video-info', methods=['POST'])
def video_info():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({ "mensage" : 'URL do video não enviada'}), 400
    
    try:
            yt = YouTube(url)
            audio_Stream = yt.streams.filter(only_audio=True).first()

            info = {
                "title": yt.title,
                "thumbnail": yt.thumbnail_url,
                "length": f"{yt.length//60}m {yt.length % 60}s",
                "views": f"{yt.views:,}".replace(",", "."),
                'tamanho':  f" {audio_Stream.filesize / 1024**2:.2f}"
            }

            return jsonify(info)

    except Exception as e:
        return jsonify({"error": str(e)}), 400




@app.route("/audio-download", methods=["GET"])
def audio_download():
    url = request.args.get("url")  # pega da query string

    if not url:
        return jsonify({"error": "URL do vídeo não enviada"}), 400

    try:
        yt = YouTube(url)

        # 🔽 Escolhe o melhor áudio (maior bitrate)
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()

        print("\n🎯 Selecionado:")
        print(f"itag: {audio_stream.itag}")
        print(f"abr: {audio_stream.abr}")
        print(f"tamanho estimado: {round(audio_stream.filesize / (1024*1024), 2)} MB")
        


        
        # Limpa o título pra evitar caracteres ilegais
        titulo = re.sub(r'[\\/*?:"<>|]', "", yt.title)
        file_name = f"{titulo}.mp3"
        file_path = os.path.join("./", file_name)

        # Baixa o áudio
        audio_stream.download(filename=file_name, output_path="./")

        # Envia o arquivo pro React Native
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_name,
            mimetype="audio/mpeg"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Remove o arquivo depois de enviar (opcional)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)