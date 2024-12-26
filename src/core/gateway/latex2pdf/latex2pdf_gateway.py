import subprocess
import tempfile


class Latex2PDFRendererGateway:
    """Gateway to render PDFs from LaTeX templates."""

    def render_pdf(self, template: str) -> bytes:
        """
        Render a PDF from a LaTeX template and context.

        Args:
            template (str): The LaTeX template.
        Returns:
            bytes: The rendered PDF content.

        Raises:
            ValueError: If LaTeX compilation fails.
        """
        try:
            # Use a temporary directory to handle intermediate files
            with tempfile.TemporaryDirectory() as temp_dir:
                tex_file = f"{temp_dir}/document.tex"
                pdf_file = f"{temp_dir}/document.pdf"

                # Write the template to a .tex file
                with open(tex_file, "w") as f:
                    f.write(template)

                # Run pdflatex to generate the PDF
                subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", tex_file],
                    cwd=temp_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )

                # Read and return the generated PDF
                with open(pdf_file, "rb") as f:
                    return f.read()

        except subprocess.CalledProcessError as e:
            stderr_output = e.stderr.decode() if e.stderr else e.stdout.decode()
            raise ValueError(f"LaTeX compilation failed: {stderr_output}") from e
