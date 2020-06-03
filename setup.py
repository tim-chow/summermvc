from setuptools import setup, find_packages


setup(
    name="summermvc",
    version="6.0.2",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,

    entry_points={
        "console_scripts": [
            "summermvc=summermvc.cmd:main"
        ],
    },

    extras_require={
        "tornado": ["tornado"]
    },

    test_suite="summermvc_tests",

    author="Tim Chow",
    author_email="jordan23nbastar@vip.qq.com",
    description="An IoC and a web mvc framework for Python",
    license="MIT",
    keywords="ioc summermvc mvc",
    url="http://timd.cn/summermvc"
)
