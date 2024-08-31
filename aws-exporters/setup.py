from setuptools import setup, find_packages

setup(
    name='aws-exporters',
    version='1.0.0+ts1.coldasyou',
    author='Hideki.M',
    author_email='Y29udGFjdC1tZUBhd3M0Lm1lLnVrCg==',
    description='A set of tools for exporting AWS information',
    packages=find_packages(),
    install_requires=[
        'boto3',
        'Flask',
        'pytz',
    ],
    url='https://github.com/Hideki-Morita/aws-native-observability-exporters',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9.16',
    entry_points={
        'console_scripts': [
            'organizations-exporter=aws_exporters.organizations_exporter:main',
            'identity-center-exporter=aws_exporters.identity_center_exporter:main',
            'freetier-usage-exporter=aws_exporters.freetier_usage_exporter:main',
            'multi-acc-iam-exporter=aws_exporters.multi_acc_iam_exporter:main',
        ],
    },
)
