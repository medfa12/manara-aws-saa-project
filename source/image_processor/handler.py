import os, io, boto3
from PIL import Image, ImageDraw, ImageFont

s3  = boto3.client("s3")
DEST= os.environ["DEST_BUCKET"]

def lambda_handler(event, context):
    rec = event["Records"][0]["s3"]
    src_bucket, key = rec["bucket"]["name"], rec["object"]["key"]
    base, _ = key.rsplit(".", 1)

    img_obj = s3.get_object(Bucket=src_bucket, Key=key)
    img = Image.open(io.BytesIO(img_obj["Body"].read()))
    img = img.resize((800, 600))

    
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", size=48)
    except:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", size=48)
        except:
            font = ImageFont.load_default()
    
    watermark_text = "Watermarked Manara"
    
  
    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    

    x = (img.width - text_width) // 2
    y = img.height - text_height - 50
    
  
    padding = 10
    rect_coords = [
        x - padding,
        y - padding,
        x + text_width + padding,
        y + text_height + padding
    ]

    
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle(rect_coords, fill=(0, 0, 0, 128))  # Semi-transparent black
    
 
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
 
    draw = ImageDraw.Draw(img)
    draw.text((x, y), watermark_text, fill="white", font=font)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)

    s3.put_object(Bucket=DEST,
                  Key=f"{base}_processed.jpg",
                  Body=buf,
                  ContentType="image/jpeg")
    return {"status": "OK"}
