.. _`package_discovery`:

========================================
Package Discovery and Namespace Package
========================================

.. note::
    a full specification for the keyword supplied to ``setup.cfg`` or
    ``setup.py`` can be found at :doc:`keywords reference <keywords>`

.. note::
    the examples provided here are only to demonstrate the functionality
    introduced. More metadata and options arguments need to be supplied
    if you want to replicate them on your system. If you are completely
    new to setuptools, the :doc:`quickstart section <quickstart>` is a good
    place to start.

``Setuptools`` provide powerful tools to handle package discovery, including
support for namespace package. Normally, you would specify the package to be
included manually in the following manner:

.. tab:: setup.cfg

    .. code-block:: ini

        [options]
        #...
        packages =
            mypkg1
            mypkg2

.. tab:: setup.py

    .. code-block:: python

        setup(
            # ...
            packages=['mypkg1', 'mypkg2']
        )

This can get tiresome really quickly. To speed things up, you can rely on
setuptools automatic discovery, or use the provided tools, as explained in
the following sections.


Automatic discovery
===================

.. warning:: Automatic discovery is an **experimental** feature and might change
   (or be completely removed) in the future.
   See :ref:`custom-discovery` for a stable way of configuring ``setuptools``.

By default setuptools will consider 2 popular project layouts, each one with
its own set of advantages and disadvantages [#layout1]_ [#layout2]_.

src-layout:
    The project should contain a ``src`` directory under the project root and
    all modules and packages meant for distribution are placed inside this
    directory::

        project_root_directory
        ├── pyproject.toml
        ├── setup.cfg  # or setup.py
        ├── ...
        └── src/
            └── mypkg/
                ├── __init__.py
                ├── ...
                └── mymodule.py

    This layout is very handy when you wish to use automatic discovery,
    since you don't have to worry about other Python files or folders in your
    project root being distributed by mistake. In some circumstances it can be
    also less error-prone for testing or when using :pep:`420`-style packages.
    On the other hand you cannot rely on the implicit ``PYTHONPATH=.`` to fire
    up the Python REPL and play with your package (you will need an
    `editable install`_ to be able to do that).

flat-layout (also known as "adhoc"):
    The package folder(s) are placed directly under the project root::

        project_root_directory
        ├── pyproject.toml
        ├── setup.cfg  # or setup.py
        ├── ...
        └── mypkg/
            ├── __init__.py
            ├── ...
            └── mymodule.py

    This layout is very practical for using the REPL, but in some situations
    it can be can be more error-prone (e.g. during tests or if you have a bunch
    of folders or Python files hanging around your project root)

There is also a handy variation of the *flat-layout* for utilities/libraries
that can be implemented with a single Python file:

single-module approach (or "few top-level modules"):
    Standalone modules are placed directly under the project root, instead of
    inside a package folder::

        project_root_directory
        ├── pyproject.toml
        ├── setup.cfg  # or setup.py
        ├── ...
        └── single_file_lib.py

Setuptools will automatically scan your project directory looking for these
layouts and try to guess the correct values for the :ref:`packages <declarative
config>` and :doc:`py_modules </references/keywords>` configuration.

In the case of *flat-layouts*, only packages or modules that match your
project's name metadata will be considered (at first). If no match is found,
then ``setuptools`` will proceed and evaluate other files and directories,
except the following:

.. autoattribute:: setuptools.discovery.FlatLayoutPackageFinder.DEFAULT_EXCLUDE

.. autoattribute:: setuptools.discovery.FlatLayoutModuleFinder.DEFAULT_EXCLUDE

Also note that you can customise your project layout by explicitly setting
``package_dir``:

.. tab:: setup.cfg

    .. code-block:: ini

        [options]
        # ...
        package_dir =
            = lib
            # similar to "src-layout" but using the "lib" folder
            # pkg.mod corresponds to lib/pkg/mod.py
        # OR
        package_dir =
            pkg1 = lib1
            # pkg1.mod corresponds to lib1/mod.py
            # pkg1.subpkg.mod corresponds to lib1/subpkg/mod.py
            pkg2 = lib2
            # pkg2.mod corresponds to lib2/mod.py
            pkg2.subpkg = lib3
            # pkg2.subpkg.mod corresponds to lib3/mod.py

.. tab:: setup.py

    .. code-block:: python

        setup(
            # ...
            package_dir = {"": "lib"}
            # similar to "src-layout" but using the "lib" folder
            # pkg.mod corresponds to lib/pkg/mod.py
        )

        # OR

        setup(
            # ...
            package_dir = {
                "pkg1": "lib1",  # pkg1.mod corresponds to lib1/mod.py
                                 # pkg1.subpkg.mod corresponds to lib1/subpkg/mod.py
                "pkg2": "lib2",   # pkg2.mod corresponds to lib2/mod.py
                "pkg2.subpkg": "lib3"  # pkg2.subpkg.mod corresponds to lib3/mod.py
                # ...
        )

.. important:: Automatic discovery will **only** be enabled if you don't
   provide any configuration for both ``packages`` and ``py_modules``.
   If at least one of them is explicitly set, automatic discovery will not take
   place.


.. _custom-discovery:

Custom discovery
================

If the automatic discovery does not work for you
(e.g., you want to distribute multiple packages together, your package or
module name does not match the name you want to display on PyPI, or you want to
*exclude* nested packages that would be otherwise included), you can use
the provided tools for package discovery:

.. tab:: setup.cfg

    .. code-block:: ini

        [options]
        packages = find:
        #or
        packages = find_namespace:

.. tab:: setup.py

    .. code-block:: python

        from setuptools import find_packages

        # or
        from setuptools import find_namespace_packages


Using ``find:`` or ``find_packages``
------------------------------------
Let's start with the first tool. ``find:`` (``find_packages``) takes a source
directory and two lists of package name patterns to exclude and include, and
then return a list of ``str`` representing the packages it could find. To use
it, consider the following directory

.. code-block:: bash

    mypkg/
        src/
            pkg1/__init__.py
            pkg2/__init__.py
            additional/__init__.py

        setup.cfg #or setup.py

To have your setup.cfg or setup.py to automatically include packages found
in ``src`` that starts with the name ``pkg`` and not ``additional``:

.. tab:: setup.cfg

    .. code-block:: ini

        [options]
        packages = find:
        package_dir =
            =src

        [options.packages.find]
        where = src
        include = pkg*
        exclude = additional

.. tab:: setup.py

    .. code-block:: python

        setup(
            # ...
            packages=find_packages(
                where='src',
                include=['pkg*'],
                exclude=['additional'],
            ),
            package_dir={"": "src"}
            # ...
        )


.. _Namespace Packages:

Using ``find_namespace:`` or ``find_namespace_packages``
--------------------------------------------------------
``setuptools``  provides the ``find_namespace:`` (``find_namespace_packages``)
which behaves similarly to ``find:`` but works with namespace package. Before
diving in, it is important to have a good understanding of what namespace
packages are. Here is a quick recap:

Suppose you have two packages named as follows:

.. code-block:: bash

    /Users/Desktop/timmins/foo/__init__.py
    /Library/timmins/bar/__init__.py

If both ``Desktop`` and ``Library`` are on your ``PYTHONPATH``, then a
namespace package called ``timmins`` will be created automatically for you when
you invoke the import mechanism, allowing you to accomplish the following

.. code-block:: pycon

    >>> import timmins.foo
    >>> import timmins.bar

as if there is only one ``timmins`` on your system. The two packages can then
be distributed separately and installed individually without affecting the
other one. Suppose you are packaging the ``foo`` part:

.. code-block:: bash

    foo/
        src/
            timmins/foo/__init__.py
        setup.cfg # or setup.py

and you want the ``foo`` to be automatically included, ``find:`` won't work
because timmins doesn't contain ``__init__.py`` directly, instead, you have
to use ``find_namespace:``:

.. code-block:: ini

    [options]
    package_dir =
        =src
    packages = find_namespace:

    [options.packages.find]
    where = src

When you install the zipped distribution, ``timmins.foo`` would become
available to your interpreter.

You can think of ``find_namespace:`` as identical to ``find:`` except it
would count a directory as a package even if it doesn't contain ``__init__.py``
file directly. As a result, this creates an interesting side effect. If you
organize your package like this:

.. code-block:: bash

    foo/
        timmins/
            foo/__init__.py
        setup.cfg # or setup.py
        tests/
            test_foo/__init__.py

a naive ``find_namespace:`` would include tests as part of your package to
be installed. A simple way to fix it is to adopt the aforementioned
``src`` layout.


Legacy Namespace Packages
=========================
The fact you can create namespace package so effortlessly above is credited
to `PEP 420 <https://www.python.org/dev/peps/pep-0420/>`_. It use to be more
cumbersome to accomplish the same result. Historically, there were two methods
to create namespace packages. One is the ``pkg_resources`` style supported by
``setuptools`` and the other one being ``pkgutils`` style offered by
``pkgutils`` module in Python. Both are now considered deprecated despite the
fact they still linger in many existing packages. These two differ in many
subtle yet significant aspects and you can find out more on `Python packaging
user guide <https://packaging.python.org/guides/packaging-namespace-packages/>`_


``pkg_resource`` style namespace package
----------------------------------------
This is the method ``setuptools`` directly supports. Starting with the same
layout, there are two pieces you need to add to it. First, an ``__init__.py``
file directly under your namespace package directory that contains the
following:

.. code-block:: python

    __import__("pkg_resources").declare_namespace(__name__)

And the ``namespace_packages`` keyword in your ``setup.cfg`` or ``setup.py``:

.. tab:: setup.cfg

    .. code-block:: ini

        [options]
        namespace_packages = timmins

.. tab:: setup.py

    .. code-block:: python

        setup(
            # ...
            namespace_packages=['timmins']
        )

And your directory should look like this

.. code-block:: bash

    /foo/
        src/
            timmins/
                __init__.py
                foo/__init__.py
        setup.cfg #or setup.py

Repeat the same for other packages and you can achieve the same result as
the previous section.

``pkgutil`` style namespace package
-----------------------------------
This method is almost identical to the ``pkg_resource`` except that the
``namespace_packages`` declaration is omitted and the ``__init__.py``
file contains the following:

.. code-block:: python

    __path__ = __import__('pkgutil').extend_path(__path__, __name__)

The project layout remains the same and ``setup.cfg`` remains the same.


.. [#layout1] https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
.. [#layout2] https://blog.ionelmc.ro/2017/09/25/rehashing-the-src-layout/

.. _editable install: https://pip.pypa.io/en/stable/cli/pip_install/#editable-installs
