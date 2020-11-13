import pygsheets
import pandas as pd
from os import path, devnull, remove
from aksharamukha import transliterate
import time

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


chapterList=[]
chapterVerseList=[]
verseList=[]
verseTable=[]
chapterTable=[]
verseTableList=[]
cellText=[]
navbox=[]
titleRow=[]

def makeNavbox(row):
    global navbox
    global titleRow
    #titleRow=wks[0]
    count=0
    chapterList=[]
    chapterVerseList=[]
    verseList=[]
    verseTable=[]
    chapterTable=[]
    verseTableList=[]
    
    navboxTag='{{Navbox\n| name = Explanations\n| image = \n| title = Explanations\n| navbar = off| state = {{{state|expanded}}}\n| bodyclass = hlist\n| style = font-size:95%\n'
    group1Tag='| group1 = English translation\n| list1  =\n'
    group2Tag='| group2 = Hindi translation\n| list2  =\n'
    group3Tag='| group3 = English Commentary\n| list3  =\n'
    group4Tag='| group4 = Hindi Commentary\n| list4  =\n'
    group5Tag='| group5 = Sanskrit Commentary\n| list5  =\n'
    group6Tag='| group6 = English translation\n| list6  =\n'
    belowTag='{{ScriptureReferences}}'
    endTag='}}\n'

    navbox = []
    navbox.append (navboxTag)
    navbox.append (group1Tag)
    navbox.append (cellText[4])  #Column E
    navbox.append (cellText[8])  #I
    navbox.append (cellText[9])  #J
    navbox.append (cellText[10]) #K
    navbox.append (cellText[11]) #L
    navbox.append (cellText[12]) #M

    navbox.append (group2Tag)
    navbox.append (cellText[5])  #F
    navbox.append (cellText[6])  #G

    navbox.append (group3Tag)
    navbox.append (cellText[7])  #H

    navbox.append (group4Tag)
    navbox.append (cellText[16]) #Q
    navbox.append (cellText[24]) #Y

    navbox.append (group5Tag)
    navbox.append (cellText[17]) #R
    navbox.append (cellText[18]) #S
    navbox.append (cellText[19]) #T
    navbox.append (cellText[20]) #U
    navbox.append (cellText[21]) #V
    navbox.append (cellText[22]) #W
    navbox.append (cellText[23]) #X
    navbox.append (cellText[25]) #Z
    navbox.append (cellText[26]) #AA
    navbox.append (cellText[27]) #AB
    navbox.append (cellText[28]) #AC
    navbox.append (cellText[29]) #AD
    navbox.append (cellText[30]) #AE

    navbox.append (group6Tag)
    navbox.append (cellText[13]) #N
    navbox.append (cellText[14]) #O
    navbox.append (cellText[15]) #P
    navbox.append (belowTag)   
    navbox.append (endTag) 


def makeLists(wks):
        global chapterList
        global chapterVerseList
        global verseList
        global verseTable
        global chapterTable
        global verseTableList

        header=True
        for row in wks:
            #Skip the Header row
            if header:
                header=False
                continue
            verseNo = row[0]
            parts=verseNo.rsplit('.', 1)
            chapter=parts[0]
            verse=''
            if (len(parts)>1 ):
                verse=parts[1]
            if ( not chapterList):
                chapterList.append("'''Chapters'''")
                chapterList.append( "[[Gita Verse "+verseNo+"|"+chapter+"]]") # first time
            if ( chapter+"]]" != chapterList[-1].rsplit('|',1)[1]): # if current chapter is not the same as the last item in chapterList
                chapterList.append("[[Gita Verse "+verseNo+"|"+chapter+"]]") 
                if  verseList:
                    chapterVerseList.append(verseList) # append only if the list is not  empty 
                #verseList=[ "[[Gita Verse "+verseNo+"|"+verseNo+"]]"] # start a new list
                verseList=[ "[[Gita Verse "+verseNo+"|"+"'''Chapter "+chapter+" verses''']]", "[[Gita Verse "+verseNo+"|"+verseNo+"]]"] # start a new list
            else:
                if (not verseList):
                        verseList=[ "[[Gita Verse "+verseNo+"|"+"'''Chapter "+chapter+" verses''']]"] # start a new list
                verseList.append("[[Gita Verse "+verseNo+"|"+verseNo+"]]")
        if  verseList:
            chapterVerseList.append(verseList) # append only if the list is not  empty 
        #print (chapterList)
        #print ("\n")
        #for ch in chapterVerseList:
        #        print (ch)

        for ch in range (len(chapterList)-1):
            verseTable.append ('<div class="siva_table4">\n{| style=" border:1px solid #BBB;margin:.66em 0 0 .2em; width:100%"\n')
            verseTable.append ('|- style="font-size:99%;"   class="siva_table4"\n')
            verseTable.append("|+ ")
            verseList=chapterVerseList[ch]
            for v in range(len(verseList)):
                if ((v-1)%5 == 0):
                    #verseTable.append ("\n|-\n| ")
                    verseTable.append ("||\n| ")
                elif (v != 0):
                    verseTable.append(" || ")
                verseTable.append (verseList[v])
            verseTable.append("\n|}\n</div>\n")
            verseTableList.append(verseTable)
            verseTable=[]

        chapterTable.append ('<div class="siva_table4">\n{| style=" border:1px solid #BBB;margin:.66em 0 0 .2em; width:100%"\n')
        chapterTable.append ('|- style="font-size:99%;"   class="siva_table4"\n')
        chapterTable.append("|+ ")
        for ch in range (len(chapterList)):
            #for v in range(len(chapterList[ch])+1):
            if ( (ch-1)%6 == 0):
                #chapterTable.append ("\n|-\n| ")
                chapterTable.append ("||\n| ")
            elif (ch != 0):
                chapterTable.append(" || ")
            chapterTable.append (chapterList[ch])
        chapterTable.append("\n|}\n</div>\n")
        #for verseTable in verseTableList:
        #    printFile("out1", verseTable)
        #printFile("out2", chapterTable)


