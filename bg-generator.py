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
            f.write(d)

#GOOGLE_SHEETS_FILE_ID = '1b069ciDNVbrx-UD3KYjxMNQ6YeJoJW6yygH5yQPMmig'
#GOOGLE_SHEETS_FILE_ID = '1eDXV4G6i479i4RFZClC6WGNlj0xj2CKGxR06QW5nysI'
GOOGLE_SHEETS_FILE_ID = '11X4F4nz58ryj0GMVrdrglQ3u4QTo7ogR7uEaewfrDKM'
google_client = pygsheets.authorize()
spreadsheet = google_client.open_by_key(GOOGLE_SHEETS_FILE_ID)
wks_list = spreadsheet.worksheets()
dirname = path.dirname(__file__)

Source = open ("SampleMediaWiki").readlines()
target = []
MAX_LINES_PER_VERSE=20
MAX_COLS_TO_READ=3
htmBlocks=[1,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,  
            56,58,60,62,64,66,68,70,72,74,76,78,80,82,84,86,88,90,92,94,96,
            104,106,108,110,112,114,116,118,120,122,124,126,128,130,132,134,136,138,140,142,144,146]
wks=wks_list[0]
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
        continue
    htmIndex=0
    if debug():
        print ("Gita Verse No: ", row[0] )
    nxtVerseNo=prevVerseNo=None
    verseNo = row[0]
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
        target.append("<div style='text-align: left;float:left;width:50%;'>[["+"Gita Verse "+prevVerseNo+"|Previous]]</div>\n")
    else:    
        target.append("<div style='text-align: left;float:left;width:50%;'>"+verseNo+"</div>\n")
    target.append("<div style='text-align: center;float:left;width:33%;'>'''"+"Gita Verse "+verseNo+"'''</div>\n")
    if nxtVerseNo is not None:
        target.append("<div style='text-align: right;float:left;width:50%;'>[["+"Gita Verse "+nxtVerseNo+"|Next]]</div>\n")

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
                    newText = transliterate.process('autodetect', 'HK', e , nativize = False)
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


