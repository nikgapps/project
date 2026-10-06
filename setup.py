from setuptools import setup, find_packages

setup(
    name="NikGapps",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.sh', '*.yml'],
        'NikGapps.helper': ['assets/*'],
    },
    author="Nikhil Menghani",
    author_email="nikgapps@gmail.com",
    description="A short description of your project",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/nikgapps/project",
    install_requires=[
        'colorama~=0.4.6',
        'pytz~=2026.5',
        'requests~=2.34.2',
        'PyYAML~=6.0.3',
        'psutil~=7.2.2',
        'setuptools~=84.0.0',
        'pexpect~=4.9.0',
        'GitPython~=3.2.0',
        'PyGithub~=2.10.0',
        'python-gitlab~=8.6.0',
        'cryptography~=50.0.2',
        'python-dotenv~=1.2.4',
        'niklibrary~=0.59'
    ],
    entry_points={
        'console_scripts': [
            'nikgapps=NikGapps.main:main',
            'nikgapps_overlay=NikGapps.overlay_control:overlay_control',
            'nikgapps_config_upload=NikGapps.config_upload:config_upload',
            'cache=NikGapps.cache:cache',
            'copy_repos=NikGapps.copy_repos:copy_repos',
            'build=NikGapps.build_config:build_config',
            'nikgapps-registry=nikgapps_registry.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.12',
)
