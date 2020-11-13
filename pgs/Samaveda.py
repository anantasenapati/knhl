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

verseNumberCol =5
MandalamCol =6
SuktamNoCol =9
mantraCol = 10
RigVedCol = 31

VedaMantraCol = 22
VedaPadaPathCol = 25
VedaMantraSwaraRohitCol = 23
VedaPadaPathSwaraRohitCol = 26

SanskritAnvayahCol = 42
SanskritManraVisayaCol = 36
SanskritPadarthaCol = 38
SanskritBhaVarthaCol = 40

HindiMantraVisayaCol = 37
HindiPadarthaCol = 39
HindiBhaVarthaCol = 41

DevataCol = 29
ChandaCol = 28
SwaraCol = 30
RishiCol = 27


bookName = 'सामवेद'
title = ''
target = []
targetTransliterated = []

ardha=''
dashatiSukta=''
verseNo=''
prevdashatiSukta=''
prevardha=''

praPathakTable=[]
ardhaTableList=[]
dashatiSuktaTableList=[]
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


def getardhadashatiSuktaVerse(verseNumber):
    global praPathak
    global ardha
    global dashatiSukta
    global verseNo
    # ardha=''       # these variables should not change if verseNumber is not given in any row.
    # dashatiSukta=''       # The corresponding verse should be just added to the current page as it is.
    # verseNo=''
    parts=str(verseNumber).split('.', 3)
    if len(parts) > 3:
        praPathak=parts[0]
        ardha=parts[1]
        dashatiSukta=parts[2]
        verseNo=parts[3]
    elif len(parts) > 2:
        ardha=parts[0]
        dashatiSukta=parts[1]
        verseNo=parts[2]
    elif len(parts) == 2:
        dashatiSukta=parts[0]
        verseNo=parts[1]
    else:
        verseNo=parts[0]
    if ((ardha == '' or ardha.isnumeric()) and 
        (dashatiSukta == '' or dashatiSukta.isnumeric()) and (verseNo == '' or verseNo.isnumeric())):
        return
    print (verseNumber + ' is not formatted correctly. Please fix the verseNumber\n')


def getTitle(row):
    bookName = 'सामवेद'
    # ardhaName =  row[MandalamCol] + '-' + row[MandalamCol+1]    # cols G-H
    # dashatiSuktaName = row[SuktamNoCol] if row[SuktamNoCol] != '-' else row[SuktamNoCol-1] # col J or I
    getardhadashatiSuktaVerse(row[verseNumberCol])
    ardhaName = praPathak + '-' + ardha
    dashatiSuktaName = dashatiSukta
    mantra = row[mantraCol]
    archika = row[1]
    KandaOrParva=(row[19] if row[19] != "nan" else row[21])
    if ardhaName == '' and dashatiSuktaName == '':
        ptitle = bookName               # derive title from verseNumber
        pardha=str(ardha)
        pdashatiSukta=str(dashatiSukta)
        if pardha:
            ptitle += ' ' + pardha + (('-' + pdashatiSukta) if pdashatiSukta else "")
        elif pdashatiSukta:
            ptitle += ' ' + pdashatiSukta
        #ptitle = bookName + pardha + '-' + pdashatiSukta                 
    else:
        ptitle= bookName + '_' + archika + '_' + KandaOrParva + '_' + ardhaName + '-' + dashatiSuktaName + '-' + mantra  # title in as given in the sheet
    return ptitle



def makeMantraList(wks):
        global mantraTableList
        SuktamMantraList = []
        mantraTable = []
        ardhaTable = []
        mantraList = []

        prevSuktam=0
        header=skipCount
        for row in wks:
            #Skip the Header row
            if header:
                header -= 1
                continue
            # Mandalam = row[MandalamCol] + '-' + row[MandalamCol+1] 
            # Suktam = row[SuktamNoCol] if row[SuktamNoCol] != '-' else row[SuktamNoCol-1]
            # mantra = row[mantraCol]
            # mandalam = praPathak + ardha
            # archika = row[1]
            # KandaOrParva=(row[19] if row[19] != "nan" else row[21])

            getardhadashatiSuktaVerse(row[verseNumberCol])
            ardhaName = praPathak + ardha
            Suktam = dashatiSukta
            mantra = row[mantraCol]

            if (Suktam != prevSuktam):
                if  mantraList:
                    SuktamMantraList.append(mantraList) # append only if the list is not  empty 
                mantraList=[ '[[' + getTitle(row) +"|" + "Sukta " + str(ardhaName) + '.' + str(Suktam) + " Mantra Index]]",
                     "[[" + getTitle(row) + "|" + str(mantra) + "]]"] # start a new list
                prevSuktam = Suktam
            else:
                if (not mantraList):
                        mantraList=[ "[[" + getTitle(row) +"|" + "Sukta " + str(ardhaName) + '.' + str(Suktam) + " Mantra Index]]"] # start a new list
                mantraList.append("[[" + getTitle(row) + "|" + str(mantra) + "]]")
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
        # ardhaTable.append ('{| style="float:right; clear:right; border:1px solid #BBB;margin:.66em 0 0 .2em"\n')
        # ardhaTable.append ('|- style="font-size:99%; width:25%;"\n')
        # ardhaTable.append("|+ ")
        # for ardha in range (len(ardhaList)):
        #     if ( (ardha-1)%6 == 0):
        #         ardhaTable.append ("\n|-\n| ")
        #     elif (ardha != 0):
        #         ardhaTable.append(" || ")
        #     ardhaTable.append (ardhaList[ardha])
        # ardhaTable.append("\n|}\n")



