import pytest

from src.core.gateway.latex2pdf.latex2pdf_gateway import Latex2PDFRendererGateway


@pytest.fixture
def pdf_renderer_gateway():
    """Fixture to provide a PDFRendererGateway instance."""
    return Latex2PDFRendererGateway()


def test_render_pdf_integration(pdf_renderer_gateway):
    """Test PDF rendering with a valid LaTeX template."""
    template = r"""
    \documentclass{article}
    \begin{document}
    Hello, World!
    \end{document}
    """
    pdf_content = pdf_renderer_gateway.render_pdf(template)

    # Check that the result is a valid PDF (starts with PDF header)
    assert pdf_content.startswith(b"%PDF")


def test_render_pdf_integration_failure(pdf_renderer_gateway):
    """Test PDF rendering with an invalid LaTeX template."""
    template = r"\invalidlatex"

    with pytest.raises(ValueError):
        pdf_renderer_gateway.render_pdf(template)
