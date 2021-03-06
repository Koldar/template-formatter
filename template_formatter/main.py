import argparse
import logging
import math
import os
import shutil

from datetime import datetime
from typing import Any, Iterable, Tuple

import sys
import toml

from template_formatter import version
from template_formatter.AppContext import AppContext
from template_formatter.FStringFormatter import FStringFormatter
from template_formatter.Jinja2Formatter import Jinja2Formatter
from template_formatter.PythonFormatFormatter import PythonFormatFormatter
from template_formatter.PythonFormatter import PythonFormatter


def safe_eval(eval_str: str, **values) -> Any:
    local_names = {}
    for k, v in values.items():
        local_names[k] = v
    return eval(eval_str, {}, local_names)


def parse_options(args):
    parser = argparse.ArgumentParser(
        prog="""template-formatter""",
        description="""
        Allows to generate a file formatted according jinja2 template or other template engines.
        """,
        epilog=f"version {version.VERSION}, Copyright 2020 Massimo Bono"
    )
    parser.add_argument("templateString", type=str, nargs='?', default=None, help="""
        If present, it represents the string with jinja2 template that we need to parse. If present, it ovewrites inputFile
    """)
    parser.add_argument("-f", "--format", type=str, required=False, default=None, help="""
        String representing how is layout the template file/string. Allowed values are:
         - jinja2 (the default): the template is formatted according jinja2 template 
                (see https://jinja.palletsprojects.com/en/2.11.x/);
         - format: the template is formatted according "format" python function 
                (see https://docs.python.org/3/library/string.html#format-specification-mini-language)
         - fstring: the python string interpolation 
                (see https://docs.python.org/3/tutorial/inputoutput.html#tut-f-strings). 
                If you use it, ensures that at the beginning and at the end of the string to interpolate
                there is a pythonic start and end element (e.g., ", ', or \"\"\")
        - python: the template string is interpreted as a python script. Everythign that you will be print
                on the standard console (e.g., with print) will the rendered 
    """)
    parser.add_argument("--configFile", type=str, required=False, default=None, help="""
        A configuration file, containing the variables used to format the jinja2 template. Follows the TOML 
        specification. For further information, please see https://toml.io/en/
    """)
    parser.add_argument("--inputFile", type=str, required=False, default=None, help="""
        the template jinja2 file. If absent we will look for the file in configFile.
    """)
    parser.add_argument("--inputDirectory", type=str, required=False, default=None, help="""
        A directory that we need to template. We will scan the whole directory. If we find any file ending with ".template"
        we will compile such file with this utility. Notice that directories with no files will not be processed at all.
    """)
    parser.add_argument("--outputDirectory", type=str, required=False, default=None, help="""
        if inputDirectory is provided, this string represents the directory to create containing the instantiated folder 
    """)
    parser.add_argument("--trailingStringTemplateFile", type=str, required=False, default=None, help="""
        The trailing substring each template file and directory we need to template has. Meaningful only if inputDirectory is set.
        Default to ".template"
    """)
    parser.add_argument("-w", "--writeOnStdout", action="store_true", required=False, default=False, help="""
        If set, we will put the content of the generated file on the stdout rather than in a file. Overwrite outputFile
    """)
    parser.add_argument("--outputFile", type=str, required=False, default=None, help="""
        name of the output file to generate. You can use:
          - {basename} to refer to the basename of the input file;
          - {basedir} to refer to the directory of the input file;
          - {filename} to refer to the absolute path of the input file, without extension
          - {ext} to ref to the extension of the input file;
        If the path is relative, it will created w.r.t the CWD
    """)
    parser.add_argument("-v", "--version", action="store_true", required=False, default=False, help="""
    If present, print the program version and stop
    """)
    parser.add_argument("-i", "--inputFileEncoding", type=str, required=False, default=None, help="""
        the encoding of the given input file. If left unspecified, it is utf8.
    """)
    parser.add_argument("-o", "--outputFileEncoding", type=str, required=False, default=None, help="""
            the encoding of the output file. If left unspecified, it is utf8.
        """)
    parser.add_argument("-l", "--loglevel", type=str, required=False, default=None, help="""
        the log level for this application. loglevel allowed values are INFO, DEBUG, CRITICAL
    """)
    parser.add_argument("-b", "--blockStartString", type=str, required=False, default=None, help="""
        the jinja2 string that will start a new python block to interpret. If unspecified, it is "{%%"
    """)
    parser.add_argument("-B", "--blockEndString", type=str, required=False, default=None, help="""
        the jinja2 string that will end a previously opened python block to interpret. If unspecified, it is "%%}"
    """)
    parser.add_argument("-c", "--commentStartString", type=str, required=False, default=None, help="""
        the jinja2 string that will start a new python comment to interpret. If unspecified, it is "{#"
    """)
    parser.add_argument("-C", "--commentEndString", type=str, required=False, default=None, help="""
        the jinja2 string that will end a previously opened python comment to interpret. If unspecified, it is "#}"
    """)
    parser.add_argument("-e", "--expressionStartString", type=str, required=False, default=None, help="""
        the jinja2 string that will start a new python expression to interpret. If unspecified, it is "{#"
    """)
    parser.add_argument("-E", "--expressionEndString", type=str, required=False, default=None, help="""
        the jinja2 string that will end a previously opened python expression to interpret. If unspecified, it is "#}"
    """)
    parser.add_argument("-L", "--lineStatementPrefix", type=str, required=False, default=None, help="""
        the jinja2 string that will start a line statement. If unspecified it is "#"
    """)
    parser.add_argument("-V", "--value", action="append", nargs=2, required=False, default=[], help="""
        Represents a key value that can be used in the jinja2 template. 
        If the same key is addded multiple time, it represents a list of values
        --value a 3 --value a 4 # a will be values.a=[3,4]
        you can generate hierarchies of values like in the following:
        --value a.b 3 --value a.c 5 # a will be values.a={b=3, c=5}
        to force the creation of an array use [x] (where x is a number):
        -- value a[0].b 3 --value a[1].b 5 # a will be value.a = [{b: 3}, {b: 5}]
        These values will override the values present in the configFile, if present.
        You can use [] without specifiynic the index to indicate the last element of the list
    """)

    return parser.parse_args(args)


