import os, io, boto3, time, uuid
from PIL import Image, ImageDraw, ImageFont

s3 = boto3.client("s3")
ddb = boto3.resource("dynamodb")
DEST = os.environ["DEST_BUCKET"]
TABLE = ddb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
   
    rec = event["Records"][0]["s3"]
    src_bucket, key = rec["bucket"]["name"], rec["object"]["key"]
    basename, ext = key.rsplit(".", 1)

 
    obj = s3.get_object(Bucket=src_bucket, Key=key)
    img = Image.open(io.BytesIO(obj["Body"].read()))


    img = img.resize((800, 600))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "Watermarked manara", fill="white", font=ImageFont.load_default(36))

 
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)

    processed_key = f"{basename}_processed.jpg"
    s3.put_object(
        Bucket=DEST, 
        Key=processed_key, 
        Body=buf, 
        ContentType="image/jpeg",
        ACL='public-read'
    )

    return {"status": "OK", "dest": DEST}
