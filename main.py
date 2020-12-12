import collections
import pathlib
import pprint
import snowleopard
from snowleopard import tkwrapper

print = pprint.pprint

class GUI(tkwrapper.App):
    def __init__(self):
        super().__init__()
        self.title = 'Project Snow Leopard'
        self.icon = pathlib.Path(__file__).parent / 'assets' / 'snow-leopard-icon.png'
        self.size = 850, 800

        # get CSV file
        tkwrapper.Label(self, 'CSV File:').grid(row=0, column=0)
        self.csv_textbox = tkwrapper.Entry(self, width=50)
        self.csv_textbox.grid(row=0, column=1)
        tkwrapper.Button(
            self,
            text='Choose File',
            command=self.get_csvfile
        ).grid(row=0, column=2)

    def get_csvfile(self):
        with self.csv_textbox.force_active():
            self.csv_textbox.content = path = tkwrapper.choose_file()

        # columns read from CSV
        tkwrapper.Label(self, 'Columns:').grid(row=1, column=0)
        self._raw_column_headers = tuple(snowleopard.processing.get_column_headers(path))
        self._column_setters = []
        j = 0
        for j, col in enumerate(self._raw_column_headers):
            checkbox = tkwrapper.Checkbox(self)
            checkbox.grid(row=2+j, column=0)

            entry = tkwrapper.Entry(self, width=15)
            entry.grid(row=2+j, column=1, columnspan=2)
            entry.content = col

            self._column_setters.append((j, checkbox, entry))

        tkwrapper.Button(
            self,
            text='Use these columns',
            command=self.get_columns
        ).grid(row=100, column=0, columnspan=6)

        # calculated columns
        tkwrapper.Label(self, 'Calculated Column:').grid(row=1, column=4)
        tkwrapper.Label(self, 'Calculation:').grid(row=1, column=5)
        self._calculated_columns = []
        for j in range(35):
            checkbox = tkwrapper.Checkbox(self)
            checkbox.grid(row=2+j, column=3)

            col_name = tkwrapper.Entry(self, width=20)
            col_name.grid(row=2+j, column=4)

            calculation = tkwrapper.Entry(self, width=20)
            calculation.grid(row=2+j, column=5)

            self._calculated_columns.append((j, checkbox, col_name, calculation))

        tkwrapper.Button(
            self,
            text='Calculated Column Help',
            command=self.calculated_column_help
        ).grid(row=0, column=5)

    def calculated_column_help(self):
        popup = tkwrapper.Popup(self)
        popup.title = 'Project Snow Leopard: Calculated Column Help'
        popup.icon = pathlib.Path(__file__).parent / 'assets' / 'snow-leopard-icon.png'

        functions = [
            {
                'name': 'SUMDROP',
                'command': 'SUMDROP(k; column_name_1, column_name_2, ...)',
                'help': 'Add a sequence of values while dropping the k lowest scores. Use SUMDROP(0; ...) to sum all values.'
            },
            {
                'name': 'BOUND',
                'command': 'BOUND(lower_bound, upper_bound; value)',
                'help': 'Limit the value between the two bounds. More formally: BOUND(a, b; v) returns a if v <= a, b if v >= b, and v itself if a <= v <= b.'
            }
        ]

        r = 0
        for function in sorted(functions, key=lambda dct: dct['name']):
            tkwrapper.Label(popup, function['name'], font=('font'), bg='#313131', fg='#dddddd').grid(row=r, column=0)
            a = tkwrapper.Label(popup, function['command'])
            a.align = 'left'
            a.grid(row=r+1, column=0)
            
            a = tkwrapper.Label(popup, function['help'])
            a.align = 'left'
            a.grid(row=r+2, column=0)

            r += 3

    def get_columns(self):
        ColumnData = collections.namedtuple('ColumnData', ('index', 'original_name', 'new_name', 'calculation'))
        cols = [
            ColumnData(index=j, original_name=self._raw_column_headers[j], new_name=entry.content, calculation=None)
            for j, checkbox, entry in self._column_setters
            if checkbox.checked
        ]

        cols += [
            ColumnData(index=j, original_name=None, new_name=name.content, calculation=calculation.content)
            for j, checkbox, name, calculation in self._calculated_columns
            if checkbox.checked
        ]

        print(cols)


if __name__ == '__main__':
    GUI().mainloop()
