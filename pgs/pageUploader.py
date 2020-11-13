import sys, getopt, re, os.path 
from selenium import webdriver
#from bs4 import BeautifulSoup
import  mwclient #import Site
import xlrd
#import xlsxwriter
import time
import multiprocessing as mp
import glob
# import warnings
# warnings.filterwarnings("ignore", category=DeprecationWarning)

local=True
test=False
flist = []
def main(argv):
    pageCount = 0
    flist = sorted (glob.glob(argv[0]))
    # for f in flist:
    #     print (f)
    # exit()
    for fl in flist:
        try:
            print (fl)
            with open(fl, 'r') as pageFile:
                contents = pageFile.read() 
                # pageCount += 1
                # continue
        except IOError:
            print(f'{fl} file is not accessible. Skipping.\n')
            continue
        # fl= input('Enter fileName to upload : ')
        # try:
        #     with open(fl) as pageFile:
        #         contents = pageFile.read() 
        # except IOError:
        #     print(fl + " File is not accessible\n")
        #     exit()

        # extract the pageName from the first occurance of this pattern: "''''<page name>'''"
        regex =re.compile( r"'''[^\n]+'''|$")
        match = regex.search (contents).group()
        if match != '':
            pageName = re.split("'''", match)[1]
        else:
            pageName = os.path.basename(fl) # Use the input file as the pageName
        # print(match)
        # print(pageName)

        # extract wikitext of the page from contents as lines between {{-start-}} and {{-start-}}
        startpattern = r"{{-start-}}\n"
        stopPattern = r"{{-stop-}}"
        ar=re.split (startpattern, contents)
        if (len(ar) == 1):
            print (f'{{-start-}} not found in the {fl}. Skipping.\n')
            pageFile.close()
            continue
        contents=ar[1] 
        ar=re.split (stopPattern, contents)
        if (len(ar) == 1):
            print (f'{{-stop-}} not found in the {fl}. Skipping.\n')
            pageFile.close() 
            continue
        contents=ar[0]
        #.group(1)
        # pool = mp.Pool(mp.cpu_count())
        # print('CPU Count = ', mp.cpu_count())

        # get current time for log
        today = time.localtime()
        today_time = f"{today.tm_year}_{today.tm_mon:02d}_{today.tm_mday:02d}_{today.tm_hour:02d}_{today.tm_min:02d}_{today.tm_sec:02d}"

        # login to hpedia site
        if local:
            server="127.0.1.1:8080"
            site = mwclient.Site(server, "/wiki/", scheme='http')
            #site.login('Ubuntu20.04bot','f95jssoclgv04vs3sklmucnvba24jmod')
            site.login('senapati','senapati1a')
        elif test:
            server="test.hinduismpedia.org"
            site = mwclient.Site(server, "/")
            site.login('Anantas','Senapati1a')        
        else:
            server="hinduismpedia.org"
            site = mwclient.Site(server, "/")
            site.login('Anantas','anant@987654')

        # check if page exists
        page = site.pages[pageName]
        pageExists = page.exists
        if pageExists is False:
            try:
                #site.upload(file=pageFile, filename=pageName, description=describe, ignore=True)  summary=description, title=pageName, 
                description=f'Page {pageName} uploaded at {today_time}\n'
                page.edit(text=contents, summary=description, bot=True, createonly=True)
                pageCount += 1
                #time.sleep(2)
            except Exception as err : 
                description=f'file {fl} upload error: {err}\n'
        else:
            description =f'Page \"{pageName}\" already exists in wiki at {server}. "{fl}" upload aborted at {today_time}.\n'
        page = site.pages[pageName]
        print (description)
        pageFile.close()
    print (f'{pageCount} pages uploaded.')

if __name__ == "__main__":
   main(sys.argv[1:])

