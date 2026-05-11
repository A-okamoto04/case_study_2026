from setuptools import find_packages, setup

package_name = 'case_study_2026'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='su-laptop-18',
    maintainer_email='ayumlkamu@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
         'talker = case_study_2026.move_on:main',
         'subscriber = case_study_2026.move_subscriber:main',
        ],
    },
)


