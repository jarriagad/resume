# This script will generate the static files for flask to serve

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase.pdfmetrics import stringWidth


from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl
from box import Box

from jinja2 import Environment, FileSystemLoader
from yaml import load
import shutil
import os

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def read_resume_config(filename: str) -> dict:
    with open(filename, "r", encoding="utf8") as file:
        resume_data = load(file.read(), Loader=Loader)

    return resume_data


def generate_pdf(template: str, target: str, resume_data: dict) -> None:
    resume = Box(resume_data)
    outfile = target
    template = PdfReader(template, decompress=False).pages[0]
    template_obj = pagexobj(template)

    # Set texts here
    full_name = f"{resume.personal.first_name} {resume.personal.last_name}"
    email = resume.personal.contact_info.email[0]

    phone_dict = Box(resume.personal.contact_info.phone[0])
    phone = (
        f"{phone_dict.country_code} ({phone_dict.area_code}) {phone_dict.phone_number}"
    )

    location = resume.personal.location

    short_summary = resume.career.short_summary
    long_summary = resume.career.long_summary

    company = resume.experience[0].company
    title = resume.experience[0].job_title
    dates = resume.experience[0].start + " - " + resume.experience[0].end

    # Letter size is 612x792
    canvas = Canvas(outfile, pagesize=letter)
    xobj_name = makerl(canvas, template_obj)

    # Import the og form
    canvas.doForm(xobj_name)

    # Title
    canvas.setFont("Times-Bold", 22)
    canvas.drawString(20, 765, full_name)

    # Sub-title
    yval = 740
    xval = 20
    canvas.setFont("Times-Bold", 12)
    canvas.drawString(xval, yval, "Professional Summary")
    canvas.setFont("Times-Roman", 14)
    canvas.drawString(165, yval, email)
    canvas.drawString(347, yval, "•")
    canvas.drawString(365, yval, phone)
    canvas.drawString(482, yval, "•")
    canvas.drawString(500, yval, location)

    line_offset = 4
    canvas.line(20, yval - line_offset, 592, yval - line_offset)

    # Summary - yes
    yval = 725
    xval = 55
    canvas.setFont("Times-Roman", 12)
    canvas.drawString(xval, yval, short_summary)

    style = ParagraphStyle(
        name="Times-Roman", fontName="Times-Roman", fontSize=12, leading=15
    )
    paragraph = Paragraph(long_summary, style)
    paragraph.wrapOn(canvas, 572, 50)
    paragraph.drawOn(canvas, xval - 35, yval - 75)

    # Work experience
    yval = 620
    xval = 20
    canvas.setFont("Times-Bold", 12)
    canvas.drawString(xval, yval, "Work Experience")
    canvas.line(20, yval - line_offset, 592, yval - line_offset)

    initx = xval
    inity = yval - 22

# loop for job tasks
    for job in resume.experience[:5]:
        company = job.company
        title = job.job_title
        location = job.location
        dates = location + "   •   " + job.start + " - " + job.end
        job_tasks = "<br/>".join(f"• {item}" for item in job.accomplishments)

        font_size_company = 12
        font_size_title = 10
        leading = 15
        space_between_title_and_paragraph = 2  # Adjust this value to change the space

        canvas.setFont("Times-Bold", 12)
        canvas.drawString(initx, inity, company)
        canvas.setFont("Times-Roman", font_size_company)
        dates_width = stringWidth(dates, "Times-Roman", font_size_company)
        canvas.drawString(592 - dates_width, inity, dates)
        inity -= leading
        canvas.setFont("Times-Italic", font_size_title)
        canvas.drawString(initx, inity, title)
        inity -= space_between_title_and_paragraph

        paragraph = Paragraph(job_tasks, style)
        paragraph_width, paragraph_height = paragraph.wrapOn(canvas, 572, 50)
        paragraph.drawOn(canvas, initx, inity - paragraph_height - leading)
        
        total_height = font_size_company + font_size_title + paragraph_height + 1 * leading
        inity -= total_height

    # New page
    canvas.showPage()

    # Skills
    yval = 740
    xval = 20
    canvas.setFont("Times-Bold", 12)
    canvas.drawString(xval, yval, "Skills Summary")
    canvas.line(20, yval - line_offset, 592, yval - line_offset)

    initx = xval
    inity = yval - 22

# loop for job tasks
    for skill in resume.career.core_skills:
        skill_title = skill.name
        skill_list = skill.skills
        skill_line = "• " + skill_title + ": " + ", ".join(skill_list)


        font_size_company = 12
        font_size_title = 10
        leading = 15
        space_between_title_and_paragraph = 2  # Adjust this value to change the space

        canvas.setFont("Times-Roman", font_size_company)
        canvas.drawString(initx, inity, skill_line)
        total_height = font_size_company + 5
        inity -= total_height
    
    # Education
    yval = inity - 15
    xval = 20
    canvas.setFont("Times-Bold", 12)
    canvas.drawString(xval, yval, "Education & Certs")
    canvas.line(20, yval - line_offset, 592, yval - line_offset)
    
    # Draw the current education
    canvas.setFont("Times-Roman", 12)
    canvas.drawString(xval, yval - 22, "Current:")
    yval -= 40
    for item in resume.education.current:
        canvas.drawString(40, yval, f"• {item}")
        yval -= 15

    # Draw the pending education
    yval -= 5
    canvas.drawString(20, yval, "Pending:")
    yval -= 20
    for item in resume.education.pending:
        canvas.drawString(40, yval, f"• {item}")
        yval -= 15

    # Save
    canvas.save()

def generate_html(
    templates_dir: str, template_index: str, static_path_index: str, resume_data: dict
) -> None:
    # render jinja things
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template(template_index)
    template_output = template.render(resume_data)

    # Write contents to file
    with open(static_path_index, "w", encoding="utf8") as file:
        file.write(template_output)


def copy_src(src: str, dest: str) -> None:
    for item in os.listdir(src):
        src_item = os.path.join(src, item)
        dest_item = os.path.join(dest, item)
        
        if os.path.isdir(src_item):
            shutil.copytree(src_item, dest_item)
        else:
            shutil.copy2(src_item, dest_item)

def main() -> None:
    data_dir = "data"
    data_file = "resume_info.yml"
    data_path = data_dir + "/" + data_file
    templates_dir = "static_templates"
    template_index = "index.html.jinja"
    static_dir = "static"
    static_index = "resume.html"
    static_path_index = static_dir + "/" + static_index
    pdf_file = templates_dir + "/blank_pdf.pdf"
    pdf_target = static_dir + "/javier-arriagada-resume.pdf"
    file_src = templates_dir + "/" + "src"

    resume_data = read_resume_config(data_path)

    generate_html(
        templates_dir=templates_dir,
        template_index=template_index,
        static_path_index=static_path_index,
        resume_data=resume_data,
    )
    print("Generated HTML")

    generate_pdf(
        template=pdf_file,
        target=pdf_target,
        resume_data=resume_data,
    )
    print("Generated PDF")

    copy_src(src=file_src, dest=static_dir)
    print("src files copied")


if __name__ == "__main__":
    main()
    print("End of script")

