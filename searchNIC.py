			#####################################################
			# 	Developed by Sergio Galán akA NaxoneZ       #
			#####################################################
			# Copiar, cambiar, hacer lo que queráis.. ITS FREE! #
			#####################################################

import sys
import urllib2
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO

#Cambia por el pattern que quieras buscas
#patternArray = ["xxxx","xxxx","xxxx"]

def searchPattern(pdfFile):
    pdfArray=pdfFile.rstrip().split('\n')
    print "[*] Posibles Dominios de Phishing"
    for line1 in pdfArray:
	for line in patternArray:
		if line in line1:
			print line1
	

def download_file(download_url):
    response = urllib2.urlopen(download_url)
    file = open("document.pdf", 'w')
    file.write(response.read())
    file.close()

def pdfparser(data):

    fp = file(data, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    # Create a PDF interpreter object.C
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.

    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
        data =  retstr.getvalue()

    return data

if __name__ == '__main__':
    
    if len(sys.argv) > 1:
	    download_file(sys.argv[1])
	    pdfTxt = pdfparser("tmp/document.pdf")  
    	    searchPattern(pdfTxt)
    else:
	    print "Falta url de nic.es"
