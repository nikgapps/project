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
        'colorama>=0.4.4',
        'pytz>=2022.1',
        'pysftp>=0.2.9',
        'PyYAML>=6.0',
        'psutil>=5.9.0',
        'setuptools>=65.5.1',
        'requests>=2.25.1',
        'GitPython>=3.1.31',
        'pexpect>=4.8.0',
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
