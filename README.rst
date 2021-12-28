building-codes is a hook for the `pre-commit framework <https://pre-commit.com/>`_.

The problem that this hook intends to solve is to help with maintaining large-codebases that need to keep up with changes in libraries and languages.
The solution offered is to borrow from the concept of building codes from conventional home/building construction.
As long as a file is unchanged, it is allowed to use the "old" technology/interface/library.
However, when a file is edited it must be brought up to date with current standards.
Using this principle, a pre-commit hook is the ideal way to enforce the new standards because it is only run against files that are being committed.

Configuration
-------------

building-codes expects a configuration file, ``.buildingcodes.yaml``  in the root of the code repository.
The purpose of the flie is to specify what to look for and suggest what to replace it with.
Not configuring correctly building-codes will produce errors when using the hook.
An example is

.. code-block:: yaml

   - pattern: Poco::Path
     message: use something else than Poco::Path
     ignore:
       - file: Framework/Kernel/src/Glob.cpp
       - file: Framework/Kernel/src/ConfigService.cpp
         lines: 189,246
   - pattern: Poco::File
     message: use something other than Poco::File
     ignore:
       - file: Framework/Kernel/src/ConfigService.cpp
         lines: 160
   - pattern: os.path
     message: use Pathlib instead


Each rule requires a ``pattern`` to find on a single line of source code (currently simple string comparison) and a ``message`` which will instruct the developer how the code needs to be modernized.
While this will not find every occurance that needs to be modernized, it does allow for a large variety to look for.
Suppressing a rule in a file can be used with the ``ignore`` parameter which has a ``file`` parameter and an optional ``lines`` parameter.
If the ``lines`` is not supplied, it is assumed that the entire file should be ignored.

Limitations
-----------

This pre-commit hook is registered to work with all languages and does not tokenize the files as more advanced tools (e.g. clang-modernize).
As a result, the pattern matching can be fooled by the clever developer.

Use in Continuous Integration
-----------------------------

`pre-commit points out <https://pre-commit.com/#usage-in-continuous-integration>`_ that it is possible to run pre-commit in CI.
If this hoook is only run on files that are changed, then the appropriate behavior will be observed.
Otherwise, one should `disable this hook <https://pre-commit.com/#temporarily-disabling-hooks>`_ in CI or files that do not currently need to be modernized will fail the build.
