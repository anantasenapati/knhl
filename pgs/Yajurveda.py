#!/usr/bin/python
# 
import pygsheets
import pandas as pd
from os import path, devnull, remove
from aksharamukha import transliterate
import time, re
import sys, getopt

#GOOGLE_SHEETS_FILE_ID = '1NnVscMf4teFY0lHcP7AKAUd6Xln7edZ6jFFZep3PkbI'  #shaunaka Samhita
#GOOGLE_SHEETS_FILE_ID = '1iVVOBV0Zi7fgady7Ebhp6XJIBMqMxAFCX-cpOlLrHAY' #gita
#GOOGLE_SHEETS_FILE_ID = '1vdrJht3PJ1MdBuRFdUKg3_MQ6kDx1B4DOIzfpIJ0REM' #Test no verse number GuruPuja
#GOOGLE_SHEETS_FILE_ID = '1YrXO2X0bde9iBxS-iZsHx3K3UrRfglUJUAsxz3NtQjs' #test z Guru Gita
#GOOGLE_SHEETS_FILE_ID = '1QKycKeCaE8w_YgHf5hXuweuJEttgc3kWx77qtMjvZPM' #test y.z Ashtavakra Gita
#GOOGLE_SHEETS_FILE_ID = '1w8SqrNkCYH6w9CkOHaVph1AsBpMgpvmd_e-o67-5kPs' #test x.y.z Brahma Sutra
KramaNo =0

verseNumberCol =1
MandalamCol =2
SuktamNoCol =2
mantraCol = 3

VedaMantraCol = 6
VedaPadaPathCol = 8
VedaMantraSwaraRohitCol = 7
VedaPadaPathSwaraRohitCol = 9

SanskritAnvayahCol = 18
SanskritManraVisayaCol = 16
SanskritPadarthaCol = 17
SanskritBhaVarthaCol = 19

HindiMantraVisayaCol = 20
HindiPadarthaCol = 21
HindiBhaVarthaCol = 22

DevataCol = 11
ChandaCol = 13
SwaraCol = 14
RishiCol = 12


bookName = 'Book'
title = ''
target = []
targetTransliterated = []

chapter=''
section=''
verseNo=''
prevSection=''
prevChapter=''

chapterList=[]
chaptersectionList=[]
sectionList=[]
sectionTable=[]
chapterTable=[]
sectionTableList=[]
mantraList = []
mantraTable = []
SuktamMantraList = []
mantraTableList = []

debugFlag=False
def debug ():
    if debugFlag:
        return True
    else:
        return False

def printFile(fname, fdata):
    f=fname.replace(' ', '-')
    f=f.replace('\\', '-')
    f=f.replace('(', '-')
    f=f.replace(')', '-')
    with open(f , "w") as f:
        for d in fdata:
            if (type(d) == list):
                for i in d:
                    f.write(i)
            else:
                f.write(str(d))


def getChapterSectionVerse(verseNumber):
    global chapter
    global section
    global verseNo
    # chapter=''       # these variables should not change if verseNumber is not given in any row.
    # section=''       # The corresponding verse should be just added to the current page as it is.
    # verseNo=''
    parts=str(verseNumber).split('.', 2)
    if len(parts) > 2:
        chapter=parts[0]
        section=parts[1]
        verseNo=parts[2]
    elif len(parts) == 2:
        section=parts[0]
        verseNo=parts[1]
    else:
        verseNo=parts[0]
    if ((chapter == '' or chapter.isnumeric()) and 
        (section == '' or section.isnumeric()) and (verseNo == '' or verseNo.isnumeric())):
        return
    print (verseNumber + ' is not formatted correctly. Please fix the verseNumber\n')


