# chilledcow-scrobbler
LastFM scrobbler for chilledcow youtube stream

## Requirements
- Tesseract-OCR

## Python Requirements
- requests
- opencv
- pafy
- youtube-dl
- numpy
- pillow image
- pytesseract
- pylast

## Usage

```
python ccs.py data_json
```
## Data File
- You need a LastFM API. You can apply from [here](https://www.last.fm/api/account/create).
- You also need a Youtube Data Api (no OAuth is necessary) [here](https://console.developers.google.com/apis/library)
- The file must be JSON in this format;
```
{
 "LASTFM_API_KEY" : "sample",
 "LASTFM_SHARED_SECRET" : "sample",
 "username" : "sample",
 "password_hash" : "sample",
 "Youtube_Data_API_Key" : "sample",
 "chilledcow_youtube_channel_id" : "UCSJ4gkVC6NrvII8umztf0Ow",
 "song_list_google_doc_id" : "1P0p0SfP_BxiG3I4i8MTYakibsdg_O4753EA-I9h3lL8"
}
```
- You can generate your password_hash by
```
pylast.md5(password)
```


## How does it work
- It gets the live youtube video id using youtube api.
- It gets the list of the songs from the google docs file
- It works in the background and scrobbles every song written in the stream until you kill the script.
- To do that it takes youtube link as argument and extracts the stream url.
- OpenCV opens the stream and captures one single frame every 30 seconds
![Example image](images/img.jpg "Example image")
- Image gets cropped
![Example cropped image](images/img_cropped.jpg "Example cropped image")
- Remove the background
![Example processed image](images/img_cropped_processed.jpg "Example processed image")
- Tesseract-OCR reads the image
- Possible mistakes are fixed by comparing the song with the list of songs and finding the best one.
- Send to Last.FM (if it didn't send it already)

