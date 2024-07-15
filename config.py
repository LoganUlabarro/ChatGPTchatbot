import os

#API_Keys
open_ai_key=os.getenv("OPENAI_API_KEY")
eleven_labs_key=os.getenv("ELEVEN_LABS_KEY")

#Settings for 11 labs or pyttsx3
eleven_labs_voice=False #if set to false, uses pytts. This will save you credits on 11 Labs
eleven_labs_chunk_size=1024
querystring = {"enable_logging":"true"}
eleven_labs_url="https://api.elevenlabs.io/v1/text-to-speech/tVkOo4DLgZb89qB0x4qP"