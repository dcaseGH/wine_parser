#The import name for this library is fitz
import fitz
from Wine import Wine
#from JohnsonReader import JohnsonReader

# Create a document object
doc = fitz.open('Johnson2023.pdf')  # or fitz.Document(filename)

# Extract the number of pages (int)
print(doc.page_count)

# the metadata (dict) e.g., the author,...
print(doc.metadata)

# Get the page by their index
page = doc.load_page(126)
 # or page = doc[0]

a = page.get_fonts()
print(a)
all_infos = page.get_text("dict")
print(all_infos)

def is_rating(span):
    if span['font'] == 'SegoeUISymbol':
        return True
    return False

def is_place(span):
    if span['font'] == 'Tahoma-Bold':
        return True
    return False

def is_red(span):
    if span['color'] == 9373699:
        return True
    return False    

def is_a_wine():
    pass

wine_list = []
wine = None 

for b in all_infos['blocks']:
    if b['type'] == 0:  # type 0 is text
        for line in b['lines']:
            for span in line['spans']:
                if is_rating(span):
                    print('rating', span['text'])
                if is_place(span):
                    print('place', span['text'])
                    if wine:
                        wine_list.append(wine)
                    wine = Wine(span['text'])

#                print(span['text'])
                #print(span['bbox'])  # bounding box of the text
                #print(span['size'])  # font size
#                print(span['flags'])  # font flags (bold, italic, etc.)
#                print(span['color'])  # color of the text

print([w.__str__() for w in wine_list])

exit()
text = page.get_text()

#print(text)

#print (paragraphs[1])


def parse_paragraph(para):
    ''' '''
    if not is_a_wine(para):
        return None
    
    print(para)

paragraphs = text.split('\n')
for p in paragraphs[1]:
    print (p, )



pix = page.get_pixmap() 
pix.save(f"page-{page.number}.png")
print(page.number)
exit()

# read a Page
text = page.get_text()

# Render and save the page as an image
pix = page.get_pixmap() 
pix.save(f"page-{page.number}.png")

# get all links on a page
links = page.get_links()
print(links)

# Render and save all the pages as images
for i in range(doc.page_count):
  page = doc.load_page(i)
  pix = page.get_pixmap()
  pix.save("page-%i.png" % page.number)

# get the links on all pages
for i in range(doc.page_count):
  page = doc.load_page(i)
  link = page.get_links()
  print(link)

