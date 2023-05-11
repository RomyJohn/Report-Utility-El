import os, sys, shutil, fitz, cv2, pdfkit, configparser, PyPDF2, glob, img2pdf, PIL, numpy, io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def loadConfigProperties():
    try:
        filePath = os.path.join(sys.path[0], fr'Resources\config.properties')
        configReader = configparser.ConfigParser()
        configReader.read(filePath)
        return configReader
    except:
        print(f'Failed to load config.properties')

def cleanTempFolder(tempFolderPath):
    try:
        print(f'Cleaning {tempFolderPath}')
        tempFolderPathFolders = os.listdir(tempFolderPath)
        for folders in tempFolderPathFolders:
            foldersPath = os.path.join(tempFolderPath, folders)
            baseFolderName=os.path.basename(foldersPath)
            if(baseFolderName!='formatPDF'):
                shutil.rmtree(foldersPath, ignore_errors=False)
    except:
        print(f'Failed in cleaning {tempFolderPath}')

def createFoldersInTempFolder(tempFolderPath):
    try:
        print(f'Creating folders in {tempFolderPath}')
        path = os.path.join(fr'{tempFolderPath}\formatPDF')
        if os.path.exists(path):
            pass
        else:
            os.makedirs(path)
        os.makedirs(fr'{tempFolderPath}\convertedPDFImages')
        os.makedirs(fr'{tempFolderPath}\croppedImages')
        os.makedirs(fr'{tempFolderPath}\extractedImages')
        os.makedirs(fr'{tempFolderPath}\extractedObject')
        os.makedirs(fr'{tempFolderPath}\generatedHTML')
        os.makedirs(fr'{tempFolderPath}\generatedPDF')
        os.makedirs(fr'{tempFolderPath}\splitPDF')
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

def splitPDF(orthoReport, tempFolderPath):
    try:
        openOrthoReport = open(orthoReport, 'rb')
        orthoReportReader = PyPDF2.PdfFileReader(openOrthoReport, strict=False)
        openGeneratedReport = open(fr'{tempFolderPath}\generatedPDF\OrthoReport.pdf', 'rb')
        generatedReportReader = PyPDF2.PdfFileReader(openGeneratedReport, strict=False)
        for page in range(orthoReportReader.numPages):
            writer = PyPDF2.PdfFileWriter()
            if(page == 1 or page == 2 or page == 9):
                writer.addPage(orthoReportReader.getPage(page))
                with open(fr'{tempFolderPath}\splitPDF\OrthoReport{page}.pdf', 'wb') as outputStream:
                    writer.write(outputStream)
        for page in range(generatedReportReader.numPages):
            writer = PyPDF2.PdfFileWriter()
            writer.addPage(generatedReportReader.getPage(page))
            with open(fr'{tempFolderPath}\splitPDF\NewOrthoReport{page}.pdf', 'wb') as outputStream:
                writer.write(outputStream)
    except:
        print(f'Failed to split PDF')
    finally:
        openOrthoReport.close()
        openGeneratedReport.close()

def convertPdfToPng(tempFolderPath):
    try:
        zoom_x = 3.5
        zoom_y = 3.5
        mat = fitz.Matrix(zoom_x, zoom_y)
        pdfFile = ''
        for item in range(1, 10):
            if(item == 1 or item == 2 or item == 9):
                pdfFile = glob.glob(fr'{tempFolderPath}\splitPDF\OrthoReport{item}.pdf')
                for page in pdfFile:
                    doc = fitz.open(page)
                    for pageNo in doc:
                        pix = pageNo.get_pixmap(matrix=mat)
                        pix.save(fr'{tempFolderPath}\convertedPDFImages\OrthoReport{item}.png')
                    doc.close()
    except:
        print(f'Failed to convert PDF to PNG')

def editImage(tempFolderPath):
    try:
        for item in range(1, 10):
            if(item == 1 or item == 2 or item == 9):
                image = PIL.Image.open(fr'{tempFolderPath}\convertedPDFImages\OrthoReport{item}.png')
                logo = PIL.Image.open(os.path.join(sys.path[0], fr'Resources\Images\logo.jpg'))
                banner = PIL.Image.open(os.path.join(sys.path[0], fr'Resources\Images\banner.png'))
                image.paste(logo.resize((130, 130)), (1820, 100))
                image.paste(banner.resize((260, 70)), (130, 2850))
                image.paste(banner.resize((269, 70)), (1550, 2850))
                image.save(fr'{tempFolderPath}\convertedPDFImages\OrthoReport{item}.png')
                logo.close()
                banner.close()
                image.close()
    except:
        print(f'Failed to edit images in {tempFolderPath}\convertedPDFImages')

