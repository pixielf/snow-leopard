import contextlib
import pathlib
import tkinter
import tkinter.filedialog
from typing import Union, Callable

PathLike = Union[str, pathlib.Path]


class BaseObject:
    wrapped_class = None

    def __init__(self, master=None, *args, **kwargs):
        if master and isinstance(master, BaseObject):
            master = master._tkobj
        self._tkobj = self.wrapped_class(master, *args, **kwargs)

class BaseWindow(BaseObject):
    @property
    def title(self):
        return self._tkobj.title()

    @title.setter
    def title(self, v):
        self._tkobj.title(v)

    @property
    def icon(self):
        raise NotImplementedError()

    @icon.setter
    def icon(self, path_to_icon: PathLike):
        self._tkobj.tk.call('wm', 'iconphoto', self._tkobj._w, tkinter.PhotoImage(file=str(path_to_icon)))

    @property
    def size(self):
        return self._tkobj.winfo_width(), self._tkobj.winfo_height()

    @size.setter
    def size(self, s):
        self._tkobj.geometry(f'{s[0]}x{s[1]}')


class App(BaseWindow):
    wrapped_class = tkinter.Tk

    def mainloop(self):
        self._tkobj.mainloop()


class Popup(BaseWindow):
    wrapped_class = tkinter.Toplevel


class BaseWidget(BaseObject):
    wrapped_class = None
    activatable = True       

    def __getitem__(self, key):
        return self._tkobj.cget(key)

    def __setitem__(self, key, value):
        self._tkobj.configure(**{key: value})

    @property
    def size(self):
        return self.winfo_width(), self.winfo_height()

    def grid(self, *args, **kwargs):
        sticky = kwargs.pop('sticky', 'NSEW')
        self._tkobj.grid(*args, sticky=sticky, **kwargs)

    @property
    def active(self) -> bool:
        if not self.activatable:
            return False

        return self['state'] == tkinter.NORMAL

    @active.setter
    def active(self, flag: bool):
        if not self.activatable:
            raise TypeError(f'widget of type {type(self)} is not activatable')

        self['state'] = tkinter.NORMAL if flag else tkinter.DISABLED

    @contextlib.contextmanager
    def force_active(self):
        original = self.active

        try:
            self.active = True
            yield
        finally:
            self.active = original


class Label(BaseWidget):
    wrapped_class = tkinter.Label
    activatable = False

    def __init__(self, master, text='', *args, **kwargs):
        var = self._var = tkinter.StringVar()
        var.set(text)
        super().__init__(master, *args, textvariable=var, **kwargs)

    @property
    def content(self):
        return self._var.get()

    @content.setter
    def content(self, t):
        self._var.set(t)

    @property
    def align(self):
        return self['justify'].lower()

    @align.setter
    def align(self, value):
        anchor = {'left': tkinter.W, 'center': tkinter.CENTER, 'right': tkinter.E}[value]
        justification = {'left': tkinter.LEFT, 'center': tkinter.CENTER, 'right': tkinter.RIGHT}[value]
        self['anchor'] = anchor
        self['justify'] = justification


class Entry(BaseWidget):
    wrapped_class = tkinter.Entry

    @property
    def content(self):
        return self._tkobj.get()

    @content.setter
    def content(self, t):
        self._tkobj.delete(0, tkinter.END)
        self._tkobj.insert(0, t)


class Text(BaseWidget):
    wrapped_class = tkinter.Text

    @property
    def content(self):
        return self._tkobj.get(1.0, tkinter.END)

    @content.setter
    def content(self, t):
        self._tkobj.delete(1.0, tkinter.END)
        self._tkobj.insert(1.0, t)


class Button(BaseWidget):
    wrapped_class = tkinter.Button

    @property
    def content(self):
        return self['text']

    @content.setter
    def content(self, t):
        self['text'] = t

    def flash(self):
        """ Causes the button to flash several times between active and normal colors. Leaves the button in the state it was in originally.
        Ignored if the button is disabled. """
        self._tkobj.flash()

    def __call__(self):
        """ Calls the button's callback, and returns what that function returns.
        Has no effect if the button is disabled or there is no callback. """
        return self._tkobj.invoke()


class Checkbox(BaseWidget):
    wrapped_class = tkinter.Checkbutton

    def __init__(self, master, *args, **kwargs):
        self._var = tkinter.IntVar()
        super().__init__(master, *args, variable=self._var, onvalue=1, offvalue=0, **kwargs)

    @property
    def checked(self):
        return self._var.get() == 1

    @checked.setter
    def checked(self, flag):
        if flag:
            self._tkobj.select()
        else:
            self._tkobj.deselect()

    def toggle(self):
        self._tkobj.toggle()


class _RadioButton(BaseWidget):
    wrapped_class = tkinter.Radiobutton

    def __init__(self, master, text, variable, value, callback=None):
        super().__init__(master, text=text, variable=variable, value=value, command=callback)
        self._var = variable
        self.value = value
        self['anchor'] = tkinter.W
        self['justify'] = tkinter.LEFT

    @property
    def checked(self):
        return self._var.get() == self.value

    @checked.setter
    def checked(self, flag):
        if flag:
            self._tkobj.select()
        else:
            self._tkobj.deselect()

    def toggle(self):
        self._tkobj.toggle()


class RadioButtonSet:
    def __init__(self, master, options, values=None, callback=None):
        self.master = master

        self._var = tkinter.IntVar()
        self.buttons = [
            _RadioButton(self.master, text=opt, variable=self._var, value=i, callback=callback)
            for i, opt in enumerate(options, start=1)
        ]
        self.values = values or [x for x in options]

    def grid(self, row, column, *, mode: str = 'vertical', **kwargs):
        dx, dy = {'vertical': (0, 1), 'horizontal': (1, 0)}[mode]

        for button in self.buttons:
            button.grid(row=row, column=column, **kwargs)
            row += dy
            column += dx

    @property
    def value(self):
        v = self._var.get()
        if v:
            return self.values[v - 1]
        else:
            return None

def choose_file():
    return pathlib.Path(tkinter.filedialog.askopenfilename()).resolve()
