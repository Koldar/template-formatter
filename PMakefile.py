

require_pmake_version("1.6.0")

global TWINE_USER
global TWINE_PASSWORD
global ADMIN_PASSWORD

TWINE_USER = "Koldar"
TWINE_PASSWORD = read_file_content("TWINE_PASSWORD")
ADMIN_PASSWORD = read_file_content("PASSWORD")


def clean():
    echo("Cleaning...", foreground="blue")
    remove_tree("dist")
    remove_tree("build")
    remove_tree("pmake.egg-info")


def update_version():
    echo(f"Updating version to {variables.NEW_VERSION} in {cwd()}...", foreground="blue")
    ensure_has_variable("NEW_VERSION")

    version_filepath = os.path.join("template_formatter", "version.py")
    write_file(version_filepath, f"VERSION = \"{variables.NEW_VERSION}\"", overwrite=True)


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
        raise PMakeException()


def generate_documentation():
    echo("Building documentation...", foreground="blue")
    oldcwd = cd("docs")
    if on_linux():
        execute_stdout_on_screen([
            "make html latexpdf"
        ])
    elif on_windows():
        execute_stdout_on_screen([
            "make.bat html latexpdf"
        ])
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
    echo("Uploading to test pypi...", foreground="blue")
    latest_version, file_list = get_latest_version_in_folder("dist", version_fetcher=semantic_version_2_only_core)
    upload_files = ' '.join(map(lambda x: f"\"{x}\"", file_list))

    if on_linux():
        echo("Uploading for linux", foreground="blue")
        execute_stdout_on_screen([
            f"twine upload --verbose --repository testpypi --username \"{TWINE_USER}\" --password \"{TWINE_PASSWORD}\" {upload_files}",
        ])
    elif on_windows():
        echo("Uploading for windows", foreground="blue")
        execute_stdout_on_screen([
            f"twine upload --verbose --repository testpypi --username \"{TWINE_USER}\" --password \"{TWINE_PASSWORD}\" {upload_files}",
        ])
    else:
        raise PMakeException()


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
    target_name="update-version",
    description="Uninstall local version of pmake in the global pip sites",
    f=update_version,
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
    description="Upload the latest version of pamek to pypi test",
    f=upload_to_test_pypi,
    requires=["build"],
)

process_targets()
