import hashlib
import hmac
import os

from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from git import Repo


def hello_world(request):
    return render(request, 'hello_world.html')


@csrf_exempt
def update_server(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST requests are supported.')

    secret = os.getenv('DEPLOY_WEBHOOK_SECRET')
    signature = request.headers.get('X-Hub-Signature-256')
    if not secret or not signature:
        return HttpResponseForbidden('Webhook signature is required.')

    expected_signature = 'sha256=' + hmac.new(
        secret.encode(), request.body, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        return HttpResponseForbidden('Invalid webhook signature.')

    if request.headers.get('X-GitHub-Event') != 'push':
        return JsonResponse({'status': 'ignored'})

    repo_path = os.getenv('DEPLOY_REPOSITORY_PATH')
    if not repo_path:
        return HttpResponseBadRequest('DEPLOY_REPOSITORY_PATH is not configured.')

    repo = Repo(repo_path)
    repo.remotes.origin.pull()
    return JsonResponse({'status': 'updated'})