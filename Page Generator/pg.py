#!/usr/bin/python
# 
import pygsheets
import pandas as pd
from os import path, devnull, remove
from aksharamukha import transliterate
import time
import sys, getopt

GOOGLE_SHEETS_FILE_ID = '1NnVscMf4teFY0lHcP7AKAUd6Xln7edZ6jFFZep3PkbI'  #shaunaka Samhita
#GOOGLE_SHEETS_FILE_ID = '1iVVOBV0Zi7fgady7Ebhp6XJIBMqMxAFCX-cpOlLrHAY' #gita
#GOOGLE_SHEETS_FILE_ID = '1vdrJht3PJ1MdBuRFdUKg3_MQ6kDx1B4DOIzfpIJ0REM' #Test no verse number
#GOOGLE_SHEETS_FILE_ID = '1YrXO2X0bde9iBxS-iZsHx3K3UrRfglUJUAsxz3NtQjs' #test z
#GOOGLE_SHEETS_FILE_ID = '1QKycKeCaE8w_YgHf5hXuweuJEttgc3kWx77qtMjvZPM' #test y.z
#GOOGLE_SHEETS_FILE_ID = '1w8SqrNkCYH6w9CkOHaVph1AsBpMgpvmd_e-o67-5kPs' #test x.y.z
chapterNameCol=0
sectionNameCol=1
verseNumberCol=2
slokaCol=3
bookName = 'Book'
title = ''

chapter=''
section=''
verseNo=''

chapterList=[]
chaptersectionList=[]
sectionList=[]
sectionTable=[]
chapterTable=[]
sectionTableList=[]

debugFlag=False
def debug ():
    if debugFlag:
        return True
    else:
        return False

def printFile(fname, fdata):
    with open(fname, "w") as f:
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
    parts=verseNumber.split('.', 2)
    if len(parts) > 2:
        chapter=parts[0]
        section=parts[1]
        verseNo=parts[2]
    if len(parts) == 2:
        section=parts[0]
        verseNo=parts[1]
    else:
        verseNo=parts[0]
    if ((chapter == '' or chapter.isnumeric()) and 
        (section == '' or section.isnumeric()) and (verseNo == '' or verseNo.isnumeric())):
        return
    print (verseNumber + ' is not formatted correctly. Please fix the rowNumbers\n')


def getTitle(row):
    if row[chapterNameCol] == '' and row[sectionNameCol] == '':
        ptitle = bookName               # derive title from rowNumber
        if chapter:
            ptitle += ' ' + chapter + (('.' + section) if section else "")
        elif section:
            ptitle += ' ' + section
        ptitle = bookName + chapter + '.' + section                 
    else:
        ptitle= bookName + ' ' + row[chapterNameCol] + ':' + row[sectionNameCol]  # title in as given in the sheet
    return ptitle