def update_using_config(app_context: AppContext, config_file: str) -> AppContext:
    abs_config_file = os.path.abspath(config_file)
    with open(abs_config_file, "r") as f:
        parsed_toml = toml.loads(f.read())

        if "general" in parsed_toml:
            general_section = parsed_toml["general"]
            if "input_file" in general_section:
                app_context.input_file = general_section["input_file"]
                if not os.path.isabs(app_context.input_file):
                    app_context.input_file = os.path.abspath(os.path.join(
                        os.path.dirname(abs_config_file),
                        app_context.input_file
                    ))
            if "inputDirectory" in general_section:
                app_context.input_directory = general_section["input_directory"]
            if "outputDirectory" in general_section:
                app_context.output_directory = general_section["output_directory"]
            if "trailingStringTemplateFile" in general_section:
                app_context.trailing_string_template_file = general_section["trailing_string_template_file"]
            if "output_file_format" in general_section:
                app_context.output_file_format = general_section["output_file_format"]
            if "log_level" in general_section:
                app_context.log_level = general_section["log_level"]
            if "block_start_string" in general_section:
                app_context.block_start_string = general_section["block_start_string"]
            if "block_end_string" in general_section:
                app_context.block_end_string = general_section["block_end_string"]
            if "comment_start_string" in general_section:
                app_context.comment_start_string = general_section["comment_start_string"]
            if "comment_end_string" in general_section:
                app_context.comment_end_string = general_section["comment_end_string"]
            if "expression_start_string" in general_section:
                app_context.expression_start_string = general_section["expression_start_string"]
            if "expression_end_string" in general_section:
                app_context.expression_end_string = general_section["expression_end_string"]
            if "line_statement_prefix" in general_section:
                app_context.line_statement_prefix = general_section["line_statement_prefix"]
            if "input_file_encoding" in general_section:
                app_context.input_file_encoding = general_section["input_file_encoding"]
            if "output_file_encoding" in general_section:
                app_context.output_file_encoding = general_section["output_file_encoding"]
            if "write_on_stdout" in general_section:
                app_context.write_on_stdout = general_section["write_on_stdout"]
            if "template_string" in general_section:
                app_context.template_string = general_section["template_string"]
            if "format" in general_section:
                app_context.format = general_section["format"]

        if "values" in parsed_toml:
            for k, v in parsed_toml["values"].items():
                app_context.model.values.set_field(k, v)

        if "functions" in parsed_toml:
            for k, v in parsed_toml["functions"].items():
                app_context.model.functions[k] = safe_eval(v)

    return app_context