def getTitle(row):
    return (bookName + ' ' + row[verseNumberCol])
    chapterName = str(row[MandalamCol] if row[MandalamCol] != 'nan' else "")
    sectionName = str(row[SuktamNoCol] if row[SuktamNoCol] != 'nan' else "")
    if chapterName == '' and sectionName == '':
        ptitle = bookName               # derive title from verseNumber
        pchapter=str(chapter)
        psection=str(section)
        if pchapter:
            ptitle += ' ' + pchapter + (('-' + psection) if psection else "")
        elif psection:
            ptitle += ' ' + psection
        #ptitle = bookName + pchapter + '-' + psection                 
    else:
        ptitle= bookName + ' ' + chapterName + '-' + sectionName  # title in as given in the sheet
    return ptitle



def makeMantraList(wks):
        global SuktamMantraList
        global mantraTableList
        global mantraList
        global mantraTable
        global chapterTable

        prevSuktam=0
        header=skipCount
        for row in wks:
            #Skip the Header row
            if header:
                header -= 1
                continue
            mantraNo = row[mantraCol]
            Mandalam = row[MandalamCol]
            Suktam = row[SuktamNoCol]
            mantra = row[mantraCol]
            if (Suktam != prevSuktam):
                if  mantraList:
                    SuktamMantraList.append(mantraList) # append only if the list is not  empty 
                mantraList=[ '[[' + getTitle(row) +"|" + "Adhyaya " + str(Suktam) + " Mantra Index]]",
                     "[[" + getTitle(row) + "|" + str(mantraNo) + "]]"] # start a new list
                prevSuktam = Suktam
            else:
                if (not mantraList):
                        mantraList=[ "[[" + getTitle(row) +"|" + "Adhyaya " + str(Suktam) + " Mantra Index]]"] # start a new list
                mantraList.append("[[" + getTitle(row) + "|" + str(mantraNo) + "]]")
        if  mantraList:
            SuktamMantraList.append(mantraList) # append only if the list is not  empty 

        for sukt in range (len(SuktamMantraList)):
            t = []
            mantraTable.append ('<div class="siva_table4">\n{| style=" border:1px solid #BBB;margin:.66em 0 0 .2em; width:100%"\n')
            mantraTable.append ('|- style="font-size:99%;"   class="siva_table4"\n')
            mantraTable.append("|+ ")
            mantraList=SuktamMantraList[sukt]
            for v in range(len(mantraList)):
                if ((v-1)%5 == 0):
                    mantraTable.append(" ||\n| ")
                elif (v != 0):
                    mantraTable.append(" || ")
                mantraTable.append (mantraList[v])
            mantraTable.append("\n|}\n</div>\n")
            mantraTableList.append(mantraTable)
            t=mantraTable
            mantraTable=[]
        mantraTable=[]
        # chapterTable.append ('{| style="float:right; clear:right; border:1px solid #BBB;margin:.66em 0 0 .2em"\n')
        # chapterTable.append ('|- style="font-size:99%; width:25%;"\n')
        # chapterTable.append("|+ ")
        # for chapter in range (len(chapterList)):
        #     if ( (chapter-1)%6 == 0):
        #         chapterTable.append ("\n|-\n| ")
        #     elif (chapter != 0):
        #         chapterTable.append(" || ")
        #     chapterTable.append (chapterList[chapter])
        # chapterTable.append("\n|}\n")



# sectionCounts = [1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1]
# def getSectionIndex(ch):
#     sum=0
#     for i in range[ch]:
#         sum += sectionCounts[i]
#     return sum-1


