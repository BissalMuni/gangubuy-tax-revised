"""목차 기반으로 PDF 페이지를 계층적 폴더 구조로 분류하는 스크립트

사용법:
    python organize_by_toc.py                    # 모든 매핑 파일 처리
    python organize_by_toc.py localtax-law1      # 특정 매핑만 처리
"""
import json
import shutil
import sys
from pathlib import Path


def get_page_ranges(section_data: dict, next_section_start: int = None) -> list[tuple[str, int, int]]:
    """섹션 데이터에서 (항목명, 시작페이지, 끝페이지) 리스트 추출

    각 항목의 끝 페이지 = 다음 항목의 시작 페이지 - 1
    """
    items = []

    for key, value in section_data.items():
        if key.startswith("_"):
            continue
        if isinstance(value, int):
            items.append((key, value))
        elif isinstance(value, dict):
            # 중첩된 딕셔너리는 재귀적으로 처리
            sub_items = get_page_ranges(value, next_section_start)
            items.extend([(f"{key}/{name}", start, end) for name, start, end in sub_items])

    # 시작 페이지 순으로 정렬
    items.sort(key=lambda x: x[1])

    # 끝 페이지 계산
    result = []
    for i, (name, start) in enumerate(items):
        if i + 1 < len(items):
            end = items[i + 1][1] - 1
        elif next_section_start:
            end = next_section_start - 1
        else:
            end = None  # 마지막 항목은 끝을 알 수 없음
        result.append((name, start, end))

    return result


def organize_by_toc(mapping_path: Path, source_dir: Path, output_base: Path):
    """매핑 파일을 기반으로 PDF 파일을 폴더 구조로 분류"""

    with open(mapping_path, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    info = mapping["_info"]
    sections = mapping["sections"]
    offset = info["page_offset"]
    total_pages = info["total_pages"]

    print(f"처리 중: {info['source']}")
    print(f"총 페이지: {total_pages}, 오프셋: {offset}")
    print("-" * 60)

    # 대분류 섹션 시작 페이지 수집 (다음 섹션 시작 계산용)
    section_starts = []
    for section_name, section_data in sections.items():
        if "_doc_start" in section_data:
            section_starts.append((section_name, section_data["_doc_start"]))
    section_starts.sort(key=lambda x: x[1])

    copied_count = 0

    for idx, (section_name, section_data) in enumerate(sections.items()):
        # 다음 대분류의 시작 페이지
        next_section_start = None
        for i, (name, start) in enumerate(section_starts):
            if name == section_name and i + 1 < len(section_starts):
                next_section_start = section_starts[i + 1][1]
                break

        if next_section_start is None:
            next_section_start = total_pages - offset + 1

        print(f"\n[{section_name}]")

        # 중분류 처리
        for sub_name, sub_data in section_data.items():
            if sub_name.startswith("_"):
                continue

            if not isinstance(sub_data, dict):
                continue

            # 세부 항목 페이지 범위 계산
            items = list(sub_data.items())
            items.sort(key=lambda x: x[1])

            for i, (item_name, start_page) in enumerate(items):
                # 끝 페이지 계산
                if i + 1 < len(items):
                    end_page = items[i + 1][1] - 1
                else:
                    # 마지막 항목: 다음 중분류 또는 대분류의 시작 전까지
                    # 간단히 다음 대분류 시작 - 1로 설정
                    end_page = next_section_start - 1

                # 폴더 생성
                folder_path = output_base / section_name / sub_name / item_name
                folder_path.mkdir(parents=True, exist_ok=True)

                # PDF 파일 복사
                page_count = 0
                for page_num in range(start_page, end_page + 1):
                    pdf_num = page_num + offset
                    src_file = source_dir / f"p{pdf_num:03d}.pdf"

                    if src_file.exists():
                        dst_file = folder_path / src_file.name
                        shutil.copy2(src_file, dst_file)
                        page_count += 1
                        copied_count += 1

                print(f"  {sub_name}/{item_name}: p{start_page+offset:03d}-p{end_page+offset:03d} ({page_count}개)")

    print("-" * 60)
    print(f"완료: {copied_count}개 파일 복사됨")
    print(f"출력 폴더: {output_base}")


def main():
    toc_dir = Path("revised/toc")

    # 처리할 매핑 파일 결정
    if len(sys.argv) > 1:
        targets = [sys.argv[1]]
    else:
        targets = ["localtax-law1", "localtax-special-law1"]

    for target in targets:
        mapping_path = toc_dir / f"{target}-mapping.json"

        if not mapping_path.exists():
            print(f"매핑 파일을 찾을 수 없습니다: {mapping_path}")
            continue

        # 소스 디렉토리 결정 (revised/pages/ 하위)
        if target == "localtax-law1":
            source_dir = Path("revised/pages/20260101 localtax law1")
        elif target == "localtax-special-law1":
            source_dir = Path("revised/pages/20260101 localtax-special law1")
        else:
            print(f"알 수 없는 대상: {target}")
            continue

        if not source_dir.exists():
            print(f"소스 디렉토리를 찾을 수 없습니다: {source_dir}")
            continue

        output_base = toc_dir / target

        organize_by_toc(mapping_path, source_dir, output_base)
        print()


if __name__ == "__main__":
    main()
