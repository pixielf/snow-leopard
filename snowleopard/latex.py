import contextlib
from typing import Optional
from . import utils


BACKSLASH = chr(92)


class Document:
    def __init__(self, doc_class: str, *options: str):
        opts = ', '.join(map(str, options))
        self.preamble = utils.Stream(f"{BACKSLASH}documentclass[{opts}]{utils.brace(doc_class)}")
        self.body = utils.Stream()

    @contextlib.contextmanager
    def environment(self, name: str, *args: str, optval: Optional[str] = None, location: str = 'body'):
        stream = self.stream_by_name(location)

        # open the environment
        stream.write(f'{BACKSLASH}begin{utils.brace(name)}')
        if optval is not None:
            stream.write(f'[{optval}]')
        if args:
            stream.write(utils.brace(', '.join(args)))
        stream.write('\n')

        try:
            yield
        finally:
            stream.writeline(f'{BACKSLASH}end{utils.brace(name)}')

    def usepackage(self, package: str, *options: str):
        opts = f"[{', '.join(map(str, options))}]" if options else ""
        self.preamble.writeline(f"{BACKSLASH}usepackage{opts}{utils.brace(package)}")

    def usepackages(self, *packages: str):
        self.preamble.writeline(f"{BACKSLASH}usepackage{utils.brace(', '.join(packages))}")

    def newcommand(
        self,
        name: str,      # does NOT start with backslash
        cmd: str,
        nargs: int = 0,
        *,
        default: Optional[str] = None,
        renew: bool = False,
        location: str = 'preamble'
    ):
        stream = self.stream_by_name(location)

        # \(re)newcommand{\name}
        stream.write(f"{BACKSLASH}{'re' if renew else ''}newcommand{utils.brace(BACKSLASH + str(name))}")

        # handle arguments
        if nargs:
            stream.write(f'[{nargs}]')
            if default is not None:
                stream.write(f'[{default}]')

        # actual command
        stream.writeline(utils.brace(cmd))

    def newenvironment(
        self,
        name: str,
        before: str,
        after: str,
        nargs: int = 0,
        *,
        default: Optional[str] = None,
        renew: bool = False,
        location: str = 'preamble'
    ):
        stream = self.stream_by_name(location)

        # \(re)newenvironment{name}
        stream.write(f"{BACKSLASH}{'re' if renew else ''}newenvironment{utils.brace(name)}")

        # handle arguments
        if nargs:
            stream.write(f'[{nargs}]')
            if default is not None:
                stream.write(f'[{default}]')

        # before and after
        stream.writeline('{ %')
        stream.writeline(before + '}{ %')
        stream.writeline(after + '}')

    def stream_by_name(self, name: str) -> utils.Stream:
        return {'body': self.body, 'preamble': self.preamble}[name]

    def __str__(self):
        return '\n\n'.join(
            self.preamble.fullread(),
            r'\begin{document}',
            self.body.fullread(),
            r'\end{document}'
        )
