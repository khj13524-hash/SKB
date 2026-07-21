"""
SKnow 통합 프록시 서버 (Naver API + KOSIS API)
----------------------------------------------
v2.html에서 외부 API를 사용하기 위한 로컬 서버입니다.
- 네이버 뉴스 API: 경쟁사 동향 검색
- KOSIS API: 통계청 인구·세대수·연령대 실제 데이터
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
from proxy_config import KOSIS_KEY

PORT = 8888

class ProxyHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path   = parsed.path  # e.g. '/kosis' or '/'

        if path == '/kosis':
            self._handle_kosis(parsed.query)
        else:
            self._handle_naver(parsed.query)

    # ── Naver 뉴스 검색 ──────────────────────────────
    def _handle_naver(self, query_string):
        params  = urllib.parse.parse_qs(query_string)
        q       = params.get('q', [''])[0]
        display = params.get('display', ['6'])[0]
        sort    = params.get('sort', ['date'])[0]

        cid  = self.headers.get('X-Naver-Client-Id', '')
        csec = self.headers.get('X-Naver-Client-Secret', '')

        if not cid or not csec:
            self._json(400, {'error': '네이버 API 키가 없습니다'})
            return

        url = (
            'https://openapi.naver.com/v1/search/news.json'
            f'?query={urllib.parse.quote(q)}&display={display}&sort={sort}'
        )
        req = urllib.request.Request(url, headers={
            'X-Naver-Client-Id':     cid,
            'X-Naver-Client-Secret': csec,
        })
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._cors()
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self._json(500, {'error': str(e)})

    # ── KOSIS 통계청 API ─────────────────────────────
    def _handle_kosis(self, query_string):
        # apiKey는 서버에서 주입 (클라이언트에 노출 안 됨)
        params = urllib.parse.parse_qs(query_string)
        qs = {k: v[0] for k, v in params.items()}
        qs['apiKey'] = KOSIS_KEY

        url = 'https://kosis.kr/openapi/Param/statisticsParamData.do?' + urllib.parse.urlencode(qs)
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = resp.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._cors()
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self._json(500, {'error': str(e)})

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin',  '*')
        self.send_header('Access-Control-Allow-Headers',
                         'X-Naver-Client-Id, X-Naver-Client-Secret, Content-Type')

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


if __name__ == '__main__':
    print('━' * 50)
    print('  SKnow 통합 프록시 서버 실행 중')
    print(f'  포트: {PORT}')
    print('  Naver API + KOSIS 통계청 API 지원')
    print('  이 창을 닫으면 API 연동이 중단됩니다.')
    print('━' * 50)
    HTTPServer(('localhost', PORT), ProxyHandler).serve_forever()
