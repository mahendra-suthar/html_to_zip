from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='Measurements',
    url='https://github.com/mahendra720/html_to_zip.',
    author='Mahendra Kumar',
    author_email='mksuthar9016@gmail.com',
    # Needed to actually package something
    packages=['mypythonlib'],
    # Needed for dependencies
    install_requires=['boto3', 'shutil', 'zipfile', 'bs4', 'flask'],
    # *strongly* suggested for sharing
    version='0.1',
    # The license can be anything you like
    license='MIT',
    description='An example of a python package from pre-existing code',
    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
)