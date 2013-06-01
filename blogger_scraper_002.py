import urllib
import contextlib
import sys
import re
import os

def main(current_page_link, file_to_write):
	while True:
		if current_page_link is not None:
		
			# open web page
			
			print "#### New Page ####"
			print "Now downloading: %s" % current_page_link
			with contextlib.closing(urllib.urlopen(current_page_link)) as f:
				current_page_data = f.read()
		
			# parse web page
		
			next_page_link = re.search(r"(<a class='blog-pager-newer-link' href=')(.*?)(' id='Blog1_blog-pager-newer-link' title='Newer Post'>)", current_page_data)
			if next_page_link is not None:
				next_page_link = next_page_link.group(2)
			current_title = re.search(r"(<h3 class='post-title entry-title' itemprop='name'>\n)(.*?)(\n</h3>)", current_page_data, re.DOTALL).group(2)
			current_body = re.search(r"(itemprop='description articleBody'>\n)(.*?)(<div style='clear: both;'></div>\n</div>\n<div class='post-footer'>)", current_page_data, re.DOTALL).group(2)
		
			# download images and re-link to local files
		
			images = re.findall(r'''(src=[",'])(.*?)([",'])''', current_body, re.DOTALL)
			if images is not []:
				if not os.path.exists(os.path.join(os.getcwd(), "images")):
					os.makedirs(os.path.join(os.getcwd(), "images"))
				for image in images:
					image_remote_location = image[1]
					image_name = re.split(r"/", image_remote_location)[-1]
					image_local_location = "%(local_path)s/images/%(image_name)s" % {"local_path" : os.getcwd(), "image_name" : image_name}
					current_body = re.sub(image_remote_location, "file://" + image_local_location, current_body)
				
					print "        --Now downloading: %s" % image_remote_location
					urllib.urlretrieve(image_remote_location, image_local_location)
		
			# append to file
		
			with open(file_to_write, "a") as f:
				f.write('<div class="title"><h3>%(title)s</h3></div>\n<br>\n<div class="body">%(body)s</div>\n<br>\n' % {"title" : current_title, "body" : current_body})		
		
			# get ready for next loop
		
			current_page_link = next_page_link
			
		else:
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