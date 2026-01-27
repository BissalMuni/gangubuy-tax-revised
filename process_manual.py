"""manual/ 폴더의 PDF를 pages.txt 기반으로 섹션별 그룹화하는 스크립트

사용법:
    python process_manual.py                    # 그룹화 + 매핑 JSON 생성
    python process_manual.py --mapping-only     # 매핑 JSON만 생성
    python process_manual.py --force            # 기존 결과 덮어쓰기
"""
import json
import shutil
import sys
from pathlib import Path


MANUAL_DIR = Path("manual")
PDF_NAME = "acquisitiontax"
PAGES_TXT = MANUAL_DIR / "pages.txt"
SOURCE_DIR = MANUAL_DIR / "pages" / PDF_NAME
TOC_DIR = MANUAL_DIR / "toc"
MAPPING_PATH = TOC_DIR / f"{PDF_NAME}-mapping.json"
OUTPUT_DIR = TOC_DIR / PDF_NAME


def read_boundaries(pages_txt_path: Path) -> list[int]:
    """pages.txt에서 섹션 경계 페이지 번호 읽기"""
    boundaries = []
    with open(pages_txt_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                boundaries.append(int(line))
    return sorted(boundaries)


def detect_total_pages(source_dir: Path) -> int:
    """분할된 PDF 폴더에서 총 페이지 수 감지"""
    pdf_files = list(source_dir.glob("p*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"분할된 PDF 파일이 없습니다: {source_dir}")
    return len(pdf_files)


def compute_groups(boundaries: list[int], total_pages: int) -> list[tuple[int, int, int]]:
    """경계 목록에서 (그룹번호, 시작페이지, 끝페이지) 리스트 계산

    Args:
        boundaries: 섹션 경계 페이지 번호 리스트 (정렬됨)
        total_pages: PDF 총 페이지 수

    Returns:
        [(group_num, start_page, end_page), ...]
    """
    groups = []
    for i, start in enumerate(boundaries):
        if i + 1 < len(boundaries):
            end = boundaries[i + 1] - 1
        else:
            end = total_pages
        groups.append((i + 1, start, end))
    return groups


def generate_mapping(boundaries: list[int], total_pages: int) -> dict:
    """pages.txt 기반으로 매핑 JSON 생성"""
    groups = compute_groups(boundaries, total_pages)

    sections = {}
    for group_num, start, end in groups:
        key = f"{group_num:02d}_section"
        sections[key] = {
            "_page_start": start,
            "_page_end": end,
            "_page_count": end - start + 1,
        }

    return {
        "_info": {
            "source": f"{PDF_NAME}.pdf",
            "total_pages": total_pages,
            "page_offset": 0,
            "boundaries_count": len(boundaries),
            "note": "pages.txt 기반 섹션 분류. 섹션명은 PDF 내용 확인 후 업데이트 필요",
        },
        "sections": sections,
    }


def organize_pages(boundaries: list[int], total_pages: int, force: bool = False):
    """경계 기반으로 PDF 파일을 그룹 폴더로 복사"""
    if OUTPUT_DIR.exists() and not force:
        existing = list(OUTPUT_DIR.iterdir())
        if existing:
            print(f"SKIP: 이미 {len(existing)}개 폴더 존재 (--force로 덮어쓰기)")
            return

    groups = compute_groups(boundaries, total_pages)
    copied_count = 0

    print(f"페이지 그룹화 시작")
    print(f"소스: {SOURCE_DIR}")
    print(f"출력: {OUTPUT_DIR}")
    print("-" * 60)

    for group_num, start, end in groups:
        folder_name = f"{group_num:02d}_p{start:03d}-p{end:03d}"
        folder_path = OUTPUT_DIR / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        page_count = 0
        for page_num in range(start, end + 1):
            src_file = SOURCE_DIR / f"p{page_num:03d}.pdf"
            if src_file.exists():
                dst_file = folder_path / src_file.name
                shutil.copy2(src_file, dst_file)
                page_count += 1
                copied_count += 1

        print(f"  그룹 {group_num:02d}: p{start:03d}-p{end:03d} ({page_count}개)")

    print("-" * 60)
    print(f"완료: {copied_count}개 파일 → {len(groups)}개 그룹")


def main():
    force = "--force" in sys.argv
    mapping_only = "--mapping-only" in sys.argv

    # 경계 읽기
    if not PAGES_TXT.exists():
        print(f"pages.txt를 찾을 수 없습니다: {PAGES_TXT}")
        return

    boundaries = read_boundaries(PAGES_TXT)
    print(f"경계 페이지: {len(boundaries)}개")
    print(f"범위: {boundaries[0]} ~ {boundaries[-1]}")

    # 총 페이지 감지
    if not SOURCE_DIR.exists():
        print(f"\n분할된 PDF 폴더가 없습니다: {SOURCE_DIR}")
        print(f"먼저 실행: python split_pdf.py manual/{PDF_NAME}.pdf")
        return

    total_pages = detect_total_pages(SOURCE_DIR)
    print(f"총 페이지: {total_pages}")

    # 매핑 JSON 생성
    TOC_DIR.mkdir(parents=True, exist_ok=True)
    mapping = generate_mapping(boundaries, total_pages)

    with open(MAPPING_PATH, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print(f"\n매핑 파일 생성: {MAPPING_PATH}")

    # 페이지 그룹화
    if not mapping_only:
        print()
        organize_pages(boundaries, total_pages, force=force)


if __name__ == "__main__":
    main()
