import nox


@nox.session(python=['3.10', '3.11', '3.12', '3.13'])
def lint(session):
    session.install('flake8')
    session.run('flake8', 'typeca')


@nox.session(python=['3.10', '3.11', '3.12', '3.13'])
def tests(session):
    session.run('python', '-m', 'unittest', 'discover', '-s', 'tests')
