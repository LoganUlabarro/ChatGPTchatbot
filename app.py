from openai import OpenAI
import os
import requests
import config as conf
import speech_recognition as sr
import pyttsx3 
import keyboard
from playsound import playsound
from time import sleep
import random

client = OpenAI()

def speak_with_pyttsx3(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_chatgpt_response(prompt):
    # Get the API key from the environment variable
    if not conf.open_ai_key:
        raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

    # Set up the OpenAI API client

    # Send a request to the ChatGPT model
    response = client.chat.completions.create(model="gpt-3.5-turbo",  # Change the model name if needed
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=150)

    # Extract and return the assistant's response
    return response.choices[0].message.content

def send_to_lab(payload, headers, CHUNK_SIZE):
    responseLAB = requests.request("POST", conf.eleven_labs_url, json=payload, headers=headers, params=conf.querystring)
    if responseLAB.status_code == 200:
        with open('output.mp3', 'wb') as f:
            for chunk in responseLAB.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
                else:
                    print("Audio URL not found in the response.")
    else:
        print(f"Failed to get audio response. Status code: {responseLAB.status_code}")
        print(responseLAB.json())

def get_payload(text, stab, sim, style):
    payload = {
            "text": text,
            "voice_settings": {
            "stability": stab,
            "similarity_boost": sim,
            "style": style
            }
        }
    return payload

def get_headers(key):
    headers = {
            "xi-api-key": key,
            "Content-Type": "application/json"
        }
    return headers

def get_random_float():
    rand_float = random.uniform(0,1)
    formatted_float= float(f"{rand_float:.2f}")
    return formatted_float
    
if __name__ == "__main__":
    audio_file = os.path.dirname(__file__) + '\\output.mp3'

    #setup voice recognition
    r = sr.Recognizer()
    r.dynamic_energy_threshold = True  # Enable dynamic energy threshold
    r.energy_threshold = 300  # Set initial energy threshold, adjust as needed
    r.pause_threshold = 0.8  # Seconds of non-speaking audio before a phrase is considered complete

    while True:
        if keyboard.is_pressed('alt'):
            try:
                # Use the microphone as source for input
                with sr.Microphone() as source2:
                    # Wait for a second to let the recognizer adjust the energy threshold
                    r.adjust_for_ambient_noise(source2, duration=0.2)

                    # Listen for the user's input
                    audio2 = r.listen(source2)

                    # Using Google to recognize audio
                    MyText = r.recognize_google(audio2)
                    MyText = MyText.lower()

                    print("Heard:", MyText)
                    responseGPT = get_chatgpt_response(MyText)
                    print("GPT response:", responseGPT)
                    if conf.eleven_labs_voice:
                        fileExists = False
                        payload = get_payload(responseGPT, get_random_float(), get_random_float(), get_random_float())
                        headers = get_headers(conf.eleven_labs_key)
                        send_to_lab(payload, headers, conf.eleven_labs_chunk_size)
                        while not fileExists:
                            file_exists = os.path.exists(audio_file)
                            if file_exists:
                                try:
                                    with open(audio_file, 'rb') as f:
                                        f.read()  # Try to read the file to ensure it's accessible
                                    sleep(1)
                                    playsound(audio_file)
                                    sleep(1)
                                    os.remove(audio_file)
                                    fileExists = True
                                except Exception as e:
                                    sleep(0.1)
                    else:
                        speak_with_pyttsx3(responseGPT)
            except sr.RequestError as e:
                print("Could not request results; {0}".format(e))

            except sr.UnknownValueError:
                print("unknown error occurred")
                
            except ValueError as e:
                print(e)
        elif keyboard.is_pressed('end'):
            print("Ending program")
            break
    