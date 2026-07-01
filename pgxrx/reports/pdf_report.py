"""PDF report generation using WeasyPrint."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def to_pdf(html_content: str, output_path: str):
    """Generate PDF report from HTML content using WeasyPrint.

    Parameters
    ----------
    html_content : HTML string
    output_path : output file path
    """
    try:
        from weasyprint import HTML
    except ImportError:
        logger.error(
            "WeasyPrint not installed. Install with: pip install pgxrx[report]"
        )
        # Fallback: save HTML
        import pathlib
        pathlib.Path(output_path).write_text(html_content)
        logger.warning("Saved as HTML instead of PDF: %s", output_path)
        return

    HTML(string=html_content).write_pdf(output_path)
    logger.info("PDF report written to %s", output_path)