def convertPngToPdf(tempFolderPath):
    try:
        for item in range(1, 10):
            if(item == 1 or item == 2 or item == 9):
                openImage = PIL.Image.open(fr'{tempFolderPath}\convertedPDFImages\OrthoReport{item}.png')
                pdf_bytes = img2pdf.convert(openImage.filename)
                pdfFile = open(fr'{tempFolderPath}\splitPDF\OrthoReport{item}.pdf', "wb")
                pdfFile.write(pdf_bytes)
                openImage.close()
            pdfFile.close()
    except:
        print(f'Filed to convert PNG to PDF')

def addPageNumber(tempFolderPath):
    try:
        pdf1 = fr'{tempFolderPath}\splitPDF\OrthoReport1.pdf'
        pdf2 = fr'{tempFolderPath}\splitPDF\OrthoReport2.pdf'
        pdf3 = fr'{tempFolderPath}\splitPDF\OrthoReport9.pdf'
        pdfFilesList = [tpr, pdf1, pdf2, pdf3, ipr]
        count = 0
        for item in pdfFilesList:
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.setFont('Helvetica', 32)
            if(item == tpr):
                can.setFont('Helvetica', 12)
                can.drawString(500, 40, 'Page 2 of 8')
            if(item == pdf1):
                can.drawString(1340, 100, 'Page 3 of 8')
            if(item == pdf2):
                can.drawString(1340, 100, 'Page 4 of 8')
            if(item == pdf3):
                can.drawString(1340, 100, 'Page 7 of 8')
            if(item == ipr):
                can.setFont('Helvetica', 16)
                can.drawString(700, 40, 'Page 8 of 8')
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
        print(f'Failed to print page number')

def mergePDFs(tempFolderPath):
    try:
        print(f'Merging PDFs')
        mergePDF = PyPDF2.PdfFileMerger(strict=False)
        pdf1 = fr'{tempFolderPath}\splitPDF\NewOrthoReport0.pdf'
        pdf2 = fr'{tempFolderPath}\splitPDF\OrthoReports0.pdf'
        pdf3 = fr'{tempFolderPath}\splitPDF\OrthoReports1.pdf'
        pdf4 = fr'{tempFolderPath}\splitPDF\OrthoReports2.pdf'
        pdf5 = fr'{tempFolderPath}\splitPDF\NewOrthoReport1.pdf'
        pdf6 = fr'{tempFolderPath}\splitPDF\NewOrthoReport2.pdf'
        pdf7 = fr'{tempFolderPath}\splitPDF\OrthoReports3.pdf'
        pdf8 = fr'{tempFolderPath}\splitPDF\OrthoReports4.pdf'
        pdfFiles = [pdf1, pdf2, pdf3, pdf4, pdf5, pdf6, pdf7, pdf8]
        for files in pdfFiles:
            pdfReader = PyPDF2.PdfFileReader(files, 'rb')
            mergePDF.append(pdfReader)
        mergePDF.write(fr'{tempFolderPath}\formatPDF\FormatReport.pdf')
    except:
        print(f'Failed to merge PDFs')
    finally:
        mergePDF.close()

def formatPDF(tempFolderPath, caseName, finalReportPath):
    try:
        src = fitz.open(fr'{tempFolderPath}\formatPDF\FormatReport.pdf')
        finalReportSrc = fitz.open()
        for pages in src:
            if pages.rect.width > pages.rect.height:
                fmt = fitz.paper_rect("a4-l")
            else:
                fmt = fitz.paper_rect("a4")
            page = finalReportSrc.new_page(width=fmt.width, height=fmt.height)
            page.show_pdf_page(page.rect, src, pages.number)
        path = os.path.join(fr'{finalReportPath}', fr'{caseName}-{pid}')
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=False)
            os.makedirs(fr'{finalReportPath}\{caseName}-{pid}')
        else:
            os.makedirs(fr'{finalReportPath}\{caseName}-{pid}')
        finalReportSrc.save(fr'{finalReportPath}\{caseName}-{pid}\{caseName}-{pid}.pdf')
    except:
        print(f'Failed to format PDF')
    finally:
        src.close()
        finalReportSrc.close()

