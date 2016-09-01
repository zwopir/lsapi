import os


def get_fixture_path(fixture):
    return os.path.join(os.path.dirname(__file__), 'fixtures', fixture)


def get_fixture(fixture):
    with open(get_fixture_path(fixture)) as f:
        return f.read()
