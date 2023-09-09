import os
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login,logout
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
from django.contrib.staticfiles import finders
from django.contrib.auth.decorators import login_required
import speech_recognition as sr
from moviepy.editor import VideoFileClip, concatenate_videoclips
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from pydub import AudioSegment
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio
import whisper

# download from git command: pip install git+https://github.com/openai/whisper.git
# with general pip install have paid dependencies
from moviepy.editor import VideoFileClip, clips_array


# from django.http import JsonResponse


# Import everything needed to edit video clips
# from moviepy.editor import *

# from django.contrib.auth.decorators import login_required
# nltk.download()

def home_view(request):
	return render(request,'home.html')


def about_view(request):
	return render(request,'about.html')


def contact_view(request):
	return render(request,'contact.html')

# def play_audio(request):
def play_audio(request):
	# ... handle file upload and save it to the media directory ...
	# '/Users/bheema.ujwala/work/gesture_bot/media/my_voice.wav'
	audio_path = '/temp/my_voice.wav'  # Replace with the actual path
	# media/media/my_voice.wav
	# temp/temp/Avengers Motivational ! English Dialogue.mp3
	return render(request,'play_audio.html', {'audio_path': '/temp/my_voice.wav'})
	# return render(request, 'play_audio.html', {'audio_path': audio_path})


