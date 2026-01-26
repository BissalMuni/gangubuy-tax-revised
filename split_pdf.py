"""PDF를 페이지별로 분할하는 스크립트

사용법:
    python split_pdf.py              # .data 폴더의 모든 새 PDF 처리
    python split_pdf.py --force      # 기존 분할 폴더가 있어도 다시 처리
    python split_pdf.py file.pdf     # 특정 PDF만 처리
"""
import sys
from pathlib import Path
from pypdf import PdfReader, PdfWriter


def split_pdf(pdf_path: str, output_dir: str = None, force: bool = False) -> list[str]:
    """PDF를 페이지별로 분할하여 저장

    Args:
        pdf_path: 원본 PDF 경로
        output_dir: 출력 폴더 (기본값: 원본 PDF와 같은 이름의 폴더)
        force: True면 기존 파일이 있어도 덮어쓰기

    Returns:
        생성된 파일 경로 목록
    """
    pdf_path = Path(pdf_path)

    if output_dir is None:
        # .data/pages/[파일명]/ 구조로 출력
        pages_dir = pdf_path.parent / "pages"
        output_dir = pages_dir / pdf_path.stem
    else:
        output_dir = Path(output_dir)

    # 이미 분할된 폴더가 있고 파일이 존재하면 건너뛰기
    if output_dir.exists() and not force:
        existing_files = list(output_dir.glob("*.pdf"))
        if existing_files:
            print(f"SKIP: {pdf_path.name} (이미 {len(existing_files)}개 파일 존재)")
            return []

    output_dir.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    created_files = []

    print(f"PDF: {pdf_path.name}")
    print(f"총 페이지 수: {total_pages}")
    print(f"출력 폴더: {output_dir}")
    print("-" * 50)

    for i, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)

        output_path = output_dir / f"p{i:03d}.pdf"
        with open(output_path, "wb") as f:
            writer.write(f)

        created_files.append(str(output_path))
        print(f"  생성: {output_path.name}")

    print("-" * 50)
    print(f"완료: {len(created_files)}개 파일 생성")

    return created_files


def main():
    data_dir = Path("revised")
    force = "--force" in sys.argv

    # 특정 PDF 파일이 인자로 주어진 경우
    pdf_args = [arg for arg in sys.argv[1:] if arg.endswith(".pdf")]
    if pdf_args:
        for pdf_arg in pdf_args:
            pdf_path = Path(pdf_arg)
            if pdf_path.exists():
                split_pdf(pdf_path, force=force)
                print()
            else:
                print(f"파일을 찾을 수 없습니다: {pdf_arg}")
        return

    # .data 폴더의 모든 PDF 처리
    pdf_files = list(data_dir.glob("*.pdf"))

    if not pdf_files:
        print("PDF 파일을 찾을 수 없습니다.")
        return

    print(f"발견된 PDF 파일: {len(pdf_files)}개")
    if force:
        print("(--force 모드: 기존 파일 덮어쓰기)")
    print()

    for pdf_file in pdf_files:
        split_pdf(pdf_file, force=force)
        print()


if __name__ == "__main__":
    main()
