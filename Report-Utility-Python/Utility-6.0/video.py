import os, cv2, ffmpeg, math, fitz, glob
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont

def reduceVideoLength(sourceFolderPath, tempFolderPath):
    try:
        print()
        src = fr'{sourceFolderPath}\Videos'
        dest = fr'{tempFolderPath}\resizedVideos'
        for root, dirs, filenames in os.walk(src, topdown=False):
            for filename in filenames:
                if(filename.endswith('.avi')):
                    inputfile = os.path.join(root, filename)
                    clip = VideoFileClip(inputfile)
                    duration = float(clip.duration/7)
                    final = clip.fx( vfx.speedx, duration)
                    final.write_videofile(fr'{dest}/{filename}',codec='libx264')
    except:
        print(f'Failed to reduce videos length in {tempFolderPath}\resizedVideos')

def cropVideos(tempFolderPath):
    try:
        print()
        print('Cropping videos')
        x,y,h,w = 90,40,930,1150
        src = fr'{tempFolderPath}\resizedVideos'
        dest = fr'{tempFolderPath}\croppedVideos'
        for root, dirs, filenames in os.walk(src, topdown=False):
            for filename in filenames:
                inputfile = os.path.join(root, filename)
                cap = cv2.VideoCapture(inputfile)
                fps, frames = cap.get(cv2.CAP_PROP_FPS), cap.get(cv2.CAP_PROP_FRAME_COUNT)
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(fr'{dest}/{filename}', fourcc, fps, (w, h))
                while(cap.isOpened()):
                    ret, frame = cap.read()
                    if ret==True:
                        crop_frame = frame[y:y+h, x:x+w]
                        out.write(crop_frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    else:
                        break
    except:
        print(fr'Failed to reduce videos length in {tempFolderPath}\croppedVideos')
    finally:
        cap.release()
        out.release()

def extractImageFromVideo(tempFolderPath):
    try:
        print('Extracting images from video')
        src = fr'{tempFolderPath}\croppedVideos'
        for root, dirs, filenames in os.walk(src, topdown=False):
            for filename in filenames:
                inputfile = os.path.join(root, filename)
                clip = cv2.VideoCapture(inputfile)
                ret,frame = clip.read()
                name = fr'{tempFolderPath}\croppedVideos\{filename}.jpg'
                cv2.imwrite(name, frame)
    except:
        print(fr'Failed to extract images from video in {tempFolderPath}\croppedVideos')       

def extractAlignersText(tpr):
    try:
        print('Extrating no. of aigners from TPR sheet')
        with fitz.open(tpr) as doc:
            text = ''
            for page in doc:
                text+=page.get_text()
            txt1 = text.partition('Active Aligners:')
            txt2 = txt1[2].partition('Chief Complaint:')
            aligners = txt2[0].strip() 
            if not (txt2[1].startswith('Chief Complaint:')):
                txt2 = txt1[2].partition('Greetings')
                aligners = txt2[0].strip() 
            return aligners
    except:
        print('Failed to extrat no. of aigners from TPR sheet')

def convertPDFToImage(ipr, tempFolderPath):
    try:
        print('Converting PDF to image')
        zoom_x = 2.0  
        zoom_y = 2.0  
        mat = fitz.Matrix(zoom_x, zoom_y)  
        path = ipr
        all_files = glob.glob(path)
        for filename in all_files:
            doc = fitz.open(filename) 
            for page in doc: 
                pix = page.get_pixmap(matrix=mat)  
                pix.save(fr'{tempFolderPath}\iprImages\IPR Sheet.jpg') 
    except:
        print(fr'Failed to convert PDF to image in {tempFolderPath}\iprImage')

def cropImage(tempFolderPath):
    try:
        print('Cropping IPR sheet')
        img = Image.open(fr'{tempFolderPath}\iprImages\IPR Sheet.jpg')
        left = 20.5
        top = 275
        right = 1170
        bottom = 1205
        image = img.crop((left, top, right, bottom))
        image.save(fr'{tempFolderPath}\iprImages\IPR.jpg')
    except:
        print('Failed to crop IPR sheet')

def createVideoThumbnail(tempFolderPath, caseName, pid, aligners, operator, logoRequired, wisealignClinic):
    try:
        clinicType = int(pid[6])
        if(clinicType != 5 and clinicType != 2 and wisealignClinic!='79' and (logoRequired=='Y' or logoRequired=='y')):
            image = Image.open(os.path.join(sys.path[0], fr'Resources\Images\thumbnail1.jpg'))
        elif(clinicType == 5 and wisealignClinic!='79' and (logoRequired=='Y' or logoRequired=='y')):
            image = Image.open(os.path.join(sys.path[0], fr'Resources\Images\thumbnail2.jpg'))
        elif(clinicType == 2 and wisealignClinic!='79' and (logoRequired=='Y' or logoRequired=='y')):
            image = Image.open(os.path.join(sys.path[0], fr'Resources\Images\thumbnail3.jpg'))
        elif(wisealignClinic=='79' and (logoRequired=='Y' or logoRequired=='y')):
            image = Image.open(os.path.join(sys.path[0], fr'Resources\Images\thumbnail4.jpg'))
        else:
            image = Image.open(os.path.join(sys.path[0], fr'Resources\Images\thumbnail5.jpg'))
        img = ImageDraw.Draw(image)
        font = ImageFont.truetype(os.path.join(sys.path[0], fr'Resources\Fonts\GothamBook.ttf'), 50)
        img.text((330, 500), pid, font=font, fill ='black', stroke_width=2)
        img.text((484, 580), caseName, font=font, fill ='black', stroke_width=2)
        img.text((484, 660), operator, font=font, fill ='black', stroke_width=2)
        img.text((530, 740), aligners, font=font, fill ='black', stroke_width=2)
        image.save(fr'{tempFolderPath}\addBackgroundVideo\thumbnail.jpg')
    except:
        print(fr'Failed to create thumbnail for video in {tempFolderPath}\addBackgroundVideo')
    finally:
        image.close()

def createFirstFrameImage(tempFolderPath, aligners):
    try:
        imagePresent = os.path.exists(fr'{tempFolderPath}\croppedVideos\upload plan 004.avi.jpg')
        image = Image.open(os.path.join(sys.path[0], fr'Resources\Images\white.jpg'))
        img1 = Image.open(fr'{tempFolderPath}\croppedVideos\upload plan 001.avi.jpg').resize((360, 300))
        img2 = Image.open(fr'{tempFolderPath}\croppedVideos\upload plan.avi.jpg').resize((360, 300))
        img3 = Image.open(fr'{tempFolderPath}\croppedVideos\upload plan 002.avi.jpg').resize((360, 300))
        img4 = Image.open(fr'{tempFolderPath}\croppedVideos\upload plan 003.avi.jpg').resize((360, 300))
        if(imagePresent==True):
            img5 = Image.open(fr'{tempFolderPath}\croppedVideos\upload plan 004.avi.jpg').resize((360, 300))
        font = ImageFont.truetype(os.path.join(sys.path[0], fr'Resources\Fonts\GothamBook.ttf'), 30)
        image.paste(img1, (10, 115))
        image.paste(img2, (395, 115))
        image.paste(img3, (780, 115))
        if(imagePresent==True):
            image.paste(img4, (202, 550))
            image.paste(img5, (587, 550))
        else:
            image.paste(img4, (395, 550))
        img = ImageDraw.Draw(image)
        img.text((110, 72), 'Right View', font=font, fill ='black')
        img.text((490, 72), 'Front View', font=font, fill ='black')
        img.text((890, 72), 'Left View', font=font, fill ='black')
        if(imagePresent==True):
            img.text((300, 508), 'Upper View', font=font, fill ='black')
            img.text((680, 508), 'Lower View', font=font, fill ='black')
        else:
            if(aligners.startswith('U/')):        
                img.text((490, 508), 'Upper View', font=font, fill ='black')
            if(aligners.startswith('L/')):
                img.text((490, 508), 'Lower View', font=font, fill ='black')
        image.save(fr'{tempFolderPath}\addBackgroundVideo\firstFrame.jpg')
    except:
         print(fr'Failed to create first frame image in {tempFolderPath}\generatedVideo')

def imagesToVideo(tempFolderPath, multiple):
    try:
        print('Converting images to video')
        image_folder = fr'{tempFolderPath}\croppedVideos'
        os.chdir(fr'{tempFolderPath}\generatedVideo')
        if(multiple):
            images = [fr'{tempFolderPath}\addBackgroundVideo\thumbnail.jpg',
            fr'{tempFolderPath}\addBackgroundVideo\firstFrame.jpg',]
        else:
            images = [ fr'{tempFolderPath}\iprImages\IPR.jpg']
        frame = cv2.imread(os.path.join(image_folder, images[0]))
        height, width, layers = frame.shape
        if(multiple):
            video = cv2.VideoWriter('generated.avi', 0, 0.2, (width, height))
        else:
            video = cv2.VideoWriter('ipr.avi', 0, 0.2, (width, height))
        for image in images:
            video.write(cv2.imread(os.path.join(image_folder, image)))
    except:
        print(fr'Failed to convert images to video in {tempFolderPath}\generatedVideo')
    finally:
        video.release()
        os.chdir(tempFolderPath)

def addProgressbarToVideo(tempFolderPath, pid, logoRequired):
    try:
        print('Adding progressbar in videos')
        print()
        clinicType = int(pid[6])
        src = fr'{tempFolderPath}\croppedVideos'
        dest = fr'{tempFolderPath}\videoProgressBar'
        for root, dirs, filenames in os.walk(src, topdown=False):
            for filename in filenames:
                if(filename.endswith('.avi')):
                    inputfile = os.path.join(root, filename)
                    capture = cv2.VideoCapture(inputfile)
                    name = fr'{dest}/{filename}'
                    frame_width = int(capture.get(3))
                    frame_height = int(capture.get(4))
                    size = (frame_width, frame_height)
                    result = cv2.VideoWriter(name, cv2.VideoWriter_fourcc(*'XVID'),10,size)
                    while(True):
                        ret, currentframe = capture.read()
                        if currentframe is not None:
                            nextFrameNo = capture.get(cv2.CAP_PROP_POS_FRAMES)
                            totalFrames = capture.get(cv2.CAP_PROP_FRAME_COUNT)
                            complete = nextFrameNo/totalFrames
                            lineThickness=2
                            y=910
                            x=0
                            w=1150
                            if(clinicType != 5 and clinicType != 2 and (logoRequired=='Y' or logoRequired=='y')):
                                pass
                            else:    
                                cv2.line(currentframe, (x, y), (w, y), (255,255,255), lineThickness)
                                cv2.line(currentframe, (x, y), (math.ceil(w*complete), y), (0,0,255), lineThickness)
                            result.write(currentframe)
                        else:
                            break
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
    except:
        print(fr'Failed to add progressbar in videos in {tempFolderPath}\videoProgressBar')
    finally:
        result.release()

def concatVideos(tempFolderPath):
    try:
        clip1=VideoFileClip(fr'{tempFolderPath}\generatedVideo\generated.avi')
        clip2=VideoFileClip(fr'{tempFolderPath}\videoProgressBar\upload plan.avi')
        clip3=VideoFileClip(fr'{tempFolderPath}\videoProgressBar\upload plan 001.avi')
        clip4=VideoFileClip(fr'{tempFolderPath}\videoProgressBar\upload plan 002.avi')
        clip5=VideoFileClip(fr'{tempFolderPath}\videoProgressBar\upload plan 003.avi')
        clip6=VideoFileClip(fr'{tempFolderPath}\videoProgressBar\upload plan 004.avi')
        clip7=VideoFileClip(fr'{tempFolderPath}\generatedVideo\ipr.avi')
        final = concatenate_videoclips([clip1, clip2, clip3, clip4, clip5, clip6, clip7])
        final.write_videofile(fr'{tempFolderPath}\addBackgroundVideo\merged.mp4',codec='libx264')
    except:
        print(fr'Failed to concatinate videos in {tempFolderPath}\addBackgroundVideo')

def addBackgroundToVideo(tempFolderPath):
    try:
        src = ffmpeg.input(fr'{tempFolderPath}\addBackgroundVideo\merged.mp4')
        output = ffmpeg.output(src, fr'{tempFolderPath}\addBackgroundVideo\final.mp4', vcodec='libx264', vf='pad=w=iw+500:h=ih+240:x=250:y=120:color=white')
        output.run()
    except:
        print(fr'Failed to add background to video in {tempFolderPath}\addBackgroundVideo')        

def createText(text, start, duration):
    textClip = TextClip(text, fontsize = 34, color = 'black') 
    textClip = textClip.set_pos(("center","top")).margin(top=35, opacity=0).set_duration(start).set_start(duration)
    return textClip

def addTextToVideo(tempFolderPath, finalReportPath, caseName, pid, aligners, logoRequired, wisealignClinic):
    try:
        video=VideoFileClip(fr'{tempFolderPath}\addBackgroundVideo\final.mp4')
        clinicType = int(pid[6])
        if(clinicType != 5 and clinicType != 2 and wisealignClinic!='79' and (logoRequired=='Y' or logoRequired=='y')):
            logo = ImageClip(os.path.join(sys.path[0], fr'Resources\Images\32watts_small.png')).set_position("top").margin(top=15, left=1250, opacity=0).set_duration(62.5).set_start(5)
        elif(clinicType == 5 and wisealignClinic!='79' and (logoRequired=='Y' or logoRequired=='y')):
            logo = ImageClip(os.path.join(sys.path[0], fr'Resources\Images\lms_small.png')).set_position("top").margin(left=1450, opacity=0).set_duration(62.5).set_start(5)
        elif(clinicType == 2 and wisealignClinic!='79' and (logoRequired=='Y' or logoRequired=='y')):
            logo = ImageClip(os.path.join(sys.path[0], fr'Resources\Images\apollo_small.png')).set_position("top").margin(top=10, left=1450, opacity=0).set_duration(62.5).set_start(5)
        elif(wisealignClinic=='79' and (logoRequired=='Y' or logoRequired=='y')):
            logo = ImageClip(os.path.join(sys.path[0], fr'Resources\Images\wisealign_small.jpg')).set_position("top").margin(top=10, left=1450, opacity=0).set_duration(62.5).set_start(5)
        circle1 = ImageClip(os.path.join(sys.path[0], fr'Resources\Images\orange_circle_1.png')).set_position("top").margin(left=1450, opacity=0).set_duration(5)
        circle2 = ImageClip(os.path.join(sys.path[0], fr'Resources\Images\orange_circle_2.png')).set_position("left").margin(top=1080, left=10, opacity=0).set_duration(5)
        patientName = TextClip(fr'Pt. Name: {caseName}', fontsize = 34, color = 'black') 
        patientName = patientName.set_pos(("left","bottom")).margin(bottom=55, left=20, opacity=0).set_duration(62.5).set_start(5)
        caseId = TextClip(fr'Case Id: {pid}', fontsize = 34, color = 'black') 
        caseId = caseId.set_pos(("left","bottom")).margin(bottom=10, left=20, opacity=0).set_duration(62.5).set_start(5) 
        pauseVideo = TextClip(fr'Click to pause', fontsize = 34, color = 'black') 
        pauseVideo = pauseVideo.set_pos(("center","bottom")).margin(bottom=35, opacity=0).set_duration(62.5).set_start(5)
        vidText1 = createText('Front Profile', 10.5, 10)
        vidText2 = createText('Right Profile', 10.5, 20.5)
        vidText3 = createText('Left Profile', 10.5, 31)
        vidText4 = createText('Upper Arch', 10.5, 41.5)
        vidText5 = createText('Lower Arch', 10.5, 52)
        imgText6 = createText(fr'IPR/ATT Details : {aligners}', 5, 62.5)
        if(logoRequired=='N' or logoRequired=='n'):
            video = CompositeVideoClip([video, circle1, circle2, patientName, caseId, pauseVideo, vidText1, vidText2, vidText3, vidText4, vidText5, imgText6]) 
        else:
            video = CompositeVideoClip([video, logo, circle1, circle2, patientName, caseId, pauseVideo, vidText1, vidText2, vidText3, vidText4, vidText5, imgText6]) 
        video.write_videofile(fr'{finalReportPath}\{caseName}-{pid}\{caseName}-{pid}.mp4', codec='libx264')
    except:
        print(fr'Failed to add text and images in video')
