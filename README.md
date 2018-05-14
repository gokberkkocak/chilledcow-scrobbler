# chilledcow-scrobbler
LastFM scrobbler for chilledcow youtube stream

## Requirements
- Tesseract-OCR

## Python Requirements
- opencv
- pafy
- numpy
- pillow image
- pytesseract
- pylast

## Usage

```
python ccs.py credentials.json stream_youtube_link
```
## Credentials File
- You need a LastFM API. You can apply from [here](https://www.last.fm/api/account/create)
- Credentials file must be JSON in this format;
```
{
 "LAST_API_KEY" : "sample",
 "LAST_SHARED_SECRET" : "sample",
 "username" : "sample",
 "password_hash" : "sample" 
}
```
- You can generate your password_hash by
```
pylast.md5(password)
```


## How does it work

- Grabs the youtube link and extracts the stream url.

- OpenCV opens the stream and captures one single frame
![Example image](images/img.jpg "Title")
- Images get cropped
![Example cropped image](images/img_cropped.jpg "Title")
- Remove the background
![Example processed image](images/img_cropped_processed.jpg "Title")
- OCR on image
- Send to Last.FM