def makeLists(wks):
    global chapter
    global sectionList
    global sectionTable
    header=True

    # preapre list of sections for each chapter and append it to the chaptersectionlist
    # sectionList is the list of sections of the current chapter
    # chaptersectionList is list of all sections of all chapters
    for row in wks:
        #Skip the Header row
        if header:
            header=False
            continue
        verseNumber = row[verseNumberCol]
        getChapterSectionVerse(verseNumber)
        if chapter == '' and section == '':
            return  # only one page. No index table needs to be prepared.
        if ( not chapterList):
            chapterList.append("'''" + (row[chapterNameCol] or ('Chapters')) + "'''")                
            chapterList.append( "[[" + getTitle(row) + "|" + (chapter or bookName) + "]]") # first time
        if ( (chapter or bookName)+"]]" != chapterList[-1].rsplit('|',1)[1]): # if current chapter is not the same as the last item in chapterList
            chapterList.append( "[[" + getTitle(row) + "|" + (chapter or bookName) + "]]")  
            if  sectionList:
                chaptersectionList.append(sectionList) # append only if the list is not  empty 
            sectionList=[ "[[" + getTitle(row) + "|" + "'''Chapter " + chapter + "''']]", 
                    "[[" + getTitle(row) + "|" + chapter + (('.' + section) if chapter else section)+ "]]"] # start a new list
        else:
            if (not sectionList): 
                    #sectionList=[ "[[" + getTitle(row) + "|" + "'''Chapter " + chapter + "''']]"] # start a new list
                    sectionList=[ "[[" + getTitle(row) + "|" + "Chapter Pages" + chapter + "]]"] # start a new list
            if (( ((chapter + ('.' + section)) if chapter else section)+"]]") != sectionList[-1].rsplit('|',1)[1]): # if current section is not the same as the last item in sectionList, skip all verses of the  same section.
                sectionList.append("[[" + getTitle(row) + "|" + chapter + (('.' + section) if chapter else section) + "]]")
    if  sectionList:
        chaptersectionList.append(sectionList) # append only if the list is not  empty 

    # create section Table list for each chapter amd append it to sectionTableList
    for ch in range (len(chapterList)-1):
        sectionTable.append ('<div class="siva_table4">\n{| style=" border:1px solid #BBB;margin:.66em 0 0 .2em"\n')
        sectionTable.append ('|- style="font-size:99%;"   class="siva_table4"\n')
        sectionTable.append("|+ ")
        sectionList=chaptersectionList[ch]
        for v in range(len(sectionList)):
            if ((v-1)%5 == 0):
                #sectionTable.append ("\n|-\n| ")
                sectionTable.append ("\n||\n| ")
            elif (v != 0):
                sectionTable.append(" || ")
            sectionTable.append (sectionList[v])
        sectionTable.append("\n|}\n</div>\n")
        sectionTableList.append(sectionTable)
        sectionTable=[]

    # create a table of chapters
    if (len(chapterList) >2):
        chapterTable.append ('<div class="siva_container">\n  <div class="siva_navtables">\n    <div class="siva_table1">\n     {| style=" border:1px solid #BBB;margin:.66em 0 0 .2em"\n|- style="font-size:99%; width:100%;"\n')
        chapterTable.append("|+ ")
        for ch in range (len(chapterList)):
            #for v in range(len(chapterList[ch])+1):
            if ( (ch-1)%6 == 0):
                #chapterTable.append ("\n|-\n| ")
                chapterTable.append ("\n||\n| ")
            elif (ch != 0):
                chapterTable.append(" || ")
            chapterTable.append (chapterList[ch])
        chapterTable.append("\n|}\n    </div>\n</div>\n")



