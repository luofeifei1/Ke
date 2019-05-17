from distutils.core import setup
setup(
  name = 'ke',         # How you named your package folder (MyLib)
  packages = ['ke'],   # Chose the same as "name"
  version = '1.2.7',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'A scraper of Beike, the best Chinese online real-estate listing website.',   # Give a short description about your library
  author = 'Qiao Zhang',                   # Type in your name
  author_email = 'qiao.zhang.qz@outlook.com',      # Type in your E-Mail
  url = 'https://github.com/qzcool/Ke',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/qzcool/Ke/archive/v1.2.7.tar.gz',    # I explain this later on
  keywords = ['scraper', 'real-estate', 'china', 'beike'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pandas',
          'bs4',
          'selenium',
          'tqdm',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)