print(f'Starting Report Utility')

config = loadConfigProperties()

logo = os.path.join(sys.path[0], fr'Resources\Images\logo.png')

sourceFolderPath = config.get('path', 'sourceFolderPath')
tempFolderPath = config.get('path', 'tempFolderPath')
finalReportPath = config.get('path', 'finalReportPath')

caseName = ''
orthoReport = ''
ipr = ''
tpr = ''

sourceFolderTotalDir = 0

for base, dirs, files in os.walk(sourceFolderPath):
    for directories in dirs:
        sourceFolderTotalDir += 1

cases=[]

for files in os.listdir(sourceFolderPath):
    cases.append(os.path.join(sourceFolderPath, files))

for caseNumber in range(0,sourceFolderTotalDir):
    caseName=os.path.basename(cases[caseNumber])
    print(f'\nGenerating report of {caseName}')
    if os.path.isdir(cases[caseNumber]):
        orthoReport = cases[caseNumber]+"\OrthoReport.pdf"
        ipr = cases[caseNumber]+"\IPR-1.pdf"
        tpr = cases[caseNumber]+"\TPR-1.pdf"

    cleanTempFolder(tempFolderPath)
    createFoldersInTempFolder(tempFolderPath)
    extractImages(orthoReport, tempFolderPath)

    imgList = [31, 32, 37, 38, 43, 44, 49, 50, 55, 56]

    cropImages(imgList, tempFolderPath)

    text = extractText(orthoReport)

    pidIndex = text.index('ID:')
    ssnIndex = text.index('SSN:')
    nameIndex = text.index('Name:')
    addressIndex = text.index('Address:')
    cityIndex = text.index('City:')
    countryIndex = text.index('Country:')
    clinicIdIndex = text.index('Clinic ID:')
    operatorIndex = text.index('Operator:')
    commentIndex = text.index('Comment:')
    caseDateIndex = text.index('Case date:')
    scanDateIndex = text.index('Scan date:')

    pid = ''
    ssn = ''
    name = ''
    address = ''
    city = ''
    country = ''
    clinicId = ''
    operator = ''
    comment = ''
    caseDate = ''
    scanDate = ''

    if(text[pidIndex+1] != 'SSN:'):
        pid = text[pidIndex+1]
    if(text[ssnIndex+1] != 'Name:'):
        ssn = text[ssnIndex+1]
    if(text[nameIndex+1] != 'Address:'):
        name = text[nameIndex+1]
    if(text[addressIndex+1] != 'City:'):
        address = text[addressIndex+1]
    if(text[cityIndex+1] != 'Country:'):
        city = text[cityIndex+1]
    if(text[countryIndex+1] != 'Clinic Id:'):
        country = text[countryIndex+1]
    if(text[clinicIdIndex+1] != 'CASE'):
        clinicId = text[clinicIdIndex+1]
    if(text[operatorIndex+1] != 'Comment:'):
        operator = text[operatorIndex+1]
    if(text[commentIndex+1] != 'Case date:'):
        comment = text[commentIndex+1]
    if(text[caseDateIndex+1] != 'Scan date:'):
        caseDate = text[caseDateIndex+1]
    if(text[scanDateIndex+1] != 'Overview'):
        scanDate = text[scanDateIndex+1]

    htmlContent = '''<html>
    <head>
        <style>
            body {
                width: 100%;
                margin: 0px;
                font-family: Verdana;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-left: 0px;
                margin-right: 0px;
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
            .heading {
                color: #384855;
                font-size: 22px;
            }
            .data {
                font-size: 19px;
                margin-top: 0px;
                margin-bottom: 0px;
            }
            .logo {
                width: 60px;
            }
            .scannedImagesSection {
                font-size: 18px;
            }
            .pageNo {
                font-size: 19px;
                text-align: right;
                font-family: Helvetica;
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
                height: 300px;
                width: 400px;
            }
            .secondPDFSection {
                font-size: 20px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div>
            <h2 class='center' style='color:transparent;'>Overview</h2>
            <br>
            <table cellpadding='1' cellspacing='1'>
                <tr>
                    <td>
                        <p class='heading'><b>PATIENT</b></p>
                        <ul>
                            <li>
                                <p class='data'> <b>ID:</b> ''' + pid + '''</p>
                            </li>
                            <li>
                                <p class='data'> <b>SSN:</b> ''' + ssn + '''</p>
                            </li>
                            <li>
                                <p class='data'> <b>Name:</b> ''' + name + '''</p>
                            </li>
                            <li>
                                <p class='data'> <b>Address:</b> ''' + address + '''</p>
                            </li>
                            <li>
                                <p class='data'> <b>City:</b> ''' + city + '''</p>
                            </li>
                            <li>
                                <p class='data'> <b>Country:</b> ''' + country + '''</p>
                            </li>
                            <li>
                                <p class='data'> <b>Clinic ID:</b> ''' + clinicId + '''</p>
                            </li>
                        </ul>
                    </td>
                    <td valign='top'>
                        <p class='heading'><b>CASE</b></p>
                        <ul>
                            <li>
                                <p class='data'> <b>ID:</b> ''' + pid + '''</p>
                            </li>
                            <li>
                                <p class='data'> <b>Operator:</b> ''' + operator + '''</p>
                            </li>
                            <li>
                                <p class='data'> <b>Comment:</b> ''' + comment + '''</p>
                            </li>
                            <li>
                                <p class='data'> <b>Case date:</b> ''' + caseDate + '''</p>
                            </li>
                            <li>
                                <p class='data'> <b>Scan date:</b> ''' + scanDate + '''</p>
                            </li>
                        </ul>
                    </td>
                    <td>
                        <p style='margin-top: -188px;' class='right'><img class='logo'
                                src="''' + logo + '''" alt='32Watts' /></p>
                    </td>
                </tr>
            </table>
            <table cellpadding='1' cellspacing='1'>
                <tr>
                    <td>
                        <p class='groove center'><img
                                src = "''' + f'{tempFolderPath}\extractedImages\Image7.png' + '''"
                                class='orthoImage' alt='No Image' /></p>
                    </td>
                    <td>
                        <p class='groove center'><img
                                src = "''' + f'{tempFolderPath}\extractedImages\Image8.png' + '''"
                                class='orthoImage' alt='No Image'></p>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p class='groove center'><img
                                src = "''' + f'{tempFolderPath}\extractedImages\Image9.png' + '''"
                                class='orthoImage' alt='No Image'></p>
                    </td>
                    <td>
                        <p class='groove center'><img
                                src = "''' + f'{tempFolderPath}\extractedImages\Image10.png' + '''"
                                class='orthoImage' alt='No Image' /></p>
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
                <tr>
                    <td class='pageNo' colspan='2'>Page 1 of 8</td>
                </tr>
            </table>
        </div>
        <div style='margin-top:11px;'>
            <table cellpadding='1' cellspacing='1' class="scannedImagesSection">
                <tr>
                    <td>
                        <p class='right'><img class='logo' src="''' + logo + '''"
                                alt='32Watts'>
                        </p>
                    </td>
                </tr>
            </table>
            <table cellpadding='1' cellspacing='1' style='margin-top:-50px;' class="scannedImagesSection">
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
            <table cellpadding='1' cellspacing='1' class="scannedImagesSection">
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
            <table cellpadding='1' cellspacing='1' class="scannedImagesSection">
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
                <tr>
                    <td colspan='2' class='pageNo'><br />Page 5 of 8</td>
                </tr>
            </table>
            <table cellpadding='1' cellspacing='1' class="secscannedImagesSectiontion2" style='margin-top:2px'>
                <tr>
                    <td></td>
                    <td>
                        <p class='right'><img class='logo' src="''' + logo + '''"
                                alt='32Watts'>
                        </p>
                    </td>
                </tr>
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
            <table cellpadding='1' cellspacing='1'>
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
                <tr>
                    <td colspan='2' class='pageNo' style='padding-top:400px;'><br />Page 6 of 8</td>
                </tr>
            </table>
        </div>
    </body>
    </html>'''

    generateHTML(tempFolderPath, htmlContent)
    convertHtmlToPdf(tempFolderPath)
    splitPDF(orthoReport, tempFolderPath)
    convertPdfToPng(tempFolderPath)
    editImage(tempFolderPath)
    convertPngToPdf(tempFolderPath)
    addPageNumber(tempFolderPath)
    mergePDFs(tempFolderPath)
    formatPDF(tempFolderPath, caseName, finalReportPath)

    print(f'Report has been generated successfully in {finalReportPath}\{caseName}-{pid}')

print(f'\nAll the reports have been generated successfully')
