import os
import json
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import UploadFileForm

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .utils.suppliers import extract_suppliers_and_cities, save_suppliers_and_cities


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_success')  # Redirect to a success page
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})



def upload_success(request):
    return render(request, 'upload_success.html')


def services_index(request):
    return render(request, 'services_index.html')


def list_files(request):
    # Get the path to the uploads directory
    uploads_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')

    # List all files in the uploads directory
    files = os.listdir(uploads_dir)

    # Filter out directories, keep only files
    files = [f for f in files if os.path.isfile(os.path.join(uploads_dir, f))]

    return render(request, 'services_index.html', {'files': files})


@csrf_exempt
def delete_file(request):
    if request.method == 'POST':
        try:
            # Load the JSON data from the request body
            data = json.loads(request.body)
            filename = data.get('filename')  # Get the filename from the JSON data

            if filename is None:
                return JsonResponse({'error': 'Filename not provided'}, status=400)

            file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                return JsonResponse({'success': True})
            return JsonResponse({'error': 'File not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def upload_suppliers(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        filename = data.get('filename')
        file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()  # Read the file content
                suppliers = extract_suppliers_and_cities(content)
                print("Extracted suppliers and cities:", suppliers)  # Debugging output
                save_suppliers_and_cities(suppliers)

            return JsonResponse({'content': content})  # Return the content as JSON
        except Exception as e:
            print("Error occurred:", str(e))  # Log the error for debugging
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