def pairs(iterable, terminate_with) -> Iterable[Tuple[Any, Any]]:
    item1_filled = False
    item1 = None
    for x in iterable:
        if not item1_filled:
            item1 = x
        else:
            yield item1, x
            item1 = x
    yield item1, terminate_with


def update_using_command_line(app_context: AppContext, options: argparse.Namespace) -> "AppContext":

    def handle_single_value(aapp_context: AppContext, akey: str, avalue: Any) -> "AppContext":
        # keep generating the value
        exec(f"app_context.model.values.{akey}.set_value(value)", {"value": avalue, "app_context": aapp_context})

    if options.inputFile is not None:
        app_context.input_file = options.inputFile
    if options.outputFile is not None:
        app_context.output_file_format = options.outputFile
    if options.inputDirectory is not None:
        app_context.input_directory = options.inputDirectory
    if options.outputDirectory is not None:
        app_context.output_directory = options.outputDirectory
    if options.trailingStringTemplateFile is not None:
        app_context.trailing_string_template_file = options.trailingStringTemplateFile
    if options.loglevel is not None:
        app_context.log_level = options.loglevel
    if options.blockStartString is not None:
        app_context.block_start_string = options.blockStartString
    if options.blockEndString is not None:
        app_context.block_end_string = options.blockEndString
    if options.commentStartString is not None:
        app_context.comment_start_string = options.commentStartString
    if options.commentEndString is not None:
        app_context.comment_end_string = options.commentEndString
    if options.expressionStartString is not None:
        app_context.expression_start_string = options.expressionStartString
    if options.expressionEndString is not None:
        app_context.expression_end_string = options.expressionEndString
    if options.lineStatementPrefix is not None:
        app_context.line_statement_prefix = options.lineStatementPrefix
    if options.inputFileEncoding is not None:
        app_context.input_file_encoding = options.inputFileEncoding
    if options.outputFileEncoding is not None:
        app_context.output_file_encoding = options.output_file_encoding
    if options.writeOnStdout is not None:
        app_context.write_on_stdout = options.writeOnStdout
    if options.templateString is not None:
        app_context.template_string = options.templateString
    if options.format is not None:
        app_context.format = options.format

    # for key, value in options.value:
    #     handle_single_value(app_context, key, value)
    for key, value in options.value:
        handle_single_value(app_context, key, value)

    return app_context


def apply_defaults(app_context: AppContext) -> AppContext:
    if app_context.input_file is None:
        app_context.input_file = "input.jinja2"
    if app_context.output_file_format is None:
        app_context.output_file_format = app_context.input_file + ".out"
    if app_context.log_level is None:
        app_context.log_level = "CRITICAL"
    if app_context.block_start_string is None:
        app_context.block_start_string = "{%"
    if app_context.block_end_string is None:
        app_context.block_end_string = "%}"
    if app_context.comment_start_string is None:
        app_context.comment_start_string = "{#"
    if app_context.comment_end_string is None:
        app_context.comment_end_string = "#}"
    if app_context.expression_start_string is None:
        app_context.expression_start_string = "{{"
    if app_context.expression_end_string is None:
        app_context.expression_end_string = "}}"
    if app_context.line_statement_prefix is None:
        app_context.line_statement_prefix = "#"
    if app_context.input_file_encoding is None:
        app_context.input_file_encoding = "utf-8"
    if app_context.output_file_encoding is None:
        app_context.output_file_format = "utf-8"
    if app_context.write_on_stdout is None:
        app_context.write_on_stdout = False
    if app_context.template_string is None:
        app_context.template_string = None
    if app_context.format is None:
        app_context.format = "jinja2"
    if app_context.input_directory is None:
        app_context.input_directory = None
    if app_context.output_directory is None:
        app_context.output_directory = None
    if app_context.trailing_string_template_file is None:
        app_context.trailing_string_template_file = ".template"

    return app_context


