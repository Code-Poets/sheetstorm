def do_not_call_in_templates(cls):
    # Decorator necessary for callable classes, which shouldn't be called by templating system and instead be treated as a static value
    cls.do_not_call_in_templates = True
    return cls
