import os, io, base64
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image

from stego import embed_message as embed_text_in_image, extract_message as extract_text_from_image
from security import encrypt_message, decrypt_message
from audio_stego import embed_text_in_wav, extract_text_from_wav
from video_stego import embed_text_in_video, extract_text_from_video

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 256 * 1024 * 1024  # allow big media

#  Home 
@app.route('/')
def home():
    return render_template('home.html', title="HideNseek")

#  Privacy Policy Route 
@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')  # Privacy Policy page

#  Terms of Service Route
@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms_of_service.html')  # Terms of Service page

#  Text -> Image 
@app.route('/text-image/embed', methods=['GET', 'POST'])
def embed_text_image():
    if request.method == 'POST':
        file = request.files.get('image')
        message = request.form.get('message', '').strip()
        use_encrypt = request.form.get('encrypt') == 'on'
        password = request.form.get('password', '')

        if not file or file.filename == '':
            flash('Please select an image file.', 'danger'); return redirect(request.url)
        if not message:
            flash('Please enter a message to embed.', 'danger'); return redirect(request.url)

        filename = secure_filename(file.filename)
        in_path = os.path.join(app.config['UPLOAD_FOLDER'], "ti_in_" + filename)
        file.save(in_path)

        if use_encrypt:
            if not password:
                flash('Password required for encryption.', 'danger'); return redirect(request.url)
            message = encrypt_message(message, password)

        out_filename = f"hidenseek_img_{filename.rsplit('.',1)[0]}.png"
        out_path = os.path.join(app.config['UPLOAD_FOLDER'], out_filename)
        try: embed_text_in_image(in_path, out_path, message)
        except Exception as e:
            flash(f"Embedding failed: {e}", 'danger'); return redirect(request.url)

        flash('Message embedded into image! Download below.', 'success')
        return render_template('embed_text_image.html', download=url_for('download_file', filename=out_filename))
    return render_template('embed_text_image.html')

@app.route('/text-image/extract', methods=['GET', 'POST'])
def extract_text_image():
    if request.method == 'POST':
        file = request.files.get('image')
        use_encrypt = request.form.get('encrypt') == 'on'
        password = request.form.get('password', '')

        if not file or file.filename == '':
            flash('Please select an image file.', 'danger'); return redirect(request.url)

        filename = secure_filename(file.filename)
        in_path = os.path.join(app.config['UPLOAD_FOLDER'], "ti_ex_" + filename)
        file.save(in_path)

        try: hidden = extract_text_from_image(in_path)
        except Exception as e:
            flash(f"Extraction failed: {e}", 'danger'); return redirect(request.url)

        if use_encrypt:
            if not password:
                flash('Password required for decryption.', 'danger'); return redirect(request.url)
            try: hidden = decrypt_message(hidden, password)
            except Exception:
                flash('Decryption failed: wrong password or corrupted data.', 'danger'); return redirect(request.url)

        return render_template('extract_text_image.html', extracted=hidden)
    return render_template('extract_text_image.html')

# - Image -> Image 
@app.route('/image-image/embed', methods=['GET', 'POST'])
def embed_image_image():
    if request.method == 'POST':
        cover = request.files.get('cover')
        secret = request.files.get('secret')
        if not cover or cover.filename == '' or not secret or secret.filename == '':
            flash('Please select both cover and secret images.', 'danger'); return redirect(request.url)

        cover_name = secure_filename(cover.filename)
        secret_name = secure_filename(secret.filename)
        cover_path = os.path.join(app.config['UPLOAD_FOLDER'], "ii_cover_" + cover_name)
        secret_path = os.path.join(app.config['UPLOAD_FOLDER'], "ii_secret_" + secret_name)
        cover.save(cover_path); secret.save(secret_path)

        cover_img = Image.open(cover_path).convert('RGB')
        cover_capacity_bits = cover_img.width * cover_img.height * 3

        secret_img = Image.open(secret_path).convert('RGBA')

        def encode_secret(img):
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            return base64.b64encode(buf.getvalue()).decode()

        b64 = encode_secret(secret_img)
        needed_bits = len(b64) * 8

        # auto-resize until fits
        while needed_bits > cover_capacity_bits:
            new_w, new_h = int(secret_img.width * 0.9), int(secret_img.height * 0.9)
            if new_w < 1 or new_h < 1:
                flash("Secret image too small to embed.", 'danger'); return redirect(request.url)
            secret_img = secret_img.resize((new_w, new_h), Image.LANCZOS)
            b64 = encode_secret(secret_img)
            needed_bits = len(b64) * 8

        out_filename = f"hidenseek_imgimg_{cover_name.rsplit('.',1)[0]}.png"
        out_path = os.path.join(app.config['UPLOAD_FOLDER'], out_filename)
        try: embed_text_in_image(cover_path, out_path, b64)
        except Exception as e:
            flash(f"Embedding failed: {e}", 'danger'); return redirect(request.url)

        flash('Secret image embedded into cover image! (resized if needed)', 'success')
        return render_template('embed_image_image.html', download=url_for('download_file', filename=out_filename))
    return render_template('embed_image_image.html')

@app.route('/image-image/extract', methods=['GET', 'POST'])
def extract_image_image():
    if request.method == 'POST':
        cover = request.files.get('image')
        if not cover or cover.filename == '':
            flash('Please select the stego image.', 'danger'); return redirect(request.url)

        cover_name = secure_filename(cover.filename)
        cover_path = os.path.join(app.config['UPLOAD_FOLDER'], "ii_ex_" + cover_name)
        cover.save(cover_path)

        try: b64 = extract_text_from_image(cover_path)
        except Exception as e:
            flash(f"Extraction failed: {e}", 'danger'); return redirect(request.url)

        try:
            raw = base64.b64decode(b64)
            out_filename = f"hidenseek_revealed_{cover_name.rsplit('.',1)[0]}.png"
            out_path = os.path.join(app.config['UPLOAD_FOLDER'], out_filename)
            with open(out_path, 'wb') as f: f.write(raw)
        except Exception:
            flash('Extracted data is not a valid embedded image.', 'danger'); return redirect(request.url)

        return render_template('extract_image_image.html', download=url_for('download_file', filename=out_filename))
    return render_template('extract_image_image.html')

