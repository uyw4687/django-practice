from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed, JsonResponse
import json
from django.contrib.auth.models import User
from .models import Article, Comment
from json import JSONDecodeError
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict

@ensure_csrf_cookie
def token(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(['GET'])

def signup(request):
    if request.method == 'POST':
        try:
            req_data = json.loads(request.body.decode())
            username = req_data['username']
            password = req_data['password']
        except (KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()
        User.objects.create_user(username=username, password=password)
        return HttpResponse(status=201)
    else:
        return HttpResponseNotAllowed(['POST'])

def signin(request):
    if request.method == 'POST':
        try:
            req_data = json.loads(request.body.decode())
            username = req_data['username']
            password = req_data['password']
        except (KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=401)
    else:
        return HttpResponseNotAllowed(['POST'])

def signout(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            logout(request)
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=401)
    else:
        return HttpResponseNotAllowed(['GET'])

def article(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            article_all_list = [model_to_dict(article) for article in Article.objects.all()]
            return JsonResponse(article_all_list, safe=False, status=200)
        else:
            return HttpResponse(status=401)
    elif request.method == 'POST':
        if request.user.is_authenticated:
            try:
                body = request.body.decode()
                article_title = json.loads(body)['title']
                article_content = json.loads(body)['content']
            except (KeyError, JSONDecodeError) as e:
                return HttpResponseBadRequest()
            article = Article(title=article_title, content=article_content, author=request.user)
            article.save()
            return JsonResponse(model_to_dict(article), status=201)

        else:
            return HttpResponse(status=401)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])

def article_detail(request, article_id):

    if request.method == 'GET':
        if request.user.is_authenticated:
            article = get_object_or_404(Article, pk=article_id)
            return JsonResponse(model_to_dict(article), status=200)
        else:
            return HttpResponse(status=401)

    elif request.method == 'PUT':
        if request.user.is_authenticated:
            article = get_object_or_404(Article, pk=article_id)
            if article.author == request.user: 
                try:
                    body = request.body.decode()
                    article_title = json.loads(body)['title']
                    article_content = json.loads(body)['content']
                except (KeyError, JSONDecodeError) as e:
                    return HttpResponseBadRequest()
                article.title = article_title
                article.content=article_content
                article.save()
                return JsonResponse(model_to_dict(article), status=201)
            else:
                return HttpResponseForbidden()
        else:
            return HttpResponse(status=401)
    elif request.method == 'DELETE':
        if request.user.is_authenticated:
            article = get_object_or_404(Article, pk=article_id)
            if article.author == request.user: 
                article.delete()
                return HttpResponse(status=200)
            else:
                return HttpResponseForbidden()
        else:
            return HttpResponse(status=401)
    else:
        return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])

def comment_detail(request, comment_id):

    if request.method == 'GET':
        if request.user.is_authenticated:
            comment = get_object_or_404(Comment, pk=comment_id)
            return JsonResponse(model_to_dict(comment), status=200)
        else:
            return HttpResponse(status=401)

    elif request.method == 'PUT':
        if request.user.is_authenticated:
            comment = get_object_or_404(Comment, pk=comment_id)
            if comment.author == request.user: 
                try:
                    body = request.body.decode()
                    comment_content = json.loads(body)['content']
                except (KeyError, JSONDecodeError) as e:
                    return HttpResponseBadRequest()
                comment.content=comment_content
                comment.save()
                return JsonResponse(model_to_dict(comment), status=201)
            else:
                return HttpResponseForbidden()
        else:
            return HttpResponse(status=401)
    elif request.method == 'DELETE':
        if request.user.is_authenticated:
            comment = get_object_or_404(Comment, pk=comment_id)
            if comment.author == request.user: 
                comment.delete()
                return HttpResponse(status=200)
            else:
                return HttpResponseForbidden()
        else:
            return HttpResponse(status=401)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])

def article_comment(request, article_id):
    
    if request.method == 'GET':
        if request.user.is_authenticated:
            article = get_object_or_404(Article, pk=article_id)
            comment_all_list = [model_to_dict(comment) for comment in article.comment_set.all()]
            return JsonResponse(comment_all_list, safe=False, status=200)
        else:
            return HttpResponse(status=401)
            
    elif request.method == 'POST':
        if request.user.is_authenticated:
            article = get_object_or_404(Article, pk=article_id)
            try:
                body = request.body.decode()
                comment_content = json.loads(body)['content']
            except (KeyError, JSONDecodeError) as e:
                return HttpResponseBadRequest()
            comment = Comment(article=article, content=comment_content, author=request.user)
            comment.save()
            return JsonResponse(model_to_dict(comment), status=201)
        else:
            return HttpResponse(status=401)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])
