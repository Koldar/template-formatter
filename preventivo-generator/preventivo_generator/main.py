import argparse
import os

import shutil
import subprocess
from datetime import datetime

import jinja2
import sys
import tempfile
import configparser

VERSION = "1.0.0"

class PreventivoEntry:

    def __init__(self):
        self.title = ""
        self.description = ""
        self.quantity = 0
        self.price_unit = 0.
        self.partial_price = 0.


class Model:

    def __init__(self):
        self.company_logo = None
        self.company_name = None
        self.company_address = None
        self.company_email = None
        self.company_telephone = None
        self.company_piva = None
        self.company_cf = None
        self.preventivo_id_year = None
        self.preventivo_id = None
        self.preventivo_date = None
        self.preventivo_object = None
        self.destinatario_name = None
        self.destinatario_address = None
        self.title_background_color = None
        self.description_background_color = None
        self.output_file = None
        self.entries = []
        self.total_price = 0


def parse_options(args):
    parser = argparse.ArgumentParser(description="""
        Allows to generate a preventivo
    """)
    parser.add_argument("--inputFile", type=str, required=False, default=None, help="""
        If present, we will load the content of the file
    """)
    parser.add_argument("--companyLogo", type=str, required=False, default=None, help="""
        Path to image to put in the preventivo representing the logo of your company
    """)
    parser.add_argument("--companyName", type=str, required=False, default=None,  help="""
        Name of your company
    """)
    parser.add_argument("--companyAddress", type=str, required=False, default=None,  help="""
        Address of your company
    """)
    parser.add_argument("--companyEmail", type=str, required=False, default=None, help="""
        Email of your company
    """)
    parser.add_argument("--companyTelephone", type=str, required=False, default=None, help="""
        Telephone of your company
    """)
    parser.add_argument("--companyPiva", type=str, required=False, default=None, help="""
        Partita IVA of your company
    """)
    parser.add_argument("--companyCf", type=str, required=False, default=None, help="""
        Codice Fiscale of your company
    """)
    parser.add_argument("--preventivoIdYear", type=str, required=False, default=None, help="""
        Year to put in the peeventivo id
    """)
    parser.add_argument("--preventivoId", type=str, required=False, default=None, help="""
        Id of the preventivo
    """)
    parser.add_argument("--preventivoDate", type=str, required=False, default=None, help="""
        Date of the preventivo
    """)
    parser.add_argument("--preventivoObject", type=str, required=False, default=None, help="""
        Object the preventivo will be aimed to
    """)
    parser.add_argument("--destinatarioName", type=str, required=False, default=None, help="""
        Name of the destinatario of this preventivo
    """)
    parser.add_argument("--destinatarioAddress", type=str, required=False, default=None, help="""
        Address of the destinatario
    """)
    parser.add_argument("--destinatarioNotes", type=str, required=False, default=None, help="""
        Notes of the destinatario. Will be skipped
    """)
    parser.add_argument("--titleBackgroundColor", type=str, required=False, default=None, help="""
        Color of the background of the table containig title rows
    """)
    parser.add_argument("--descriptionBackgroundColor", type=str, required=False, default=None, help="""
        Color of the background of the table containig title rows
    """)
    parser.add_argument("--outputFile", type=str, required=False, default=None, help="""
        name of the output file
    """)

    return parser.parse_args(args)


