# 개정세법 쇼츠 영상 제작 워크플로우

## 프로젝트 목표
2026년 지방세법 개정 내용을 설명하는 쇼츠 영상 제작

## 전체 파이프라인

```
+=====================================================================+
|              Tax Law Shorts Video Production Pipeline               |
+=====================================================================+

  +-------------------+      +-------------------+      +-------------------+
  |                   |      |                   |      |                   |
  |   STEP 1          |      |   STEP 2          |      |   STEP 3          |
  |                   |      |                   |      |                   |
  |   PDF Page        | ===> |   Scenario        | ===> |   Video           |
  |   Classification  |      |   Generation      |      |   Production      |
  |                   |      |                   |      |                   |
  +-------------------+      +-------------------+      +-------------------+
          |                          |                          |
          v                          v                          v
  +---------------+          +---------------+          +---------------+
  | WORKFLOW-     |          | WORKFLOW-     |          | WORKFLOW-     |
  | SPLITPDFS.md  |          | SCENARIO.md   |          | ANIMAKER.md   |
  +---------------+          +---------------+          +---------------+


  INPUT                      PROCESS                    OUTPUT
  -----                      -------                    ------
  Original PDF               Read PDFs by TOC           MP4 Shorts Video
       |                          |                          |
       v                          v                          v
  revised/*.pdf              scenario.json              exports/*_final.mp4
       |                     script.md                  thumbnail.png
       v                          |
  pages/p001.pdf...               v
       |                     Narration Script
       v
  toc/[category]/...
```

## 워크플로우 문서

| 단계 | 문서 | 설명 |
|------|------|------|
| 1 | [WORKFLOW-SPLITPDFS.md](WORKFLOW-SPLITPDFS.md) | PDF 페이지 분할 및 목차 기반 분류 |
| 2 | [WORKFLOW-SCENARIO.md](WORKFLOW-SCENARIO.md) | 시나리오 및 스크립트 생성 |
| 3 | [WORKFLOW-ANIMAKER.md](WORKFLOW-ANIMAKER.md) | Animaker 애니메이션 제작 |

## 폴더 구조

```
gangubuy-tax-revised/
├── revised/                    # 1단계 작업 폴더
│   ├── *.pdf                   # 원본 PDF
│   ├── pages/                  # 페이지별 분할
│   └── toc/                    # 목차 기반 분류
│       ├── *-mapping.json
│       └── [문서명]/
├── scenarios/                  # 2단계 작업 폴더
│   └── [문서명]/
│       └── [분류 경로]/
│           ├── scenario.json
│           └── script.md
├── exports/                    # 3단계 결과물
│   └── [문서명]/
│       └── [세부항목]/
│           ├── *_final.mp4
│           └── *_thumbnail.png
├── split_pdf.py               # PDF 분할 스크립트
├── organize_by_toc.py         # 목차 분류 스크립트
├── WORKFLOW.md                # PDF 처리 워크플로우
├── WORKFLOW-SCENARIO.md       # 시나리오 생성 워크플로우
├── WORKFLOW-ANIMAKER.md       # 애니메이션 제작 워크플로우
└── WORKFLOW-INDEX.md          # 이 문서
```

## 작업 현황

### 완료된 작업
- [x] PDF 페이지 분할 스크립트 (split_pdf.py)
- [x] 목차 기반 분류 스크립트 (organize_by_toc.py)
- [x] localtax-law1 매핑 및 분류
- [x] localtax-special-law1 매핑 및 분류

### 진행 중
- [ ] 시나리오 생성 템플릿 구체화
- [ ] Animaker 템플릿 제작

### 예정
- [ ] 각 세부항목별 시나리오 생성
- [ ] 쇼츠 영상 제작
- [ ] YouTube 업로드

## 빠른 시작

### 새 PDF 추가 시
```bash
# 1. PDF를 revised/에 복사
# 2. 페이지 분할
python split_pdf.py

# 3. 목차 분석 후 매핑 JSON 생성
# 4. 분류 실행
python organize_by_toc.py [문서명]
```

### 시나리오 생성 시
```
# Claude Code에서 세부항목 PDF 읽기 후 시나리오 요청
# WORKFLOW-SCENARIO.md 참조
```

### 영상 제작 시
```
# Animaker에서 시나리오 기반 영상 제작
# WORKFLOW-ANIMAKER.md 참조
```
