from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.urls import reverse

from .models import PicUpload
from .forms import ImageForm

# Create your views here.
def index(request):
    return render(request, 'index.html')


def list(request):
    image_path = ''
    image_path1=''
    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES)

        if form.is_valid():
            newdoc = PicUpload(imagefile=request.FILES['imagefile'])
            newdoc.save()

            return HttpResponseRedirect(reverse('list'))

    else:
        form = ImageForm()

    documents = PicUpload.objects.all()
    for document in documents:
        image_path = document.imagefile.name
        image_path1 = '/' + image_path

        document.delete()

    request.session['image_path'] = image_path

    return render(request, 'list.html',
    {'documents':documents, 'image_path1': image_path1, 'form':form}
    )


#------------------------ Whats_going_on_in_the_Picture ------------------------

# --------------------------- Import essentials --------------------------------
from numpy import argmax
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import Model, load_model
import os, json
from pickle import load

# --------------Extract features from each image in the directory--------------
def extract_features(filename):
	# load the model
	model = MobileNetV2()
	# re-structure the model
	model.layers.pop()
	model = Model(inputs=model.inputs, outputs=model.layers[-2].output)
	# load the image
	image = load_img(filename, target_size=(224, 224))
	# convert the image pixels to a numpy array
	image = img_to_array(image)
	# reshape data for the model
	image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
	# prepare the image for the VGG model
	image = preprocess_input(image)
	# get features
	feature = model.predict(image, verbose=0)
	return feature

# ----------------------- Map an integer to a word -----------------------------
def word_for_id(integer, tokenizer):
	for word, index in tokenizer.word_index.items():
		if index == integer:
			return word
	return None

# ---------------------- Generate a description for an image -------------------
def generate_desc(model, tokenizer, feature, max_length):
	# seed the generation process
	in_text = 'startseq'
	# iterate over the whole length of the sequence
	for i in range(max_length):
		# integer encode input sequence
		sequence = tokenizer.texts_to_sequences([in_text])[0]
		# pad input
		sequence = pad_sequences([sequence], maxlen=max_length)
		# predict next word
		yhat = model.predict([feature,sequence], verbose=0)
		# convert probability to integer
		yhat = argmax(yhat)
		# map integer to word
		word = word_for_id(yhat, tokenizer)
		# stop if we cannot map the word
		if word is None:
			break
		# append as input for generating the next word
		in_text += ' ' + word
		# stop if we predict the end of the sequence
		if word == 'endseq':
			break
	return in_text

# ------------------------------- Prediction -----------------------------------

def prediction(request):

    image = request.session['image_path']
    img_path = image
    request.session.pop('image_path', None)
    request.session.modified = True

    # pre-define the max sequence length (from training)
    max_length = 34

    # Generate Caption
    feature = extract_features(img_path)
    tokenizer = load(open('model/tokenizer.pkl', 'rb'))
    model = load_model('model/model.h5')
    description = generate_desc(model, tokenizer, feature, max_length)
    caption = description[8:-6]
    context = {'caption' : caption}

    src= 'images/'
    for image_file_name in os.listdir(src):
        if image_file_name.endswith(".jpg") :
            os.remove(src + image_file_name)

    results = json.dumps(context)
    return HttpResponse(results, content_type='application/json')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ENGINE ENDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#******************************************************************************