# @login_required(login_url="login")
def animation_view(request):
	text = ''
	file_path = ''
	cleaned_extension = None
	
	if request.method == 'POST' and request.POST.get('sen'):
		text = request.POST.get('sen')
		temp_file_path = None

	if request.POST.get('file_type') == 'audio' and request.method == 'POST' and request.FILES and request.FILES['audio_file']:
		wav_file = request.FILES['audio_file']
		myFile = request.FILES.get('myFile')

		file_name = os.path.splitext(wav_file.name)[0]
		file_ext = os.path.splitext(wav_file.name)[1].lower()
		temp_file_path = os.path.join(wav_file.name)
		

		stored_path = default_storage.save(temp_file_path, wav_file)
		print('stored_pathstored_pathstored_pathstored_path::', stored_path)
		print('temp_file_pathtemp_file_pathtemp_file_pathtemp_file_path::', temp_file_path)
		# full_path = os.path.abspath(stored_path)
		file_path = 'temp/'+stored_path
		print('file_pathfile_pathfile_path::', file_path)
		cleaned_extension = file_ext.lstrip('.')
		if file_ext in ['.m4a', '.mp3']:
			audio = AudioSegment.from_file(file_path, format=cleaned_extension)
			audio.export(file_path, format='wav')

		text = audio_file_to_text(file_path)

	if request.method == 'POST' and request.POST.get('file_type') == 'video' and request.FILES['video_file']:
		video_file = request.FILES['video_file']
		video_temp_file_path = os.path.join('media', video_file.name)
		audio_file = 'media/video_converted_temp_audio.wav'
		print ('request.FILES:: video_filevideo_file ', video_file)
		# myFile = request.FILES.get('myFile')
		ffmpeg_extract_audio(video_temp_file_path, audio_file)
		print ('ffmpeg_extract_audioffmpeg_extract_audio audio_file: ', audio_file)
		text = audio_file_to_text(audio_file)

	print("Recognized text:", text)
	if text:
		#tokenizing the sentence
		text.lower()
		words = word_tokenize(text)

		tagged = nltk.pos_tag(words)
		tense = {}
		tense["future"] = len([word for word in tagged if word[1] == "MD"])
		tense["present"] = len([word for word in tagged if word[1] in ["VBP", "VBZ","VBG"]])
		tense["past"] = len([word for word in tagged if word[1] in ["VBD", "VBN"]])
		tense["present_continuous"] = len([word for word in tagged if word[1] in ["VBG"]])

		#stopwords that will be removed
		stop_words = set(["mightn't", 're', 'wasn', 'wouldn', 'be', 'has', 'that', 'does', 'shouldn', 'do', "you've",'off', 'for', "didn't", 'm', 'ain', 'haven', "weren't", 'are', "she's", "wasn't", 'its', "haven't", "wouldn't", 'don', 'weren', 's', "you'd", "don't", 'doesn', "hadn't", 'is', 'was', "that'll", "should've", 'a', 'then', 'the', 'mustn', 'i', 'nor', 'as', "it's", "needn't", 'd', 'am', 'have',  'hasn', 'o', "aren't", "you'll", "couldn't", "you're", "mustn't", 'didn', "doesn't", 'll', 'an', 'hadn', 'whom', 'y', "hasn't", 'itself', 'couldn', 'needn', "shan't", 'isn', 'been', 'such', 'shan', "shouldn't", 'aren', 'being', 'were', 'did', 'ma', 't', 'having', 'mightn', 've', "isn't", "won't"])

		#removing stopwords and applying lemmatizing nlp process to words
		lr = WordNetLemmatizer()
		filtered_text = []
		for w,p in zip(words,tagged):
			if w not in stop_words:
				if p[1]=='VBG' or p[1]=='VBD' or p[1]=='VBZ' or p[1]=='VBN' or p[1]=='NN':
					filtered_text.append(lr.lemmatize(w,pos='v'))
				elif p[1]=='JJ' or p[1]=='JJR' or p[1]=='JJS'or p[1]=='RBR' or p[1]=='RBS':
					filtered_text.append(lr.lemmatize(w,pos='a'))

				else:
					filtered_text.append(lr.lemmatize(w))


		#adding the specific word to specify tense
		words = filtered_text
		temp=[]
		for w in words:
			if w=='I':
				temp.append('Me')
			else:
				temp.append(w)
		words = temp
		probable_tense = max(tense,key=tense.get)

		if probable_tense == "past" and tense["past"]>=1:
			temp = ["Before"]
			temp = temp + words
			words = temp
		elif probable_tense == "future" and tense["future"]>=1:
			if "Will" not in words:
					temp = ["Will"]
					temp = temp + words
					words = temp
			else:
				pass
		elif probable_tense == "present":
			if tense["present_continuous"]>=1:
				temp = ["Now"]
				temp = temp + words
				words = temp


		filtered_text = []
		mp4_paths = []
		print("Process wordswordswords: %s" % words)
		for w in words:
			
			path = w + ".mp4"
			f = finders.find(path)
			print("Process word: %s" % w)
			print('found path: %s' % f)
			#splitting the word if its animation is not present in database
			if not f:
				for c in w:
					filtered_text.append(c)
					single_letter_path = c + ".mp4"
					letter = finders.find(single_letter_path)
					print("Process letter : %s" % c)
					print('letter found path: %s' % letter)
					mp4_paths.append(letter)
			else:
				filtered_text.append(w)
				word_path = finders.find(path)
				print("word Process word: %s" % w)
				print('word found path: %s' % word_path)
				mp4_paths.append(word_path)

		words = filtered_text;

		video_clips = []
		print(f"mp4_pathsmp4_pathsmp4_pathsFile not found: {mp4_paths}")
		for file in mp4_paths:
			if file and os.path.exists(file):
					video_clips.append(VideoFileClip(file))
			else:
					print(f"File not found: {file}")

		print('video_clipsvideo_clipsvideo_clips::', video_clips)
		final = concatenate_videoclips(video_clips)

		# Set the output file name and duration
		output_file = "temp/merged_video.mp4"
		stored_video = final.write_videofile(output_file, codec="libx264")

		print('stored_videostored_videostored_video:: ', stored_video)
		return render(request,'animation.html', {'words':words,'text':text, 'temp_file_path': file_path })
	else:
		return render(request,'animation.html')


def audio_file_to_text(audio_file):
	# Initialize the recognizer
	model = whisper.load_model("base")

	print("audio_file_to_textaudio_file_to_text:: ", audio_file)

	try:
			result = model.transcribe(audio_file)
			print('recognized text:', result['text'])
			# Input string with special characters
			# input_string = "Hello, World! This is a test string with $pecial characters."

			# Create an empty string to store the result
			output_string = ""

			# Iterate through each character in the input string
			for char in result['text']:
					# Check if the character is a letter, digit, or whitespace
					if char.isalnum() or char.isspace():
							# If yes, add it to the output string
							output_string += char

			print(output_string)

			return output_string
	except sr.UnknownValueError:
			print("Speech recognition could not understand audio")
	except sr.RequestError as e:
			print("Could not request results from Google Speech Recognition service; {0}".format(e))

