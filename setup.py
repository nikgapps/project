from setuptools import setup, find_packages

setup(
    name="NikGapps",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.sh', '*.yml'],
        'NikGapps.helper': ['assets/*'],
        'NikGapps.helper.assets': ['*'],
    },
    author="Nikhil Menghani",
    author_email="nikgapps@gmail.com",
    description="A short description of your project",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/nikgapps/project",
    install_requires=[
        'colorama>=0.4.6',
        'pytz>=2024.1',
        'pysftp>=0.2.9',
        'PyYAML>=6.0.1',
        'psutil>=5.9.8',
        'setuptools>=69.0.3',
        'requests>=2.31.0',
        'GitPython>=3.1.42',
        'pexpect>=4.9.0',
        'PyGithub>=2.3.0',
        'python-gitlab>=4.4.0',
    ],
    entry_points={
        'console_scripts': [
            'nikgapps=NikGapps.main:main',
            'nikgapps_overlay=NikGapps.overlay_control:overlay_control',
            'nikgapps_config_upload=NikGapps.config_upload:config_upload',
            'cache=NikGapps.cache:cache',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.10',
)