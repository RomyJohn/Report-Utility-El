import os, sys, shutil, fitz, cv2, pdfkit, PyPDF2, numpy, io
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from bs4 import BeautifulSoup
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from video import *

def cleanTempFolder(tempFolderPath, condition):
    try:
        if(condition):
            print(f'Cleaning {tempFolderPath}')
        tempFolderPathFolders = os.listdir(tempFolderPath)
        for folders in tempFolderPathFolders:
            foldersPath = os.path.join(tempFolderPath, folders)
            shutil.rmtree(foldersPath, ignore_errors=False)
    except:
        print(f'Failed in cleaning {tempFolderPath}')

def createFoldersInTempFolder(tempFolderPath):
    try:
        print(f'Creating folders in {tempFolderPath}')
        #For Report
        os.makedirs(fr'{tempFolderPath}\croppedImages')
        os.makedirs(fr'{tempFolderPath}\extractedImages')
        os.makedirs(fr'{tempFolderPath}\extractedObject')
        os.makedirs(fr'{tempFolderPath}\generatedHTML')
        os.makedirs(fr'{tempFolderPath}\generatedPDF')
        os.makedirs(fr'{tempFolderPath}\splitPDF')

        #For Video
        os.makedirs(fr'{tempFolderPath}\addBackgroundVideo')
        os.makedirs(fr'{tempFolderPath}\croppedVideos')
        os.makedirs(fr'{tempFolderPath}\generatedVideo')
        os.makedirs(fr'{tempFolderPath}\iprImages')
        os.makedirs(fr'{tempFolderPath}\resizedVideos')
        os.makedirs(fr'{tempFolderPath}\videoProgressBar')
    except:
        print(f'Failed in creating folders in {tempFolderPath}')

def extractImages(orthoReport, tempFolderPath):
    try:
        print(f'Extracting images in {tempFolderPath}\extractedImages')
        openOrthoReport = fitz.open(orthoReport)
        for files in range(9):
            image_list = openOrthoReport.get_page_images(files)
            for image in image_list:
                xref = image[0]
                pix = fitz.Pixmap(openOrthoReport, xref)
                pix.save(fr'{tempFolderPath}\extractedImages\Image{xref}.png')
    except:
        print(f'Failed to extract images in {tempFolderPath}\extractedImages')
    finally:
        openOrthoReport.close()

