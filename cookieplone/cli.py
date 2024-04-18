"""Main `cookieplone` CLI."""

import os
import sys
from pathlib import Path
from typing import Annotated

import typer
from cookiecutter import __version__ as __cookiecutter_version__
from cookiecutter.log import configure_logger
from rich import print

from cookieplone import __version__, data
from cookieplone.exceptions import GeneratorException
from cookieplone.generator import generate


def validate_extra_context(value: list[str] | None = None):
    """Validate extra content follows the correct pattern."""
    if not value:
        return {}
    for string in value:
        if "=" not in string:
            raise typer.BadParameter(
                f"EXTRA_CONTEXT should contain items of the form key=value; "
                f"'{string}' doesn't match that form"
            )
    # Convert list -- e.g.: ['program_name=foobar', 'startsecs=66']
    # to dict -- e.g.: {'program_name': 'foobar', 'startsecs': '66'}
    return dict([s.split("=", 1) for s in value])


def version_info() -> str:
    """Return the Cookieplone version, location and Python powering it."""
    python_version = sys.version
    location = Path(__file__).parent
    return (
        f"Cookieplone {__version__} from {location} "
        f"(Cookiecutter {__cookiecutter_version__}, "
        f"Python {python_version})"
    )


def cli(
    template: Annotated[str, typer.Argument(help="Template to be used.")] = "",
    extra_context: Annotated[
        data.OptionalListStr,
        typer.Argument(callback=validate_extra_context, help="Extra context."),
    ] = None,
    output_dir: Annotated[
        data.OptionalPath,
        typer.Option("--output-dir", "-o", help="Where to generate the code."),
    ] = None,
    tag: Annotated[str, typer.Option(help="Tag.")] = "",
    version: Annotated[
        bool, typer.Option("--version", help="Display the version of cookieplone.")
    ] = False,
    no_input: Annotated[
        bool,
        typer.Option(
            "--no_input",
            help=(
                "Do not prompt for parameters and only use cookiecutter.json "
                "file content. Defaults to deleting any cached resources and "
                "redownloading them. Cannot be combined with the --replay flag."
            ),
        ),
    ] = False,
    replay: Annotated[bool, typer.Option("--replay", "-r")] = False,
    replay_file: Annotated[data.OptionalPath, typer.Option("--replay-file")] = None,
    skip_if_file_exists: Annotated[
        bool,
        typer.Option(
            "--skip-if-file-exists",
            "-s",
            help=(
                "Skip the files in the corresponding directories "
                "if they already exist"
            ),
        ),
    ] = False,
    overwrite_if_exists: Annotated[
        bool, typer.Option("--overwrite-if-exists", "-f")
    ] = False,
    config_file: Annotated[
        data.OptionalPath, typer.Option("--config-file", help="User configuration file")
    ] = None,
    default_config: Annotated[
        bool,
        typer.Option(
            "--default-config",
            help="Do not load a config file. Use the defaults instead",
        ),
    ] = False,
    keep_project_on_failure: Annotated[
        bool,
        typer.Option(
            "--keep-project-on-failure", help="Do not delete project folder on failure"
        ),
    ] = False,
    debug_file: Annotated[
        data.OptionalPath,
        typer.Option(
            "--debug-file", help="File to be used as a stream for DEBUG logging"
        ),
    ] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
):
    """Generate a new Plone codebase."""
    if version:
        info = version_info
        print(info)
        raise typer.Exit()
    repository = os.environ.get("COOKIEPLONE_REPOSITORY")
    if not repository:
        repository = "gh:plone/cookiecutter-plone"

    if replay_file:
        replay = replay_file
    passwd = os.environ.get(
        "COOKIECUTTER_REPO_PASSWORD", os.environ.get("COOKIEPLONE_REPO_PASSWORD")
    )
    if not output_dir:
        output_dir = Path().cwd()
    configure_logger(stream_level="DEBUG" if verbose else "INFO", debug_file=debug_file)
    # Run generator
    try:
        generate(
            repository,
            tag,
            no_input,
            extra_context,
            replay,
            overwrite_if_exists,
            output_dir,
            config_file,
            default_config,
            passwd,
            template,
            skip_if_file_exists,
            keep_project_on_failure,
        )
    except GeneratorException:
        # TODO: Handle error
        raise typer.Exit(1)  # noQA:B904
    except Exception:
        # TODO: Handle error
        raise typer.Exit(1)  # noQA:B904


def main():
    """Run the cli."""
    typer.run(cli)