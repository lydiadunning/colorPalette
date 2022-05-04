import pandas as pd
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, flash
import os

from werkzeug.utils import secure_filename


class ImageColors:
    def __init__(self):
        self.filename = None
        self.image = None
        self.unique_colors = 100
        self.rgb_colors = []
        self.hex_colors = []
        self.count = 0
    def colors_from_image(self, filename):
        self.filename = f"{UPLOAD_FOLDER}/{filename}"
        self.image = Image.open(self.filename)
        self.simplify_image()
        self.find_top_ten_colors()
        self.rgb2hex()
        self.count = len(self.rgb_colors)
    def simplify_image(self):
        im_simplified = self.image.quantize(100)
        self.image = im_simplified.convert("RGB")
    def rgb2hex(self):
        self.hex_colors = []
        for rgb in self.rgb_colors:
            self.hex_colors.append("#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2]))
    def find_top_ten_colors(self):
        all_colors = self.image.getcolors(maxcolors=self.unique_colors)
        df = pd.DataFrame(all_colors, columns=["count", "pixel"])
        top_ten = df.sort_values(by="count", ascending=False).head(10)
        self.rgb_colors = top_ten["pixel"].to_list()
    def reset(self):
        self.image = None
        self.unique_colors = None
        self.rgb_colors = []
        self.hex_colors = []


image_colors = ImageColors()

UPLOAD_FOLDER = 'static/image-uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# web functionality
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    print("it's happening")
    if request.method == 'POST':
        print("it's really happening")
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
              <input type=file name=file>
              <input type=submit value=Upload>
            </form>
            '''

@app.route("/palette/<name>")
def display(name):
    image_colors.colors_from_image(name)
    return render_template("display.html", image=image_colors.filename,
                           hex_colors=image_colors.hex_colors,
                           rgb_colors=image_colors.rgb_colors,
                           color_count=image_colors.count)


if __name__ == '__main__':
    app.run(debug=True)