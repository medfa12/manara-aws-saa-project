import os, io, boto3, time, uuid
from urllib.parse import unquote_plus
from PIL import Image, ImageDraw, ImageFont

s3 = boto3.client("s3")
ddb = boto3.resource("dynamodb")
DEST = os.environ["DEST_BUCKET"]
TABLE = ddb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
   
    rec = event["Records"][0]["s3"]
    src_bucket = rec["bucket"]["name"]
    key = unquote_plus(rec["object"]["key"])
    basename, ext = os.path.splitext(key)

    obj = s3.get_object(Bucket=src_bucket, Key=key)
    img = Image.open(io.BytesIO(obj["Body"].read()))

    img = img.resize((800, 600))
    draw = ImageDraw.Draw(img)
    
    
    font_size = 48
    try:
        font = ImageFont.truetype('arial.ttf', size=font_size)  
    except:
        font = ImageFont.load_default()  
    
    watermark_text = "Watermarked manara"
    

    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    

    x = 10
    y = 10
    
 
    box_padding = 10
    box_coords = [x - box_padding, y - box_padding, x + text_width + box_padding, y + text_height + box_padding]
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle(box_coords, fill=(0, 0, 0, 128)) 
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    

    draw = ImageDraw.Draw(img)
    draw.text((x, y), watermark_text, fill="white", font=font)

    buf = io.BytesIO()
    img.convert('RGB').save(buf, format="JPEG", quality=85)
    buf.seek(0)

    processed_key = f"{basename}_processed.jpg"
    s3.put_object(
        Bucket=DEST, 
        Key=processed_key, 
        Body=buf, 
        ContentType="image/jpeg"
    )

    item = {
        "imageId": str(uuid.uuid4()),
        "srcBucket": src_bucket,
        "srcKey": key,
        "processedKey": processed_key,
        "timestamp": int(time.time())
    }
    TABLE.put_item(Item=item)

    return {"status": "OK", "dest": DEST, "metadata_status": "SAVED"}