def add_commons(app_context: AppContext) -> AppContext:
    now = datetime.now()
    utc_now = datetime.utcnow()

    # add data to commons
    app_context.model.commons["now"] = now
    app_context.model.commons["utc_now"] = utc_now
    app_context.model.commons["program_version"] = version.VERSION

    return app_context


def add_functions(app_context: AppContext) -> AppContext:
    standard = dict(
        # commons function (they are so popular that we put them on the cwd)
        enumerate=enumerate,
        map=map,
        filter=filter,
        len=len,
        math=math,
        datetime=datetime,
    )
    app_context.model.functions.update(standard)
    return app_context


def template_string(app_context: AppContext, string: str, formatter: "ITemplateFormatter") -> str:
    # we need to templatize the string
    formatter.init_string(string, app_context)

    actual_file_content = formatter.render_template(
        model=app_context.model.values,
        commons=app_context.model.commons,
        functions=app_context.model.functions
    )

    formatter.reset()
    return actual_file_content


def template_file(app_context: AppContext, file: str, formatter: "ITemplateFormatter") -> str:
    """
    Template a single user file

    :param app_context: context of the whole application
    :param file: file to template
    :param formatter: formatter used to instantiate the template
    :return: a string containing the content of the instantiated file, where each parameter has been replaced with its instantiation
    """
    formatter.init_file(os.path.abspath(file), app_context.input_file_encoding, app_context)
    actual_file_content = formatter.render_template(
        model=app_context.model.values,
        commons=app_context.model.commons,
        functions=app_context.model.functions
    )
    formatter.reset()
    return actual_file_content


