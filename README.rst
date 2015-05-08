===================================================================================
loan_payoff_tools: Simulates multiple different scenarios in which to payoff loans.
===================================================================================

.. image:: https://travis-ci.org/phillipgreenii/loan_payoff_tools.svg
    :target: https://travis-ci.org/phillipgreenii/loan_payoff_tools
    :alt: Build Status

This project is designed to determine the optimal way of paying off multiple loans.
This tool can be used to determine if is better to payoff the smallest loan or
the highest interest rate or any other technique.

Installation
------------

The easiest way to install most Python packages is via ``easy_install`` or ``pip``:

.. code-block:: bash

  $ easy_install loan_payoff_tools

Usage
-----

  >> import loan_payoff_tools

When the package is installed via ``easy_install`` or ``pip`` this function will be bound to the ``loan_payoff_tools`` executable in the Python installation's ``bin`` directory (on Windows - the ``Scripts`` directory).

Development
-----------

Run Tests
^^^^^^^^^

.. code-block:: bash

  $ python setup.py test

Install
^^^^^^^

.. code-block:: bash

  $ python setup.py develop

Copyright & License
-------------------

  * Copyright 2014, Phillip Green II
  * License: MIT
