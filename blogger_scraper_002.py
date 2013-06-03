import urllib
import contextlib
import sys
import re
import os
import lxml
import codecs
from bs4 import BeautifulSoup





def main(current_page_link, file_to_write):
	while True:
		if current_page_link != None:
		
			# open web page
			
			print "#### New Page ####"
			print "Now downloading: %s" % current_page_link
			with contextlib.closing(urllib.urlopen(current_page_link)) as f:
				current_page_data = f.read()
			
			soup = BeautifulSoup(current_page_data, "html.parser")
			
			try:
				current_date_tags = soup.select(".date_header")
			except:
				print "Couldn't find date."
				current_date = 
			
			try:
				current_title_tags = soup.select(".post-title")[0]
				current_title = current_title_tags.get_text(strip=True)
			except:
				print "Couldn't find title."
				current_title = ""
			
			try:
				current_body_tags = soup.select(".post-body")[0]
			except:
				print "Couldn't find post body."
				current_body = ""
			
			try:
				next_page_link = soup.select(".blog-pager-newer-link")[0]['href']
			except:
				print "Couldn't find next page link."
				next_page_link = None
			
			# manage folders to put images in
			
			if current_title != "":
				short_title = current_title[:40]
			else:
				short_title = "untitled_posts"
			
			image_local_folder = os.path.join(os.getcwd(), "images", short_title)
			
			# download images and re-link to local files (embedded and thumbnails)
			try:
				images = current_body_tags("img")
				# images = re.findall(r'''(src=[",'])(.*?)([",'])''', current_body, re.DOTALL)
			except:
				print "Couldn't find images."
				images = []
			
			if images != []:
				if not os.path.exists(image_local_folder):
					os.makedirs(image_local_folder)
			for image in images:
				image_remote_location = image["src"]
				image_name = re.split(r"/", image_remote_location)[-1]
				image_local_location = os.path.join(image_local_folder, "thumbnail-" + image_name)
				image["src"] = u'file://' + image_local_location
				print "        --Now downloading thumbnail: %s" % image_remote_location
				urllib.urlretrieve(image_remote_location, image_local_location)
			
			# download full-size images and re-link to local files
			try:
				full_images = current_body_tags("a", href=re.compile(r"[jpg,png,gif,bmp,JPG,GIF,PNG,BMP]$"))
			except:
				full_images = []
			
			if full_images != []:
				if not os.path.exists(image_local_folder):
					os.makedirs(image_local_folder)
				for image in full_images:
					image_remote_location = image["href"]
					image_name = re.split(r"/", image_remote_location)[-1]
					image_local_location = os.path.join(image_local_folder, "full-size-" + image_name)
					image["href"] = image_local_location
					print "        --Now downloading full-size image: %s" % image_remote_location	
					urllib.urlretrieve(image_remote_location, image_local_location)
			
			#current_title = current_title_tags.prettify(formatter="html")
			current_body = current_body_tags.prettify(formatter="html")
			
			
			# append title and body to file
			
			with codecs.open(file_to_write, "a", encoding='utf-8') as f:
				f.write('<div class="title"><h3>%(title)s</h3></div>\n<br>\n<div class="body">%(body)s</div>\n<br>\n' % {"title" : current_title, "body" : current_body})		
		
			# get ready for next loop
		
			current_page_link = next_page_link
			
		else:
			print current_page_link
			break
			
			
if __name__ == "__main__":
	
	try:
		# get commandline args

		current_page_link = sys.argv[1]
		file_to_write = sys.argv[2]

		# ensure file is there

		with open(file_to_write, "w") as f:
			f.write("")

		page_aggregator = []
		main(current_page_link, file_to_write)
	except KeyboardInterrupt:
		pass
		