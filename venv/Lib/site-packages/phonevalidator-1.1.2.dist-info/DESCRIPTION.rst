===============================
phonevalidator
===============================

.. image:: https://img.shields.io/travis/m-housh/phonevalidator.svg
        :target: https://travis-ci.org/m-housh/phonevalidator

.. image:: https://coveralls.io/repos/github/m-housh/phonevalidator/badge.svg?branch=master
        :target: https://coveralls.io/github/m-housh/phonevalidator?branch=master


Custom `cerberus.Validator` for phone numbers


* Free software: MIT license


Features
--------

* Custom validation mixin for `Cerberus`_ or an `Eve`_ API.  
  Uses the `phonenumbers`_ package for validation's and formatting.
  Tested under Python 2.7, Python 3.3, Python 3.4, and Python 3.5.

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

This package also use the `phonenumbers`_ package which is licensed under
the `Apache2`_ license. The `Cerberus`_ package which is an open-source project.
`Eve`_ is licensed under the `BSD`_ license.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`Cerberus`:  http://docs.python-cerberus.org
.. _`Eve`: http://python-eve.org
.. _`phonenumbers`:  https://github.com/daviddrysdale/python-phonenumbers
.. _`Apache2`: http://www.apache.org/licenses/LICENSE-2.0
.. _`BSD`: http://python-eve.org/license.html


=======
History
=======

0.0.1 (2016-07-22)
------------------

    Initial dev package.

1.0.0 (2016-07-23)
------------------

    Only support's python-3.5

1.1.0 (2016-07-24)
------------------

    Adds support and tests for python-2.7


