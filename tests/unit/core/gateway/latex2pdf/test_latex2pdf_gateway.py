import subprocess
from unittest.mock import MagicMock, mock_open, patch

import pytest

from src.core.gateway.latex2pdf.latex2pdf_gateway import Latex2PDFRendererGateway


@pytest.fixture
def pdf_renderer_gateway():
    """Fixture to provide a PDFRendererGateway instance."""
    return Latex2PDFRendererGateway()


def test_render_pdf_success(pdf_renderer_gateway):
    """Test successful PDF rendering."""
    template = r"""
    \documentclass{article}
    \begin{document}
    Hello, John!
    \end{document}
    """
    with (
        patch("subprocess.run") as mock_run,
        patch("builtins.open", mock_open(read_data=b"PDF_CONTENT")) as mock_file,
        patch("tempfile.TemporaryDirectory") as mock_temp_dir,
    ):
        # Mock the temporary directory
        mock_temp_dir.return_value.__enter__.return_value = "/mock/tempdir"

        # Mock subprocess output
        mock_run.return_value = MagicMock(stdout=b"", stderr=b"")

        result = pdf_renderer_gateway.render_pdf(template)

        # Verify subprocess.run call
        mock_run.assert_called_once_with(
            ["pdflatex", "-interaction=nonstopmode", "/mock/tempdir/document.tex"],
            cwd="/mock/tempdir",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        # Verify PDF file was read
        mock_file.assert_any_call(
            "/mock/tempdir/document.tex", "w"
        )  # Writing the LaTeX template
        mock_file.assert_any_call(
            "/mock/tempdir/document.pdf", "rb"
        )  # Reading the generated PDF
        assert result == b"PDF_CONTENT"


def test_render_pdf_failure(pdf_renderer_gateway):
    """Test PDF rendering failure due to LaTeX error."""
    template = r"\invalidlatex"
    with (
        patch("subprocess.run") as mock_run,
        patch("builtins.open", mock_open()) as mock_file,
        patch("tempfile.TemporaryDirectory") as mock_temp_dir,
    ):
        # Mock the temporary directory
        mock_temp_dir.return_value.__enter__.return_value = "/mock/tempdir"

        # Simulate LaTeX compilation failure
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="pdflatex", stderr=b"Compilation failed"
        )

        with pytest.raises(
            ValueError, match="LaTeX compilation failed: Compilation failed"
        ):
            pdf_renderer_gateway.render_pdf(template)

        # Verify subprocess.run call
        mock_run.assert_called_once_with(
            ["pdflatex", "-interaction=nonstopmode", "/mock/tempdir/document.tex"],
            cwd="/mock/tempdir",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        # Verify file write was attempted for the LaTeX template
        mock_file.assert_called_with("/mock/tempdir/document.tex", "w")