def cellSection(row):
    global cellText
    toggleTag='* <p class="mw-collapsible mw-collapsed"  style="background:#faf6ed"  data-expandtext="'
    collapseTag='"  data-collapsetext="'
    #collapseTail='" class=" mw-collapsible mw-collapsed"><p  style="color:#0080ff">'
    bold="'''"
    collapseTail='"> '
    belowTag='| below = {{ScriptureReferences}}'
    endTag='</p>\n'
    cellText=[]
    for col in range(0,4): 
        cellText.append('')
    for col in range(4,31): 
        # Assign the {{anchor}} ↓
        #target.append('{{anchor|'+titleRow[col]+'}}')
        id=row[0]+str(col)
        linkName=titleRow[col].strip('"')
        title=bold+linkName+bold
        #lineText = (toggleTag + linkName + '▼' + collapseTag + linkName + '▲' + collapseTail)
        lineText = (toggleTag + linkName + '↓' + collapseTag + linkName + '↑' + collapseTail)
        new = str(row[col]).splitlines()
        linesToRead=0  # no of lines of text witin the given cell
        for e in new:
            linesToRead= len(new)
            #for line in range(0,linesToRead):
            lineText += e + '<br>'
                #cellText.append(e + '<br />')
        cellText.append(lineText + endTag)



#GOOGLE_SHEETS_FILE_ID = '1b069ciDNVbrx-UD3KYjxMNQ6YeJoJW6yygH5yQPMmig'
#GOOGLE_SHEETS_FILE_ID = '1eDXV4G6i479i4RFZClC6WGNlj0xj2CKGxR06QW5nysI'
GOOGLE_SHEETS_FILE_ID = '11X4F4nz58ryj0GMVrdrglQ3u4QTo7ogR7uEaewfrDKM'
google_client = pygsheets.authorize()
spreadsheet = google_client.open_by_key(GOOGLE_SHEETS_FILE_ID)
wks_list = spreadsheet.worksheets()
dirname = path.dirname(__file__)
wks=wks_list[0]
#headers = wks.get_row(1, include_tailing_empty=False)
count=0
chapterList=[]
chapterVerseList=[]
verseList=[]
verseTable=[]
chapterTable=[]
verseTableList=[]
makeLists(wks)

Source = open ("SampleMediaWiki").readlines()
target = []
MAX_LINES_PER_VERSE=20
MAX_COLS_TO_READ=3
htmBlocks=[1,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48, 
			55,57,59,61,63,65,67,69,71,73,75,77,79,81,83,85,87,89,91,93,95,
            102,104,106,108,110,112,114,116,118,120,122,124,126,128,130,132,134,136,138,140,142,144]
#wks=wks_list[0]
#makeLists(wks)
#headers = wks.get_row(1, include_tailing_empty=False)
rowCount=0
header=True
slokaCol=1

