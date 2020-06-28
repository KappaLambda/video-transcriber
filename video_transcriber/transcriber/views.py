import glob
import json
import os
import re

from django.http import JsonResponse
from django.shortcuts import render

from . import audio2text


def home(request):
    if request.method == 'POST':
        ajax_data = json.loads(request.body)
        print(f'Got json data: {ajax_data}')
        youtube_url = ajax_data['youtube-url']
        regex = r'^(?:https?:\/\/)?(?:m\.|www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))(.{11})$'  # noqa: E501
        youtube_url_valid = re.search(regex, youtube_url)
        if youtube_url_valid:
            youtube_id = youtube_url_valid.group(1)
            print(f'YouTube URL is: {youtube_url}')
            print(f'YouTube ID is: {youtube_id}')
        else:
            error = 'Invalid YouTube URL'
            status_code = 400
            return JsonResponse({'error': error}, status=status_code)

        if not os.path.exists('/var/tmp/video_transcriber_transcript_cache'):
            os.makedirs('/var/tmp/video_transcriber_transcript_cache')

        transcript_cache_path = f'/var/tmp/video_transcriber_transcript_cache/{youtube_id}.txt'  # noqa: E501
        lock_file_path = f'/var/tmp/video_transcriber_transcript_cache/{youtube_id}.lock'  # noqa: E501
        transcript_cache = glob.glob(transcript_cache_path)
        lock_file_exists = glob.glob(lock_file_path)
        print('Filepaths created and checked')

        if lock_file_exists:
            print('Found lock file')
            error = 'Video is being processed...'
            status_code = 503
            response = JsonResponse({'error': error}, status=status_code)
            response['Retry-After'] = 15
            return response

        if transcript_cache:
            print('Found cached transcript')
            with open(transcript_cache_path, 'r') as fh:
                transcript = fh.readlines()

        else:
            print('Creating lock file')
            with open(lock_file_path, 'w') as fh:
                pass

            try:
                print('Begin transcription')
                transcript = audio2text.AudioToText(youtube_id)
                with open(transcript_cache_path, 'w') as fh:
                    fh.write(transcript)

                print('Transcription successfull')

            except Exception as e:
                print(f'Exception class: {type(e)}')
                print(f'Εxception message: {str(e)}')
                if 'This video does not exist' in str(e):
                    error = 'Check youtube id. Video does not exist'
                    status_code = 400
                else:
                    error = 'Internal server error'
                    status_code = 500

                return JsonResponse({'error': error}, status=status_code)

            finally:
                os.remove(lock_file_path)

        return JsonResponse({'transcript': transcript})

    return render(request, 'transcriber/home.html', {})
