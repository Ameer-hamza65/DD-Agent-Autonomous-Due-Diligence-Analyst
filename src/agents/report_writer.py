from src.report.pdf_generator import generate_pdf_report


def report_writer_node(state: dict) -> dict:
    return {"report_pdf_path": generate_pdf_report(state)}