def cropImages(imgList, tempFolderPath):
    try:
        print(f'Cropping images in {tempFolderPath}\croppedImages')
        count = 0
        for i in imgList:
            imgSrcPath = fr'{tempFolderPath}\extractedImages\Image{i}.png'
            imgDstPath = fr'{tempFolderPath}\croppedImages\Image{i}.png'
            cropImage = cv2.imread(imgSrcPath)
            y = 0
            x = 300
            h = 830
            w = 1000
            crop = cropImage[y:y+h, x:x+w]
            cv2.imwrite(imgDstPath, crop)
            image = cv2.imread(imgDstPath)
            original = image.copy()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            canny = cv2.Canny(blurred, 120, 255, 1)
            kernel = numpy.ones((5, 5), numpy.uint8)
            dilate = cv2.dilate(canny, kernel, iterations=1)
            cnts = cv2.findContours(
                dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            for items in cnts:
                x, y, w, h = cv2.boundingRect(items)
                cv2.rectangle(image, (x, y), (x + w, y + h), (36, 255, 12), 2)
                ROI = original[y:y+h, x:x+w]
                cv2.imwrite(fr"{tempFolderPath}\extractedObject\Image{count}.png", ROI)
            count = count+1
    except:
        print(f'Failed to crop images in {tempFolderPath}\extractedImages')

def extractText(orthoReport):
    try:
        text = []
        openOrthoReport = fitz.open(orthoReport)
        textReader = openOrthoReport.load_page(0).get_text()
        text = list(textReader.split("\n"))
        return text
    except:
        print(f'Failed to extract text from {orthoReport}')
    finally:
        openOrthoReport.close()

def getHTMLContent(orthoReportHTML, id):
    try:
        HTMLFileToBeOpened = open(orthoReportHTML, 'r')
        content = HTMLFileToBeOpened.read()
        beautifulSoupText = BeautifulSoup(content, 'lxml')
        content = beautifulSoupText.find('div', attrs={'id': id})
        return content
    except:
        print(f'Failed to extract HTML content from {orthoReportHTML}')
    finally:
        HTMLFileToBeOpened.close()

def generateHTML(tempFolderPath, htmlContent):
    try:
        print(f'Generating HTML file in {tempFolderPath}\generatedHTML')
        generateHTMLFile = open(fr'{tempFolderPath}\generatedHTML\Report.html', 'w')
        generateHTMLFile.write(htmlContent)
    except:
        print(f'Failed to generate HTML file in {tempFolderPath}\generatedHTML')
    finally:
        generateHTMLFile.close()

def convertHtmlToPdf(tempFolderPath):
    try:
        print(f'Converting HTML to PDF file')
        htmlPath = fr'{tempFolderPath}\generatedHTML\Report.html'
        pdfPath = fr'{tempFolderPath}\generatedPDF\OrthoReport.pdf'
        pdfkit.from_file(htmlPath, pdfPath.replace(chr(92), '/'))
    except:
        print(f'Failed to convert HTML to PDF file ')

def splitPDF(tempFolderPath):
    try:
        openGeneratedReport = open(fr'{tempFolderPath}\generatedPDF\OrthoReport.pdf', 'rb')
        generatedReportReader = PyPDF2.PdfFileReader(openGeneratedReport, strict=False)
        for page in range(generatedReportReader.numPages):
            writer = PyPDF2.PdfFileWriter()
            writer.addPage(generatedReportReader.getPage(page))
            with open(fr'{tempFolderPath}\splitPDF\OrthoReport{page}.pdf', 'wb') as outputStream:
                writer.write(outputStream)
    except:
        print(f'Failed to split PDF')
    finally:
        openGeneratedReport.close()

def editPDF(tempFolderPath, tpr, ipr, pid, name, operator, clinicId, wisealignClinic):
    try:
        pdf1 = fr'{tempFolderPath}\splitPDF\OrthoReport0.pdf'
        pdf2 = tpr
        pdf3 = fr'{tempFolderPath}\splitPDF\OrthoReport1.pdf'
        pdf4 = fr'{tempFolderPath}\splitPDF\OrthoReport2.pdf'
        pdf5 = fr'{tempFolderPath}\splitPDF\OrthoReport3.pdf'
        pdf6 = fr'{tempFolderPath}\splitPDF\OrthoReport4.pdf'
        pdf7 = ipr
        pdf8 = fr'{tempFolderPath}\splitPDF\OrthoReport5.pdf'
        pdfFilesList = [pdf1, pdf2, pdf3, pdf4, pdf5, pdf6, pdf7, pdf8]
        count = 0
        clinicType = int(pid[6])
        for item in pdfFilesList:
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            if(wisealignClinic!='79' or (logoRequired=='N' or logoRequired=='n')):
                logo = os.path.join(sys.path[0], fr'Resources\Images\logo.png')
                banner = os.path.join(sys.path[0], fr'Resources\Images\banner.png')
                smile = os.path.join(sys.path[0], fr'Resources\Images\smile.jpg')
                circle = os.path.join(sys.path[0], fr'Resources\Images\circle.png')
                apollo_logo = os.path.join(sys.path[0], fr'Resources\Images\apollo.png')
                lms_logo = os.path.join(sys.path[0], fr'Resources\Images\lms.png')
                if(item == pdf7):
                    can.drawImage(banner, 31.7, 761.2, 290.8, 59.5, mask='auto')
                    if(clinicType != 5 and clinicType != 2 and (logoRequired=='Y' or logoRequired=='y')):
                        can.drawImage(logo, 32, 761.5, 78, 58, preserveAspectRatio=True, mask='auto')
                    elif(clinicType == 5 and (logoRequired=='Y' or logoRequired=='y')):
                        can.drawImage(lms_logo, 32, 761.5, 78, 58, preserveAspectRatio=True, mask='auto')
                    elif(clinicType == 2 and (logoRequired=='Y' or logoRequired=='y')):
                        can.drawImage(apollo_logo, 32, 761.5, 78, 58, preserveAspectRatio=True, mask='auto')
                else:
                    can.drawImage(banner, 0, 762, 400, 80, mask='auto')
                    if(clinicType != 5 and clinicType != 2 and (logoRequired=='Y' or logoRequired=='y')):
                        can.drawImage(logo, 0, 762, 110, 80, preserveAspectRatio=True, mask='auto')
                    elif(clinicType == 5 and (logoRequired=='Y' or logoRequired=='y')):
                        can.drawImage(lms_logo, 0, 762, 110, 80, preserveAspectRatio=True, mask='auto')
                    elif(clinicType == 2 and (logoRequired=='Y' or logoRequired=='y')):
                        can.drawImage(apollo_logo, 0, 762, 110, 80, preserveAspectRatio=True, mask='auto')
                can.drawImage(banner, 0, 0, 550, 30, mask='auto')
                can.drawImage(circle, 6, 5, 20, 20, preserveAspectRatio=True, mask='auto')
                can.drawImage(smile, 550, 0, 45, 45, preserveAspectRatio=True, mask='auto')
                pdfmetrics.registerFont(TTFont('MuseoSansRounded', os.path.join(sys.path[0], fr'Resources\Fonts\MuseoSansRounded.ttf')))
                can.setFillColor(HexColor('#FFFFFF'))
                if(clinicType != 5 and clinicType != 2 and (logoRequired=='Y' or logoRequired=='y')):
                    can.setFont('MuseoSansRounded', 14)
                    can.drawString(100, 10, 'www.32watts.com | info@32watts.com | +91-9-560-570-580')
                elif(clinicType == 2 and (logoRequired=='Y' or logoRequired=='y')):
                    can.setFont('MuseoSansRounded', 14)
                    can.drawString(130, 10, 'www.apollo247.com | alignercare@apollo247.org')
                can.setFont('MuseoSansRounded', 10)
                can.setFillColor(HexColor('#F58320'))
                if(item == pdf1):
                    can.drawString(404, 806, 'Treating Doctor:')
                    can.drawString(404, 790, 'Clinic:')
                    can.setFillColor(HexColor('#000000'))
                    can.drawString(482, 806, operator)
                    can.drawString(435, 790, clinicId)                
                elif(item == pdf7):
                    pass
                else:
                    can.drawString(404, 822, 'Patient Name:')
                    can.drawString(404, 806, 'Treating Doctor:')
                    can.drawString(404, 790, 'Clinic:')
                    can.drawString(404, 774, 'Case ID:')
                    can.setFillColor(HexColor('#000000'))
                    can.drawString(471, 822, name)
                    can.drawString(482, 806, operator)
                    can.drawString(435, 790, clinicId)
                    can.drawString(444, 774, pid)
                can.setFont('MuseoSansRounded', 20)
                can.setFillColor(HexColor('#FFFFFF'))
                if(item == pdf1):
                    can.drawString(150, 795, 'Smile Assessment')
                if(item == pdf2):
                    can.drawString(175, 805, 'Treatment')
                    can.drawString(150, 785, 'Planning Report')
                if(item == pdf3 or item == pdf4):
                    can.drawString(150, 795, 'Overview Report')
                if(item == pdf5 or item == pdf6):
                    can.drawString(177, 815, 'Comparison of')
                    can.drawString(150, 795, 'Pre & Post Treatment')
                    can.drawString(215, 775, 'Views')
                if(item == pdf7):
                    can.drawString(150, 785, 'IPR Sheet')
                    can.setFont('MuseoSansRounded', 10)
                    can.setFillColor(HexColor('#000000'))
                    can.drawString(38, 828, 'ANNEXURE-2')
                if(item == pdf8):
                    can.drawString(200, 805, 'Tooth')
                    can.drawString(150, 785, 'Movement Report')
                can.setFont('MuseoSansRounded', 12)
                can.setFillColor(HexColor('#000000'))
                if(item == pdf1):
                    can.drawString(12, 10, '1')
                if(item == pdf2):
                    can.drawString(12, 10, '2')
                if(item == pdf3):
                    can.drawString(12, 10, '3')
                if(item == pdf4):
                    can.drawString(12, 10, '4')
                if(item == pdf5):
                    can.drawString(12, 10, '5')
                if(item == pdf6):
                    can.drawString(12, 10, '6')
                if(item == pdf7):
                    can.drawString(12, 10, '7')
                if(item == pdf8):
                    can.drawString(12, 10, '8')
            else:
                layout1 = os.path.join(sys.path[0], fr'Resources\Images\wisealign_layout.png')
                can.drawImage(layout1, 0, 0, 600, 845, mask='auto')
                layout2 = os.path.join(sys.path[0], fr'Resources\Images\wisealign_layout1.png')
                pdfmetrics.registerFont(TTFont('MuseoSansRounded', os.path.join(sys.path[0], fr'Resources\Fonts\MuseoSansRounded.ttf')))
                can.setFillColor(HexColor('#FFFFFF'))
                can.setFont('MuseoSansRounded', 20)
                if(item == pdf1):
                    can.drawString(80, 805, 'Digital Smile Correction')
                if(item == pdf2):
                    can.drawString(80, 805, 'Treatment Report')
                if(item == pdf5 or item == pdf6):
                    can.drawString(80, 805, 'Comparison - Views')
                if(item == pdf7):
                    can.drawImage(layout2, 0, 0, 600, 845, mask='auto')
                    can.drawString(80, 805, 'IPR Sheet')
            can.save()
            packet.seek(count)
            new_pdf = PyPDF2.PdfFileReader(packet, strict=False)
            seperatedOrthoReport = open(item, 'rb')
            existing_pdf = PyPDF2.PdfFileReader(seperatedOrthoReport, strict=False)
            writer = PyPDF2.PdfFileWriter()
            page = existing_pdf.getPage(0)
            page2 = new_pdf.getPage(0)
            page.mergePage(page2)
            writer.addPage(page)
            with open(fr'{tempFolderPath}\splitPDF\OrthoReports{count}.pdf', 'wb') as outputStream:
                writer.write(outputStream)
            count = count + 1
            seperatedOrthoReport.close()
    except:
        print(f'Failed to edit PDF')

def mergePDFs(tempFolderPath, caseName, finalReportPath, wisealignClinic):
    try:
        print(f'Merging PDFs')
        mergePDF = PyPDF2.PdfFileMerger(strict=False)
        pdf1 = fr'{tempFolderPath}\splitPDF\OrthoReports0.pdf'
        pdf2 = fr'{tempFolderPath}\splitPDF\OrthoReports1.pdf'
        pdf3 = fr'{tempFolderPath}\splitPDF\OrthoReports2.pdf'
        pdf4 = fr'{tempFolderPath}\splitPDF\OrthoReports3.pdf'
        pdf5 = fr'{tempFolderPath}\splitPDF\OrthoReports4.pdf'
        pdf6 = fr'{tempFolderPath}\splitPDF\OrthoReports5.pdf'
        pdf7 = fr'{tempFolderPath}\splitPDF\OrthoReports6.pdf'
        pdf8 = fr'{tempFolderPath}\splitPDF\OrthoReports7.pdf'
        if(wisealignClinic=='79' and (logoRequired=='Y' or logoRequired=='y')):
            pdfFiles = [pdf1, pdf2, pdf5, pdf6, pdf7]
        else:
            pdfFiles = [pdf1, pdf2, pdf3, pdf4, pdf5, pdf6, pdf7, pdf8]
        for files in pdfFiles:
            pdfReader = PyPDF2.PdfFileReader(files, 'rb')
            mergePDF.append(pdfReader)
        path = os.path.join(fr'{finalReportPath}', fr'{caseName}-{pid}')
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=False)
            os.makedirs(fr'{finalReportPath}\{caseName}-{pid}')
        else:
            os.makedirs(fr'{finalReportPath}\{caseName}-{pid}')
        mergePDF.write(fr'{finalReportPath}\{caseName}-{pid}\{caseName}-{pid}.pdf')      
    except:
        print(f'Failed to merge PDFs')
    finally:
        mergePDF.close()

