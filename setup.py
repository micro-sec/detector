from setuptools import setup, find_packages

setup(name='detector',
      version='1.0',
      packages=find_packages(exclude=["examples"]),
      entry_points={
          'console_scripts': [
              'detector = detector.main:main',
              'daemon = daemon.main:main',
              'agent = agent.main:main',
          ],
      })
