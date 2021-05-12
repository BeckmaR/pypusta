from pusta.generator.output import IndentedWriter

def test_indented_writer():
    w = IndentedWriter()
    w.append("Hello World")

    assert str(w) == "Hello World\n"

    w = IndentedWriter()
    w.incr()
    w.append("Hello World")
    w.decr()

    assert str(w) == "    Hello World\n"

    w = IndentedWriter()
    w.append('a')
    w.incr()
    w.append('b')
    w.incr()
    w.append('c')

    assert str(w) == "a\n    b\n        c\n"

    a = IndentedWriter()
    a.append(w)

    assert str(a) == str(w)