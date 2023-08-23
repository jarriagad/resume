# This script will generate the static files for flask to serve

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph


from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl
from box import Box

from jinja2 import Environment, FileSystemLoader
from yaml import load

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
    phone      = f"{phone_dict.country_code} ({phone_dict.area_code}) {phone_dict.phone_number}"

    location = resume.personal.location

    short_summary = resume.career.short_summary
    long_summary  = resume.career.long_summary

    company = resume.experience[0].company
    title   = resume.experience[0].job_title
    dates   = resume.experience[0].start + " - " + resume.experience[0].end

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

    # Summary
    yval = 720
    xval = 55
    canvas.setFont("Times-Roman", 12)
    canvas.drawString(xval, yval, short_summary)

    style = ParagraphStyle(name="Times-Roman", fontName="Times-Roman", fontSize=12, leading=15)
    paragraph = Paragraph(long_summary, style)
    paragraph.wrapOn(canvas, 572, 50)
    paragraph.drawOn(canvas, xval - 35, yval - 75)

    # Work experience
    yval = 620
    xval = 20
    canvas.setFont("Times-Bold", 12)
    canvas.drawString(xval, yval, "Work Experience")
    canvas.line(20, yval - line_offset, 592, yval - line_offset)

    canvas.drawString(xval, yval - 22, company)
    canvas.setFont("Times-Roman", 12)
    canvas.drawString(510, yval - 22, dates)
    canvas.setFont("Times-Italic", 10)
    canvas.drawString(xval, yval - 35, title)



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
    pdf_target = static_dir + "/test_resume.pdf"

    resume_data = read_resume_config(data_path)

    generate_html(
        templates_dir=templates_dir,
        template_index=template_index,
        static_path_index=static_path_index,
        resume_data=resume_data,
    )

    generate_pdf(
        template=pdf_file,
        target=pdf_target,
        resume_data=resume_data,
    )


if __name__ == "__main__":
    main()