# dashatiSuktaCounts = [1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1]
# def getdashatiSuktaIndex(ch):
#     sum=0
#     for i in range[ch]:
#         sum += dashatiSuktaCounts[i]
#     return sum-1


def makeLists(wks):
    global ardha
    global dashatiSuktaTableList
    global ardhaTableList
    global praPathakTable
    global skipCount
    global dashatiSuktaCounts
    header=skipCount
    makeMantraList(wks)
    header=skipCount
    ardhaList=[]
    praPathakList=[]
    praPathakardhaList=[]
    dashatiSuktaList=[]
    praPathakTable=[]
    ardhadashatiSuktaList=[]
    dashatiSuktaTable=[]

    # preapre list of dashatiSuktas for each ardha and append it to the ardhadashatiSuktalist
    # dashatiSuktaList is the list of dashatiSuktas of the current ardha
    # ardhadashatiSuktaList is list of all dashatiSuktas of all ardhas
    ch=1
    sec=0
    for row in wks:
        #Skip the Header row
        if header:
            header -= 1
            continue

        verseNumber = row[verseNumberCol]
        getardhadashatiSuktaVerse(verseNumber)
        if (not praPathakList):
            praPathakList.append("'''Prapathak Index'''")
            praPathakList.append( "[[" + getTitle(row) + "|" + praPathak + "]]")
            ardhaList=[ "[[" + getTitle(row) + "|" + "Prapathak " + praPathak + " Ardha Prapathak Index]]"]
            ardhaList.append("[[" + getTitle(row) + "|" + praPathak + '.' + ardha + "]]") # start a new list
            dashatiSuktaList=[ "[[" + getTitle(row) + "|" + "Ardha Prapathak " + praPathak +'.' + ardha + " Sukta Index]]"] 
            dashatiSuktaList.append ("[[" + getTitle(row) + "|" + praPathak + '.' + ardha + '.' + dashatiSukta + "]]") # start a new list
        elif ( praPathak + "]]"   !=   praPathakList[-1].rsplit('|',1)[1]): # if current ardha is not the same as the last item in ardhaList
            praPathakList.append( "[[" + getTitle(row) + "|" + praPathak + "]]") 
            if  ardhaList:
                praPathakardhaList.append(ardhaList) # append only if the list is not  empty 
            ardhaList=[ "[[" + getTitle(row) + "|" + "Prapathak " + praPathak + " Ardha Prapathak Index]]"]
            ardhaList.append("[[" + getTitle(row) + "|" + praPathak + '.' + ardha + "]]") # start a new list
            if  dashatiSuktaList:
                ardhadashatiSuktaList.append(dashatiSuktaList) # append only if the list is not  empty 
            dashatiSuktaList=[ "[[" + getTitle(row) + "|" + "Ardha Prapathak " + praPathak +'.' + ardha + " Sukta Index]]"] 
            dashatiSuktaList.append ("[[" + getTitle(row) + "|" + praPathak + '.' + ardha + '.' + dashatiSukta + "]]") # start a new list
        elif ( (praPathak + '.' + ardha +"]]") != ardhaList[-1].rsplit('|',1)[1]): # if current dashatiSukta is not the same as the last item in dashatiSuktaList, skip all verses of the  same dashatiSukta.
                ardhaList.append("[[" + getTitle(row) + "|" + praPathak + '.' + ardha + "]]")
                if  dashatiSuktaList:
                    ardhadashatiSuktaList.append(dashatiSuktaList) # append only if the list is not  empty 
                dashatiSuktaList=[ "[[" + getTitle(row) + "|" + "Ardha Prapathak " + praPathak +'.' + ardha + " Sukta Index]]"] 
                dashatiSuktaList.append ("[[" + getTitle(row) + "|" + praPathak + '.' + ardha + '.' + dashatiSukta + "]]") # start a new list
        elif ( (praPathak + '.' + ardha + '.' + dashatiSukta+"]]") != dashatiSuktaList[-1].rsplit('|',1)[1]): # if current dashatiSukta is not the same as the last item in dashatiSuktaList, skip all verses of the  same dashatiSukta.
            dashatiSuktaList.append("[[" + getTitle(row) + "|" + praPathak + '.' + ardha + '.' + dashatiSukta + "]]")

    if  dashatiSuktaList:
        ardhadashatiSuktaList.append(dashatiSuktaList) # append only if the list is not  empty 
    if  ardhaList:
        praPathakardhaList.append(ardhaList)  

    # create dashatiSukta Table list for each ardha amd append it to dashatiSuktaTableList
    for ch in range (len(ardhadashatiSuktaList)):
        t = []
        dashatiSuktaTable.append ('<div class="siva_table4">\n{| style=" border:1px solid #BBB;margin:.66em 0 0 .2em; width:100%"\n')
        dashatiSuktaTable.append ('|- style="font-size:99%;"   class="siva_table4"\n')
        dashatiSuktaTable.append("|+  ")
        dashatiSuktaList=ardhadashatiSuktaList[ch]
        for v in range(len(dashatiSuktaList)):
            if ((v-1)%5 == 0):
                dashatiSuktaTable.append ("||\n| ")
            elif (v != 0):
                dashatiSuktaTable.append(" || ")
            dashatiSuktaTable.append (dashatiSuktaList[v])
        dashatiSuktaTable.append("\n|}\n</div>\n")
        dashatiSuktaTableList.append(dashatiSuktaTable)
        t=dashatiSuktaTable
        dashatiSuktaTable=[]
    dashatiSuktaTable=[]

    # create a table of Suktas
    for ch in range (len(praPathakardhaList)):
        t = []
        ardhaTable=[]
        ardhaTable.append ('<div class="siva_table4">\n{| style=" border:1px solid #BBB;margin:.66em 0 0 .2em; width:100%"\n')
        ardhaTable.append ('|- style="font-size:99%;"   class="siva_table4"\n')
        ardhaTable.append("|+  ")
        ardhaList=praPathakardhaList[ch]
        for v in range(len(ardhaList)):
            if ((v-1)%5 == 0):
                ardhaTable.append ("||\n| ")
            elif (v != 0):
                ardhaTable.append(" || ")
            ardhaTable.append (ardhaList[v])
        ardhaTable.append("\n|}\n</div>\n")
        ardhaTableList.append(ardhaTable)
        t=ardhaTable
        ardhaTable=[]
    ardhaTable=[]


    # create a table of ardhas
    if (len(praPathakList) >2):
        praPathakTable.append ('<div class="siva_table4">\n{| style=" border:1px solid #BBB;margin:.66em 0 0 .2em; width:100%"\n')
        praPathakTable.append ('|- style="font-size:99%;"   class="siva_table4"\n')
        praPathakTable.append("|+  ")
        for ch in range (len(praPathakList)):
            if ( (ch-1)%6 == 0):
                praPathakTable.append ("||\n| ")
            elif (ch !=0):
                praPathakTable.append(" || ")
            praPathakTable.append (praPathakList[ch])
        praPathakTable.append("\n|}\n</div>\n")


