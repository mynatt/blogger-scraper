import urllib
import contextlib
import sys
import re
import os
from HTMLParser import HTMLParser

class TitleParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		for attr in attrs:
			if attr == ('class', 'blog-pager-newer-link'):
				self.is_title = True
	def handle_data(self, data):
		print "Data     :", data
titl = MyHTMLParser()




def main(current_page_link, file_to_write):
	while True:
		if current_page_link is not None:
		
			# open web page
			
			print "#### New Page ####"
			print "Now downloading: %s" % current_page_link
			with contextlib.closing(urllib.urlopen(current_page_link)) as f:
				current_page_data = f.read()
		
			##### parse web page
			
			# find link to next page
			try:
				next_page_link = re.search(r"(class='blog-pager-newer-link'.*?href=')(.*?(?=')))", current_page_data)
				next_page_link = next_page_link.group(2)
			except:
				print "Exception on trying to find next page link."
				next_page_link = None
			
			# find title
			try:
				current_title = re.search(r"(<h3.*?class='post-title entry-title'.*?>\n?)(.*?)(\n</h3>)", current_page_data, re.DOTALL).group(2)
			except:
				print "Exception on trying to find current title."
				current_title = ""
			try:
				title_link = re.search(r'''(<a.*?>)(.*?)(</a>)''', current_title, re.DOTALL).group(2)
				current_title = title_link
				print "Title contained a link, converting to plain text."
			except:
				pass
			
			# find body				
			try:
				current_body = re.search(r"(class='post-body entry-content'.*?>\n)(.*?)(<div style='clear: both;'></div>\n</div>)", current_page_data, re.DOTALL).group(2)
			except:
				print "Exception finding the body text."
				current_body = ""
			
			# manage folders to put images in
			
			short_title = current_title[:40]
			image_local_folder = os.path.join(os.getcwd(), "images", short_title)
			
			# download images and re-link to local files (embedded and thumbnails)
			try:
				images = re.findall(r'''(src=[",'])(.*?)([",'])''', current_body, re.DOTALL)
			except:
				images = []
			
			if images != []:
				if not os.path.exists(image_local_folder):
					os.makedirs(image_local_folder)
				for image in images:
					image_remote_location = image[1]
					image_name = re.split(r"/", image_remote_location)[-1]
					image_local_location = os.path.join(image_local_folder, "thumbnail-" + image_name)
					current_body = re.sub(image_remote_location, "file://" + image_local_location, current_body)
				
					print "        --Now downloading thumbnail: %s" % image_remote_location
					urllib.urlretrieve(image_remote_location, image_local_location)
			
			# download full-size images and re-link to local files
			try:
				images = re.findall(r'''(<a href=[",'])(http://.*?[jpg,png,gif,bmp,JPG,GIF,PNG,BMP](?=[",']))(>.*?</a>)''', current_body, re.DOTALL)
				print images
			except:
				images = []
			
			if images != []:
				if not os.path.exists(image_local_folder):
					os.makedirs(image_local_folder)
				for image in images:
					print "image"
					print image
					image_remote_location = image[1]
					image_name = re.split(r"/", image_remote_location)[-1]
					print "image_name"
					print image_name
					image_local_location = os.path.join(image_local_folder, "full-size-" + image_name)
					print "image local location"
					print image_local_location
					current_body = re.sub(image_remote_location, "file://" + image_local_location, current_body)
					
					# open page that contains the real link
					with contextlib.closing(urllib.urlopen(image_remote_location)) as f:
						image_remote_page_data = f.read() 
					
					# find the real image link
					images = re.findall(r'''(src=[",'])(.*?)([",'])''', image_remote_page_data, re.DOTALL)
					for image in images:
						image_remote_location = image[1]
					
					print "        --Now downloading full-size image: %s" % image_remote_location	
					urllib.urlretrieve(image_remote_location, image_local_location)
			
			
			# append title and body to file
			
			with open(file_to_write, "a") as f:
				f.write('<div class="title"><h3>%(title)s</h3></div>\n<br>\n<div class="body">%(body)s</div>\n<br>\n' % {"title" : current_title, "body" : current_body})		
		
			# get ready for next loop
		
			current_page_link = next_page_link
			
		else:
			print current_page_link
			break
			
			
if __name__ == "__main__":

	# get commandline args

	current_page_link = sys.argv[1]
	file_to_write = sys.argv[2]

	# ensure file is there

	with open(file_to_write, "w") as f:
		f.write("")

	page_aggregator = []
	main(current_page_link, file_to_write)