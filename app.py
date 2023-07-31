from flask import Flask, render_template, request, Response, redirect, url_for
import cv2
import threading

app = Flask(__name__)
app.config['CAMERAS'] = []  # Lista para armazenar as informações das câmeras

def get_video_stream(ip):
    video = cv2.VideoCapture(ip)

    # Reduza a resolução do vídeo para 100x100 pixels (ajuste os valores conforme necessário)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, 100)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 100)

    # Controle a taxa de quadros (ajuste o FPS conforme necessário)
    video.set(cv2.CAP_PROP_FPS, 30)

    return video

def video_stream_thread(camera):
    while True:
        check, frame = camera['camera'].read()
        if not check:
            break
        # Redimensione o frame para 300x200 pixels
        frame = cv2.resize(frame, (300, 200))
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def start_video_stream(camera):
    video_thread = threading.Thread(target=video_stream_thread, args=(camera,))
    video_thread.start()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ip = request.form['ip']
        if ip:
            camera = get_video_stream(ip)
            if camera.isOpened():
                camera_info = {
                    'camera': camera,
                    'clients': []
                }
                app.config['CAMERAS'].append(camera_info)

                # Inicie a transmissão de vídeo em uma thread separada
                start_video_stream(camera_info)

    return render_template('index.html', cameras=app.config['CAMERAS'])

@app.route('/remove_camera/<int:index>', methods=['POST'])
def remove_camera(index):
    if index <= len(app.config['CAMERAS']):
        camera_info = app.config['CAMERAS'][index - 1]
        camera_info['camera'].release()  # Libere a câmera antes de remover
        app.config['CAMERAS'].pop(index - 1)
    return redirect(url_for('index'))

@app.route('/video_feed/<int:index>')
def video_feed(index):
    if index <= len(app.config['CAMERAS']):
        camera_info = app.config['CAMERAS'][index - 1]
        return Response(video_stream_thread(camera_info), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
