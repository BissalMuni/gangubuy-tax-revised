"""dreamtax PDF 페이지를 목차 기반으로 계층적 폴더 구조로 분류하는 스크립트

사용법:
    python dreamtax/organize_by_toc.py
"""
import json
import shutil
from pathlib import Path


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

    # 대분류(Part) 시작 페이지 수집
    section_starts = []
    for section_name, section_data in sections.items():
        if "_doc_start" in section_data:
            section_starts.append((section_name, section_data["_doc_start"]))
    section_starts.sort(key=lambda x: x[1])

    copied_count = 0

    for section_name, section_data in sections.items():
        # 다음 대분류의 시작 페이지 계산
        next_section_start = None
        for i, (name, start) in enumerate(section_starts):
            if name == section_name and i + 1 < len(section_starts):
                next_section_start = section_starts[i + 1][1]
                break

        if next_section_start is None:
            next_section_start = total_pages - offset + 1

        print(f"\n[{section_name}]")

        # 챕터 항목 수집 (시작 페이지 기준 정렬)
        items = []
        for key, value in section_data.items():
            if key.startswith("_"):
                continue
            if isinstance(value, int):
                items.append((key, value))
        items.sort(key=lambda x: x[1])

        for i, (item_name, start_page) in enumerate(items):
            # 끝 페이지 계산
            if i + 1 < len(items):
                end_page = items[i + 1][1] - 1
            else:
                end_page = next_section_start - 1

            # 폴더 생성
            folder_path = output_base / section_name / item_name
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

            print(f"  {item_name}: p{start_page+offset:03d}-p{end_page+offset:03d} ({page_count}개)")

    print("-" * 60)
    print(f"완료: {copied_count}개 파일 복사됨")
    print(f"출력 폴더: {output_base}")


def main():
    base_dir = Path(__file__).parent
    mapping_path = base_dir / "toc-mapping.json"
    source_dir = base_dir / "pages"
    output_base = base_dir / "toc"

    if not mapping_path.exists():
        print(f"매핑 파일을 찾을 수 없습니다: {mapping_path}")
        return

    if not source_dir.exists():
        print(f"소스 디렉토리를 찾을 수 없습니다: {source_dir}")
        return

    organize_by_toc(mapping_path, source_dir, output_base)


if __name__ == "__main__":
    main()