def load_from_config(config_filepath: str, model: Model):
    config = configparser.ConfigParser()
    config.read(config_filepath)

    if "Company" in config.sections():
        company_section = config["Company"]
        try:
            model.company_telephone = company_section["companyTelephone"]
        except KeyError:
            pass
        try:
            model.company_piva = company_section["companyPIVA"]
        except KeyError:
            pass
        try:
            model.company_name = company_section["companyName"]
        except KeyError:
            pass
        try:
            model.company_logo = company_section["companyLogo"]
        except KeyError:
            pass
        try:
            model.company_email = company_section["companyEmail"]
        except KeyError:
            pass
        try:
            model.company_address = company_section["companyAddress"]
        except KeyError:
            pass
        try:
            model.company_cf = company_section["companyCF"]
        except KeyError:
            pass

    if "Destinatario" in config.sections():
        destinatario_section = config["Destinatario"]

        try:
            model.destinatario_name = destinatario_section["destinatarioName"]
        except KeyError:
            pass

        try:
            model.destinatario_address = destinatario_section["destinatarioAddress"]
        except KeyError:
            pass

        try:
            model.destinatario_notes = list(filter(lambda x: len(x) > 0, destinatario_section["destinatarioNotes"].splitlines()))
        except KeyError:
            pass

    if "Settings" in config.sections():
        settings_section = config["Settings"]

        try:
            model.output_file = settings_section["outputFile"]
        except KeyError:
            pass

    if "Customization" in config.sections():
        customization_section = config["Customization"]

        try:
            model.description_background_color = customization_section["descriptionBackgroundColor"]
        except KeyError:
            pass
        try:
            model.title_background_color = customization_section["titleBackgroundColor"]
        except KeyError:
            pass

    for section_name in config.sections():

        if section_name in ["Settings", "Customization", "Destinatario", "Company"]:
            continue

        entry_section = config[section_name]

        entry = PreventivoEntry()
        try:
            entry.title = entry_section["title"]
        except KeyError:
            pass
        try:
            entry.description = entry_section["description"]
        except KeyError:
            pass
        try:
            entry.quantity = int(entry_section["quantity"])
        except KeyError:
            pass
        try:
            entry.price_unit = float(entry_section["priceUnit"])
        except KeyError:
            pass

        model.entries.append(entry)

    return model


def generate_model(args) -> Model:
    model = Model()
    options = parse_options(args)

    # load the config file, if any
    if options.inputFile is not None:
        load_from_config(options.inputFile, model)

    # overwrite from command line, if present
    if options.companyLogo is not None:
        model.company_logo = options.companyLogo

    if options.companyName is not None:
        model.company_name = options.companyName

    if options.companyAddress is not None:
        model.company_address = options.companyAddress

    if options.companyEmail is not None:
        model.company_email = options.companyEmail

    if options.companyTelephone is not None:
        model.company_telephone = options.companyTelephone

    if options.companyPiva is not None:
        model.company_piva = options.companyPiva

    if options.companyCf is not None:
        model.company_cf = options.companyCf

    if options.preventivoIdYear is not None:
        model.preventivo_id_year = options.preventivoIdYear

    if options.preventivoId is not None:
        model.preventivo_id = options.preventivoId

    if options.preventivoDate is not None:
        model.preventivo_date = options.preventivoDate

    if options.preventivoObject is not None:
        model.preventivo_object = options.preventivoObject

    if options.destinatarioName is not None:
        model.destinatario_name = options.destinatarioName

    if options.destinatarioAddress is not None:
        model.destinatario_address = options.destinatarioAddress

    if options.destinatarioNotes is not None:
        model.destinatario_notes = options.destinatarioNotes

    if options.titleBackgroundColor is not None:
        model.title_background_color = options.titleBackgroundColor

    if options.descriptionBackgroundColor is not None:
        model.description_background_color = options.descriptionBackgroundColor

    if options.outputFile is not None:
        model.output_file = options.outputFile

    # use default values
    now = datetime.utcnow()

    if model.company_logo is None:
        model.company_logo = "logo.png"

    if model.company_name is None:
        model.company_name = "<company name>"

    if model.company_address is None:
        model.company_address = "<company address>"

    if model.company_email is None:
        model.company_email = "company@company.com"

    if model.company_telephone is None:
        model.company_telephone = "<company telephone>"

    if model.company_piva is None:
        model.company_piva = "<company PIVA>"

    if model.company_cf is None:
        model.company_cf = "<company CF>"

    if model.preventivo_id_year is None:
        model.preventivo_id_year = now.year

    if model.preventivo_id is None:
        model.preventivo_id = 0

    if model.preventivo_date is None:
        model.preventivo_date = f"{now.day:02d}/{now.month:02d}/{now.year:04d}"

    if model.preventivo_object is None:
        model.preventivo_object = "<object>"

    if model.destinatario_name is None:
        model.destinatario_name = "<destinatario name>"

    if model.destinatario_address is None:
        model.destinatario_address = "client@client.com"

    if model.destinatario_notes is None:
        model.destinatario_notes = []

    if model.title_background_color is None:
        model.title_background_color = "0.68,0.93,0.93"

    if model.description_background_color is None:
        model.description_background_color = "1,1,1"

    if model.output_file is None:
        model.output_file = "preventivo.pdf"

    return model