print(f'Starting Report Utility')

logoRequired = input('Do you want to add logo ? [y/n] : ')

while(True):
    if(logoRequired=='Y' or logoRequired=='N' or logoRequired=='y' or logoRequired=='n'):
        break
    else:
       logoRequired = input('Do you want to add logo ? [y/n] : ') 

sourceFolderPath = os.path.join(sys.path[0], fr'sourceFolder')
tempFolderPath = os.path.join(sys.path[0], fr'tempFolder')
finalReportPath = os.path.join(sys.path[0], fr'finalReport')

caseName = ''
orthoReport = ''
ipr = ''
tpr = ''

sourceFolderTotalDir = 0

for base, dirs, files in os.walk(sourceFolderPath):
    for directories in dirs:
        if(directories.startswith('Videos')==False):
            sourceFolderTotalDir += 1

cases=[]

for files in os.listdir(sourceFolderPath):
    cases.append(os.path.join(sourceFolderPath, files))

for caseNumber in range(0,sourceFolderTotalDir):
    caseName=os.path.basename(cases[caseNumber])
    print(f'\nGenerating report of {caseName}')
    if os.path.isdir(cases[caseNumber]):
        orthoReport = cases[caseNumber]+"\OrthoReport.pdf"
        orthoReportHTML = cases[caseNumber]+"\OrthoReport.html"
        ipr = cases[caseNumber]+"\IPR-1.pdf"
        tpr = cases[caseNumber]+"\TPR-1.pdf"

    cleanTempFolder(tempFolderPath, True)
    createFoldersInTempFolder(tempFolderPath)
    extractImages(orthoReport, tempFolderPath)

    imgList = [31, 32, 37, 38, 43, 44, 49, 50, 55, 56]

    cropImages(imgList, tempFolderPath)

    text = extractText(orthoReport)

    pidIndex = text.index('ID:')
    nameIndex = text.index('Name:')
    clinicIdIndex = text.index('Clinic ID:')
    operatorIndex = text.index('Operator:')

    pid = ''
    name = ''
    clinicId = ''
    operator = ''

    if(text[pidIndex+1] != 'SSN:'):
        pid = text[pidIndex+1]
    if(text[nameIndex+1] != 'Address:'):
        name = text[nameIndex+1]
    if(text[clinicIdIndex+1] != 'CASE'):
        clinicId = text[clinicIdIndex+1]
    if(text[operatorIndex+1] != 'Comment:'):
        operator = text[operatorIndex+1]

    div1 = getHTMLContent(orthoReportHTML, 'ToothWidthAnalysisTable')
    div2 = getHTMLContent(orthoReportHTML, 'SpaceAnalysis')
    div3 = getHTMLContent(orthoReportHTML, 'BoltonAnalysis')
    div4 = getHTMLContent(orthoReportHTML, 'TeethSetupTable')

    char1 = str(int(pid[6]))
    char2 = str(int(pid[7]))
    wisealignClinic = char1+''+char2

    htmlContent = '''<html>
    <head>
        <style>
            @font-face {
                font-family: Gotham;
                src: url(" '''+ os.path.join(sys.path[0], fr'Resources\Fonts\GothamBook.ttf').replace(chr(92), '/') +''' ");
            }
            @font-face {
                font-family: MuseoSansRounded;
                src: url(" '''+ os.path.join(sys.path[0], fr'Resources\Fonts\MuseoSansRounded.ttf').replace(chr(92), '/') +''' ");
            }
            body {
                width: 100%;
                margin: 0px;
                font-family: Gotham;
            }
            .heading{
                font-family: MuseoSansRounded;
            }
            table {
                width: 100%;
                margin-left: 0px;
                margin-right: 0px;
                border-collapse: collapse;
            }
            p.groove {
                border-style: groove;
            }
            ul li::before {
                font-size: 30px;
                color: #007bff;
                font-weight: bold;
                display: inline-block;
            }
            .data {
                font-size: 19px;
                margin-top: 0px;
                margin-bottom: 0px;
            }
            .scannedImagesSection {
                font-size: 18px;
            }
            td {
                padding-top: 10px;
                padding-left: 5px;
                padding-right: 5px;
            }
            .right {
                text-align: right;
            }
            .center {
                text-align: center;
            }
            .orthoImage {
                height: 270px;
                width: 370px;
            }
            .secondPDFSection {
                font-size: 20px;
                text-align: center;
            }
            .child {
                display: inline-block;
                vertical-align: middle;
            }
            .AnalysisTableDiv table {
                border-collapse: collapse;
                border: 1px solid #7090A9;
                border-spacing: 5px;
                text-align: left;
                font-size: 12pt;
                white-space: nowrap;
                margin-top: 20px;
                margin-bottom: 30px;
            }
            .AnalysisTableDiv td {
                border: 1px solid #7090A9;
                padding-left: 5px;
                padding-right: 5px;
            }
            .OrthoLeftDiv {
                margin-top: 20px;
                text-align: left;
            }
            .OrthoCenterCaption {
                margin: auto;
                margin-bottom: 20px;
                margin-top: 10px;
                display: table;
                font-weight: bold;
                font-size: 15pt;
            }
            .SpaceAnalysisBlock {
                width: 48%;
                margin: 5px;
                margin-top: 10px;
            }
            .OrthoValueTable th {
                color: #7090A9;
                border-bottom: 1px solid #7090A9;
                border-collapse: collapse;
                text-align: left;
                font-size: 13pt;
            }
            .SpaceAnalysisBlockInline {
                width: 48%;
                margin: 5px;
                display: inline-block;
                vertical-align: top;
            }
            .SpaceAnalysisBlockInline {
                width: 48%;
                margin: 5px;
                display: inline-block;
                vertical-align: top;
            }
            .OrthoValueTable li {
                color: #7090A9;
            }
            .OrthoPropertyName {
                color: DimGray;
                font-size: 12pt;
                font-weight: normal;
                margin-right: 20px;
                font-weight: bold;
            }
            .OrthoPropertyValue {
                font-weight: normal;
                font-size: 12pt;
            }          
            .BoltonAnalysisBlock {
                width: 48%;
                display: inline-block;
                margin: 5px;
                vertical-align: top;
            }
            .OrthoValueTable {
                width: 95%;
                margin-left: 10px;
                border-spacing: 0;
            }
            .AnalysisTableDiv {
                margin: auto;
                display: table;
            }
            .TeethMovementDiv {
                width: 100%;
                max-width: 100%;
            }
            .TeethMovementDiv table {
                border-collapse: collapse;
                border: 1px solid #7090A9;
                border-spacing: 5px;
                text-align: left;
                font-size: 9pt;
                white-space: nowrap;
                margin-top: 20px;
            }
            .TeethMovementDiv tr:nth-of-type(1) {
                white-space: normal;
            }
            .TeethMovementDiv table caption {
                font-weight: normal;
                text-align: left;
                padding-left: 10px;
            }
            .TeethMovementDiv td {
                border: 1px solid #7090A9;
                padding:5px;
                font-size: 10pt;
            }
            .TeethMovementDiv td:nth-of-type(1) {
                max-width: 50px;
            }
            .TeethMovementDiv td:nth-of-type(n+2) {
                min-width: 30px;
                max-width: 100px;
            }
            .TeethMovementDiv table caption {
                font-weight: bold;
                text-align: left;
                padding-left: 10px;
            }
        </style>
    </head>
    <body>
        <div>
            <br/><br/><br/><br/><br/><br/>'''            
    if(wisealignClinic=='79' and (logoRequired=='Y' or logoRequired=='y')):
        htmlContent = htmlContent+'''<div class='parent'>
                <div class='child'>
                    <p style='font-size:30px;padding-bottom:0px;margin-bottom:0px;' class='heading'>Hello ''' + name + '''</p>
                    <p style='font-size:30px;padding:0px;margin:0px;' class='heading'>Location: ''' + clinicId + '''</p>
                    <p style='font-size:30px;padding-top:0px;margin-top:0px;' class='heading'>Patient ID: ''' + pid + '''</p>
                </div>
                </div>
                <p style='font-size:28px;color:#132B47;line-height:150%;'>Here is your digitally designed smile assessment based upon your specification.</p>'''
    else:
        htmlContent = htmlContent+'''<div class='parent'>
                <div class='child' style='height:50px;width:50px;background-color:#D3D3D3;border-radius:100%;text-align:center;margin-right:6px;'>
                    <p style='font-size:35px;margin-top:4px;' class='heading'>''' + name[0] + '''</p>
                </div>
                <div class='child'>
                    <p style='font-size:40px;color:#F58320;padding-bottom:0px;margin-bottom:0px;' class='heading'>Hello ''' + name + '''</p>
                    <p style='font-size:20px;padding-top:0px;margin-top:0px;' class='heading'>Case ID: ''' + pid + '''</p>
                </div>
                </div>
                <p style='font-size:28px;color:#54BDE3;line-height:150%;'>Get ready for the memorable journey towards your perfect smile!! Your customised treatment plan is ready based on your desire. Let’s explore the digital design of your comprehensive treatment plan.</p>'''
    htmlContent = htmlContent+'''<br/><br/><br/><br/><br/><br/>
            <span class="OrthoCenterCaption">PRE-TREATMENT VIEW</span>
            <br/>
            <table cellpadding='1' cellspacing='1'>
                <tr>
                    <td>
                        <p class='groove center'><img
                                src = "''' + f'{tempFolderPath}\extractedImages\Image7.png' + '''"
                                class='orthoImage' alt='No Image' /></p>
                    </td>
                    <td>
                        <p class='groove center'><img
                                src = "''' + f'{tempFolderPath}\extractedImages\Image9.png' + '''"
                                class='orthoImage' alt='No Image'></p>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p class='groove center'><img
                                src = "''' + f'{tempFolderPath}\extractedImages\Image11.png' + '''"
                                class='orthoImage' alt='No Image'></p>
                    </td>
                    <td>
                        <p class='groove center'><img
                                src = "''' + f'{tempFolderPath}\extractedImages\Image12.png' + '''"
                                class='orthoImage' alt='No Image' /></p>
                    </td>
                </tr>
            </table>
            <br/><br/><br/><br/><br/>
        </div>
        <div>
            <br/><br/><br/><br/><br/><br/>
            <span><b>ANNEXURE-1</b></span>
            <br/>
            <span class='OrthoCenterCaption' id='CaptionToothWidthAnalysis'>Tooth width analysis</span>
            '''+str(div1)+str(div2)+'''
            <br/>
        </div>
        <div>
            <br/><br/><br/><br/><br/><br/><br/><br/>
            '''+str(div3)+'''
            <br/>
        </div>
        <div>
            <br/><br/><br/><br/><br/><br/><br/><br/>
            <table cellpadding='1' cellspacing='1' style='margin-top:-50px;' class='scannedImagesSection'>
                <tr>
                    <td colspan='3'>
                        <p class='secondPDFSection'><b>Front View</b></p>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p class='center'>Pre - Treatment </p>
                    </td>
                    <td>
                        <p class='center'>Post - Treatment</p>
                    </td>
                </tr>
                <tr>  
                    <td class='center'><img src="''' + f'{tempFolderPath}\extractedObject\Image0.png' + '''"
                            class='orthoImage' alt='No Image'></td>
                    <td class='center'><img src="''' + f'{tempFolderPath}\extractedObject\Image5.png' + '''"
                            class='orthoImage' alt='No Image'></td>
                </tr>
            </table>
            <table cellpadding='1' cellspacing='1' class='scannedImagesSection'>
                <tr>
                    <td colspan='3'>
                        <br />
                        <p class='secondPDFSection'><b>Right View</b></p>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p class='center'>Pre - Treatment </p>
                    </td>
                    <td>
                        <p class='center'>Post - Treatment</p>
                    </td>
                </tr>
                <tr>
                    <td class='center'><img src="''' + f'{tempFolderPath}\extractedObject\Image1.png' + '''"
                            class='orthoImage' alt='No Image'></td>
                    <td class='center'><img src="''' + f'{tempFolderPath}\extractedObject\Image6.png' + '''"
                            class='orthoImage' alt='No Image'></td>
                </tr>
            </table>
            <table cellpadding='1' cellspacing='1' class='scannedImagesSection'>
                <tr>
                    <td colspan='3'>
                        <br />
                        <p class='secondPDFSection'><b>Left View</b></p>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p class='center'>Pre - Treatment </p>
                    </td>
                    <td>
                        <p class='center'>Post - Treatment</p>
                    </td>
                </tr>
                <tr>
                    <td class='center'><img src="''' + f'{tempFolderPath}\extractedObject\Image2.png' + '''"
                            class='orthoImage' alt='No Image'></td>
                    <td class='center'><img src="''' + f'{tempFolderPath}\extractedObject\Image7.png' + '''"
                            class='orthoImage' alt='No Image'></td>
                </tr>
            </table>
            <br/>
        </div>
        <div>
            <br/><br/><br/><br/><br/><br/><br/><br/><br/>
            <table cellpadding='1' cellspacing='1' class='scannedImagesSection'>
                <tr>
                    <td colspan='3'>
                        <p class='secondPDFSection'><b>Upper View</b></p>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p class='center'>Pre - Treatment </p>
                    </td>
                    <td>
                        <p class='center'>Post - Treatment</p>
                    </td>
                </tr>
                <tr>
                    <td class='center'><img src="''' + f'{tempFolderPath}\extractedObject\Image3.png' + '''"
                            class='orthoImage' alt='No Image'></td>
                    <td class='center'><img src="''' + f'{tempFolderPath}\extractedObject\Image8.png' + '''"
                            class='orthoImage' alt='No Image'></td>
                </tr>
            </table>
            <table cellpadding='1' cellspacing='1' class='scannedImagesSection'>
                <tr>
                    <td colspan='3'>
                        <br />
                        <p class='secondPDFSection'><b>Lower View</b></p>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p class='center'>Pre - Treatment </p>
                    </td>
                    <td>
                        <p class='center'>Post - Treatment</p>
                    </td>
                </tr>
                <tr>
                    <td class='center'><img src="''' + f'{tempFolderPath}\extractedObject\Image4.png' + '''"
                            class='orthoImage' alt='No Image'></td>
                    <td class='center'><img src="''' + f'{tempFolderPath}\extractedObject\Image9.png' + '''"
                            class='orthoImage' alt='No Image'></td>
                </tr>
            </table>
            <br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
        </div>
        <div>
            <br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
            <span><b>ANNEXURE-3</b></span>
            <span class='OrthoCenterCaption' id='CaptionToothWidthAnalysis'>Teeth Movement Report</span>
            '''+str(div4)+'''
            <br/><br/><br/>'''
    if(int(pid[6]) != 2 or (logoRequired=='N' or logoRequired=='n')):
           htmlContent = htmlContent + '''<p style='font-size:28px;color:#54BDE3;line-height:150%;'>Do reach out to our team if you have any further questions and we’d be happy to have our executives speak to you. Have a great day, and remember, <span style='color:#F58320;'> keep smiling.</span></p>
            <br/>'''
    if(int(pid[6]) == 2 and (logoRequired=='Y' or logoRequired=='y')):
        htmlContent = htmlContent + '''
        <img src="''' + os.path.join(sys.path[0], fr'Resources\Images\apollo_banner.jpg') + '''" class='orthoImage' style='width:100%;' alt='No Image'>
        <p style='font-size:32px;color:#F58320;line-height:150%;text-align:center;'><b>Thank you for choosing Apollo 24|7</b></p>'''
    if(int(pid[6]) != 5 and int(pid[6]) != 2 and (logoRequired=='Y' or logoRequired=='y')):
        htmlContent = htmlContent + '''<p style='font-size:28px;color:#F58320;line-height:150%;margin-bottom:0px;padding-bottom:0px;'>Best Regards <br/> (Team 32Watts)</p>'''
    htmlContent = htmlContent + '''</div>
    </body>
    </html>'''

    generateHTML(tempFolderPath, htmlContent)
    convertHtmlToPdf(tempFolderPath)
    splitPDF(tempFolderPath)
    editPDF(tempFolderPath, tpr, ipr, pid, name, operator, clinicId, wisealignClinic)
    mergePDFs(tempFolderPath, caseName, finalReportPath, wisealignClinic)

    print(f'PDF has been generated successfully in {finalReportPath}\{caseName}-{pid}')

    if(os.path.exists(fr'{sourceFolderPath}\{caseName}\Videos')==True):
        reduceVideoLength(fr'{sourceFolderPath}\{caseName}', tempFolderPath)
        cropVideos(tempFolderPath)
        extractImageFromVideo(tempFolderPath)
        aligners = extractAlignersText(tpr)
        convertPDFToImage(ipr, tempFolderPath)
        cropImage(tempFolderPath)
        createVideoThumbnail(tempFolderPath, caseName, pid, aligners, operator, logoRequired, wisealignClinic)
        createFirstFrameImage(tempFolderPath, aligners)
        imagesToVideo(tempFolderPath, True)
        imagesToVideo(tempFolderPath, False)
        addProgressbarToVideo(tempFolderPath)
        concatVideos(tempFolderPath)
        addBackgroundToVideo(tempFolderPath)
        addTextToVideo(tempFolderPath, finalReportPath, caseName, pid, aligners, logoRequired, wisealignClinic)

        print(f'Video has been generated successfully in {finalReportPath}\{caseName}-{pid}')

cleanTempFolder(tempFolderPath, False)

print(f'\nAll the reports have been generated successfully')