def appendPageLists(row):
    global ardha
    global dashatiSuktaTableList
    global ardhaTableList
    global praPathakTable
    global target

    # Keep the ardha index and Mantra index in a container.
    # Keep the dashatiSukta index seperately as it can be large occasionally.
    # if (row[verseNumberCol] == '7...1'):
    #     x=1
    target.append('<div class="siva_container">\n')
    if (len(praPathakTable) >2):            
        target.append(praPathakTable)  # index table of the ardhas 
    # Get the mantra list
    from  builtins import any as b_any
    word = row[verseNumberCol].replace('.', '-')
    mantraList = None
    for ml in mantraTableList:
        if (b_any(word in x for x in ml)):
            mantraList = ml
            break
    if mantraList:
        target.append(mantraList)
    target.append('</div>\n')  
    # Get the Ardha list 
    target.append('<div class="siva_container">\n')
    if (ardha != ''):
    #     if dashatiSuktaTableList: # only if dashatiSuktaTableList was prepared, append it.
    #         target.append(ardhaTableList[0]) # index table of the dashatiSuktas
    # else:
        target.append(ardhaTableList[int(praPathak)-1]) # index table of the dashatiSuktas
    # Get the DashatiSukta list
    from  builtins import any as b_any
    #word = row[verseNumberCol].replace('.', '-')
    word = row[verseNumberCol].rsplit('.', 1)[0]  # only take a.b.c out of a.b.c.d
    mantraList = None
    for ml in dashatiSuktaTableList:
        if (b_any(word in x for x in ml)):
            mantraList = ml
            break
    if mantraList:
        target.append(mantraList)
    target.append('</div>\n')  


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
    global dashatiSukta
    global ardha
    global prevdashatiSukta
    global prevardha
    global bookName
    stopPageFooter(row)
    printFile("verses/"+ getTitle(row), target)
    prevdashatiSukta = dashatiSukta
    prevardha = ardha
    # targetTransliterated.clear()
    # target.append("{{-start-}}\n")
    # appendPageLists()
    # target.append (startPageHeader('Page',  getTitle(row)))
    # targetTransliterated.append('{{ScriptureTransliterateSource500|\n')  # start code for transliteration


