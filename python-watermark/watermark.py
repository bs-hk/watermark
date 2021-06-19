from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps
import pandas as pd
record = pd.read_csv('./temp/record.csv')
import math

def draw_rotated_text(image, angle, xy, text, fill, *args, **kwargs):
    """ Draw text at an angle into an image, takes the same arguments
        as Image.text() except for:

    :param image: Image to write text into
    :param angle: Angle to write text at
    """
    # get the size of our image
    width, height = image.size
    max_dim = max(width, height)

    # build a transparency mask large enough to hold the text
    mask_size = (max_dim * 2, max_dim * 2)
    mask = Image.new('L', mask_size, 0)

    # add text to mask
    draw = ImageDraw.Draw(mask)
    draw.text((max_dim, max_dim), text, 255, *args, **kwargs)

    if angle % 90 == 0:
        # rotate by multiple of 90 deg is easier
        rotated_mask = mask.rotate(angle)
    else:
        # rotate an an enlarged mask to minimize jaggies
        bigger_mask = mask.resize((max_dim*8, max_dim*8),
                                  resample=Image.BICUBIC)
        rotated_mask = bigger_mask.rotate(angle).resize(
            mask_size, resample=Image.LANCZOS)

    # crop the mask to match image
    mask_xy = (max_dim - xy[0], max_dim - xy[1])
    b_box = mask_xy + (mask_xy[0] + width, mask_xy[1] + height)
    mask = rotated_mask.crop(b_box)

    # paste the appropriate color, with the text transparency mask
    color_image = Image.new('RGBA', image.size, fill)
    image.paste(color_image, mask)

def copyright_apply(input_image_path,output_image_path,text):
    photo = Image.open(input_image_path)
    if text == 'chanjing55555@gmail.com':
        qrcode = Image.open('./temp/qr2.jpeg')
        chooseFont = 'Georgia.ttf'
    else:
        qrcode = Image.open('./temp/qr1.jpeg')
        chooseFont = 'Apple-Chancery.ttf'

    #Store image width and height
    width, height  = photo.size
    qrcode_width, qrcode_height = qrcode.size

    if width < height:
        qrcode = qrcode.resize((int(qrcode_width*qrcode_width/width+width/25),int(qrcode_width*qrcode_width/width+width/25)))
    else:
        qrcode = qrcode.resize((int(qrcode_height*qrcode_height/height+height/25),int(qrcode_height*qrcode_height/height+height/25)))

    # make the image editable
    drawing = ImageDraw.Draw(photo)

    # Set font size

    fontsize = 1  
    # portion of image width you want text width to be
    img_fraction = 0.30

    font = ImageFont.truetype("./temp/"+chooseFont, fontsize)
    while font.getsize(text)[0] < img_fraction*photo.size[0]:
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        font = ImageFont.truetype("./temp/"+chooseFont, fontsize)

    # optionally de-increment to be sure it is less than criteria
    fontsize -= 1
    font = ImageFont.truetype("./temp/"+chooseFont, fontsize)

    #get text width and height
    text_width, text_height = drawing.textsize(text, font)
    rotateAng = 40
    # rotateAng = math.degrees(math.atan(height/width))
    print(width,height)
    print(rotateAng)

    if text == 'amy96665895@gmail.com':
        pos = int(math.cos(rotateAng)*text_width/2+ qrcode.width*1.5),int(math.sin(rotateAng)*text_width/2+ qrcode.width*1.5)
        qrcodePos = int(width - qrcode.width*1.5), int(height - qrcode.width*1.5)
        colour = "#fdfcfa"
        middle = int(width-((width- math.cos(rotateAng)*text_width)/2)-text_height/2), int(height-((height - math.sin(rotateAng)*text_width)/2)+text_height/2)
        draw_rotated_text(photo, rotateAng, middle, text, colour, font=font)
    elif text == 'chanjing55555@gmail.com':
        pos = int(width - text_width - width/30), int(height - text_height - width/25)
        qrcodePos = int(qrcode.width*0.5), int(qrcode.width*0.5)
        colour = "#6b00bd"
    
    draw_rotated_text(photo, rotateAng, pos, text, colour, font=font)
    
    # paste QR code
    photo.paste(qrcode, qrcodePos)
   
    photo.save(output_image_path)

import time
import telepot
from telepot.loop import MessageLoop
import os
import datetime

chat_id = ''

def handle(msg):
    global chat_id, record
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(datetime.datetime.now(),content_type, chat_type, chat_id)
    

    if content_type == 'photo':
        i = 0
        while i<len(record['chat_id']):
            if str(chat_id) == str(record['chat_id'][i]):
                text = record['text'][i]
                break
            i+=1
            if i==len(record['chat_id']):
                text = 'amy96665895@gmail.com'

        inputFile = './temp/'+msg['photo'][-1]['file_unique_id']+'.png'
        outputFile = './temp/'+msg['photo'][-1]['file_unique_id']+'_out.png'

        bot.download_file(msg['photo'][-1]['file_id'], inputFile)
        copyright_apply(inputFile,outputFile,text)
        bot.sendPhoto(chat_id, photo=open(outputFile, 'rb'))
        os.remove(inputFile)
        os.remove(outputFile)

    elif  content_type == 'text':
        if msg['text'] == '/amy96665895':
            text = 'amy96665895@gmail.com'
        elif msg['text'] == '/chanjing55555':
            text = 'chanjing55555@gmail.com'

        if msg['text'] == '/amy96665895' or msg['text'] == '/chanjing55555':
            i = 0
            while i<len(record['chat_id']):
                if str(chat_id) == str(record['chat_id'][i]):
                    record['text'][i] = text 
                    break
                i+=1
                if i==len(record['chat_id']):
                    new_row = {'chat_id':chat_id, 'text':text}
                    record = record.append(new_row, ignore_index=True)
            bot.sendMessage(chat_id, 'Watermark is set to '+text, parse_mode=None, disable_web_page_preview=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)
            record.to_csv('./temp/record.csv', index = False)        


TOKEN = '1601242271:AAGBtOjPjtQVlxJ3HsuZguHkiy-125nPjfE'

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(20)