def template_directory(app_context: AppContext, directory_to_copy: str, directory_to_generate: str, formatter: "ITemplateFormatter"):
    """
    Scan a gien directory. We create a new whole root directory where each file is instantiated.
    If the file ends with a specific substring, it is assumed it is a template file. If so, we create an instantiation of the file.
    Otherwise, the file is copied as is.

    Notice that also filenames and directory names can be templates as well

    :param app_context: context of the whole directory
    :param directory_to_copy: directory where templates are
    :param directory_to_generate: directory to generate
    :param formatter: formatter to use to format each template file
    :return:
    """

    if not os.path.exists(directory_to_copy):
        raise ValueError(f"{directory_to_copy} does not exist")
    if not os.path.isdir(directory_to_copy):
        raise ValueError(f"{directory_to_copy} is not a valid directory!")

    for dir_path, folders, filenames in os.walk(directory_to_copy):
        # directories to original root. It i9s most likely somethign like a/b/c
        path_to_dir_path = os.path.relpath(start=directory_to_copy, path=dir_path)
        # output dir_path
        output_dir_path = os.path.abspath(os.path.normpath(os.path.join(directory_to_generate, path_to_dir_path)))
        # We must not create the input directory, since it may be instantiated!
        # manage directories
        for folder_name in folders:
            # manage a directory
            if folder_name.endswith(app_context.trailing_string_template_file):
                # strip the trailing string extension
                string_to_template = os.path.basename(folder_name)[:-len(app_context.trailing_string_template_file)]
                # the directory name is a template
                new_folder_name = template_string(app_context, string_to_template, formatter)
            else:
                new_folder_name = folder_name

            # copy directory
            folder_abs_path = os.path.abspath(os.path.join(output_dir_path, new_folder_name))
            os.makedirs(folder_abs_path, exist_ok=True)

        # Manage files
        for f in filenames:
            file_to_copy = os.path.join(dir_path, f)

            if file_to_copy.endswith(app_context.trailing_string_template_file):
                # the filename is a template. Rename the file as well
                string_to_template = os.path.basename(file_to_copy)[:-len(app_context.trailing_string_template_file)]
                new_filename = template_string(
                    app_context=app_context,
                    string=string_to_template,
                    formatter=formatter
                )

                file_content = template_file(
                    app_context=app_context,
                    file=file_to_copy,
                    formatter=formatter
                )

                # write the file
                output_file = os.path.join(output_dir_path, new_filename)
                logging.info(f"Writing instantiated file {output_file}...")
                with open(output_file, mode="w", encoding=app_context.output_file_encoding) as fw:
                    fw.write(file_content)
            else:
                output_file = os.path.join(output_dir_path, f)
                # the filename is not a template. Copy the whole file as is
                shutil.copyfile(file_to_copy, output_file)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    app_context = AppContext()
    options = parse_options(args)

    if options.version:
        print(version.VERSION)
        return

    # read values from config if  present
    if options.configFile is not None:
        app_context = update_using_config(app_context, options.configFile)

    # overwrite values from config
    app_context = update_using_command_line(app_context, options)
    # apply defaults on required items
    app_context = apply_defaults(app_context)

    logging.basicConfig(level=getattr(logging, app_context.log_level))
    logging.info(f"logging level is {app_context.log_level}")

    logging.debug(f"input file = {app_context.input_file}")
    logging.debug(f"input string = {app_context.template_string}")
    logging.debug(f"input directory = {app_context.input_directory}")
    logging.debug(f"block_start_string = {app_context.block_start_string}")
    logging.debug(f"block_end_string = {app_context.block_end_string}")
    logging.debug(f"expression_start_string = {app_context.expression_start_string}")
    logging.debug(f"expression_end_string = {app_context.expression_end_string}")
    logging.debug(f"comment_start_string = {app_context.comment_start_string}")
    logging.debug(f"comment_end_string = {app_context.comment_end_string}")
    logging.debug(f"line_statement_prefix = {app_context.line_statement_prefix}")
    logging.debug(f"format = {app_context.format}")

    # add commons
    app_context = add_commons(app_context)
    app_context = add_functions(app_context)

    logging.info(f"loading file template: {app_context.input_file}")
    logging.debug(f"parameters are {app_context.model}")

    if app_context.format == "jinja2":
        formatter = Jinja2Formatter()
    elif app_context.format == "format":
        formatter = PythonFormatFormatter()
    elif app_context.format == "fstring":
        formatter = FStringFormatter()
    elif app_context.format == "python":
        formatter = PythonFormatter()
    else:
        raise ValueError(f"invalid format {app_context.format}")

    if app_context.input_directory is not None:
        template_directory(app_context, app_context.input_directory, app_context.output_directory, formatter)
        # we need to template a whole directory
        return
    else:
        if app_context.template_string is not None:
            actual_file_content = template_string(app_context, app_context.template_string, formatter)
        elif app_context.input_file is not None:
            actual_file_content = template_file(app_context, app_context.input_file, formatter)
        else:
            raise ValueError(f"Invalid input! Either input_file or template_string needs to be defined!")

        if app_context.write_on_stdout:
            print(actual_file_content)
        else:
            # generate actual output file
            # '/path/to/somefile', '.ext'
            input_filename, input_ext = os.path.splitext(app_context.input_file)
            input_filename = os.path.abspath(input_filename)
            input_basedir = os.path.abspath(os.path.dirname(app_context.input_file))
            input_basename = os.path.basename(app_context.input_file)
            actual_output_file = os.path.abspath(app_context.output_file_format.format(
                filename=input_filename,
                ext=input_ext,
                basename=input_basename,
                basedir=input_basedir
            ))
            with open(actual_output_file, "w", encoding=app_context.output_file_encoding) as f:
                f.write(actual_file_content)


if __name__ == "__main__":
    main()
