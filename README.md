# Template Tutorial

(C) Jack Betteridge (j.d.betteridge@bath.ac.uk) and James Grant (r.j.grant@bath.ac.uk)

This repository is a template-tutorial for the jupyter notebooks based build system developed by Jack Betteridge and James Grant for Advancing Research Computing at University of Bath.
It consists of a series of episodes which instruct how to use the build-system, set up remote builds of a repository, and add material to your training course.
In addition to acting as a tutorial for using the template the repository also serves as the development sandpit for the build system (currently).
Instructions on how to fork, update and build your course locally and online are given in the tutorial.

## The template

The template consists of a set of `tools` which make up the build system, and example, tutorial material `notebooks-plain`.
If you would like to contribute to the build system please see the notes below, the tutorially is principally aimed at users who will be developing courses.
Jupyter notebooks were chosen as the medium for a number of reasons:

*  They use markdown which is simple to use even for those not familiar.
*  Modifying individual codeblocks is intuitive compared with Sphinx/Jekyll builds.
*  Although not generally used for training courses, we like being able to mix markdown and executable codeblocks.

Reproducing the formatting richness of the [Software Carpentry](https://software-carpentry.org/) lessons was a key element to include the good teaching practice.
In order to retain this richness we created a build system to process initial notebooks into rich notebooks for use by students, html pages and pdfs for distribution as hard copies.
As a result this template tutorial has been created to assist users in creating their own courses, as both an lesson and demonstration of its use.
The tutorial is available online in [rendered html](https://james-grant1.github.io/template-tutorial/00\_schedule.html)

## Contributions to the build system

If you would like to contribute to the build system please fork the repository and create a pull request against the build-dev branch.
