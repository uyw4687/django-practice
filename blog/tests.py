from django.test import TestCase, Client
import json
from .models import Article, Comment
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class BlogTestCase(TestCase):
    def test_csrf(self):
        # By default, csrf checks are disabled in test client
        # To test csrf protection we enforce csrf checks here
        client = Client(enforce_csrf_checks=True)
        response = client.post('/api/signup/', json.dumps({'username': 'chris', 'password': 'chris'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  # Request without csrf token returns 403 response

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        response = client.post('/api/signup/', json.dumps({'username': 'chris', 'password': 'chris'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)  # Pass csrf protection

    def test_model_str(self):
        test_user = User.objects.create_user(username='testusername', password='testpassword')
        test_article = Article.objects.create(title='test_title', content='test_content', author=test_user)
        test_comment = Comment.objects.create(article=test_article, content='test_content', author=test_user)
        self.assertEqual(test_article.__str__(), "test_title")
        self.assertEqual(test_comment.__str__(), "test_content")
        
    def test_sign(self):
        client = Client(enforce_csrf_checks=True)

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie
        response = client.get('/api/signout/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)
        response = client.post('/api/signup/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)
        response = client.post('/api/signin/', json.dumps({'username': 'chris', 'password': 'notchris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)
        response = client.post('/api/signin/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 204)
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie
        response = client.get('/api/signout/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 204)

    def test_HTTPResponse_405(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie
        client.post('/api/signup/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        response = client.post('/api/signin/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        #starts here
        response = client.post('/api/token/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)
        response = client.get('/api/signup/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)
        response = client.get('/api/signin/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)
        response = client.post('/api/signout/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)
        response = client.delete('/api/article/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)
        response = client.post('/api/article/3/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)
        response = client.delete('/api/article/1/comment/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)
        response = client.post('/api/comment/2/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)

    def test_HTTPResponse_401(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        #starts here
        response = client.get('/api/article/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)
        response = client.post('/api/article/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)
        response = client.get('/api/article/1/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)
        response = client.put('/api/article/1/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)
        response = client.delete('/api/article/1/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)
        response = client.get('/api/article/1/comment/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)
        response = client.post('/api/article/1/comment/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)
        response = client.get('/api/comment/1/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)
        response = client.put('/api/comment/1/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)
        response = client.delete('/api/comment/1/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)

    def test_HTTPResponse_404(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie
        client.post('/api/signup/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        response = client.post('/api/signin/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        #starts here
        response = client.get('/api/article/1/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 404)
        response = client.put('/api/article/1/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 404)
        response = client.delete('/api/article/1/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 404)
        response = client.get('/api/article/1/comment/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 404)
        response = client.post('/api/article/1/comment/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 404)
        response = client.get('/api/comment/1/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 404)
        response = client.put('/api/comment/1/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 404)
        response = client.delete('/api/comment/1/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 404)

    def test_HTTPResponse_403(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie
        client.post('/api/signup/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        response = client.post('/api/signin/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        #starts here
        test_user = User.objects.create_user(username='testusername', password='testpassword')
        test_article = Article.objects.create(title='test_title', content='test_content', author=test_user)
        test_comment = Comment.objects.create(article=test_article, content='test_content', author=test_user)
        response = client.put('/api/article/1/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 403)
        response = client.delete('/api/article/1/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 403)
        response = client.put('/api/comment/1/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 403)
        response = client.delete('/api/comment/1/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 403)

    def test_HTTPResponse_400(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie
        client.post('/api/signup/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        response = client.post('/api/signin/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie


        #starts here
        test_user = authenticate(username='chris', password='chris')
        test_article = Article.objects.create(title='test_title', content='test_content', author=test_user)
        test_comment = Comment.objects.create(article=test_article, content='test_content', author=test_user)
        response = client.post('/api/signup/', json.dumps({'x': 'chris', 'y': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)
        response = client.post('/api/signin/', json.dumps({'x': 'chris', 'y': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)
        response = client.post('/api/article/', json.dumps({'x': 'chris', 'y': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)
        response = client.put('/api/article/1/', json.dumps({'x': 'chris', 'y': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)
        response = client.post('/api/article/1/comment/', json.dumps({'x': 'chris', 'y': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)
        response = client.put('/api/comment/1/', json.dumps({'x': 'chris', 'y': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)

    def test_article_comment(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie
        client.post('/api/signup/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        response = client.post('/api/signin/', json.dumps({'username': 'chris', 'password': 'chris'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        #starts here
        response = client.get('/api/article/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)

        test_user = authenticate(username='chris', password='chris')

        response = client.post('/api/article/', json.dumps({'title': 'chris', 'content': 'chris_domati'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)
        self.assertIsInstance(response.json()['id'], int)
        self.assertEqual(response.json()['author'], test_user.id)
        self.assertEqual(response.json()['title'], 'chris')
        self.assertEqual(response.json()['content'], 'chris_domati')
        test_articles = response.json()

        response = client.post('/api/article/', json.dumps({'title': 'chrisx', 'content': 'chris_domatix'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['author'], test_user.id)
        self.assertEqual(response.json()['title'], 'chrisx')
        self.assertEqual(response.json()['content'], 'chris_domatix')

        response = client.get('/api/article/1/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['author'], test_user.id)
        self.assertEqual(response.json()['title'], 'chris')
        self.assertEqual(response.json()['content'], 'chris_domati')

        response = client.put('/api/article/1/', json.dumps({'title': 'chrispy', 'content': 'doughnut'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.json()['author'], test_user.id)
        self.assertEqual(response.json()['title'], 'chrispy')
        self.assertEqual(response.json()['content'], 'doughnut')

        response = client.post('/api/article/1/comment/', json.dumps({'content': 'chris_domatix is here'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['article'], test_articles['id'])
        self.assertEqual(response.json()['content'], 'chris_domatix is here')
        self.assertEqual(response.json()['author'], test_user.id)
        
        response = client.get('/api/article/1/comment/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()[0]['id'], int)
        self.assertEqual(response.json()[0]['article'], test_articles['id'])
        self.assertEqual(response.json()[0]['content'], 'chris_domatix is here')
        self.assertEqual(response.json()[0]['author'], test_user.id)

        response = client.get('/api/comment/1/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['article'], test_articles['id'])
        self.assertEqual(response.json()['content'], 'chris_domatix is here')
        self.assertEqual(response.json()['author'], test_user.id)

        response = client.put('/api/comment/1/', json.dumps({'content': 'doughnut'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.json()['article'], test_articles['id'])
        self.assertEqual(response.json()['content'], 'doughnut')
        self.assertEqual(response.json()['author'], test_user.id)

        response = client.post('/api/article/1/comment/', json.dumps({'content': 'chris_domatix is not here'}), 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)

        response = client.delete('/api/comment/2/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)

        response = client.get('/api/comment/1/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)

        response = client.delete('/api/article/1/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)

        response = client.get('/api/comment/1/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 404)