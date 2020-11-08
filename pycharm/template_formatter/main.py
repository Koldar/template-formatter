import argparse
import logging
import math
import os
import pprint

from datetime import datetime
from typing import Any, Dict, Callable, Optional

import jinja2
import sys
import toml
from jinja2 import BaseLoader

import version


class Jinja2Model:

    def __init__(self):
        self.values: Dict[str, Any] = {}
        self.functions: Dict[str, Callable] = {}
        self.commons: Dict[str, Any] = {}

    def __str__(self) -> str:
        pp = pprint.PrettyPrinter(indent=4, sort_dicts=True)
        obj = {
            "values": self.values,
            "functions": self.functions,
            "commons": self.commons
        }
        return pp.pformat(obj)


class AppContext:

    def __init__(self):
        self.model = Jinja2Model()
        self.input_file: Optional[str] = None
        self.output_file_format: Optional[str] = None
        self.log_level: Optional[str] = None
        self.block_start_string: Optional[str] = None
        self.block_end_string: Optional[str] = None
        self.comment_start_string: Optional[str] = None
        self.comment_end_string: Optional[str] = None
        self.expression_start_string: Optional[str] = None
        self.expression_end_string: Optional[str] = None
        self.line_statement_prefix: Optional[str] = None
        self.input_file_encoding: Optional[str] = None
        self.output_file_encoding: Optional[str] = None
        self.write_on_stdout: bool = False
        self.template_string: Optional[str] = None


def safe_eval(eval_str: str, **values) -> Any:
    local_names = {}
    for k, v in values.items():
        local_names[k] = v
    return eval(eval_str, {}, local_names)


