import os
from pickle import load
from flask import Flask, request, render_template
from predict import *

# pre-define the max sequence length (from training)
max_length = 34

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def predict():
	if request.method == 'GET':
		return render_template('index.html', value='Home')
	if request.method == 'POST':
		print(request.files)
		if 'file' not in request.files:
			print('Image not uploaded')
			return
		image = request.files['file']
		image.filename = 'upload.jpg'
		image.save(os.path.join('static',image.filename))
		feature = extract_features('./static/upload.jpg')
		# load model and tokenizer
		tokenizer = load(open('./model/tokenizer.pkl', 'rb'))
		model = load_model('./model/model.h5')
		description = generate_desc(model, tokenizer, feature, max_length)
		return render_template('result.html', description=description[8:-6])

if __name__ == '__main__':
	app.run(debug=True, port=8000)
