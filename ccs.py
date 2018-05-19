#!/usr/bin/env python3
import cv2
import pafy
import numpy as np
import time
import requests
from PIL import Image
import pytesseract
import pylast
import difflib
import sys
import json

def main():
    if len(sys.argv) < 2:
        print("Usage: python ccs.py <data_file_json>")
        sys.exit()
    data_file = sys.argv[1]
    with open(data_file, "r") as f:
        data = json.load(f)
    url = get_live_video_url(data["Youtube_Data_API_Key"], data["chilledcow_youtube_channel_id"])
    stream = get_video_url(url)
    prev_song_details = ""
    lastfm_network = pylast.LastFMNetwork(api_key=data["LASTFM_API_KEY"], api_secret=data["LASTFM_SHARED_SECRET"], \
                     username=data["username"], password_hash=data["password_hash"])
    document = get_doc_file(data["song_list_google_doc_id"])
    entries = get_entries_from_doc(document)
    while True:
        image_file = take_snapshot(stream)
        cropped_image_file = cut_image(image_file)
        processed_image_file = cv2_process(cropped_image_file)
        song_details = tesseract_ocr_read(processed_image_file)
        matched_song_details, confidence = find_closest_match_from_entries(entries, song_details)
        diff_flag = diff_song_details(prev_song_details, matched_song_details)
        if diff_flag:
            prev_song_details = matched_song_details
            artist, song = check_song_details(matched_song_details)
            if artist is not None:
                scrobble_to_lastfm(lastfm_network, artist, song, confidence)
        time.sleep(30)

def get_live_video_url(youtube_data_api_key, chilledcow_youtube_channel_id):
    request_link = "https://www.googleapis.com/youtube/v3/search?order=date&part=snippet&channelId={}&maxResults=5&key={}"
    new_request_link = request_link.format(chilledcow_youtube_channel_id, youtube_data_api_key)
    response = requests.get(new_request_link, allow_redirects=True)
    response = response.json()
    for item in response["items"]:
        if item["snippet"]["liveBroadcastContent"] == "live":
            return item["id"]["videoId"]
            
def get_doc_file(song_list_google_doc_id):
    request_link = "https://docs.google.com/document/d/{}/export?format={}"
    new_request_link = request_link.format(song_list_google_doc_id, "txt")
    response = requests.get(new_request_link)
    response = response.text
    return response

def get_entries_from_doc(document):
    entries = []
    for line in document.split("\n"):
        if " - " in line:
            entries.append(line.strip())
    return entries

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

def find_closest_match_from_entries(entries, song_details):
    max_similarity_score = 0
    matched_entry = ""
    for entry in entries:
        seq = difflib.SequenceMatcher(a=entry.lower(), b=song_details.lower())
        similarity_score = seq.ratio()
        if similarity_score > max_similarity_score:
            max_similarity_score = similarity_score
            matched_entry = entry
    # print(song_details, " | ", matched_entry,  " | ", max_similarity_score)
    return matched_entry, max_similarity_score


def diff_song_details(previous_song_details, song_details):
    seq = difflib.SequenceMatcher(a=previous_song_details.lower(), b=song_details.lower())
    similarity_score = seq.ratio()
    # print("Similarity ratio: {}".format(similarity_score))
    if similarity_score < 0.8:
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

def scrobble_to_lastfm(lastfm_network, artist, song, confidence):
    timestamp = int(time.time())
    lastfm_network.scrobble(artist, song, timestamp)
    print("Scrobled: {} - {} ({}% confidence)".format(artist, song, int(confidence*100)))

if __name__ == '__main__':
    main()