# get the prev, current and next rows to create the links to prev and next slokas
#### implement >>> l = [None, *l, None] and then for prev, cur, nxt in zip(l, l[1:], l[2:]):
wks = [None, *wks, None] 
for prev, row, nxt in zip(wks, wks[1:], wks[2:]):
#for row in wks:
    #Skip the Header row
    if header:
        header=False
        titleRow=row
        continue
    htmIndex=0
    if debug():
        print ("Gita Verse No: ", row[0] )
    nxtVerseNo=prevVerseNo=None
    verseNo = row[0]
    chapter=verseNo.rsplit('.', 1)[0]
    if prev is not None:
        prevVerseNo=prev[0]
    if nxt is not None:
        nxtVerseNo =nxt[0]
    startBlock = htmBlocks[htmIndex]-1
    endBlock = htmBlocks[htmIndex+1]-1  
    colCount=0

        # insert the uplader tags for eachpage of a sloka >>>>>
        # {{-start-}}
        # <div style='text-align: left;float:left;width:33%;'> [[Gita 3.1|Previous]]</div>
        # <div style='text-align: center;float:left;width:33%;'>'''Gita 3.2'''</div>
        # <div style='text-align: right;float:left;width:33%;'>[[Gita 3.3|Next]]</div>
        # target.append()
    target.append("{{-start-}}\n")
    if prevVerseNo is not None and prevVerseNo != "Verse Number":
        target.append("<div style='text-align: left;float:left;width:33%;'>[["+"Gita Verse "+prevVerseNo+"|←Previous]]</div>\n")
    else:    
        target.append("<div style='text-align: left;float:left;width:33%;'>"+verseNo+"</div>\n")
    target.append("<div style='text-align: center;float:left;width:33%;'>'''"+"Gita Verse "+verseNo+"'''</div>\n")
    if nxtVerseNo is not None:
        target.append("<div style='text-align: right;float:left;width:33%;'>[["+"Gita Verse "+nxtVerseNo+"|Next→]]</div>\n")
    target.append("\n")

    target.append('<div class="siva_container">\n')
    target.append(chapterTable)
    target.append(verseTableList[int(chapter)-1])
    target.append('</div>\n')
    target.append ('{{#widget:LanguageSelectorWidgetNew|textDiv=sloka|displayDiv=transliteration}}\n' )
    for col in range(1,MAX_COLS_TO_READ+1): # Need to process only columns B,C and D for now.
        if debug():
            print (startBlock+1,endBlock, " Starting lines to be appended")
        for n in range (startBlock,endBlock):
            if debug():
                print (n+1, "Appending starting headers")
            target.append(Source[n])   
        startBlock=endBlock
        htmIndex += 1
        endBlock = htmBlocks[htmIndex+1]-1
        # extract the sloka lines  # new = str(row[1]).splitlines(keepends=True)
        new = str(row[col]).splitlines()  
        linesRead=0  # no of lines of text witin the given cell
        linesToRead=0  # no of lines of text witin the given cell
        for e in new:
            linesToRead= len(new)
            if debug():
                print( "line ", htmIndex, e)
            # Replace the tag only once in the given source row and append that row to target
            if linesRead < linesToRead-1:
                #target.append(str(Source[startBlock]).replace("A1A2A3A4A5A6A7A8", e,1))
                if colCount == slokaCol:  # get the Sanskrit sloka transliterated
                    #newText = transliterate.process('autodetect', 'HK', e , nativize = False)
                    newText = transliterate.process('autodetect', 'IAST', e , nativize = False)
                else:
                     newText = e
                target.append(str(Source[startBlock]).replace("A1A2A3A4A5A6A7A8", newText,1))
                for n in range (startBlock+1,endBlock): #append the remaining rows in this block to target
                    target.append(str(Source[n]))
            if debug():
                print (startBlock+1, endBlock, " Appended. ")
            startBlock=endBlock
            htmIndex += 1
            endBlock = htmBlocks[htmIndex+1]-1
            linesRead += 1
        htmIndex = htmIndex+(MAX_LINES_PER_VERSE-linesRead)-1 # update htmIndex and endBlock
        endBlock = htmBlocks[htmIndex]-1
        # skip (MAX_LINES_PER_VERSE-linesRead)-1 no of blocks
        if debug():
            print (startBlock+1,endBlock," To be ignored")
        for n in range (startBlock,endBlock):
            n += 1
            if debug():
               print (n+1, "Ingnoring")
        # Append the last block after adding the verse number
        startBlock=endBlock
        endBlock = htmBlocks[htmIndex+1]-1
        # target.append(str(Source[startBlock]).replace("A1A2A3A4A5A6A7A8", e,1))
        # if the last two character are ||, strip them

        if colCount == slokaCol:  # get the Sanskrit sloka transliterated
            newText = transliterate.process('autodetect', 'HK', e , nativize = False)
        else:
             newText = e
        lastVerse = (str(Source[startBlock]).replace("A1A2A3A4A5A6A7A8", newText,1).rstrip())
        parts=lastVerse.rsplit(' ', 1)
        if (len(parts)>1 and parts[1] == "||"):
            lastVerse=parts[0]
        #lastVerse = (str(Source[startBlock]).replace("A1A2A3A4A5A6A7A8", e,1).rstrip())
        # append <nowiki>||1.1||</nowiki>
        lastVerse = lastVerse + " <nowiki>||" + verseNo +"||</nowiki>\n"
        target.append(lastVerse)
        for n in range (startBlock+1,endBlock): #append the remaining rows in this block to target
            target.append(str(Source[n]))
        htmIndex += 1
        startBlock=endBlock
        endBlock = htmBlocks[htmIndex+1]-1
        colCount += 1
    if debug():
        print (startBlock+1, endBlock, " To be appended")
    for n in range (startBlock, endBlock):
        if debug():
            print (n+1, "Appending")
        target.append(Source[n])
    
    cellSection(row)
    makeNavbox(row) # prepare the navbox wth the header row
    target.append(navbox)
        
    # appnd the uploader tag to stop    
    target.append("{{-stop-}}")
    rowCount += 1
    #if debug():
    print (rowCount, verseNo, "-------------------------------------------")
        #print (target)
    printFile("verses/GitaVerse-"+verseNo, target)
    #time.sleep(5)
    #print ("Verse No: ", verseNo)
    target.clear()
    #quit()


