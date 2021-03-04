import os

import semantic_version
from semantic_version import Version

require_pmakeup_version("1.6.0")

global TWINE_TEST_PYPI_USER
global TWINE_TEST_PYPI_PASSWORD
global ADMIN_PASSWORD

TWINE_TEST_PYPI_USER = "Koldar"

TWINE_PYPI_USER = "Koldar"

ADMIN_PASSWORD = read_file_content("PASSWORD")


def clean():
    echo("Cleaning...", foreground="blue")
    remove_tree("dist")
    remove_tree("build")
    remove_tree("pmake.egg-info")


def _read_version() -> Version:
    version_filepath = os.path.join("template_formatter", "version.py")
    with open(version_filepath, "r") as f:
        version = f.read().split("=")[1].strip("\" \t\n")
    return Version(version)


def update_version_major():
    version = _read_version()
    new_version = version.next_major()
    version_filepath = os.path.join("template_formatter", "version.py")

    echo(f"Updating version from {version} to {new_version} in {cwd()}...", foreground="blue")
    write_file(version_filepath, f"VERSION = \"{new_version}\"", overwrite=True)


def update_version_minor():
    version = _read_version()
    new_version = version.next_minor()
    version_filepath = os.path.join("template_formatter", "version.py")

    echo(f"Updating version from {version} to {new_version} in {cwd()}...", foreground="blue")
    write_file(version_filepath, f"VERSION = \"{new_version}\"", overwrite=True)


def update_version_patch():
    version = _read_version()
    new_version = version.next_patch()
    version_filepath = os.path.join("template_formatter", "version.py")

    echo(f"Updating version from {version} to {new_version} in {cwd()}...", foreground="blue")
    write_file(version_filepath, f"VERSION = \"{new_version}\"", overwrite=True)


def uninstall():
    echo("Uninstall...", foreground="blue")
    execute_admin_with_password_stdout_on_screen(
        password=ADMIN_PASSWORD,
        commands="pip3 uninstall --yes pmake",
    )


def build():
    echo("Building...", foreground="blue")
    if on_linux():
        echo("building for linux", foreground="blue")
        execute_stdout_on_screen([
            f"source {path('venv', 'bin', 'activate')}",
            f"python setup.py bdist_wheel",
            f"deactivate"
        ])
    elif on_windows():
        echo(f"building for windows in {cwd()}", foreground="blue")
        execute_stdout_on_screen([
            f"python setup.py bdist_wheel",
        ])
    else:
        raise PdMakeException()


def generate_documentation():
    echo("Building documentation...", foreground="blue")
    oldcwd = cd("docs")
    if on_linux():
        execute_stdout_on_screen([
                "make html latexpdf"
            ],
        )
    elif on_windows():
        execute_stdout_on_screen([
            "make.bat html latexpdf"
        ],
        )
    cd(oldcwd)


def install():
    echo("Installing...", foreground="blue")
    ADMIN_PASSWORD = read_file_content("PASSWORD")
    latest_version, file_list = get_latest_version_in_folder("dist", version_fetcher=semantic_version_2_only_core)
    echo(f"file list = {' '.join(file_list)}")
    wheel_file = list(filter(lambda x: '.whl' in x, file_list))[0]
    if on_linux():
        execute_admin_with_password_stdout_on_screen(
            password=ADMIN_PASSWORD,
            commands=f"pip3 install {wheel_file}",
        )
    elif on_windows():
        execute_admin_with_password_stdout_on_screen(
            password=ADMIN_PASSWORD,
            commands=f"pip install {wheel_file}",
        )


def upload_to_test_pypi():
    TWINE_TEST_PYPI_PASSWORD = read_file_content("TWINE_TEST_PYPI_PASSWORD")
    echo("Uploading to test pypi...", foreground="blue")
    latest_version, file_list = get_latest_version_in_folder("dist", version_fetcher=semantic_version_2_only_core)
    upload_files = ' '.join(map(lambda x: f"\"{x}\"", file_list))

    if on_linux():
        echo("Uploading for linux", foreground="blue")
        execute_stdout_on_screen([
            #"source venv/bin/activate",
            f"twine upload --verbose --repository testpypi --username \"{TWINE_TEST_PYPI_USER}\" --password \"{TWINE_TEST_PYPI_PASSWORD}\" {upload_files}",
            #"deactivate"
        ])
    elif on_windows():
        echo("Uploading for windows", foreground="blue")
        execute_stdout_on_screen([
            #"venv/Scripts/activate.bat",
            f"twine upload --verbose --repository testpypi --username \"{TWINE_TEST_PYPI_USER}\" --password \"{TWINE_TEST_PYPI_PASSWORD}\" {upload_files}",
            #"venv/Scripts/deactivate.bat"
        ])
    else:
        raise PMakeupException()


def upload_to_pypi():
    TWINE_PYPI_PASSWORD = read_file_content("TWINE_PYPI_PASSWORD")
    echo("Uploading to pypi ...", foreground="blue")
    latest_version, file_list = get_latest_version_in_folder("dist", version_fetcher=semantic_version_2_only_core)
    upload_files = ' '.join(map(lambda x: f"\"{x}\"", file_list))
    echo(f"File to upload is {upload_files}...", foreground="blue")

    if on_linux():
        echo("Uploading for linux", foreground="blue")
        execute_stdout_on_screen([
            f"twine upload --verbose --non-interactive --username \"{TWINE_PYPI_USER}\" --password \"{TWINE_PYPI_PASSWORD}\" {upload_files}",
        ])
    elif on_windows():
        echo("Uploading for windows", foreground="blue")
        execute_stdout_on_screen([
            f"twine upload --verbose --non-interactive --username \"{TWINE_PYPI_USER}\" --password \"{TWINE_PYPI_PASSWORD}\" {upload_files}",
        ])
    else:
        raise PMakeupException()


declare_file_descriptor(f"""
    This file allows to build, locally install and potentially upload a new version of pmake.
""")
declare_target(
    target_name="clean",
    description="Clean all folders that are automatically generated",
    f=clean,
    requires=[],
)
declare_target(
    target_name="uninstall",
    description="Uninstall local version of pmake in the global pip sites",
    f=uninstall,
    requires=[],
)
declare_target(
    target_name="update-version-patch",
    description="Uninstall local version of pmake in the global pip sites",
    f=update_version_patch,
    requires=[],
)
declare_target(
    target_name="update-version-minor",
    description="Uninstall local version of pmake in the global pip sites",
    f=update_version_minor,
    requires=[],
)
declare_target(
    target_name="update-version-major",
    description="Uninstall local version of pmake in the global pip sites",
    f=update_version_major,
    requires=[],
)
declare_target(
    target_name="build",
    description="Build the application",
    f=build,
    requires=[],
)
declare_target(
    target_name="generate-documentation",
    description="Generate documentation of the application",
    f=generate_documentation,
    requires=["build"],
)
declare_target(
    target_name="install",
    description="Install the application on your system. Uses elevated privileges",
    f=install,
    requires=["build"],
)
declare_target(
    target_name="upload-to-test-pypi",
    description="Upload the latest version of pmake to pypi test",
    f=upload_to_test_pypi,
    requires=["build"],
)
declare_target(
    target_name="upload-to-pypi",
    description="Upload the latest version of pmake to pypi",
    f=upload_to_pypi,
    requires=["build"],
)

process_targets()
