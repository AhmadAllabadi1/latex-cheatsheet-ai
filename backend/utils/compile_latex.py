import subprocess
import os
import uuid
import shutil

def compile_latex_to_pdf(latex_code: str) -> str:
    # Create temp directory if it doesn't exist
    temp_dir = os.path.join(os.getcwd(), "temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    job_id = str(uuid.uuid4())
    work_dir = os.path.join(temp_dir, job_id)
    os.makedirs(work_dir)

    tex_path = os.path.join(work_dir, "document.tex")
    pdf_path = os.path.join(work_dir, "document.pdf")

    # Print the LaTeX code being compiled
    print("Compiling LaTeX code:")
    print(latex_code)
    print("-" * 80)

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_code)

    try:
        # Check if pdflatex is installed
        try:
            subprocess.run(["pdflatex", "--version"], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE, 
                         check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise Exception("pdflatex is not installed. Please install a LaTeX distribution like MiKTeX or TeX Live.")

        # Run pdflatex
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_path],
            cwd=work_dir,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("LaTeX output:")
        print(result.stdout)
        if result.stderr:
            print("LaTeX errors:")
            print(result.stderr)

        if not os.path.exists(pdf_path):
            raise Exception("PDF was not generated")

        return pdf_path 
    except subprocess.CalledProcessError as e:
        error_msg = f"LaTeX compilation failed:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        print(error_msg)
        # Clean up the temporary directory
        shutil.rmtree(work_dir, ignore_errors=True)
        raise Exception(error_msg)
    except Exception as e:
        print("LaTeX compile error:", str(e))
        # Clean up the temporary directory
        shutil.rmtree(work_dir, ignore_errors=True)
        raise Exception(f"LaTeX compilation failed: {str(e)}")
