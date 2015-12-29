import requests
from bs4 import BeautifulSoup
import os
import string #for zfill
from PIL import ImageFont, Image, ImageDraw, ImageOps
import os
import sys
from image_utils import ImageText
 
 
#takes in the image source, and local filename then downloads the image to out/localname
def download(src, localname):
    image = get_page(src, 5)
    if not image:
        return False
 
    f = open('out/' + localname, 'wb')
    f.write(image)
    f.close()
 
    return True
 
def make_page(infile, outfile, text = "", text2 = ""): # takes the inputfilename, outputfilename and text to put it in at the bottom
 
    font = 'Aller_Rg.ttf' #some random font, just fine one that is legible enough
    color = (50, 50, 50) # color of the text box
    page = Image.open(infile) # opening original image
    width, original_height = page.size # size of original image
    temp = ImageText((1000, 500), background = (255, 255, 255, 200)) # making a large temp Image text object to put  the text in.
    height = temp.write_text_box((0, 0), text, box_width = width, font_filename = font, font_size = 16, color = color)[1] + 20 # +20 y offset writer leaves that much space at the top
    textbox = temp.image.crop((0, 0, width, height)) #crop textbox
     
    temp = ImageText((1000, 500), background = (255, 255, 255, 200)) # making a large temp Image text object to put  the text in.
    height2 = temp.write_text_box((0, 0), text2, box_width = width, font_filename = font, font_size = 16, color = color)[1] + 20# +20 y offset writer leaves that much space at the top
    textbox2 = temp.image.crop((0, 0, width, height)) #crop textbox
     
    output = Image.new("RGBA", (width, original_height + height + height2), (120, 20, 20)) # make new blank image with computed dimensions
    output.paste(textbox2, (0,0))
    output.paste(page, (0,height2)) # paste original
    output.paste(textbox, (0, original_height + height2)) # paste textbox
    output.save(outfile) # save file
 
 
#function to check if the requested page returns the correct page and did not time out.
def get_page(url, max_attempts):
    for i in xrange(max_attempts):
        print "attempt no.", i + 1
        r = requests.get(url)
         
        if r.status_code == 200:
            return r.content
 
    print r.status_code
    return False
 
def extract_archive(link):
    html = get_page(link, 5)
    if html:
        soup = BeautifulSoup(html)
        comic = soup.findAll('a')
        for i in comic:
            # get can obtain data with a var=data format            
            address = i.get('href')
             
            joiner = ""         
            new_addr = joiner.join(('http://oglaf.com/',address[1:]))
            print new_addr
 
            html_inner =  get_page(new_addr, 5)
 
 
            if html_inner:
                soup_inner = BeautifulSoup(html_inner)
                comic = soup_inner.find(id = 'strip')
                print comic
 
                src = comic.get('src')
                alt = comic.get('alt')
                title = comic.get('title')
 
                filename = address[1:][:-1] + '-' + string.zfill(1, 3) + '.' + src[-3:].lower()
                print filename
                download(src, filename)
 
                #okay so it works but i still have to study it so I can put the alt at the top
                try:
                    make_page(os.path.join('out', filename), os.path.join(outpath, os.path.basename(filename)), title, alt) # process the page
                except Exception, e:
                    print e
                sys.stdout.flush() # printing is buffered by default and this makes the display  as soon as it is encountered
 
                comic = soup_inner.find(href = address + '2/')
 
                if comic:
                    count = 2
                    while True:
                        new_addr_2  = new_addr + str(count) + '/'
                        new_page = get_page(new_addr_2,2)
 
                        if new_page:
                            new_page = BeautifulSoup(new_page)
                            comic2 = new_page.find(id = 'strip')
 
                            src = comic2.get('src')
                            alt = comic2.get('alt')
                            title = comic2.get('title')
 
                            filename = address[1:][:-1] + '-' + string.zfill(count, 3) + '.' + src[-3:].lower()
                            download(src, filename)
 
 
                            print filename
                            print os.path.join(outpath, os.path.basename(filename))
                            print title
                            print alt
 
                            try:
                                make_page(os.path.join('out', filename), os.path.join(outpath, os.path.basename(filename)), title, alt)
                            except Exception, e:
                                print e
 
                            sys.stdout.flush()
 
                            count = count + 1
 
                            comic2 = new_page.find(href = address + str(count) + '/')
 
                            if comic2:
                                continue
                            else:
                                break
 
 
 
if __name__ == "__main__":
 
    for directory in ['out', 'final']:
        if not os.path.exists(directory):
            os.makedirs(directory)
 
    outpath = os.path.join(os.getcwd(), 'final')
 
    url = 'http://oglaf.com/archive/'
    extract_archive(url)
