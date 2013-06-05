import urllib
import contextlib
import sys
import re
import os
import codecs
import cgi
from bs4 import BeautifulSoup

def select_tags_by_class(css_class, error_message,
							soup,
							new_soup,
							strip_attributes=True,
							text_only=False,
							new_tag_name='', 
							return_none_on_fail=False):
	try:
		selected_tag = soup.select("." + css_class)[0]
		if strip_attributes == True:
			selected_tag.attrs = {u'class': css_class}
		if new_tag_name != '':
			selected_tag.name = unicode(new_tag_name)
		if text_only == True:
			selected_tag.string = selected_tag.get_text(strip=True)
	except:
		print error_message
		if return_none_on_fail == False:
			selected_tag = new_soup.new_tag("div")
			selected_tag['class'] = css_class
			selected_tag.string = cgi.escape(error_message).encode('ascii', 'xmlcharrefreplace')
		else:
			return None
	
	return selected_tag


def main(current_page_link, file_to_write):
	while True:
		if current_page_link != None:
		
			# open web page
			
			print "#### New Page ####"
			print "Now downloading: %s" % current_page_link
			with contextlib.closing(urllib.urlopen(current_page_link)) as f:
				current_page_data = f.read()
			
			soup = BeautifulSoup(current_page_data, "html.parser")
			new_soup = BeautifulSoup()
			
			current_date_tags = select_tags_by_class('date-header',
												     'Date not found', 
												     soup, 
													 new_soup, 
												     new_tag_name=u'h3')
			current_title_tags = select_tags_by_class('post-title',
													  'Title not found',
													  soup, 
													  new_soup,
													  text_only=True,
													  new_tag_name=u'h1')
			current_body_tags = select_tags_by_class('post-body',
			                                         'Body not found',
													 soup,
													 new_soup,
													 new_tag_name=u'div')
			
			next_page_tags = select_tags_by_class('blog-pager-newer-link', 
												  'Newer page not found',
												  soup,
												  new_soup,
												  strip_attributes=False,
												  return_none_on_fail=True)
			
			
			if next_page_tags != None:
				next_page_link = next_page_tags['href']
			else:
				next_page_link = None
			
			current_title = current_title_tags.get_text(strip=True)
			
			# manage folders to put images in
			
			if current_title != "":
				short_title = current_title[:40]
			else:
				short_title = "untitled_posts"
			
			date_for_filename = "".join([x if x.isalnum() else "_" for x in current_date_tags.get_text(strip=True)]) 
			image_local_folder = os.path.join(os.getcwd(), "images", date_for_filename)
			
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
				full_images = current_body_tags("a", href=re.compile(r"(jpe?g|png|gif|bmp|JPE?G|GIF|PNG|BMP)$"))
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
					
					opener = urllib.urlopen(image_remote_location)
					if opener.headers.maintype == 'image':
						urllib.urlretrieve(image_remote_location, image_local_location)
					else:
						with contextlib.closing(urllib.urlopen(image_remote_location)) as f:
							full_size_image_page = f.read()
						full_size_image_soup = BeautifulSoup(full_size_image_page, "html.parser")
						
						try:
							images = full_size_image_soup("img")
							# images = re.findall(r'''(src=[",'])(.*?)([",'])''', current_body, re.DOTALL)
						except:
							print "Couldn't find images."
							images = []

						if images != []:
							if not os.path.exists(image_local_folder):
								os.makedirs(image_local_folder)
						for image in images:
							image_remote_location = image["src"]
							urllib.urlretrieve(image_remote_location, image_local_location)
						
#					urllib.urlretrieve(image_remote_location, image_local_location)
			
			new_soup.append(current_title_tags)
			
			new_soup.append(current_date_tags)
			
			new_soup.append(current_body_tags)
			
			current_formatted_post = new_soup.prettify(formatter="html")
			
			# append title and body to file
			
			with codecs.open(file_to_write, "a", encoding='utf-8') as f:
				#f.write('<div class="title"><h3>%(title)s</h3></div>\n<br>\n<div class="body">%(body)s</div>\n<br>\n' % {"title" : current_title, "body" : current_body})		
				f.write(current_formatted_post)
			# get ready for next loop
		
			current_page_link = next_page_link
			
		else:
			break
			
			
if __name__ == "__main__":
	
	try:
		# get commandline args

		current_page_link = sys.argv[1]
		file_to_write = sys.argv[2]

		# ensure file is there

		#with open(file_to_write, "w") as f:
			#f.write("")

		main(current_page_link, file_to_write)
	except KeyboardInterrupt:
		pass
		