import requests

rachel_voice_id = '21m00Tcm4TlvDq8ikWAM'
daniel_1_voice_id = 'Gogkxoul0LAwgcsm40y9'
daniel_2_voice_id = 'amFKNICHLcUGZQOsBIrZ'

ELEVENLABS_API_KEY = ""
ELEVENLABS_VOICE_ID = ""

ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1/"
ELEVENLABS_TTS = "text-to-speech/{voice_id}?optimize_streaming_latency=0"
ELEVENLABS_VOICES = "voices"

ELEVENLABS_TTS_URL = ELEVENLABS_BASE_URL + ELEVENLABS_TTS
ELEVENLABS_VOICES = ELEVENLABS_BASE_URL + ELEVENLABS_VOICES


def convert_to_sound(text, voice_id=rachel_voice_id) -> bytes:
    """
    Convert text to sound using the ElevenLabs Text-to-Speech API.

    Parameters:
        text (str): The text to convert to sound.
        voice_id (star): The voice id of the of the voice from Elevenlabs

    Returns:
        bytes: The audio content as bytes if successful, else None.
    """
    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }

    elevenlabs_tts_url = ELEVENLABS_TTS_URL.format(voice_id=voice_id)

    try:
        # TODO Add handling for no API tokens
        response = requests.post(elevenlabs_tts_url,
                                 headers=headers,
                                 json=payload)
        if response.status_code == 200:
            audio = response.content
            return audio
    except requests.exceptions.RequestException as e:
        # TODO convert this to logging
        print("Error converting text to sound:", e)

    return None


def query_voices() -> dict:
    """
    Query the ElevenLabs Text-to-Speech API to retrieve available voices.

    Returns:
        dict: The JSON response containing the available voices if successful, else None.
    """
    headers = {"accept": "application/json", "xi-api-key": ELEVENLABS_API_KEY}

    try:
        # TODO Add handling for no API tokens
        response = requests.get(ELEVENLABS_VOICES, headers=headers)
        if response.status_code == 200:
            voices = response.json()["voices"]
            voice_info = [{
                "voice_id": voice["voice_id"],
                "name": voice["name"]
            } for voice in voices]
            return {"voices": voice_info}
    except requests.exceptions.RequestException as e:
        # TODO convert this to logging
        print("Error querying voices:", e)

    return None


def set_elevenlabs_api_key(api_key):
    """
    Set the ElevenLabs API key.

    Parameters:
        api_key (str): The ElevenLabs API key.
    """
    global ELEVENLABS_API_KEY
    ELEVENLABS_API_KEY = api_key

def is_api_key_set() -> bool:
    """
    Check if the ElevenLabs API key has been set.

    Returns:
        bool: True if the API key is set, False otherwise.
    """
    return bool(ELEVENLABS_API_KEY)