from setuptools import setup, find_packages

setup(
    name="NikGapps",
    version="",
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
        'pytz>=2024.2,<2026.0',
        'pysftp~=0.2.9',
        'requests~=2.32.3',
        'PyYAML~=6.0.2',
        'psutil~=6.1.0',
        'setuptools>=75.3,<80.10',
        'pexpect~=4.9.0',
        'GitPython~=3.1.43',
        'PyGithub~=2.4.0',
        'python-gitlab>=5.0,<6.2',
        'cryptography>=43.0.3,<46.1.0',
        'python-dotenv>=1.0.1,<1.2.0',
        'niklibrary~=0.28'
    ],
    entry_points={
        'console_scripts': [
            'nikgapps=NikGapps.main:main',
            'nikgapps_overlay=NikGapps.overlay_control:overlay_control',
            'nikgapps_config_upload=NikGapps.config_upload:config_upload',
            'cache=NikGapps.cache:cache',
            'copy_repos=NikGapps.copy_repos:copy_repos',
            'build=NikGapps.build_config:build_config',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.12',
)