{%- if cookiecutter.test_automation_tool == "Nox" %}import nox
from nox.sessions import Session
import pathlib

nox.options.sessions = ["test", "docs"]
# nox.options.sessions = ["lint", "test"]

nox.options.envdir = ".nox" if nox.options.envdir is None else nox.options.envdir

@nox.session
def test(session: Session):
    session.install('pytest')
    session.install('pytest-cov')
    session.install('hypothesis')
    session.run('pytest')

@nox.session
def docs(session: Session):
{%- if cookiecutter.documentation_framework == "Sphinx" %}
    session.install('sphinx >= 3.0')
    session.install('sphinx-rtd-theme')
{%- elif cookiecutter.documentation_framework == "MkDocs" %}
    session.install('Markdown')
    session.install('Pygments')
    session.install('mkdocs')
    session.install('mkdocs-awesome-pages-plugin')
    session.install('mkdocs-material')
    session.install('mkdocs-minify-plugin')
    session.install('pymdown-extensions')
{%- endif %}

    output_directory = pathlib.Path(session.invoked_from) / nox.options.envdir / "docs_out"

    with session.chdir('docs'):
{%- if cookiecutter.documentation_framework == "Sphinx" %}
        session.run('sphinx-build', '--color', '-W', '-b', 'html', 'source/', output_directory)
{%- elif cookiecutter.documentation_framework == "MkDocs" %}
        session.run('mkdocs', 'build', '--strict', '--site-dir', output_directory)
{%- endif %}

    print(f"Documentation available via: file://{output_directory / 'index.html'}")
{%- endif %}
