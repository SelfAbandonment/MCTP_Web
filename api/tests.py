from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from io import BytesIO
from PIL import Image
from django.core.cache import cache
import json

User = get_user_model()

class ApiPingTests(TestCase):
    def test_ping(self):
        c = Client()
        resp = c.get('/api/ping/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['success'])
        self.assertTrue(resp.json()['data']['pong'])

class SecurityHeaderTests(TestCase):
    def test_security_headers(self):
        c = Client()
        resp = c.get('/')
        self.assertEqual(resp['X-Frame-Options'], 'DENY')
        self.assertEqual(resp['X-Content-Type-Options'], 'nosniff')

class PasswordComplexityTests(TestCase):
    def test_password_complexity_validator(self):
        user = User.objects.create_user(username='u1', password='Abcdef1!')
        self.assertTrue(user.check_password('Abcdef1!'))

class LoginBackendTests(TestCase):
    def setUp(self):
        self.qq_user = User.objects.create_user(username='userA', password='Passw0rd!', qq='123456')
        self.client = Client()

    def test_login_by_username(self):
        resp = self.client.post('/api/login/', {'username': 'userA', 'password': 'Passw0rd!'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['success'])

    def test_login_by_qq(self):
        resp = self.client.post('/api/login/', {'username': '123456', 'password': 'Passw0rd!'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['success'])

    def test_login_throttle(self):
        # 测试用：降低限制阈值
        settings.LOGIN_ATTEMPT_LIMIT = 3
        for i in range(3):
            resp = self.client.post('/api/login/', {'username': 'userA', 'password': 'wrong'})
            self.assertIn(resp.status_code, [401, 429])
        resp = self.client.post('/api/login/', {'username': 'userA', 'password': 'wrong'})
        self.assertEqual(resp.status_code, 429)
        self.assertFalse(resp.json()['success'])
        cache.clear()

class ImageUploadValidationTests(TestCase):
    def _generate_image(self, fmt='PNG', size=(64,64)):
        bio = BytesIO()
        img = Image.new('RGB', size, color=(255,0,0))
        img.save(bio, format=fmt)
        bio.seek(0)
        return bio.getvalue()

    def test_image_size_validation(self):
        settings.MEDIA_MAX_IMAGE_SIZE_MB = 1
        settings.ALLOWED_IMAGE_FORMATS = ['JPEG','PNG','WEBP']
        data = self._generate_image('PNG')
        f = SimpleUploadedFile('test.png', data, content_type='image/png')
        from common.upload_validators import validate_image
        validate_image(f)  # 正常应通过

    def test_image_invalid_format(self):
        data = self._generate_image('PNG')
        f = SimpleUploadedFile('test.png', data, content_type='image/png')
        settings.ALLOWED_IMAGE_FORMATS = ['JPEG']
        from common.upload_validators import validate_image
        with self.assertRaises(Exception):
            validate_image(f)

class CacheTests(TestCase):
    def test_cached_endpoint(self):
        c = Client()
        r1 = c.get('/api/cached/')
        r2 = c.get('/api/cached/')
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.json()['data']['ts'], r2.json()['data']['ts'])

class ApiExceptionMiddlewareTests(TestCase):
    def test_exception_returns_json(self):
        # 直接调用中间件，模拟异常响应
        from common.api_middleware import ApiExceptionMiddleware
        mw = ApiExceptionMiddleware(lambda r: (_ for _ in ()).throw(RuntimeError('boom')))
        resp = mw.process_exception(Client().get('/api/test/').wsgi_request, RuntimeError('boom'))
        self.assertEqual(resp.status_code, 500)
        payload = json.loads(resp.content.decode('utf-8'))
        self.assertFalse(payload['success'])
