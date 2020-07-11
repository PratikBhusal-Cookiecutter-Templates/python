# Minimal makefile for {{cookiecutter.documentation_framework}} documentation

# You can set these variables from the command line, and also
# from the environment for the first two.
BUILDOPTS ?=
{% if cookiecutter.documentation_framework == 'Sphinx' -%}
BUILDTOOL ?= sphinx-build
SOURCEDIR  = source
BUILDDIR   = build
{% elif cookiecutter.documentation_framework == 'MkDocs' -%}
BUILDTOOL ?= mkdocs
{% endif %}
# Put it first so that "make" without argument is like "make help".
help:
{%- if cookiecutter.documentation_framework == 'Sphinx' %}
	@$(BUILDTOOL) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(BUILDOPTS) $(O)
{%- elif cookiecutter.documentation_framework == 'MkDocs' %}
	@$(BUILDTOOL) --help $(BUILDOPTS) $(O)
{%- endif %}

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option. $(O) is meant as a shortcut for $(BUILDOPTS).
%: Makefile
{%- if cookiecutter.documentation_framework == 'Sphinx' %}
	@$(BUILDTOOL) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(BUILDOPTS) $(O)
{%- elif cookiecutter.documentation_framework == 'MkDocs' %}
	@$(BUILDTOOL) $@ $(BUILDOPTS) $(O)
{%- endif %}
