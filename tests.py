import pytest
from run import Pygdb, take_input, NotRunningException

@pytest.fixture
def pygdb():
    return Pygdb()

class TestAll:
    def test_breakpoints(self, pygdb):
        with pytest.raises(NotRunningException):
            pygdb.add_breakpoint(5)
    def test_help(self, pygdb):
        assert pygdb.help() == None

    def assert_types(self, pygdb):
        methods = pygdb.get_methods()
        assert isinstance(methods, list)
        assert isinstance(methods[0], tuple)

    def test_fns(self, pygdb):
        fns = pygdb.get_functions()
        assert fns[0]['name'] == 'do_stuff'
        assert fns[0]['low_pc'] == 0x80483e4
        assert fns[1]['name'] == 'main'
        assert fns[1]['low_pc'] == 0x804841e

    def Ntest_breakpoint(self, pygdb):
        assert not pygdb.loaded
        pygdb.load_program('tracedprog2')
        assert pygdb.loaded

        pygdb.wait()
        #assert pygdb.current_eip() == -0x488ffe30 # TODO why negative? Too high? But how?
        # TODO looking at the current_eip here.. why is it so different from use.py?
        # Does it have to do with the program running in a different form.. (like in.. a bigger
        # environment here)?
        # I know that the child is going to start in some rando place at the start (before it
        # even runs the program), but I don't know why the two are so very different
        pygdb.add_breakpoint(0x80483e4)
        pygdb.start()
        pygdb.wait()
        assert pygdb.current_eip() == 0x80483e5
        assert pygdb.loaded
        pygdb.cont()
        pygdb.wait()
        # Should be finished
        assert not pygdb.loaded
        pygdb.cleanup_breakpoint()

    def Ntest_no_breakpoint(self, pygdb):
        assert not pygdb.loaded
        pygdb.load_program('traced_c_loop')
        assert pygdb.loaded

        assert pygdb.wait() == Pygdb.WAIT_STOPPED
        pygdb.start()

        assert pygdb.wait() == Pygdb.WAIT_EXITED
        assert not pygdb.loaded
        pygdb.cleanup_breakpoint()

    def test_breakpoint2(self, pygdb):
        assert not pygdb.loaded
        pygdb.load_program('traced_c_loop')
        print 'load program'
        assert pygdb.loaded

        assert pygdb.wait() == Pygdb.WAIT_STOPPED
        pygdb.add_breakpoint(0x8048429)

        print 'Now start'
        pygdb.start()
        assert pygdb.wait() == Pygdb.WAIT_STOPPED
        assert pygdb.current_eip() == 0x804842a
        assert pygdb.loaded
        pygdb.cont()
        print 'Then wait'
        assert pygdb.wait() == Pygdb.WAIT_EXITED
        assert not pygdb.loaded
        with pytest.raises(NotRunningException):
            pygdb.cont()
        pygdb.cleanup_breakpoint()

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