def main(argv):
    global GOOGLE_SHEETS_FILE_ID
    global prevSection
    global section
    global title
    global bookName
    try:
        opts, args = getopt.getopt(argv, "i:b:", ["InputFile=", "BookName="])
    except getopt.GetoptError:
        print ('pg.py [-i] <GoogleSheetId> [-b <BookName>]')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            GOOGLE_SHEETS_FILE_ID = arg
        elif opt in ("-b", "--BookName"):
            bookName = arg
    if GOOGLE_SHEETS_FILE_ID == '' or bookName == '':
        print ('pg.py [-i] <GoogleSheetId> [-b <BookName>]')
        sys.exit()
    google_client = pygsheets.authorize()
    spreadsheet = google_client.open_by_key(GOOGLE_SHEETS_FILE_ID)
    wks_list = spreadsheet.worksheets()
    dirname = path.dirname(__file__)
    wks=wks_list[0]
    count=0
    firstPageList = ''
    target = []
    targetTransliterated = []
    firstTime=True
    #wks = [*wks]
    makeLists(wks)   # prepare the index tables for chapter pages and chapters, if any.
    prevSection=''
    section=''
    for row in [*wks][1:]:
        verseNumber = row[verseNumberCol]
        if firstTime:
            prevSection = section
            target.append("{{-start-}}\n")
            if sectionTableList: # only if sectionTableList was prepared, append it.
                target.append(sectionTableList[0]) # index table of the sections
            firstPageList +="<div style='text-align: center;float:left;width:100%;'>'''"+ 'XXXXXXXXXX' +"'''</div>\n"  # title div
            firstPageList += "\n"
            firstPageList += '{{#widget:LanguageSelectorWidgetNew|textDiv=sloka|displayDiv=transliteration}}\n'  # insert the language selection dropdown
            firstPageList += '<div class="siva_container">\n'  # div for sloka text for transliteration
            firstPageList += '<div id="sloka";name="sloka" class="siva_sutra">\n'  # div for sloka text for transliteration
            firstPageList += '{{ScriptureTranscludeSource500|\n' # ttemplate
            #firstPageList += 'YYYYYYYYYY' + '|\n'  # Sloka heading
            targetTransliterated.append('{{ScriptureTransliterateSource500|\n')  # start code for transliteration
        getChapterSectionVerse(verseNumber)        
        if firstTime:
            firstTime=False
            firstPageList = firstPageList.replace ( 'XXXXXXXXXX', getTitle(row))    # update title now that we know it.
            #firstPageList = firstPageList.replace ( 'YYYYYYYYYY', (row[sectionNameCol] or getTitle(row)))    # update Section now that we know it.
            target.append (firstPageList)
            prevSection = section
        if (section != prevSection):
            target.append("}}\n</div>\n")                           # complete template ScriptureTranscludeSource500
            targetTransliterated.append("}}\n</div>\n")             # complete template ScriptureTransliteratedSource500
            target.append(targetTransliterated)             # add the transliterated table
            if (chapter == ''):
                target.append(sectionTableList[0]) # index table of the sections
            else:
                target.append(sectionTableList[int(chapter)-1]) # index table of the sections
            if (len(chapterList) >2):            
                target.append(chapterTable)                 # index table of the chapters 
            target.append("{{-stop-}}\n")
            #targetTransliterated.append("}}\n")
            printFile("verses/"+ bookName + chapter + prevSection, target)
            prevSection = section
            target.clear()
            targetTransliterated.clear()
            target.append("{{-start-}}\n")
            if (chapter == ''):
                target.append(sectionTableList[0]) # index table of the sections
            else:
                target.append(sectionTableList[int(chapter)-1]) # index table of the sections
            target.append("<div style='text-align: center;float:left;width:100%;'>'''" + getTitle(row) +"'''</div>\n")  # title div
            target.append("\n")
            target.append('{{#widget:LanguageSelectorWidgetNew|textDiv=sloka|displayDiv=transliteration}}\n')  # insert the language selection dropdown
            target.append('<div class="siva_container">\n')
            target.append('<div id="sloka";name="sloka" class="siva_sutra">\n')
            target.append('{{ScriptureTranscludeSource500|\n')
            #target.append((row[sectionNameCol] or getTitle(row)) + "|\n" )
            targetTransliterated.append('{{ScriptureTransliterateSource500|\n')  # start code for transliteration
        lines = str(row[slokaCol]).splitlines()
        linesRead=0                 # no of lines of text witin the given cell
        linesToRead= len(lines)     # no of lines of text witin the given cell
        for e in lines:
            e='{{ns}}'+e.lstrip().rstrip()   #strip all leand and traing white space
            if e.rstrip('|') == '':         # ignore empty lines or lines with only '|'
                continue
            parts=e.rsplit('||', 2)
            if len(parts) > 1:
                appendSlokaNo = True
            else:
                appendSlokaNo = False
            e=e.replace ("|", "{{!}}") 
            if appendSlokaNo and verseNumber:
                e = e + verseNumber + "{{!}}{{!}}|\n"
            else:
                e = e + "|\n"
            if debug():
                print( "line: ", e)
            if linesRead < linesToRead:
                transliteratedText = transliterate.process('autodetect', 'IAST', e, nativize = False)
                target.append(e)
                targetTransliterated.append(transliteratedText)
            if appendSlokaNo:
                target.append("----\n")
                targetTransliterated.append("----\n")
            linesRead += 1

    target.append("}}\n</div>\n")                           # complete template ScriptureTranscludeSource500
    targetTransliterated.append("}}\n</div>\n")             # complete template ScriptureTransliteratedSource500
    target.append(targetTransliterated) 
    if (chapter == ''):
        if sectionTableList: # only if at least one sectionTableList was prepared, append it.
            target.append(sectionTableList[0]) # index table of the sections
    else:
        target.append(sectionTableList[int(chapter)-1]) # index table of the sections
    if (len(chapterList) >2):            
        target.append(chapterTable)                 # index table of the chapters 
    target.append("{{-stop-}}\n")
    printFile("verses/"+ bookName + chapter + prevSection, target)
    target.clear()
    targetTransliterated.clear()
    debug()


if __name__ == "__main__":
   main(sys.argv[1:])