def main():
    model = generate_model(sys.argv[1:])

    template_loader = jinja2.FileSystemLoader(
        searchpath=os.path.abspath(os.path.join(os.curdir, "templates")),
        encoding="utf-8"
    )
    env = jinja2.Environment(
        loader=template_loader,
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="<<",
        variable_end_string=">>",
        comment_start_string="<#",
        comment_end_string="#>",
    )

    model.total_price = 0
    for i, preventivo_entry in enumerate(model.entries):
        preventivo_entry.partial_price = preventivo_entry.quantity * preventivo_entry.price_unit
        model.total_price += preventivo_entry.partial_price

    template_filepath = os.path.abspath(os.path.join(os.curdir, "templates", "preventivoTemplate.tex.jinja2"))
    print(f"loading file template: {template_filepath}")
    template = env.get_template("preventivoTemplate.tex.jinja2")
    actual_file_content = template.render(
        model=model,
        # commons function
        enumerate=enumerate,
        len=len,
        program_version=VERSION
    )

    with tempfile.TemporaryDirectory():
        tempdir = tempfile.mkdtemp(prefix="preventivo")
        latex_src_filepath = os.path.abspath(os.path.join(tempdir, 'preventivo.tex'))
        with open(latex_src_filepath, "w", encoding="utf-8") as f:
            f.write(actual_file_content)

        # call latex
        pdf_filename = "preventivo"
        call_latex(
            aux_directory=tempdir,
            output_directory=tempdir,
            job_name=pdf_filename,
            tex_path=latex_src_filepath
        )

        pdf_filepath = os.path.abspath(os.path.join(tempdir, f"{pdf_filename}.pdf"))

        if not os.path.exists(pdf_filepath):
            raise ValueError(f"cannot find generated file \"{pdf_filepath}\"!")

        print(f"moving file: {pdf_filepath} to {model.output_file}")
        shutil.move(pdf_filepath, model.output_file)


def call_latex(aux_directory: str, job_name: str, output_directory: str, tex_path: str):
    result_code = subprocess.call(args=[
        f"lualatex.exe",
        f"--aux-directory={aux_directory}",
        f"--c-style-errors",
        f"--halt-on-error",
        f"--interaction=nonstopmode",
        f"--output-format=pdf",
        f"--job-name={job_name}",
        f"--output-directory={output_directory}",
        f"{tex_path}",
    ], stdout=True, stderr=True, shell=True)
    if result_code != 0:
        raise ValueError(f"latex generated an error (first run). Result code={result_code}.")

    result_code = subprocess.call(args=[
        f"lualatex.exe",
        f"--aux-directory={aux_directory}",
        f"--c-style-errors",
        f"--halt-on-error",
        f"--interaction=nonstopmode",
        f"--output-format=pdf",
        f"--job-name={job_name}",
        f"--output-directory={output_directory}",
        f"{tex_path}",
    ], stdout=True, stderr=True, shell=True)
    if result_code != 0:
        raise ValueError(f"latex generated an error (second run). Result code={result_code}.")


if __name__ == "__main__":
    main()
