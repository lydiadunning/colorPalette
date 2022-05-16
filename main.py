import os

import pandas as pd
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename


class ImageColors:
    def __init__(self, filename):
        self.color_limit = 100
        self.filename = f"{UPLOAD_FOLDER}/{filename}"
        self.image = Image.open(self.filename)
        self.image = self.simplify_image()
        self.rgb_colors = self.find_top_ten_colors()
        self.hex_colors = self.rgb2hex()
        self.count = len(self.rgb_colors)

    def simplify_image(self):
        return self.image.quantize(self.color_limit).convert("RGB")

    def rgb2hex(self):
        return ["#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2]) for rgb in self.rgb_colors]

    def find_top_ten_colors(self):
        all_colors = self.image.getcolors()
        df = pd.DataFrame(all_colors, columns=["count", "pixel"])
        top_ten = df.sort_values(by="count", ascending=False).head(10)
        return top_ten["pixel"].to_list()

    def reset(self):
        self.image = None
        self.color_limit = None
        self.rgb_colors = []
        self.hex_colors = []


UPLOAD_FOLDER = 'static/image-uploads'
ALLOWED_EXTENSIONS = {'PNG', 'JPG', 'JPEG', 'GIF'}

# web functionality
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000


# This comes directly from Flask's documentation on file uploads.
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].upper() in ALLOWED_EXTENSIONS

# fix error handling
# This comes directly from Flask's documentation on file uploads.
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('display', name=filename))
    return '''
            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File</h1>
            <form method=post enctype=multipart/form-data>
              <input type=file name=file accept=".png,.jpg,.jpeg,.gif">
              <input type=submit value=Upload>
            </form>
            '''


@app.route("/palette/<name>")
def display(name):
    image_colors = ImageColors(name)
    return render_template("display.html", image=image_colors.filename,
                           hex_colors=image_colors.hex_colors,
                           rgb_colors=image_colors.rgb_colors,
                           color_count=image_colors.count)


if __name__ == '__main__':
    app.run(debug=True)
