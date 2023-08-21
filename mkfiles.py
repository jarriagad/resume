# This script will generate the static files for flask to serve
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def main():
    data_dir = "data"
    data_file = "resume_info.yml"
    data_path = data_dir + '/' + data_file
    templates_dir = "static_templates"
    template_index = "index.html.jinja"
    static_dir = "static"
    static_index = "resume.html"
    static_path_index = static_dir + "/" + static_index
    pdf_file = "static/test-javier-arriagada-resume.pdf"

    # Load resume data
    with open(data_path, 'r') as file:
        resume_data = load(file.read(), Loader=Loader)

    # render jinja things
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template(template_index)
    template_output = template.render(resume_data)

    # Write contents to file
    with open(static_path_index, 'w') as file:
        file.write(template_output)

    # pdf the things
    pdf_obj = open(pdf_file, 'w+b')

    pisa.CreatePDF(
        template_output,                # the HTML to convert
        dest=pdf_obj)

    pdf_obj.close()

if __name__ == "__main__":
    main()


