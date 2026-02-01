# PDF 인덱싱 워크플로우

## 개요

여러 권의 세무 관련 PDF 책을 개별 페이지로 분리하고, 목차(TOC) 구조에 따라 분류하는 워크플로우.
최종 목적인 시나리오 생성의 전처리 단계이다.

> **TOC** = Table of Contents (목차). 목차 구조에 따라 페이지를 폴더별로 분류한다는 의미.

## 대상 책 목록

| 폴더 | 책 이름 | PDF | 페이지 |
|------|---------|-----|--------|
| `dreamtax/` | 2025 강남 드림 택스 | dreamtax.pdf | 198 |
| `manual/` | 취득세 실무편람 | acquisitiontax.pdf | 71 |
| `revised/` | 2026 지방세법령 개정 | localtax law1.pdf | 212 |
| `revised/` | 2026 지방세특례법령 개정 | localtax-special law1.pdf | 255 |

## 표준 폴더 구조

각 책 폴더는 다음 구조를 따른다:

```
[book-folder]/
├── origin/                         # 원본 PDF
│   └── [book].pdf
├── pages/                          # Step 1: 개별 페이지 분할
│   └── [book-name]/
│       ├── p001.pdf
│       ├── p002.pdf
│       └── ...
├── index/                          # Step 2: 목차 페이지 추출
│   └── [book-name]/
│       ├── p003.pdf
│       └── ...
├── toc/                            # Step 4: 목차별 분류 결과
│   ├── [book-name]-mapping.json    # Step 3: 매핑 JSON
│   └── [book-name]/
│       ├── [대분류]/
│       │   ├── [세부항목]/
│       │   │   ├── p009.pdf
│       │   │   └── ...
│       │   └── ...
│       └── ...
└── scenarios/                      # (후속) 시나리오 생성 결과
    └── [book-name]/
```

## 워크플로우 단계

### Step 1. PDF 개별 페이지 분할

원본 PDF를 1페이지씩 개별 PDF 파일로 분리한다.

```bash
python split_pdf.py [book-folder]/origin/[book].pdf
```

- 입력: `origin/[book].pdf`
- 출력: `pages/[book-name]/p001.pdf, p002.pdf, ...`
- 파일명 규칙: `p` + 3자리 zero-padded 번호 (p001, p002, ..., p198)
- 기존 분할 결과가 있으면 건너뜀 (`--force`로 재처리)

### Step 2. 목차 페이지 추출 (index)

처음 ~20페이지 중 목차에 해당하는 페이지만 `index/` 폴더에 복사한다.

```bash
# 목차 페이지를 직접 확인하고 복사
mkdir [book-folder]/index/[book-name]
copy [book-folder]/pages/[book-name]/p006.pdf [book-folder]/index/[book-name]/
```

- 처음 10~20페이지를 Claude로 읽어서 목차 위치 파악
- 표지, 인사말, 빈 페이지 등은 제외하고 **목차만** 추출
- `page_offset` 계산: `PDF 파일 번호 - 문서 페이지 번호 = offset`
  - 예: 프론트매터 8페이지 → offset = 8 → 문서 1페이지 = p009.pdf

### Step 3. 목차 구조 파싱 → JSON 생성

index 폴더의 목차 페이지를 분석하여 매핑 JSON을 생성한다.

```
[book-folder]/toc/[book-name]-mapping.json
```

#### 통일 JSON 구조

모든 책이 동일한 JSON 형식을 사용한다:

```json
{
  "_info": {
    "source": "원본파일명.pdf",
    "total_pages": 198,
    "page_offset": 8,
    "index_pages": [6, 7],
    "note": "설명"
  },
  "sections": {
    "대분류명": {
      "_doc_start": 1,
      "세부항목명_또는_중분류명": 3
    }
  }
}
```

**`_info` 필드 (공통)**:

| 필드 | 설명 | 예시 |
|------|------|------|
| `source` | 원본 PDF 파일명 | `"dreamtax.pdf"` |
| `total_pages` | 총 물리적 페이지 수 | `198` |
| `page_offset` | 문서 페이지 → 물리 페이지 변환값 | `8` |
| `index_pages` | 목차 페이지 번호 (물리) | `[6, 7]` |
| `note` | 추가 설명 | `"프론트매터 8페이지 후 본문"` |

**`sections` 구조 (유연한 깊이)**:

책마다 목차 깊이가 다르지만 아래 규칙으로 통일한다:

- **키 이름**: `_`로 시작하면 메타 필드 (`_doc_start` 등), 아니면 항목 이름
- **값이 정수**: 해당 항목의 시작 페이지 (문서 페이지 번호)
- **값이 dict**: 하위 계층이 있음 (재귀)
- **범위 계산**: 시작 = 본 항목 값, 끝 = 다음 항목 값 - 1

```
깊이 1단 (dreamtax):
  sections > Part명 > 항목 = 페이지번호

깊이 2단 (revised):
  sections > 세목명 > 법령구분 > 항목 = 페이지번호

깊이 1단 (manual - 이름 부여 후):
  sections > 항목명 = 페이지번호
```

#### 책별 JSON 구조 비교

| 책 | 깊이 | 대분류 | 중분류 | 비고 |
|----|------|--------|--------|------|
| dreamtax | 1단 | Part1~Part9, 부록 | (없음) | offset=8 |
| manual | 1단 | 항목별 | (없음) | offset=0, 이름 미확정 |
| revised/law1 | 2단 | Ⅰ_취득세~Ⅹ_지역자원시설세 | 지방세법/시행령/시행규칙 | offset=6 |
| revised/special | 2단 | Ⅰ~Ⅲ | 개요/개정내용/참고 | offset=8 |

