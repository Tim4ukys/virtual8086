import vproc.instructions as t

def test_remove_comments():
    assert t._remove_comments("") == ''
    assert t._remove_comments('aboba; sdf;;daf;sadf;') == 'aboba'
    assert t._remove_comments('; fdsvdsf') == ''



