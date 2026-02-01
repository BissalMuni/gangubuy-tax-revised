# MDX 템플릿 설계 및 파일 생성 계획

## 반영된 요구사항 (Constitution + Feature Spec 기반)

- **프레임워크**: Next.js (MDX)
- **대상 분리**: frontmatter에 `audience: "internal"` 필수 (현재 단계는 internal만)
- **개조식 공문서 스타일**: 번호/글머리 기호 구조화, 표 형식, 법령 근거 명시
- **버전 관리**: 파일명에 버전 포함 (예: `01_section-v1.0.mdx`)
- **콘텐츠 버전**: semver (v1.0, v1.1, v2.0)

## 생성 구조

```text
manual/toc/mdx/
├── _template.mdx                ← 복사용 원본 템플릿
├── 01_section-v1.0.mdx
├── 02_section-v1.0.mdx
├── ...
└── 42_section-v1.0.mdx
```

## MDX 템플릿 구조

Next.js MDX 호환 + Constitution 준수:

```mdx
---
title: ""
section_id: "01"
category: "취득세"
subcategory: ""
audience: "internal"
source: "acquisitiontax.pdf"
page_range: [1, 1]
version: "1.0"
effective_date: "2026-01-01"
last_updated: "2026-01-31"
status: "draft"
law_reference: ""
tags: []
---

# 섹션 제목

> 한 줄 요약

---

## 1. 적용 대상

- 대상 항목
  - 세부 조건

## 2. 주요 내용

### 가. 소제목

- 핵심 내용
  - 세부 설명
  - 세부 설명

### 나. 소제목

- 핵심 내용

## 3. 세율·금액

| 구분 | 세율 | 과세표준 | 비고 |
|------|------|----------|------|
| - | - | - | - |

## 4. 관련 법령

| 구분 | 법령명 | 조항 | 비고 |
|------|--------|------|------|
| 근거법 | 지방세법 | §00 | |

## 5. 주의사항

<Callout type="caution">
- 주의할 점
</Callout>

## 6. 자주 묻는 질문

<details>
<summary>Q. 질문?</summary>

- 답변

</details>

---

> 본 자료는 지방세 정보 안내용이며, 법적 효력이 없습니다.
> 정확한 내용은 관할 지자체 세무부서에 문의하세요.
```

## 설계 근거

| 요소                                | Constitution 원칙  | 설명                        |
| ----------------------------------- | ------------------ | --------------------------- |
| `audience: "internal"`              | I. 대상 분리       | 현재 단계 internal만        |
| 개조식 번호 체계 (1. 2. 가. 나.)    | II. 공문서 스타일  | 공문서 표준 번호 체계       |
| 표 형식 (세율, 법령)                | II. 공문서 스타일  | 수치/법령은 표로            |
| `law_reference`                     | III. 정보 정확성   | 법적 근거 필수 명시         |
| `version: "1.0"`                    | Content Constraints | 파일명+frontmatter 이중 관리 |
| `<Callout>` 컴포넌트               | Next.js MDX        | 프레임워크 네이티브 방식    |
| `<details>` HTML                    | 범용               | FAQ 접기/펼치기             |

## 실행 결과

1. `manual/toc/mdx/` 폴더 생성 완료
2. `_template.mdx` 공용 템플릿 파일 생성 완료
3. 42개 섹션별 `XX_section-v1.0.mdx` 파일 생성 완료
   - mapping.json의 page_range 자동 반영
   - 나머지는 템플릿 구조 유지 (내용은 PDF 확인 후 채움)
