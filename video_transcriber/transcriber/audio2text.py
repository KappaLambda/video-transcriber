import io
import logging
import os
import uuid

import pafy
from google.cloud import speech
from pydub import AudioSegment


def AudioFromVideo(url, path, file_identifier, logger):

    # Create a video instance from url givel by user
    video = pafy.new(url)
    logger.info('Pafy video instance created')
    # Create path
    mp4_path = os.path.join(path, f'audio-{file_identifier}.mp4')
    # Get best audio stream and download
    bestaudio = video.getbestaudio(preftype='m4a')
    bestaudio.download(filepath=mp4_path, quiet=True)
    logger.info(f'Downloaded to: {mp4_path}')
    # Convert audio file to 1 channel.
    multi_audio_segment = AudioSegment.from_file(mp4_path, 'mp4')
    logger.info(f'Multi channel audio file: {mp4_path}')
    single_audio_segment = multi_audio_segment.set_channels(1)
    logger.info(f'Single channel audio file: {mp4_path}')

    return single_audio_segment


def SplitAudio(audiofile, path, file_identifier, logger):

    audio_file_remaining_time = len(audiofile)
    audio_file_duration = audio_file_remaining_time
    paths_to_audio_parts = []
    part = 1
    # Checking lenght of audio file and split into one minute parts
    # if it is over one minute. Finally save audio file(s).
    # Time in milliseconds
    logger.info('Splitting to 1 minute parts')
    if audio_file_duration <= 60000:
        flac_part_path = os.path.join(
            path,
            f'audio-{file_identifier}-part{part}.flac',
        )
        audiofile.export(flac_part_path, format='flac')
        paths_to_audio_parts.append(flac_part_path)
        logger.info(f'FLAC audio export to: {flac_part_path}')
    else:
        while audio_file_remaining_time > 60000:
            flac_part_path = os.path.join(
                path,
                f'audio-{file_identifier}-part{part}.flac',
            )
            audio = audiofile[60000*(part-1):60000*part]
            audio.export(flac_part_path, format='flac')
            paths_to_audio_parts.append(flac_part_path)
            part += 1
            audio_file_remaining_time -= 60000
            logger.info(f'FLAC audio export to: {flac_part_path}')

        flac_part_path = os.path.join(
            path,
            f'audio-{file_identifier}-part{part}.flac',
        )
        audio = audiofile[60000*(part-1):audio_file_duration]
        audio.export(flac_part_path, format='flac')
        paths_to_audio_parts.append(flac_part_path)
        logger.info(f'FLAC audio export to: {flac_part_path}')

    return paths_to_audio_parts


def SpeechRecognition(audiofile, logger):

    # Instantiates a client
    speech_client = speech.Client()
    logger.info('Authentication with google speech successfull')

    # Loads the audio into memory
    logger.info(f'Loading for speech recognition: {audiofile}')
    with io.open(audiofile, 'rb') as fh:
        content = fh.read()
        sample = speech_client.sample(
            content,
            source_uri=None,
            encoding='FLAC',
            sample_rate_hertz=44100
        )

    # Detects speech in the audio file
    alternatives = sample.recognize('en-US')
    logger.info('Got alternatives of sample')

    return ' '.join([a.transcript for a in alternatives])


def AudioToText(url):

    # Setting up Logger
    logger = logging.getLogger('AudioText Logger')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '{asctime} - {name} - {levelname} - {message}',
        datefmt='%d/%m/%Y %H:%M:%S',
        style='{'
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    audio_text_logger = logging.getLogger('pydub.converter')
    audio_text_logger.setLevel(logging.DEBUG)
    audio_text_logger.addHandler(logging.StreamHandler())

    logger.info('Got: {url}')
    default_files_path = '/tmp/'
    file_identifier = uuid.uuid4()

    audio_segment = AudioFromVideo(
        url,
        default_files_path,
        file_identifier,
        logger
    )
    logger.info('Audio Segment of video created')
    part_paths = SplitAudio(
        audio_segment,
        default_files_path,
        file_identifier,
        logger
    )
    logger.info('Splitting audio segment to one minute parts finished')

    transcripts = []
    logger.info('Starting speech recognition procedure')
    for path in part_paths:
        try:
            transcript = SpeechRecognition(path, logger)
            logger.info('Got text from {path}')
            logger.info('Segment transcript:\n{transcript}')
        except ValueError:
            logger.warning('No voice in {path}')

        transcripts.append(transcript)

    transcipt_string = ' '.join(transcripts)
    logger.info('Transcript:\n{transcipt_string}')
    logger.info('Success')
    return transcipt_string

# # url = input('Enter YouTube link or Youtube video id:')
# url = 'https://www.youtube.com/watch?v=CDnNH2zV2jw'
# # url = 'https://www.youtube.com/watch?v=9eUl4gF0ED4'
# output = AudioToText(url)
