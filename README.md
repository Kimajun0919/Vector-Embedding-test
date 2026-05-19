# AI 공공서비스 시민 의견 임베딩 지도

LUXIA Cloud Vector Embedding API, cosine similarity, UMAP, KMeans 군집화를 사용해 시민 의견 100건을 2D 의견 지도로 시각화하는 로컬 풀스택 프로토타입입니다.

의견 지도는 x축과 y축 자체를 해석하는 도구가 아닙니다. 각 점 사이의 거리, 군집, 군집 대표 의견을 기준으로 의견 구조를 살펴보는 도구입니다.

## 프로젝트 개요

Agenda:

```text
AI 기반 공공서비스 도입에 대한 시민 의견
```

처리 흐름:

1. `backend/sample_data.py`에 작성된 시민 의견 100건을 사용합니다.
2. FastAPI 백엔드가 LUXIA Cloud Embedding API를 호출해 실제 임베딩 벡터를 생성합니다.
3. 임베딩 벡터 간 cosine similarity를 계산합니다.
4. 각 의견마다 Top 5 유사 의견을 찾습니다.
5. UMAP으로 임베딩 벡터를 2차원 좌표로 축소합니다.
6. KMeans로 임베딩 기반 군집을 만들고, 각 군집의 대표 의견을 계산합니다.
7. React + Plotly.js 프론트엔드에서 의견 지도를 시각화합니다.

API 키는 `backend/.env`에만 저장하며, 프론트엔드에는 노출하지 않습니다. 프론트엔드는 FastAPI 백엔드만 호출합니다.

## 주요 기능

- 한국어 시민 의견 100건 제공
- LUXIA Cloud Embedding API 기반 실제 임베딩 생성
- cosine similarity 기반 Top 5 유사 의견 탐색
- UMAP 기반 2D 좌표 생성
- KMeans 기반 군집화
- 군집별 대표 의견 자동 선정
- Plotly.js 기반 인터랙티브 의견 지도
- 점 클릭 시 선택 의견, 군집 대표 의견, 유사 의견 표시

## 기술 스택

Backend:

- Python
- FastAPI
- httpx
- python-dotenv
- numpy
- scikit-learn
- umap-learn
- pydantic

Frontend:

- React
- TypeScript
- Vite
- Plotly.js

## 프로젝트 구조

```text
opinion-embedding-map/
  backend/
    main.py
    luxia_client.py
    similarity.py
    projection.py
    clustering.py
    sample_data.py
    requirements.txt
    .env.example
  frontend/
    src/
      App.tsx
      components/
        OpinionMap.tsx
        OpinionDetailPanel.tsx
      types/
        opinion.ts
      api/
        opinionApi.ts
    package.json
    vite.config.ts
    tsconfig.json
  README.md
```

## 데이터 구조

샘플 데이터는 `stance`나 찬반 필드를 사용하지 않습니다. 주관식/객관식 응답 유형과 주제 카테고리를 기준으로 구성합니다.

```python
{
    "id": "opinion_001",
    "text": "AI 공공서비스는 행정 처리 속도를 높일 수 있어 도입이 필요하다고 생각합니다.",
    "responseType": "주관식",
    "category": "효율성",
}
```

응답 유형 분포:

- `주관식`: 40건
- `객관식-단일`: 30건
- `객관식-복수`: 30건

카테고리:

- 효율성
- 예산
- 개인정보
- 접근성
- 공정성
- 기술 신뢰성
- 행정 책임
- 사회적 영향
- 고령층/디지털 취약계층
- 단계적 도입

## API 응답 구조

`POST /api/analyze-opinions`는 분석된 의견 배열을 반환합니다.

```json
{
  "opinions": [
    {
      "id": "opinion_001",
      "text": "AI 공공서비스는 행정 처리 속도를 높일 수 있어 도입이 필요하다고 생각합니다.",
      "responseType": "주관식",
      "category": "효율성",
      "x": 0.123,
      "y": -0.456,
      "clusterId": 4,
      "clusterName": "AI를 활용하면 민원 처리 시간이 단축되고 시민 편의가 더 높...",
      "clusterLabel": "대표 의견 opinion_005: AI를 활용하면 민원 처리 시간이 단축되고 시민 편의가 더 높...",
      "clusterRepresentative": {
        "id": "opinion_005",
        "text": "AI를 활용하면 민원 처리 시간이 단축되고 시민 편의가 더 높아질 수 있습니다.",
        "responseType": "주관식",
        "category": "효율성"
      },
      "similarOpinions": [
        {
          "id": "opinion_017",
          "text": "민원 처리 시간을 줄이고 시민 편의를 높일 수 있으므로 AI 활용에 긍정적으로 평가합니다.",
          "responseType": "주관식",
          "category": "효율성",
          "similarity": 0.87,
          "interpretation": "strongly similar opinion"
        }
      ]
    }
  ]
}
```

## 실행 방법

### 1. Backend 실행

macOS/Linux:

```bash
cd opinion-embedding-map/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

Windows PowerShell:

```powershell
cd opinion-embedding-map/backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn main:app --reload
```

백엔드는 기본적으로 `http://localhost:8000`에서 실행됩니다.

### 2. Frontend 실행

