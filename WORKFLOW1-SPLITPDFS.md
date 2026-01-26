# PDF 처리 워크플로우

## 개요
지방세 관련 PDF 문서를 목차 기반으로 분류하는 자동화 워크플로우

## 폴더 구조

```
revised/
├── [원본 PDF 파일].pdf              # 1단계: 원본 PDF 추가
├── pages/                          # 2단계: 페이지별 분할 결과
│   └── [원본 PDF 파일명]/
│       ├── p001.pdf
│       ├── p002.pdf
│       └── ...
└── toc/
    ├── [문서명]-mapping.json        # 3단계: 목차 매핑 파일
    └── [문서명]/                    # 4단계: 목차 기반 분류 결과
        ├── Ⅰ_취득세/
        │   ├── 지방세법/
        │   │   ├── 01_항목명/
        │   │   │   ├── p009.pdf
        │   │   │   └── ...
        │   │   └── ...
        │   └── ...
        └── ...
```

## 실행 단계

### 1단계: PDF 페이지 분할
```bash
# 새 PDF를 revised 폴더에 추가 후 실행
python split_pdf.py

# 또는 특정 파일만 처리
python split_pdf.py "revised/새파일.pdf"

# 기존 분할 결과 덮어쓰기
python split_pdf.py --force
```

### 2단계: 목차 페이지 확인 (Claude 사용)
```
# Claude Code에서 목차 페이지 읽기
처음 10페이지 정도를 읽어서 목차 페이지 위치 확인
- 표지, 빈 페이지, 목차 페이지, 본문 시작 페이지 파악
- page_offset 계산: PDF 파일 번호 = 문서 페이지 + offset
```

### 3단계: 목차 매핑 JSON 생성
`revised/toc/[문서명]-mapping.json` 파일 생성

```json
{
  "_info": {
    "source": "원본파일명.pdf",
    "total_pages": 212,
    "page_offset": 6,
    "note": "문서 페이지 + offset = PDF 파일 번호"
  },
  "sections": {
    "Ⅰ_대분류명": {
      "_doc_start": 1,
      "중분류명": {
        "01_세부항목명": 3,
        "02_세부항목명": 7
      }
    }
  }
}
```

### 4단계: 목차 기반 분류 실행
```bash
# 모든 매핑 파일 처리
python organize_by_toc.py

# 특정 문서만 처리
python organize_by_toc.py localtax-law1
```

## 스크립트 설명

### split_pdf.py
- 기능: PDF를 페이지별 개별 파일로 분할
- 입력: `revised/*.pdf`
- 출력: `revised/pages/[파일명]/p001.pdf, p002.pdf, ...`
- 특징: 이미 분할된 폴더가 있으면 건너뜀 (--force로 덮어쓰기)

### organize_by_toc.py
- 기능: JSON 매핑 기반으로 계층적 폴더 구조 생성
- 입력: `revised/toc/[문서명]-mapping.json`
- 출력: `revised/toc/[문서명]/[대분류]/[중분류]/[세부항목]/`
- 특징: 시작 페이지 기준으로 다음 항목 전까지 범위 자동 계산

## 새 PDF 추가 시 체크리스트

1. [ ] PDF 파일을 `revised/` 폴더에 복사
2. [ ] `python split_pdf.py` 실행
3. [ ] 처음 20페이지 읽어서 목차 위치 확인
4. [ ] page_offset 계산 (PDF 파일 번호 - 문서 페이지 번호)
5. [ ] `revised/toc/[문서명]-mapping.json` 작성
6. [ ] `python organize_by_toc.py [문서명]` 실행
7. [ ] 결과 폴더 구조 확인

## 예시: 새 PDF 처리

```bash
# 1. PDF 추가 (수동)
# revised/20260101 new-tax-law.pdf 복사

# 2. 페이지 분할
python split_pdf.py

# 3-5. Claude와 대화하며 목차 분석 및 JSON 생성
# "목차 페이지 확인해줘" → 10페이지씩 읽어서 분석

# 6. 분류 실행
python organize_by_toc.py new-tax-law

# 7. 결과 확인
ls -la "revised/toc/new-tax-law"
```

## 주의사항

- 목차의 페이지 번호는 **문서 내 페이지 번호**임 (표지, 목차 제외)
- PDF 파일 번호는 p001.pdf부터 시작 (물리적 페이지)
- `page_offset = PDF파일번호 - 문서페이지번호`
- 마지막 항목의 끝 페이지는 다음 대분류 시작 - 1로 계산됨