def makeLists(wks):
    global chapter
    global sectionList
    global sectionTable
    global skipCount
    global sectionCounts
    header=skipCount
    makeMantraList(wks)
    header=skipCount
    # preapre list of sections for each chapter and append it to the chaptersectionlist
    # sectionList is the list of sections of the current chapter
    # chaptersectionList is list of all sections of all chapters
    ch=1
    sec=0
    for row in wks:
        #Skip the Header row
        if header:
            header -= 1
            continue
        # prepare array for sections in each chapter
        # if ch != row[MandalamCol]:
        #     sectionCounts[ch-1] = sec
        #     sec = 0
        #     ch = row[MandalamCol]
        # sec += 1

        verseNumber = row[verseNumberCol]
        getChapterSectionVerse(verseNumber)
        if chapter == '' and section == '':
            return  # only one page. No index table needs to be prepared.
        if ( not chapterList):
            #chapterList.append(str(row[MandalamCol]) or ("'''Mandalam List'''"))                
            chapterList.append(("'''Mandalam Index'''"))                
            chapterList.append( "[[" + getTitle(row) + "|" + (chapter or bookName) + "]]") # first time
        if ( (chapter or bookName)+"]]" != chapterList[-1].rsplit('|',1)[1]): # if current chapter is not the same as the last item in chapterList
            chapterList.append( "[[" + getTitle(row) + "|" + (chapter or bookName) + "]]")  
            if  sectionList:
                chaptersectionList.append(sectionList) # append only if the list is not  empty 
            sectionList=[ "[[" + getTitle(row) + "|" + "" + chapter + " Adhyaya Index]]", 
                    "[[" + getTitle(row) + "|" + chapter + (('.' + section) if chapter else section)+ "]]"] # start a new list
        else:
            if (not sectionList): 
                    sectionList=[ "[[" + getTitle(row) + "|" + "" + chapter + " Adhyaya Index]]"] # start a new list
            if (( ((chapter + ('.' + section)) if chapter else section)+"]]") != sectionList[-1].rsplit('|',1)[1]): # if current section is not the same as the last item in sectionList, skip all verses of the  same section.
                sectionList.append("[[" + getTitle(row) + "|" + chapter + (('.' + section) if chapter else section) + "]]")
    if  sectionList:
        chaptersectionList.append(sectionList) # append only if the list is not  empty 

    # create section Table list for each chapter amd append it to sectionTableList
    for ch in range (len(chapterList)-1):
        t = []
        sectionTable.append ('<div class="siva_table4">\n{| style=" border:1px solid #BBB;margin:.66em 0 0 .2em; width:100%"\n')
        sectionTable.append ('|- style="font-size:99%;"   class="siva_table4"\n')
        sectionTable.append("|+  ")
        sectionList=chaptersectionList[ch]
        for v in range(len(sectionList)):
            if ((v-1)%5 == 0):
                #sectionTable.append ("\n||\n| ")
                sectionTable.append ("||\n| ")
            elif (v != 0):
                sectionTable.append(" || ")
            sectionTable.append (sectionList[v])
        sectionTable.append("\n|}\n</div>\n")
        sectionTableList.append(sectionTable)
        t=sectionTable
        sectionTable=[]
    sectionTable=[]

    # create a table of chapters
    if (len(chapterList) >2):
        #chapterTable.append ('<div class="siva_container">\n  <div class="siva_navtables">\n    <div class="siva_table1">\n     {| style=" border:1px solid #BBB;margin:.66em 0 0 .2em"\n|- style="font-size:99%; width:100%;"\n')
        chapterTable.append ('<div class="siva_table4">\n{| style=" border:1px solid #BBB;margin:.66em 0 0 .2em; width:100%"\n')
        chapterTable.append ('|- style="font-size:99%;"   class="siva_table4"\n')
        chapterTable.append("|+  ")
        for ch in range (len(chapterList)):
            #for v in range(len(chapterList[ch])+1):
            if ( (ch-1)%6 == 0):
                #chapterTable.append ("\n|-\n| ")
                chapterTable.append ("||\n| ")
            elif (ch !=0):
                chapterTable.append(" || ")
            chapterTable.append (chapterList[ch])
        chapterTable.append("\n|}\n</div>\n")
        #chapterTable.append("\n|}\n    </div>\n</div>\n")


