import os
import time
import pickle

# Constants
SEC = 1
FILE_WAIT = 5*SEC
MAX_TRIES = 3


# Current working directory
cwd = os.getcwd()
file_directory = os.path.join(cwd, 'output')

LOGIN_URL = 'https://blu94anjel.diaryland.com/'

files = {
	"logFile": os.path.join(file_directory, 'diary.txt'),
	"logFile_reverse": os.path.join(file_directory, 'diary_reverse.txt'),
	"logFile_pickle_text": os.path.join(file_directory, 'pickle_diary_text.pkl'),
	"logFile_pickle_text_reverse": os.path.join(file_directory, 'pickle_diary_text_reverse.pkl'),
	"logFile_pickle_font": os.path.join(file_directory, 'pickle_diary_font.pkl'),
	"logFile_pickle_font_reverse": os.path.join(file_directory, 'pickle_diary_font_reverse.pkl')
}


def clear_files():

	if not os.path.isdir(file_directory):
		os.mkdir(file_directory)

	for f in files.values():
		open(f, "w").write("")

	return True


def text_format(obj, count):
	digits = digits_integer(count)
	num_hashes = digits + 8
	header = num_hashes * '#' + '\n### ' + str(count) + ' ###\n' + num_hashes * '#' + 2 * '\n'
	title = '- ' + obj.title + '\n'
	date = '- ' + obj.date + '\n'
	content = '-\n' + obj.content
	footer = 3 * '\n'

	return header + title + date + content + footer


def add_to_file(filename, obj, count, reverse=False):

	entry = text_format(obj, count)

	count = 0

	while True:
		count += 1
		try:
			if reverse is False:
				with open(filename, "a") as f:
					f.write(entry)
			else:
				with open(filename, 'r+') as f:
					content = f.read()
					f.seek(0, 0)
					f.write(entry + content)
			break
		except:
			print("Opening file failed: " + filename + " - count: " + str(count) + " - trying again...")
			if count < MAX_TRIES:
				time.sleep(FILE_WAIT)
				pass
			else:
				print("Failed too many times, aborting...")
				return False

	return True


def add_to_file_pickle(filename, object_list):
	with open(filename, 'ab') as output:
		for diary_entry in object_list:
			pickle.dump(diary_entry, output, pickle.HIGHEST_PROTOCOL)

	return True


def read_from_file_pickle(filename):
	with open(filename, 'rb') as input:
		try:
			while True:
				diary_entry = pickle.load(input)
				print("-----")
				print("Title:   " + diary_entry.title)
				print("Date:    " + diary_entry.date)
				print("Content: " + diary_entry.content)
		except EOFError:
			pass

	return True


def digits_integer(val):
	return len(str(val))


