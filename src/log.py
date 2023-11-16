colored = True


def debug(*args, **kwargs):
    if colored:
        print("\x1b[34m($)", *args, "\x1b[0m", **kwargs)
    else:
        print("($)", *args, **kwargs)


def info(*args, **kwargs):
    if colored:
        print("\x1b[32m(*)", *args, "\x1b[0m", **kwargs)
    else:
        print("(*)", *args, **kwargs)


def warning(*args, **kwargs):
    if colored:
        print("\x1b[33m(!)", *args, "\x1b[0m", **kwargs)
    else:
        print("(!)", *args, **kwargs)


def error(*args, **kwargs):
    if colored:
        print("\x1b[31m(X)", *args, "\x1b[0m", **kwargs)
    else:
        print("(X)", *args, **kwargs)


def kawaii(*args, **kwargs):
    if colored:
        s = kwargs.get("sep", " ")
        s = s.join(("(♡)", *args))
        c = [31, 33, 32, 36, 34, 35]
        r = "".join((f"\x1b[{c[i % len(c)]}m{s[i]}") for i in range(len(s)))
        print(r, "\x1b[0m", **kwargs)
    else:
        print("(♡)", *args, **kwargs)


if __name__ == "__main__":
    debug("Debug")
    info("Info")
    warning("Warning")
    error("Error")
    kawaii("Kawaii")