def appendPageLists(row):
    global chapter
    global section
    global sectionTableList
    global chapterTable
    global chapterList
    global target

    # Keep the chapter index and Mantra index in a container.
    # Keep the section index seperately as it can be large occasionally.

    target.append('<div class="siva_container">\n')
    if (len(chapterList) >2):            
        target.append(chapterTable)  # index table of the chapters 

    # Get the mantra list
    from  builtins import any as b_any
    word = row[verseNumberCol]
    for ml in mantraTableList:
        if (b_any(word in x for x in ml)):
            mantraList = ml
            break
    target.append(mantraList)
    target.append('</div>\n')  

    # Get the section list 
    if (chapter == ''):
        if sectionTableList: # only if sectionTableList was prepared, append it.
            target.append(sectionTableList[0]) # index table of the sections
    else:
        target.append(sectionTableList[int(chapter)-1]) # index table of the sections


def startPageHeader( id, pageName):
    if csvFile:
        pageName += ' ' + str(newCsvPage)
    pageHeader = ''
    if id == 'Page':
        #pageHeader +="<div style='text-align: center;float:left;width:100%;'>'''"+ pageName +"'''</div>\n"  # title div
        pageHeader += '{{#widget:LanguageSelectorWidgetNew|textDiv=sloka|displayDiv=transliteration}}\n'    # dropdown widget
        return pageHeader
    if id == 'VedaMantra' or id == 'VedaMantraSwaraRohit' or id == 'VedaSanskritCommentary' or id == 'VedaMeta':
        pageHeader += '<div class="siva_container">\n'  # div for sloka text for transliteration
    pageHeader += '<div id=' + id + ';name=' + id + ' class="siva_sutra">\n'  # div for the given id of class siva-sutra
    if id == 'VedaMantra':
        pageHeader += '{{VedaMantra|\n' # template
    elif id == 'VedaPadaPath':
        pageHeader += '{{VedaPadaPath|\n' # template
    elif id == 'VedaMantraSwaraRohit':
        pageHeader += '{{VedaMantraSwaraRohit|\n' # template
    elif id == 'VedaPadaPathSwaraRohit':
        pageHeader += '{{VedaPadaPathSwaraRohit|\n' # template
    elif id == 'VedaSanskritCommentary':
        pageHeader += '{{RigVedaSanskritCommentary|\n' # template
    elif id == 'VedaHindiCommentary':
        pageHeader += '{{RigVedaHindiCommentary|\n' # template
    elif id == 'VedaMeta':
        pageHeader += '{{RigVedaMeta|\n' # template
    else:
        pageHeader += '<div class="siva_container">\n'  # div for sloka text for transliteration
        pageHeader += '<div id="sloka";name="sloka" class="siva_sutra">'
        pageHeader += '{{ScriptureTranscludeSource500|\n' # template
    return pageHeader


def stopPageFooter(row):
    global target
    global targetTransliterated
    #target.append("}}\n</div>\n")                           # complete template ScriptureTranscludeSource500
    #targetTransliterated.append("}}\n</div>\n")             # complete template ScriptureTransliteratedSource500
    #target.append(targetTransliterated) 
    appendPageLists(row)
    target.append(r'{{ScriptureReferences}}'+'\n')
    target.append("{{-stop-}}\n")

def startNewPage(row):
    global target
    global targetTransliterated
    global section
    global chapter
    global prevSection
    global prevChapter
    global bookName
    stopPageFooter(row)
    printFile("verses/"+ bookName + row[verseNumberCol], target)
    prevSection = section
    prevChapter = chapter
    # targetTransliterated.clear()
    # target.append("{{-start-}}\n")
    # appendPageLists()
    # target.append (startPageHeader('Page',  getTitle(row)))
    # targetTransliterated.append('{{ScriptureTransliterateSource500|\n')  # start code for transliteration