def main(argv):
    global GOOGLE_SHEETS_FILE_ID
    global prevardha
    global prevdashatiSukta
    global ardha
    global dashatiSukta
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
        df.insert(0,'dashatiSukta','')
        df.insert(0,'ardha','')
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
    makeLists(wks)   # prepare the index tables for ardha pages and ardhas, if any.

    prevdashatiSukta=''
    prevardha=''
    dashatiSukta=''
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
        prevdashatiSukta = dashatiSukta
        #prevardha = ardha
        target.append("{{-start-}}\n")
        target.append("__NOTOC__\n")

        nxtVerseNo=prevVerseNo=None
        #verseNo = row[verseNumberCol]
        verseNo = row[0]
        #ardha=verseNo.rsplit('.', 2)[0]
        if prev is not None:
            prevVerseNo=prev[verseNumberCol]
        if nxt is not None:
            nxtVerseNo =nxt[verseNumberCol]

        RigVedaVerseNumber = row[RigVedCol]
        RigVedaVerseNumber = transliterate.process('autodetect', 'IAST', RigVedaVerseNumber, nativize = False)
        RigVedaVerseNumber = RigVedaVerseNumber.replace('.0', '.')
        RigVedaVerseNumber = RigVedaVerseNumber.replace('.0', '.')
        RigVedaVerseNumber = '[ [[RigVeda ' + RigVedaVerseNumber.lstrip('0') + ']] ]' if (RigVedaVerseNumber != 'nan') else ''

        if prevVerseNo is not None and prevVerseNo != "Verse Number":
            target.append("<div style='text-align: left;float:left;width:33%;'>[["+getTitle(prev)+"|←Previous]]</div>\n")
        else:    
            target.append("<div style='text-align: left;float:left;width:33%;'>"+verseNumber+"</div>\n")
        target.append("<div style='text-align: center;float:left;width:33%;'>'''" + getTitle(row) + "''' " + RigVedaVerseNumber + "</div>\n")
        if nxtVerseNo is not None:
            target.append("<div style='text-align: right;float:left;width:33%;'>[["+getTitle(nxt)+"|Next→]]</div>\n")
        target.append("\n")

        getardhadashatiSuktaVerse(verseNumber)        
        target.append(startPageHeader('Page', getTitle(row)))
        appendPageLists(row)
        VedaMantra.append(startPageHeader('VedaMantra', ''))
        VedaPadaPath.append(startPageHeader('VedaPadaPath', ''))
        VedaMantraSwaraRohit.append(startPageHeader('VedaMantraSwaraRohit', ''))
        VedaPadaPathSwaraRohit.append(startPageHeader('VedaPadaPathSwaraRohit', ''))
        VedaSanskritCommentary.append(startPageHeader('VedaSanskritCommentary', ''))
        VedaHindiCommentary.append(startPageHeader('VedaHindiCommentary', ''))
        VedaMeta.append(startPageHeader('VedaMeta', ''))
        # if (dashatiSukta != prevdashatiSukta):
        #     startNewPage(row)
        
        # वेद मन्त्र स्वर सहित
        temp = str(row[VedaMantraCol]).replace('।', '।\n') 
        lines = re.split("\n+", temp)       # ignore empty lines
        linesRead=0                 # no of lines of text witin the given cell
        linesToRead= len(lines)     # no of lines of text witin the given cell
        for e in lines:
            e='{{ns}}' + e.lstrip().rstrip()   #strip all leading and and traling white space

            if (e.find('॥') != -1):   # append verse number and create a new <span id=x > for transliteration.
                e +=  "॥" + f'|\n' #----\n' 
            elif (e.find('||') != -1):
                e = e.replace ("||", "{{!}}{{!}}")
                e +=  "{{!}}{{!}}" + f'|\n' #----\n'
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
                # e += verseNo + "॥" + f'|\n' #----\n' 
                e +=  "॥" + f'|\n' #----\n' # verseno is already present in these slokas
            elif (e.find('||') != -1):
                e = e.replace ("||", "{{!}}{{!}}")
                # e += verseNo + "{{!}}{{!}}" + f'|\n' #----\n'
                e += "{{!}}{{!}}" + f'|\n' #----\n'    # verseno is already present in these slokas
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
        prevardha = newCsvPage
        newCsvPage += 1
    debug()


if __name__ == "__main__":
   main(sys.argv[1:])