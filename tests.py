import pytest
from run import Pygdb, take_input

@pytest.fixture
def pygdb():
    return Pygdb('tracedprog2')

class TestAll:
    def test_breakpoints(self, pygdb):
        pygdb.add_breakpoint(5)
        assert pygdb.get_breakpoints() == [5]
    def test_help(self, pygdb):
        assert pygdb.help() == None

    def assert_types(self, pygdb):
        methods = pygdb.get_methods()
        assert isinstance(methods, list)
        assert isinstance(methods[0], tuple)

    def test_fns(self, pygdb):
        fns = pygdb.get_functions()
        assert fns[0]['name'] == 'do_stuff'
        assert fns[0]['low_pc'] == 0x4004f4
        assert fns[1]['name'] == 'main'
        assert fns[1]['low_pc'] == 0x400536

class TestInput:
    def test_fns_called(self, monkeypatch, pygdb):
        self.call_count = 0
        def callme(self):
            # TODO nasty.. so much state modification
            def inner():
                self.call_count += 1
            return inner
        monkeypatch.setattr(pygdb, 'get_methods', lambda: [('first', callme(self))])
        take_input(pygdb, 'first')
        assert self.call_count == 1

    def test_nomethod(self, monkeypatch, pygdb):
        def bad_fn():
            raise Exception
        monkeypatch.setattr(pygdb, 'get_methods', lambda: [('first', bad_fn)])
        assert take_input(pygdb, 'wrong') == False

    def test_arguments_mismatch(self, monkeypatch, pygdb):
        def bad_fn(one, two, three):
            return True
        monkeypatch.setattr(pygdb, 'get_methods', lambda: [('first', bad_fn)])
        assert take_input(pygdb, 'first') == False

