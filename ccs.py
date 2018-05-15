#!/usr/bin/env python3
import cv2
import pafy
import numpy as np
import time
from PIL import Image
import pytesseract
import pylast
import difflib
import sys
import json

def main():
    if len(sys.argv) < 3:
        print("Usage: python ccs.py <credentials.json> <chilledcow_youtube_stream_link>")
        sys.exit()
    credentials_file = sys.argv[1]
    with open(credentials_file, "r") as f:
        credentials = json.load(f)
    url = sys.argv[2]
    stream = get_video_url(url)
    prev_song_details = ""
    lastfm_network = pylast.LastFMNetwork(api_key=credentials["LASTFM_API_KEY"], api_secret=credentials["LASTFM_SHARED_SECRET"], \
                     username= credentials["username"], password_hash=credentials["password_hash"])
    while True:
        image_file = take_snapshot(stream)
        cropped_image_file = cut_image(image_file)
        processed_image_file = cv2_process(cropped_image_file)
        song_details = tesseract_ocr_read(processed_image_file)
        diff_flag = diff_song_details(prev_song_details, song_details)
        if diff_flag:
            prev_song_details = song_details
            artist, song = check_song_details(song_details)
            if artist is not None:
                scrobble_to_lastfm(lastfm_network, artist, song)
        time.sleep(30)
        
def get_video_url(youtube_link):
    videoPafy = pafy.new(youtube_link)
    # print(videoPafy)
    best = videoPafy.getbest()
    # print(best)
    stream = best.url
    # print("Stream link: {}".format(stream))
    return stream

def take_snapshot(stream):
    capture = cv2.VideoCapture(stream)
    success, image = capture.read()
    if not success:
        print("OpenCV can't read video stream.") 
        sys.exit()
    image_file = "img.jpg"
    cv2.imwrite(image_file, image)
    capture.release()
    # print("Snapshot taken")
    return image_file

def cut_image(image):
    img = Image.open(image)
    width = img.size[0]
    area = (0, 0, width, 50)
    cropped_img = img.crop(area)
    new_image = image.split(".")[0]+"_cropped.jpg"
    cropped_img.save(new_image)
    # print("Snapshot cropped")
    return new_image

def cv2_process(image):
    img = cv2.imread(image)
    low = np.array([200,200,200])
    up = np.array([255,255,255])
    mask = cv2.inRange(img, low, up)
    res = cv2.bitwise_and(img,img, mask= mask)
    new_image = image.split(".")[0]+"_processed.jpg"
    cv2.imwrite(new_image, res)
    # print("Snapshot background removed")
    return new_image

def tesseract_ocr_read(image):
    img = Image.open(image)
    song_details = pytesseract.image_to_string(img)
    # print("Song details read by tesseract")
    return song_details

def diff_song_details(previous_song_details, song_details):
    seq = difflib.SequenceMatcher(a=previous_song_details.lower(), b=song_details.lower())
    # print("Similarity ratio: {}".format(seq.ratio()))
    if seq.ratio() < 0.95:
        return True
    else:
        return False

def check_song_details(song_details):
    song_info = song_details.split(" - ")
    if len(song_info) == 2:
        artist, song = song_info
        return artist, song
    else:
        return None, None

def scrobble_to_lastfm(lastfm_network, artist, song):
    timestamp = int(time.time())
    lastfm_network.scrobble(artist, song, timestamp)
    print("Scrobble completed: {} - {}".format(artist, song))

if __name__ == '__main__':
    main()