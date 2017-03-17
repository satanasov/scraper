import distutils.core

distutils.core.setup(
    name='Scraper',
    version='0.5',
    packages=[''],
    url='',
    license='GPL',
    author='Stanislav Atanasov',
    author_email='lucifer@anavaro.com',
    description='Scrape kink.com and create NFOs for your Media DB.', requires=['lxml', 'requests']
)