def parse_options(args):
    parser = argparse.ArgumentParser(
        prog="""template-formatter""",
        description="""
        Allows to generate a file formatted according jinja2 template
        """,
        epilog=f"version {version.VERSION}, Copyright 2020 Massimo Bono"
    )
    parser.add_argument("templateString", type=str, nargs=1, default=None, help="""
        If present, it represents the string with jinja2 template that we need to parse. If present, it ovewrites inputFile
    """)
    parser.add_argument("--configFile", type=str, required=False, default=None, help="""
        A configuration file, containing the variables used to format the jinja2 template. Follows the TOML 
        specification. For further information, please see https://toml.io/en/
    """)
    parser.add_argument("--inputFile", type=str, required=False, default=None, help="""
        the template jinja2 file. If absent we will look for the file in configFile
    """)
    parser.add_argument("--writeOnStdout", action="store_true", required=False, default=False, help="""
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
    parser.add_argument("--inputFileEncoding", type=str, required=False, default=None, help="""
        the encoding of the given input file. If left unspecified, it is utf8.
    """)
    parser.add_argument("--outputFileEncoding", type=str, required=False, default=None, help="""
            the encoding of the output file. If left unspecified, it is utf8.
        """)
    parser.add_argument("--loglevel", type=str, required=False, default=None, help="""
        the log level for this application. loglevel allowed values are INFO, DEBUG, CRITICAL
    """)
    parser.add_argument("--blockStartString", type=str, required=False, default=None, help="""
        the jinja2 string that will start a new python block to interpret. If unspecified, it is "{%%"
    """)
    parser.add_argument("--blockEndString", type=str, required=False, default=None, help="""
        the jinja2 string that will end a previously opened python block to interpret. If unspecified, it is "%%}"
    """)
    parser.add_argument("--commentStartString", type=str, required=False, default=None, help="""
        the jinja2 string that will start a new python comment to interpret. If unspecified, it is "{#"
    """)
    parser.add_argument("--commentEndString", type=str, required=False, default=None, help="""
        the jinja2 string that will end a previously opened python comment to interpret. If unspecified, it is "#}"
    """)
    parser.add_argument("--expressionStartString", type=str, required=False, default=None, help="""
        the jinja2 string that will start a new python expression to interpret. If unspecified, it is "{#"
    """)
    parser.add_argument("--expressionEndString", type=str, required=False, default=None, help="""
        the jinja2 string that will end a previously opened python expression to interpret. If unspecified, it is "#}"
    """)
    parser.add_argument("--lineStatementPrefix", type=str, required=False, default=None, help="""
        the jinja2 string that will start a line statement. If unspecified it is "#"
    """)
    parser.add_argument("--value", action="append", required=False, default=[], help="""
        NOT WORKING ATM
        Represents a key value that can be used in the jinja2 template. 
        If the same key is addded multiple time, it represents a list of values
        --value a=3 --value a=4 # a will be values.a=[3,4]
        you can generate hierarchies of values like in the following:
        --value a.b=3 --value a.c=5 # a will be values.a={b=3, c=5}
        to force the creation of an array use [x] (where x is a number):
        -- value a[0].b=3 --value a[1].b=5 # a will be value.a = [{b: 3}, {b: 5}]
        These values will override the values present in the configFile, if present
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

        if "values" in parsed_toml:
            for k, v in parsed_toml["values"].items():
                app_context.model.values[k] = v

        if "functions" in parsed_toml:
            for k, v in parsed_toml["functions"].items():
                app_context.model.functions[k] = safe_eval(v)

    return app_context


def update_using_command_line(app_context: AppContext, options: argparse.Namespace) -> AppContext:

    # def recursive_handle_single_value(app_context: AppContext, container: Union[List[Any], Dict[str, Any]], depth: int,
    #                                   key_part: str, value: Any, last_key_part_index: int, key_parts: List[str]):
    #     m = re.search(r"^[\w_][\w\d_]*\[(?P<index>\d*)\]$", key_part)
    #     if m is not None:
    #         is_array = True
    #         index_str = m.group("index")
    #         index = None if index_str == "" else int(index_str)
    #         key = key_part.split("[")[0]
    #     else:
    #         is_array = False
    #         index = None
    #         key = key_part
    #
    #     # generate the current item in the hierarchy (current_container). None if it does not exists

    # def handle_single_value(app_context: AppContext, key: str, value: Any) -> AppContext:
    #     # split the key depending on "."
    #     key_parts = key.split('.')
    #     recursive_handle_single_value(
    #         app_context=app_context,
    #         container=app_context.model.values,
    #         depth=0,
    #         key_part=key_parts[0],
    #         value=value,
    #         last_key_part_index=len(key_parts) - 1,
    #         key_parts=key_parts
    #     )
    #
    #     return app_context

    if options.inputFile is not None:
        app_context.input_file = options.inputFile
    if options.outputFile is not None:
        app_context.output_file_format = options.outputFile
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
        app_context.template_string = options.templateString[0]

    # for key, value in map(lambda x: (x.split("=")[0], x.split("=")[1:]), options.value):
    #     handle_single_value(app_context, key, value)

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

    return app_context


def main():
    app_context = AppContext()
    options = parse_options(sys.argv[1:])

    # read values from config if  present
    if options.configFile is not None:
        app_context = update_using_config(app_context, options.configFile)

    # overwrite values from config
    app_context = update_using_command_line(app_context, options)

    # apply defaults on required items
    app_context = apply_defaults(app_context)

    logging.basicConfig(level=getattr(logging, app_context.log_level))
    logging.info(f"logging level is {app_context.log_level}")

    app_context.input_file = os.path.abspath(app_context.input_file)

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

    logging.debug(f"input file = {app_context.input_file}")
    logging.debug(f"input string = {app_context.template_string}")
    logging.info(f"output_file = {actual_output_file}")
    logging.debug(f"block_start_string = {app_context.block_start_string}")
    logging.debug(f"block_end_string = {app_context.block_end_string}")
    logging.debug(f"expression_start_string = {app_context.expression_start_string}")
    logging.debug(f"expression_end_string = {app_context.expression_end_string}")
    logging.debug(f"comment_start_string = {app_context.comment_start_string}")
    logging.debug(f"comment_end_string = {app_context.comment_end_string}")
    logging.debug(f"line_statement_prefix = {app_context.line_statement_prefix}")

    if app_context.template_string is not None:
        # we need to templatize the string
        template_loader = BaseLoader()
    else:
        # create file
        template_loader = jinja2.FileSystemLoader(
            searchpath=os.path.abspath(os.path.dirname(app_context.input_file)),
            encoding=app_context.input_file_encoding
        )

    env = jinja2.Environment(
        loader=template_loader,
        block_start_string=app_context.block_start_string,
        block_end_string=app_context.block_end_string,
        variable_start_string=app_context.expression_start_string,
        variable_end_string=app_context.expression_end_string,
        comment_start_string=app_context.comment_start_string,
        comment_end_string=app_context.comment_end_string,
        line_statement_prefix=app_context.line_statement_prefix
    )

    now = datetime.now()
    utc_now = datetime.utcnow()

    # add data to commons
    app_context.model.commons["now"] = now
    app_context.model.commons["utc_now"] = utc_now
    app_context.model.commons["program_version"] = version.VERSION

    logging.info(f"loading file template: {app_context.input_file}")
    logging.debug(f"parameters are {app_context.model}")

    if app_context.template_string is not None:
        # we need to render a string
        template = env.from_string(app_context.template_string)
    else:
        # we need to render a file
        template = env.get_template(os.path.basename(app_context.input_file))

    actual_file_content = template.render(
        # data
        model=app_context.model.values,
        commons=app_context.model.commons,
        # commons function (they are so popular that we put them on the cwd)
        enumerate=enumerate,
        map=map,
        filter=filter,
        len=len,
        math=math,
        datetime=datetime,
        **app_context.model.functions
    )

    if app_context.write_on_stdout:
        print(actual_file_content)
    else:
        with open(actual_output_file, "w", encoding=app_context.output_file_encoding) as f:
            f.write(actual_file_content)


if __name__ == "__main__":
    main()