def main(argv):
    global GOOGLE_SHEETS_FILE_ID
    global prevChapter
    global prevSection
    global chapter
    global section
    global title
    global bookName
    global xcelFile
    global  csvFile
    global skipCount
    global  target
    global  targetTransliterated
    global newCsvPage
    bookName=''
    xcelFile =''
    csvFile = ''
    skipCount=1


    try:
        opts, args = getopt.getopt(argv, ":g:c:x:b:s:", ["GoogleSheetId=", "CsvFile=", "Skip=", "BookName=", "Excel="])
    except getopt.GetoptError:
        print ('pg.py [ -g <GoogleSheetId> | -x <ExcelFile> | -c <CsvFile> ] [-s <SkipLines>] [-b <BookName>]')
        sys.exit(2)
    for opt, arg in opts: 
        if opt in ("-s", "--Skip"):
            skipCount = int(arg)
        if opt in ("-b", "--BookName"):            
            bookName = arg          
        if opt in ("-g", "--GoogleSheetId"):
            GOOGLE_SHEETS_FILE_ID = arg
            if bookName == '':
                bookName=(str(arg).split('.', 2)[0]).replace(' ', '_')   # first part ofthe filename is taken as the bookname
        elif opt in ("-x", "--Excel"):
            GOOGLE_SHEETS_FILE_ID = ""
            xcelFile = arg
            if bookName == '':
                bookName=(str(arg).split('.', 2)[0]).replace(' ', '_')   # first part ofthe filename is taken as the bookname
                #bookName = arg 
        elif opt in ("-c", "--CsvFile"):
            GOOGLE_SHEETS_FILE_ID = ""
            csvFile = arg     
            if bookName == '':
                bookName=(str(arg).split('.', 2)[0]).replace(' ', '_')   # first part ofthe filename is taken as the bookname

    if (GOOGLE_SHEETS_FILE_ID == '' and xcelFile == '' and csvFile == '') or bookName == '':
        print ('pg.py [ -g <GoogleSheetId> | -x <ExcelFile> | -c <CsvFile> ] [-s <SkipLines>] [-b <BookName>]')
        sys.exit()
    if GOOGLE_SHEETS_FILE_ID:
        google_client = pygsheets.authorize()
        spreadsheet = google_client.open_by_key(GOOGLE_SHEETS_FILE_ID)
        wks_list = spreadsheet.worksheets()
        wks=wks_list[0].applymap(str)
        wks=wks.get_all_values()
    elif csvFile:
        # pip3 install requests
        import requests
        df = pd.read_csv(csvFile, header=None, skiprows=None).applymap(str)
        df.insert(0,'verseNumber','')
        df.insert(0,'Section','')
        df.insert(0,'Chapter','')
        wks=df.values
    elif xcelFile:
        # pip3 install openpyxl
        from openpyxl import load_workbook
        wks = pd.read_excel(xcelFile, sheet_name=1, header=None, skiprows=None).applymap(str)
        wks = wks.values
        #wks= df

    count=0
    firstTime=True
    #wks = [*wks]
    makeLists(wks)   # prepare the index tables for chapter pages and chapters, if any.

    prevSection=''
    prevChapter=''
    section=''
    firstPageList = ''

    target = []
    targetTransliterated = []
    VedaMantra = []
    VedaPadaPath = []
    VedaMantraSwaraRohit = []
    VedaPadaPathSwaraRohit = []
    VedaSanskritCommentary = []
    VedaHindiCommentary = []
    VedaMeta = []

    newCsvPage=1

    # get the prev, current and next rows to create the links to prev and next slokas