#  Text -> Audio 
@app.route('/text-audio/embed', methods=['GET', 'POST'])
def embed_text_audio():
    if request.method == 'POST':
        file = request.files.get('audio')
        message = request.form.get('message', '').strip()
        use_encrypt = request.form.get('encrypt') == 'on'
        password = request.form.get('password', '')

        if not file or file.filename == '':
            flash('Please select a WAV file.', 'danger'); return redirect(request.url)
        if not message:
            flash('Please enter a message.', 'danger'); return redirect(request.url)
        if not file.filename.lower().endswith('.wav'):
            flash('Only WAV files are supported.', 'danger'); return redirect(request.url)

        filename = secure_filename(file.filename)
        in_path = os.path.join(app.config['UPLOAD_FOLDER'], "ta_in_" + filename)
        file.save(in_path)

        if use_encrypt:
            if not password:
                flash('Password required for encryption.', 'danger'); return redirect(request.url)
            message = encrypt_message(message, password)

        out_filename = f"hidenseek_audio_{filename.rsplit('.',1)[0]}.wav"
        out_path = os.path.join(app.config['UPLOAD_FOLDER'], out_filename)
        try: embed_text_in_wav(in_path, out_path, message)
        except Exception as e:
            flash(f"Embedding failed: {e}", 'danger'); return redirect(request.url)

        flash('Message embedded into audio!', 'success')
        return render_template('embed_text_audio.html', download=url_for('download_file', filename=out_filename))
    return render_template('embed_text_audio.html')

@app.route('/text-audio/extract', methods=['GET', 'POST'])
def extract_text_audio():
    if request.method == 'POST':
        file = request.files.get('audio')
        use_encrypt = request.form.get('encrypt') == 'on'
        password = request.form.get('password', '')

        if not file or file.filename == '':
            flash('Please select a WAV file.', 'danger'); return redirect(request.url)

        filename = secure_filename(file.filename)
        in_path = os.path.join(app.config['UPLOAD_FOLDER'], "ta_ex_" + filename)
        file.save(in_path)

        try: hidden = extract_text_from_wav(in_path)
        except Exception as e:
            flash(f"Extraction failed: {e}", 'danger'); return redirect(request.url)

        if use_encrypt:
            if not password:
                flash('Password required for decryption.', 'danger'); return redirect(request.url)
            try: hidden = decrypt_message(hidden, password)
            except Exception:
                flash('Decryption failed: wrong password or corrupted data.', 'danger'); return redirect(request.url)

        return render_template('extract_text_audio.html', extracted=hidden)
    return render_template('extract_text_audio.html')

#  Text -> Video 
@app.route('/text-video/embed', methods=['GET', 'POST'])
def embed_text_video():
    if request.method == 'POST':
        file = request.files.get('video')
        message = request.form.get('message', '').strip()
        use_encrypt = request.form.get('encrypt') == 'on'
        password = request.form.get('password', '')

        if not file or file.filename == '':
            flash('Please select a video file.', 'danger'); return redirect(request.url)
        if not message:
            flash('Please enter a message.', 'danger'); return redirect(request.url)

        filename = secure_filename(file.filename)
        in_path = os.path.join(app.config['UPLOAD_FOLDER'], "tv_in_" + filename)
        file.save(in_path)

        if use_encrypt:
            if not password:
                flash('Password required for encryption.', 'danger'); return redirect(request.url)
            message = encrypt_message(message, password)

        out_filename = f"hidenseek_video_{filename.rsplit('.',1)[0]}.avi"
        out_path = os.path.join(app.config['UPLOAD_FOLDER'], out_filename)
        try: embed_text_in_video(in_path, out_path, message)
        except Exception as e:
            flash(f"Embedding failed: {e}", 'danger'); return redirect(request.url)

        flash('Message embedded into video!', 'success')
        return render_template('embed_text_video.html', download=url_for('download_file', filename=out_filename))
    return render_template('embed_text_video.html')

@app.route('/text-video/extract', methods=['GET', 'POST'])
def extract_text_video():
    if request.method == 'POST':
        file = request.files.get('video')
        use_encrypt = request.form.get('encrypt') == 'on'
        password = request.form.get('password', '')

        if not file or file.filename == '':
            flash('Please select a video file.', 'danger'); return redirect(request.url)

        filename = secure_filename(file.filename)
        in_path = os.path.join(app.config['UPLOAD_FOLDER'], "tv_ex_" + filename)
        file.save(in_path)

        try: hidden = extract_text_from_video(in_path)
        except Exception as e:
            flash(f"Extraction failed: {e}", 'danger'); return redirect(request.url)

        if use_encrypt:
            if not password:
                flash('Password required for decryption.', 'danger'); return redirect(request.url)
            try: hidden = decrypt_message(hidden, password)
            except Exception:
                flash('Decryption failed: wrong password or corrupted data.', 'danger'); return redirect(request.url)

        return render_template('extract_text_video.html', extracted=hidden)
    return render_template('extract_text_video.html')

# --File Download
@app.route('/download/<path:filename>')
def download_file(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(path):
        flash('File not found.', 'danger'); return redirect(url_for('home'))
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
