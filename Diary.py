class Diary_Entry:
	def __init__(self, title, date, content):
		self.title = title
		self.date = date
		self.content = content


def add_to_diary(text):
	# Split text into 3 parts
	split_text = text.split('\n', 2)

	title = remove_non_ascii(split_text[0]).strip()
	date = split_text[1].strip()
	content = remove_non_ascii(split_text[2]).replace('stay a while', '') .strip()

	diary_object = Diary_Entry(title, date, content)

	return diary_object


def add_to_diary_font(text):
	split_text = text.split('\n')

	title = remove_non_ascii(split_text[1]).strip()[:-5]
	date = split_text[2].strip()[:-5]
	content = remove_non_ascii(split_text[4]).strip()[:-5]

	diary_object = Diary_Entry(title, date, content)

	return diary_object


def remove_non_ascii(s): return "".join(i for i in s if ord(i) < 128)