#### implement >>> l = [None, *l, None] and then for prev, cur, nxt in zip(l, l[1:], l[2:]):
    wks = [*wks][skipCount:]
    wks = [None, *wks, None] 
    for prev, row, nxt in zip(wks, wks[1:], wks[2:]):
        
    #for row in [*wks][skipCount:]:
        verseNumber = row[verseNumberCol]
        prevSection = section
        #prevChapter = chapter
        target.append("{{-start-}}\n")
        target.append("__NOTOC__\n")

        nxtVerseNo=prevVerseNo=None
        verseNo = row[verseNumberCol]
        #chapter=verseNo.rsplit('.', 2)[0]
        if prev is not None:
            prevVerseNo=prev[verseNumberCol]
        if nxt is not None:
            nxtVerseNo =nxt[verseNumberCol]
        if prevVerseNo is not None and prevVerseNo != "Verse Number":
            target.append("<div style='text-align: left;float:left;width:33%;'>[["+"YajurVeda "+prevVerseNo+"|←Previous]]</div>\n")
        else:    
            target.append("<div style='text-align: left;float:left;width:33%;'>"+verseNo+"</div>\n")
        target.append("<div style='text-align: center;float:left;width:33%;'>'''"+"YajurVeda "+verseNo+"'''</div>\n")
        if nxtVerseNo is not None:
            target.append("<div style='text-align: right;float:left;width:33%;'>[["+"YajurVeda "+nxtVerseNo+"|Next→]]</div>\n")
        target.append("\n")

        getChapterSectionVerse(verseNumber)        
        target.append(startPageHeader('Page', getTitle(row)))
        appendPageLists(row)
        VedaMantra.append(startPageHeader('VedaMantra', ''))
        VedaPadaPath.append(startPageHeader('VedaPadaPath', ''))
        VedaMantraSwaraRohit.append(startPageHeader('VedaMantraSwaraRohit', ''))
        VedaPadaPathSwaraRohit.append(startPageHeader('VedaPadaPathSwaraRohit', ''))
        VedaSanskritCommentary.append(startPageHeader('VedaSanskritCommentary', ''))
        VedaHindiCommentary.append(startPageHeader('VedaHindiCommentary', ''))
        VedaMeta.append(startPageHeader('VedaMeta', ''))
        # if (section != prevSection):
        #     startNewPage(row)
        
        # वेद मन्त्र स्वर सहित
        temp = str(row[VedaMantraCol]).replace('।', '।\n') 
        lines = re.split("\n+", temp)       # ignore empty lines
        linesRead=0                 # no of lines of text witin the given cell
        linesToRead= len(lines)     # no of lines of text witin the given cell
        for e in lines:
            e='{{ns}}' + e.lstrip().rstrip()   #strip all leading and and traling white space

            if (e.find('॥') != -1):   # append verse number and create a new <span id=x > for transliteration.
                e += verseNumber + "॥" + f'|\n' #----\n' 
            elif (e.find('||') != -1):
                e = e.replace ("||", "{{!}}{{!}}")
                e += verseNumber + "{{!}}{{!}}" + f'|\n' #----\n'
            elif (e.find('|') != -1):
                e = e.replace ("|", "{{!}}|\n")    # for use in tempaltes
            else:                
                t1 = e.find('।')
                t2 = e.find('॥')
                if ( t1 != -1 and (t2 == -1 or t2 > t1) ):   # if both are present, introduce newline.
                    e = e.replace('।', '।|\n', 1)
                elif (t1 == -1 and t2 == -1):
                    e += '|\n'
            e=e.replace ('=', '<nowiki>=</nowiki>')
            VedaMantra.append(e)
        VedaMantra.append('}}\n</div>\n')

        VedaPadaPath.append('{{ns}}' + row[VedaPadaPathCol].replace('=', '<nowiki>=</nowiki>'))
        VedaPadaPath.append('}}\n</div>\n')
        VedaPadaPath.append('</div>\n')  

        # वेद मन्त्र स्वर रहित
        temp = str(row[VedaMantraSwaraRohitCol]).replace('।', '।\n') 
        lines = re.split("\n+", temp)       # ignore empty lines
        linesRead=0                 # no of lines of text witin the given cell
        linesToRead= len(lines)     # no of lines of text witin the given cell
        for e in lines:
            e='{{ns}}' + e.lstrip().rstrip()   #strip all leading and and traling white space

            if (e.find('॥') != -1):   # append verse number and create a new <span id=x > for transliteration.
                e += verseNumber + "॥" + f'|\n' #----\n' 
            elif (e.find('||') != -1):
                e = e.replace ("||", "{{!}}{{!}}")
                e += verseNumber + "{{!}}{{!}}" + f'|\n' #----\n'
            elif (e.find('|') != -1):
                e = e.replace ("|", "{{!}}|\n")    # for use in tempaltes
            else:                
                t1 = e.find('।')
                t2 = e.find('॥')
                if ( t1 != -1 and (t2 == -1 or t2 > t1) ):   # if both are present, introduce newline.
                    e = e.replace('।', '।|\n', 1)
                elif (t1 == -1 and t2 == -1):
                    e += '|\n'
            e=e.replace ('=', '<nowiki>=</nowiki>')
            VedaMantraSwaraRohit.append(e)
        VedaMantraSwaraRohit.append('}}\n</div>\n')

        VedaPadaPathSwaraRohit.append('{{ns}}' + row[VedaPadaPathSwaraRohitCol].replace('=', '<nowiki>=</nowiki>'))
        VedaPadaPathSwaraRohit.append('}}\n</div>\n')
        VedaPadaPathSwaraRohit.append('</div>\n')

        VedaSanskritCommentary.append('{{ns}}' + row[SanskritManraVisayaCol].replace('=', '<nowiki>=</nowiki>') + '|\n')
        VedaSanskritCommentary.append('{{ns}}' + row[SanskritAnvayahCol].replace('=', '<nowiki>=</nowiki>') + '|\n')
        VedaSanskritCommentary.append('{{ns}}' + row[SanskritPadarthaCol].replace('=', '<nowiki>=</nowiki>') + '|\n')
        VedaSanskritCommentary.append('{{ns}}' + row[SanskritBhaVarthaCol].replace('=', '<nowiki>=</nowiki>') + '|\n')
        VedaSanskritCommentary.append('}}\n</div>\n')

        VedaHindiCommentary.append('{{ns}}' + row[HindiMantraVisayaCol].replace('=', '<nowiki>=</nowiki>') + '|\n')
        VedaHindiCommentary.append('{{ns}}' + row[HindiPadarthaCol].replace('=', '<nowiki>=</nowiki>') + '|\n')
        VedaHindiCommentary.append('{{ns}}' + row[HindiBhaVarthaCol].replace('=', '<nowiki>=</nowiki>') + '|\n')
        VedaHindiCommentary.append('}}\n</div>\n')
        VedaHindiCommentary.append('</div>\n')

        VedaMeta.append('{{ns}}'+row[DevataCol] + '|\n')
        VedaMeta.append('{{ns}}'+row[RishiCol] + '|\n')
        VedaMeta.append('{{ns}}'+row[ChandaCol] + '|\n')
        VedaMeta.append('{{ns}}'+row[SwaraCol])
        VedaMeta.append('}}\n</div>\n')
        VedaMeta.append('</div>\n')

        target.append(VedaMeta)

        target.append(VedaMantra)
        target.append(VedaPadaPath)

        target.append(VedaMantraSwaraRohit)
        target.append(VedaPadaPathSwaraRohit)

        target.append(VedaSanskritCommentary)
        target.append(VedaHindiCommentary)

        startNewPage(row)
        target.clear()
        VedaMantra.clear()
        VedaPadaPath.clear()
        VedaMantraSwaraRohit.clear()
        VedaPadaPathSwaraRohit.clear()
        VedaSanskritCommentary.clear()
        VedaHindiCommentary.clear()
        VedaMeta.clear()

    if csvFile:
        prevChapter = newCsvPage
        newCsvPage += 1
    debug()


if __name__ == "__main__":
   main(sys.argv[1:])