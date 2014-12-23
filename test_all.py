import pytest
from run import Pygdb, take_input, NotRunningException, NotLoadedException
import sys

@pytest.fixture
def pygdb():
    return Pygdb()

def capsys_output_only(capsys):
    out, err = capsys.readouterr()
    print out # Put it back out
    assert err == ''
    return out

class TestAll:
    def test_breakpoints(self, pygdb):
        with pytest.raises(NotLoadedException):
            pygdb.add_breakpoint(5)
    def test_help(self, pygdb):
        assert pygdb.help() == None

    def assert_types(self, pygdb):
        methods = pygdb.get_methods()
        assert isinstance(methods, list)
        assert isinstance(methods[0], tuple)

    def test_fns(self, pygdb):
        pygdb.load_program('tracedprog2')
        fns = pygdb.get_functions()
        assert fns[0]['name'] == 'do_stuff'
        assert fns[0]['low_pc'] == 0x80483e4
        assert fns[1]['name'] == 'main'
        assert fns[1]['low_pc'] == 0x804841e

    def test_breakpoint_prog1(self):
        pygdb = Pygdb()
        assert not pygdb.loaded
        pygdb.load_program('tracedprog2')
        assert pygdb.loaded

        #assert pygdb.current_eip() == -0x488ffe30 # TODO why negative? Too high? But how?
        # TODO looking at the current_eip here.. why is it so different from use.py?
        # Does it have to do with the program running in a different form.. (like in.. a bigger
        # environment here)?
        # I know that the child is going to start in some rando place at the start (before it
        # even runs the program), but I don't know why the two are so very different
        pygdb.add_breakpoint(0x80483e4)
        assert pygdb.run() == Pygdb.WAIT_STOPPED
        assert pygdb.current_eip() == 0x80483e5
        pygdb.cont()
        with pytest.raises(NotRunningException):
            pygdb.cont()
        # Should be finished
        assert not pygdb.loaded
        pygdb.cleanup_breakpoint()

    def test_no_breakpoint(self, pygdb):
        assert not pygdb.loaded
        assert pygdb.load_program('traced_c_loop') == Pygdb.WAIT_STOPPED
        assert pygdb.loaded
        assert pygdb.run() == Pygdb.WAIT_EXITED
        assert not pygdb.loaded

    def test_invalid_wait(self, pygdb):
        with pytest.raises(NotLoadedException):
            pygdb.wait()

    def test_breakpoint2(self, pygdb):
        assert not pygdb.loaded
        pygdb.load_program('traced_c_loop') == Pygdb.WAIT_STOPPED
        assert pygdb.loaded

        pygdb.add_breakpoint(0x8048429)

        assert pygdb.run() == Pygdb.WAIT_STOPPED
        assert pygdb.current_eip() == 0x804842a
        assert pygdb.loaded
        pygdb.cont()
        assert not pygdb.loaded
        with pytest.raises(NotRunningException):
            pygdb.cont()
        pygdb.cleanup_breakpoint()

    def test_step(self, pygdb):
        pygdb.load_program('traced_c_loop') == Pygdb.WAIT_STOPPED
        pygdb.add_breakpoint(0x8048414)
        pygdb.run()

        # There was a 0xCC opcode (interrupt) at 414. So our eip is at 415, but the next step()
        # we run runs the replaced (real) opcode at 414. If that's of size 1, our next instruction
        # is at 415. But the step after that is not.
        # TODO our eip should kinda be 414 here.. I can tell run() to do that?
        assert pygdb.current_eip() == 0x8048415
        assert pygdb.step() == Pygdb.WAIT_STOPPED

        assert pygdb.current_eip() == 0x8048415
        assert pygdb.step() == Pygdb.WAIT_STOPPED

        assert pygdb.current_eip() == 0x8048417
        assert pygdb.step() == Pygdb.WAIT_STOPPED

        assert pygdb.current_eip() == 0x804841a
        assert pygdb.cont() == Pygdb.WAIT_STOPPED
        pygdb.cleanup_breakpoint()

    def test_breakpoint_in_loop(self, pygdb):
        assert not pygdb.loaded
        assert pygdb.load_program('traced_c_loop') == Pygdb.WAIT_STOPPED
        assert pygdb.loaded

        pygdb.add_breakpoint(0x8048414)

        assert pygdb.run() == Pygdb.WAIT_STOPPED
        assert pygdb.current_eip() == 0x8048415
        assert pygdb.loaded
        pygdb.cont()
        pygdb.cont()
        pygdb.cont()
        assert pygdb.loaded
        pygdb.cont()
        assert not pygdb.loaded
        with pytest.raises(NotRunningException):
            pygdb.cont()
        pygdb.cleanup_breakpoint()

    def test_fns(self, pygdb):
        pygdb.load_program('tracedprog2')
        mem = pygdb.read_memory(0x80483e4, 3)
        assert mem[0] == 0x55
        assert mem[1] == 0x89
        assert mem[2] == 0xe5

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

    def test_breakpoint_in_loop(self, pygdb, capsys):
        take_input(pygdb, 'b 0x8048414')
        assert 'NotLoadedException' in capsys_output_only(capsys)
        take_input(pygdb, 'exec-file traced_c_loop')
        take_input(pygdb, 'b 0x8048414')
        assert 'Adding breakpoint at  0x8048414' in capsys_output_only(capsys)

        take_input(pygdb, 'c')
        assert 'NotRunningException' in capsys_output_only(capsys)

        take_input(pygdb, 'run')
        take_input(pygdb, 'regs')
        assert 'eip: 0x8048415' in capsys_output_only(capsys)
        take_input(pygdb, 'c')
        take_input(pygdb, 'c')
        take_input(pygdb, 'c')
        assert 'Child exited' not in capsys_output_only(capsys)
        take_input(pygdb, 'c')
        assert 'Child exited' in capsys_output_only(capsys)

    def test_breakpoint_read_mem(self, pygdb, capsys):
        take_input(pygdb, 'example')
        take_input(pygdb, 'read 0x8048080 4')
        assert "0x8048080: ['0xcc', '0x7', '0x0', '0x0']" in capsys_output_only(capsys)


if __name__ == "__main__":
    pygdb = Pygdb()