```bash
cd opinion-embedding-map/frontend
npm install
npm run dev
```

프론트엔드는 기본적으로 `http://localhost:5173`에서 실행됩니다.

Vite proxy 설정으로 `/api` 요청은 `http://localhost:8000`의 FastAPI 서버로 전달됩니다.

## .env 설정

`backend/.env` 파일을 만들고 LUXIA API 키를 입력합니다.

```env
LUXIA_API_KEY=your_luxia_api_key_here
LUXIA_EMBEDDING_URL=https://bridge.luxiacloud.com/luxia/v1/embedding
LUXIA_EMBEDDING_BATCH_SIZE=20
```

LUXIA 호출 형식:

```bash
curl --location 'https://bridge.luxiacloud.com/luxia/v1/embedding' \
  --header 'apikey: YOUR_API_KEY' \
  --header 'Content-Type: application/json' \
  --data '{
    "inputs": [
      "I'm happy to introduce our new model"
    ]
  }'
```

백엔드는 100건을 한 번에 보내지 않고 `LUXIA_EMBEDDING_BATCH_SIZE` 기준으로 나누어 호출합니다. 기본값은 20입니다.

## Backend API

### GET `/api/sample-opinions`

샘플 의견 100건을 반환합니다.

### POST `/api/analyze-opinions`

요청 본문에 `opinions`가 있으면 해당 의견을 분석합니다. 본문이 비어 있으면 `SAMPLE_OPINIONS` 100건을 기본으로 분석합니다.

```json
{}
```

또는:

```json
{
  "opinions": [
    {
      "id": "custom_001",
      "text": "AI 공공서비스는 민원 처리 시간을 줄일 수 있습니다.",
      "responseType": "주관식",
      "category": "효율성"
    }
  ]
}
```

## 의견 지도 해석 방법

- 각 점은 시민 의견 1건을 의미합니다.
- 가까운 점은 의미적으로 유사한 의견입니다.
- 멀리 떨어진 점은 상대적으로 다른 관점의 의견입니다.
- x축과 y축 자체에는 고정된 의미가 없습니다.
- x축은 찬성/반대가 아닙니다.
- y축은 중요도/강도가 아닙니다.
- 좌표는 UMAP이 임베딩 벡터 간 거리 관계를 2차원으로 축소한 결과입니다.
- 점 색상은 임베딩 기반 KMeans 군집을 의미합니다.
- 군집명은 해당 군집의 중심에 가장 가까운 대표 의견 문장을 짧게 줄인 값입니다.
- 점을 클릭하면 오른쪽 패널에서 선택 의견, 군집 대표 의견, Top 5 유사 의견을 확인할 수 있습니다.

## 유사도 기준

cosine similarity 해석 기준:

- `>= 0.90`: 거의 동일한 의견
- `>= 0.82`: 강한 유사 의견
- `>= 0.75`: 관련 의견
- `< 0.75`: 약한 관련 또는 비유사 의견

## 군집 대표 의견 선정 방식

1. 각 의견의 LUXIA embedding을 정규화합니다.
2. 정규화된 벡터를 KMeans로 군집화합니다.
3. 각 군집의 centroid와 가장 가까운 의견을 찾습니다.
4. 해당 의견을 `clusterRepresentative`로 사용합니다.
5. 대표 의견 문장을 짧게 줄여 `clusterName`으로 표시합니다.

현재 기본 군집 수는 `backend/main.py`에서 `n_clusters=6`으로 설정되어 있습니다.

## 주의사항

- 이 프로젝트는 로컬 실행용 프로토타입입니다.
- 실제 운영 환경에서는 API 키 관리, 요청 제한, 장애 처리, 캐싱 전략을 강화해야 합니다.
- 대량 데이터에서는 전체 pairwise similarity 계산을 피해야 합니다.
- 10만 건 이상 데이터에서는 vector DB 또는 ANN 기반 Top-K 검색 구조로 전환해야 합니다.
- UMAP 좌표는 실행 설정과 데이터 구성에 따라 달라질 수 있습니다.
- 군집명은 자동 생성된 대표 의견 기반 라벨이므로, 운영 환경에서는 사람이 검수하거나 별도 요약 모델을 붙이는 방식을 고려할 수 있습니다.

## 문제 해결

### 분석 버튼 클릭 시 502가 발생하는 경우

대부분 LUXIA API 호출 실패입니다. 아래 항목을 확인합니다.

- `backend/.env`에 `LUXIA_API_KEY`가 있는지 확인
- 백엔드를 재시작했는지 확인
- `LUXIA_EMBEDDING_URL`이 올바른지 확인
- LUXIA API 사용량 제한이나 인증 오류가 없는지 확인

### 점 클릭 후 오른쪽 패널이 바뀌지 않는 경우

- 브라우저에서 `Ctrl + F5`로 강력 새로고침
- 프론트엔드 dev server 재시작
- `npm run build`로 TypeScript 빌드 확인

### PowerShell에서 `npm` 실행이 막히는 경우

PowerShell 실행 정책 때문에 `npm.ps1`이 막힐 수 있습니다. 이 경우 아래처럼 실행합니다.

```powershell
npm.cmd install
npm.cmd run dev
```
