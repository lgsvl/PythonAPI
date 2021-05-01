#!/usr/bin/env python3

from setuptools import setup

# Without enabling the user site, "python3 -m pip install --user -e ." fails
# with:
#
#  WARNING: The user site-packages directory is disabled.
#  error: can't create or remove files in install directory
#  ...
#  [Errno 13] Permission denied: '/usr/local/lib/python3.6/dist-packages/<FILE>'
#
# Taken from https://github.com/pypa/pip/issues/7953#issuecomment-645133255.
import site
import sys
site.ENABLE_USER_SITE = "--user" in sys.argv[1:]


def get_version(git_tag):
    """
    Returns a PEP 440 version identifier

        <public version identifier>[+<local version label>]

    derived from its <git_tag> parameter and the output from:

        git describe --match <git_tag> --tags

    which has the format:

        <git_tag>[-<NR-OF-COMMITS>-g<ABBREV-HASH>]

    The public version identifier is formed from <git_tag>. PEP 440 versioning
    allows only digits without leading zeros in the release segments of public
    version identifiers, so they are dropped along with any "P"-s found in
    <git_tag>. And PEP 440 does not allow hyphens in pre-release segments, so
    any "-rc"-s are replaced with "rc". Fortunately, this mapping doesn't
    introduce any ambiguities when used for the tags that currently exist.

    The optional local version label is formed from the portion of the
    "git describe" output which follows <git_tag> with all hyphens converted to
    periods (except the first, which is dropped). This segment will be empty if:
    - Git is not available, or
    - the working tree is not a Git repository, or
    - the tag <git_tag> is not present or not on the currrent branch, or
    - the HEAD of the current branch is coincident with the tag <git_tag>.

    NB. - Not using https://pypi.org/project/setuptools-git-version/ because it
          passes "--long" to "git describe".
        - Not using https://pypi.org/project/setuptools-scm/ because it's way
          more complicated to configure it to do what is wanted.
    """

    # ASSERT(<git_tag> has no more than one leading "0", no more than one "-rc",
    #        and no more than one "P", which is expected to be at the end -- but
    #        this is not checked)
    public_version_identifier = git_tag.replace(".0", ".", 1) \
                                       .replace("P", "", 1) \
                                       .replace("-rc", "rc", 1)
    from os import getenv
    try:
        from git import Repo
        # PWD is the directory from where we invoked "pip install", which is
        # the root of the Git repository; when setup() is
        # called, pip has changed the current directory to be under /tmp.
        repo = Repo(path=getenv('PWD'))
        val = repo.git.describe('--match', git_tag, '--tags')
    except Exception:
        val = ""

    # Remove <git_tag> and convert the first hyphen to a "+":
    local_version_label_with_plus = val.replace(git_tag, '', 1) \
                                       .replace('-', '+', 1) \
                                       .replace('-', '.')

    return public_version_identifier + local_version_label_with_plus


package_name = 'lgsvl'

setup(
    name=package_name,
    version=get_version('2021.1'),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    description="Python API for SVL Simulator",
    author="LGSVL",
    author_email="contact@svlsimulator.com",
    python_requires=">=3.6.0",
    url="https://github.com/lgsvl/PythonAPI",
    packages=["lgsvl", "lgsvl.dreamview", "lgsvl.evaluator", "lgsvl.wise"],
    install_requires=[
        "environs",
        "numpy",
        "setuptools",
        "websocket-client",
        "websockets"
    ],
    setup_requires=[
        "GitPython==3.1.14"
    ],
    extras_require={
        "ci": [
            "flake8>=3.7.0"
        ],
    },
    zip_safe=True,
    maintainer='Hadi Tabatabaee',
    maintainer_email='hadi.tabatabaee@lge.com',
    license='Other',
    classifiers=[
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
)
