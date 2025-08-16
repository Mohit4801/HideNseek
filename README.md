
# HideNseek - Multimedia Steganography Web Application

HideNseek is a web-based multimedia steganography application built with Flask. It allows users to embed and extract messages within various types of media, including images, audio, and video. The application supports both plain text and encrypted messages, ensuring a secure and flexible approach to hiding information.

## Features

- **Text in Image**: Embed and extract hidden text within images. Supports optional encryption for added security.
- **Image in Image**: Embed one image within another. The secret image is resized if needed to fit within the cover image.
- **Text in Audio (WAV)**: Embed and extract hidden text in WAV audio files.
- **Text in Video**: Embed and extract hidden text within video files (AVI format).
- **Encryption/Decryption**: Optionally encrypt or decrypt the hidden messages using a password for additional security.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Hidenseek.git
   cd Hidenseek
   ```

2. **Install dependencies**:
   Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

   Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the app**:
   - Ensure you have Python 3.x installed.
   - Install any necessary dependencies (such as `Flask`, `Pillow`, `werkzeug`, etc.) by running:
   ```bash
   pip install flask pillow werkzeug
   ```

4. **Run the app**:
   Start the Flask development server:
   ```bash
   python app.py
   ```

   The application should now be accessible at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).


### 5. File Download
Once a message has been successfully embedded or extracted, the file will be available for download.

## File Formats Supported

- **Images**: PNG, JPG, JPEG, BMP
- **Audio**: WAV (for text embedding)
- **Video**: AVI (for text embedding)

## Contributing

Feel free to fork the repository, make changes, and submit pull requests. Any improvements or bug fixes are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- **Flask** for the web framework.
- **Pillow** for image processing.
- **Werkzeug** for file handling and security utilities.
- **PyCryptodome** for encryption functionality (if used).
