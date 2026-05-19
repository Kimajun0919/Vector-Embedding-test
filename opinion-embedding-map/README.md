# AI 공공서비스 시민 의견 임베딩 지도

## 1. 프로젝트 개요

이 프로젝트는 "AI 기반 공공서비스 도입에 대한 시민 의견" 100건을 LUXIA Cloud Vector Embedding API로 임베딩하고, cosine similarity로 의미적 유사도를 계산한 뒤, UMAP으로 2차원 좌표를 생성해 Plotly.js 기반 인터랙티브 의견 지도로 시각화하는 로컬 풀스택 프로토타입입니다.

프론트엔드는 FastAPI 백엔드만 호출하며, LUXIA API 키는 `backend/.env`에만 저장됩니다. 브라우저에는 API 키가 전달되지 않습니다.

## 2. 주요 기능

- 더미 의견 100건 제공
- 주관식, 객관식-단일, 객관식-복수 응답 유형 제공
- LUXIA 임베딩 생성
- cosine similarity 기반 유사 의견 탐색
- UMAP 기반 2D 좌표 생성
- Plotly 기반 의견 지도 시각화
- 의견 클릭 시 Top 5 유사 의견 표시

## 데이터 구조

샘플 데이터는 찬성/반대 입장 필드를 사용하지 않고, 설문 응답 유형을 기준으로 구성합니다.

```python
{
  "id": "opinion_001",
  "text": "AI 공공서비스는 행정 처리 속도를 높일 수 있어 도입이 필요하다고 생각합니다.",
  "responseType": "주관식",
  "category": "효율성"
}
```

응답 유형 분포:

- 주관식: 40건
- 객관식-단일: 30건
- 객관식-복수: 30건

## 3. 실행 방법

### Backend

```bash
cd opinion-embedding-map/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

Windows PowerShell에서는 가상환경 활성화와 파일 복사를 다음처럼 실행할 수 있습니다.

```powershell
cd opinion-embedding-map/backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn main:app --reload
```

### Frontend

```bash
cd opinion-embedding-map/frontend
npm install
npm run dev
```

Vite 개발 서버는 기본적으로 `http://localhost:5173`에서 실행되며, `/api` 요청은 `http://localhost:8000`의 FastAPI 서버로 프록시됩니다.

## 4. .env 설정

`backend/.env.example`:

```env
LUXIA_API_KEY=your_luxia_api_key_here
LUXIA_EMBEDDING_URL=https://bridge.luxiacloud.com/luxia/v1/embedding
LUXIA_EMBEDDING_BATCH_SIZE=20
```

LUXIA 문서 기준으로 백엔드는 `POST https://bridge.luxiacloud.com/luxia/v1/embedding`에 `apikey` 헤더와 `inputs` 본문을 보내 임베딩을 생성합니다.

## 5. 의견 지도 해석 방법

- 각 점은 시민 의견 1건을 의미합니다.
- 가까운 점은 의미적으로 유사한 의견입니다.
- 멀리 떨어진 점은 상대적으로 다른 관점의 의견입니다.
- x축과 y축 자체에는 고정된 의미가 없습니다.
- 좌표는 UMAP 알고리즘이 임베딩 벡터 간 거리 관계를 2차원으로 축소한 결과입니다.

## 6. 유사도 기준

- cosine similarity >= 0.90: 거의 동일한 의견
- cosine similarity >= 0.82: 강한 유사 의견
- cosine similarity >= 0.75: 관련 의견
- cosine similarity < 0.75: 약한 관련 또는 비유사 의견

## 7. 주의사항

- 본 프로젝트는 프로토타입입니다.
- 실제 운영 환경에서는 대량 데이터 처리를 위해 vector DB 또는 ANN 검색 구조가 필요합니다.
- 10만 건 이상 데이터에서는 전체 pairwise comparison을 수행하지 말고 Top-K vector search 방식으로 전환해야 합니다.
