import os

from google.cloud import texttospeech

from lib.logger import logger


tones = {
    "neutral": {
        "pitch": 2,
        "speaking_rate": 1.0,
    },
    "happy": {
        "pitch": 3,
        "speaking_rate": 1.0,
    },
    "sad": {
        "pitch": 1,
        "speaking_rate": 0.9,
    },
    "angry": {
        "pitch": 1,
        "speaking_rate": 1.1,
    },
    "excited": {
        "pitch": 4,
        "speaking_rate": 1.2,
    },
    "frustrated": {
        "pitch": 1,
        "speaking_rate": 1.0,
    },
    "bored": {
        "pitch": 1,
        "speaking_rate": 0.85,
    },
    "confused": {
        "pitch": 1,
        "speaking_rate": 0.9,
    },
    "disgusted": {
        "pitch": 1,
        "speaking_rate": 1.0,
    },
    "surprised": {
        "pitch": 3,
        "speaking_rate": 1.0,
    },
    "fearful": {
        "pitch": 3,
        "speaking_rate": 1.2,
    },
    "calm": {
        "pitch": 2,
        "speaking_rate": 0.9,
    },
    "tired": {
        "pitch": 1,
        "speaking_rate": 0.8,
    },
    "satisfied": {
        "pitch": 3,
        "speaking_rate": 1.0,
    },
    "aroused": {
        "pitch": 4,
        "speaking_rate": 1.2,
    },
    "seductive": {
        "pitch": 0,
        "speaking_rate": 0.8,
    },
}


def synthesize_speech(input_data, voice_name, tone, user):
    try:
        client = texttospeech.TextToSpeechClient()

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=voice_name,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            pitch=tones[tone]["pitch"],
            speaking_rate=tones[tone]["speaking_rate"],
        )

        response = client.synthesize_speech(
            input=input_data, voice=voice, audio_config=audio_config
        )

        output_file = f'tts_output/{user}_{voice_name}.mp3'
        with open(output_file, "wb") as out_file:
            out_file.write(response.audio_content)
            logger.debug(f'audio content written to file', output_file)

        return output_file
    except Exception as e:
        logger.error(f'error synthesizing speech for {user}: {str(e)}')
        return


def process_text(text, voice_name, tone, user):
    input_text = texttospeech.SynthesisInput(text=text)
    return synthesize_speech(input_text, voice_name, tone, user)


def process_ssml(ssml, voice_name, tone, user):
    input_ssml = texttospeech.SynthesisInput(ssml=ssml)
    return synthesize_speech(input_ssml, voice_name, tone, user)


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'google-cloud-service-account.json'
