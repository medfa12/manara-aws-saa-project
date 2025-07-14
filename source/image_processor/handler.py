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
    draw.text((10, 10), "Watermarked", fill="white", font=ImageFont.load_default())

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)

    s3.put_object(Bucket=DEST,
                  Key=f"{base}_processed.jpg",
                  Body=buf,
                  ContentType="image/jpeg")
    return {"status": "OK"}
