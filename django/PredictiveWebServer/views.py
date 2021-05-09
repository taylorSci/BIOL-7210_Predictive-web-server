import mimetypes

from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings


def redirect(request):
    return HttpResponseRedirect('fbp/')


def download_results(request, userEmail, fileName):
    with open(f'{settings.MEDIA_ROOT}{userEmail}/{fileName}', 'rb') as dl:
        mimeType = mimetypes.guess_type(f'{fileName}')
        response = HttpResponse(dl, content_type=mimeType)
        response['Content-Disposition'] = f"attachment; filename={fileName}"
        return response