### Step 4. 매핑 JSON 기반 페이지 분류 → toc 폴더

JSON 구조에 따라 분할된 페이지를 계층적 폴더로 복사한다.

```bash
python organize_by_toc.py [book-name]
```

- 입력: `toc/[book-name]-mapping.json` + `pages/[book-name]/p*.pdf`
- 출력: `toc/[book-name]/[대분류]/[항목]/p009.pdf, ...`
- 각 항목 폴더에 해당 범위의 페이지가 복사됨
- `page_offset`을 적용하여 문서 페이지 → 물리 페이지 변환

---

## 현재 상태 검증

### dreamtax/ 검증

| 단계 | 항목 | 상태 | 비고 |
|------|------|------|------|
| 원본 | `origin/dreamtax.pdf` | OK | 198페이지 |
| Step 1 | `pages/p001~p198.pdf` | **구조 불일치** | `pages/` 직접 배치 (표준: `pages/dreamtax/`) |
| Step 2 | `index/p006.pdf, p007.pdf` | **구조 불일치** | `index/` 직접 배치 (표준: `index/dreamtax/`) |
| Step 3 | `toc-mapping.json` | **위치 불일치** | 루트에 위치 (표준: `toc/dreamtax-mapping.json`) |
| Step 4 | `toc/Part1~부록/` | OK | 10개 Part, 22개 항목 정상 분류 |

**불일치 사항**:
1. `pages/` 아래에 `dreamtax/` 하위 폴더 없이 직접 배치됨
2. `index/` 아래에 `dreamtax/` 하위 폴더 없이 직접 배치됨
3. `toc-mapping.json`이 책 루트에 위치 (`toc/` 안이 아님)
4. `_info`에 `index_pages` 필드 없음

### manual/ 검증

| 단계 | 항목 | 상태 | 비고 |
|------|------|------|------|
| 원본 | `acquisitiontax.pdf` | **위치 불일치** | 루트에 위치 (표준: `origin/`) |
| Step 1 | `pages/acquisitiontax/p001~p071.pdf` | OK | 71페이지 |
| Step 2 | index 폴더 | **미완료** | index 폴더 없음 |
| Step 3 | `toc/acquisitiontax-mapping.json` | **형식 불일치** | `_page_start/_page_end` 방식 (표준과 다름) |
| Step 4 | `toc/acquisitiontax/01_p001-p001~42_p071-p071/` | **임시 상태** | 번호 기반 그룹 (섹션명 미부여) |

**불일치 사항**:
1. 원본 PDF가 `origin/` 폴더에 있지 않음
2. `index/` 폴더 자체가 없음 (목차 페이지 미추출)
3. 매핑 JSON이 `_page_start/_page_end` 형식으로, 표준 형식과 다름
4. toc 폴더가 번호 기반 임시 구조 (내용 기반 이름 필요)
5. `pages.txt` 경계 파일은 표준에 없는 추가 파일

### revised/ 검증

| 단계 | 항목 | 상태 | 비고 |
|------|------|------|------|
| 원본 | `origin/localtax law1.pdf` | OK | 212페이지 |
| 원본 | `origin/localtax-special law1.pdf` | OK | 255페이지 |
| Step 1 | `pages/20260101 localtax law1/p001~p212.pdf` | OK | 212페이지 |
| Step 1 | `pages/20260101 localtax-special law1/p001~p255.pdf` | OK | 255페이지 |
| Step 2 | `index/localtax-law1/00_목차/p003~p006.pdf` | OK | 4페이지 |
| Step 2 | `index/localtax-special-law1/00_목차/p003~p005.pdf` | OK | 3페이지 |
| Step 3 | `toc/localtax-law1-mapping.json` | OK | 10개 대분류, offset=6 |
| Step 3 | `toc/localtax-special-law1-mapping.json` | OK | 3개 대분류, offset=8 |
| Step 4 | `toc/localtax-law1/Ⅰ_취득세~Ⅹ_지역자원시설세/` | OK | 계층 구조 정상 |
| Step 4 | `toc/localtax-special-law1/Ⅰ~Ⅲ/` | OK | 계층 구조 정상 |

**불일치 사항**:
1. `_info`에 `index_pages` 필드 없음 (사소)
2. 그 외 표준 구조와 일치

### 검증 요약

```
            origin/  pages/    index/   mapping.json   toc/
            ------   ------    ------   ------------   ----
dreamtax      OK     구조불일치  구조불일치  위치불일치      OK
manual      위치불일치   OK      미완료     형식불일치    임시상태
revised       OK       OK        OK        OK          OK
```

**가장 표준에 가까운 것**: revised/ (기준 모델)
**작업 필요**: dreamtax/ (구조 정리), manual/ (Step 2~4 재작업)

## 정리 작업 체크리스트

### dreamtax/ 정리
- [ ] `pages/p*.pdf` → `pages/dreamtax/p*.pdf`로 이동
- [ ] `index/p*.pdf` → `index/dreamtax/p*.pdf`로 이동
- [ ] `toc-mapping.json` → `toc/dreamtax-mapping.json`으로 이동
- [ ] `toc-mapping.json`에 `index_pages` 필드 추가

### manual/ 정리
- [ ] `acquisitiontax.pdf` → `origin/acquisitiontax.pdf`로 이동
- [ ] 목차 페이지 확인 후 `index/acquisitiontax/` 생성
- [ ] 매핑 JSON을 표준 형식으로 재생성 (섹션명 부여 필요)
- [ ] toc 폴더를 내용 기반 이름으로 재구성

### revised/ 정리
- [ ] 매핑 JSON에 `index_pages` 필드 추가 (선택)
