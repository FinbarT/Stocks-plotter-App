# -*- coding: utf-8 -*-
"""
Created on Mon May 13 02:47:07 2013

@author: finbar
"""
import matplotlib.pylab as plt
import datetime as dt
import csv

from Tkinter import *
from tkFileDialog import askopenfilename
from tkMessageBox import showerror, askokcancel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class csv_stocks_app(object):
    '''
    A class that defines a GUI for opening and displaying the contents 		of a CSV file containing compnay stock trading prices
    '''
    def __init__(self, master_win):
        '''
        sets up the class, takes two arguments self and master_win.
        master_win is a Tk() root window
        '''
        self.master = master_win
        self.init_UI()

    def init_UI(self):
        '''
        sets up the user inerface with everything it needs
        '''
        self.display = Frame(self.master)
        self.fill_display()
        self.build_menu_bar()

    def fill_display(self):
        '''
        Fills the display frame with all the widgets it needs to display
        initially and later on. It will contain a scroll bar and four widgets.
        Three text displays and one matplotlib graph
        '''
        self.title_win = Text(self.display, height=32, width=93)
        self.data_win = Text(self.display, height=32, width=93)
        self.table_win = Text(self.display, height=32, width=93)
        self.graph_win = None  # initialise the variable here, for clearity
                               # really. Its widget will come after the graph
                               # is built

        self.display_scroller = Scrollbar(self.display)
        self.title_win.insert(
			END,
	        "Click browse to selct a file "
            "that you would like to import!"
		)
        self.current_view = self.title_win
        self.display.pack()
        self.title_win.pack()

    def build_menu_bar(self):
        '''
        sets up all the menu buttons. Initially, only the browse and quit
        buttons will be visible. The rest appear when the file has been loaded.
        The browse button the disappears
        '''
        self.browse_button = Button(
			self.master,
            text="Browse",
            command=self.load_file
		)
        self.quit_button = Button(
			self.master,
            text="Quit",
            command=self.quit_app
		)
        self.data_button = Button(
			self.master,
            text="Raw Data",
            command=self.render_file_contents
		)
        self.table_button = Button(
			self.master,
            text="Table",
            command=self.render_table
		)
        self.graph_button = Button(
			self.master,
            text="Graph",
            command=self.render_graph
		)
        self.browse_button.pack(side=LEFT, padx=3, pady=3)
        self.quit_button.pack(side=RIGHT, padx=3, pady=3)

    def load_file(self):
        '''
        allows the user browse their file system for the file the would like
        to load. Then reads it entirely and saves the data in self.raw_data
        then reads it again to as a CSV reader saving the CSV data in
        self.csv_data. It then displays the menu buttons. Then calls the
        functions to build the windows it later needs to display.
        '''
        self.filename = askopenfilename(filetypes=[("csv Files", "*.csv")])
        load_successful = False

        try:
            if self.filename:
                csv_file = open(self.filename, 'rU')

                try:
                    self.raw_data = csv_file.read()
                except:
                    showerror("Read Error",
                              "Failed to read file\n'%s'"
                              % self.filename)

                csv_file.seek(0, 0)  # reset file reader position

                try:
                    self.csv_data = csv.reader(csv_file)
                    self.daily_data = [row for row in self.csv_data]
                except:
                    showerror("CSV Read Error",
                              "Failed to read CSV data in file\n'%s'"
                              % self.filename)

                csv_file.close()

                if self.raw_data and self.csv_data:
                    load_successful = True
                else:
                    pass

        except IOError:
            showerror(
				"Open Source File",
                 "Failed to open file\n'%s'" %
                 self.filename
			)
        finally:
            if load_successful:

                self.browse_button.forget()

                self.data_button.pack(side=LEFT, padx=3, pady=3)
                self.table_button.pack(side=LEFT, padx=3, pady=3)
                self.graph_button.pack(side=LEFT, padx=3, pady=3)
                self.display_scroller.pack(side=RIGHT, fill=Y)

                self.data_win.insert(END, self.raw_data)
                self.render_file_contents()

                self.get_table()
                self.plot_graph()
            else:
                pass

    def get_table(self):
        '''
        gets the longest string in the data to determine the table cell
        sizes. Also builds the dividers for each row in the table. Then
        inserts the table returned from the self.build_table() function into
        the table_win text widget.
        '''
        self.longest_string = len(
			max([max(row, key=len) for row in self.daily_data], key=len)
		)
        self.table_row_divider = (
			("+" + ("-" * (self.longest_string + 2))) *
            len(self.daily_data[0]) + "+\n"
		)
        self.table_win.insert(END, self.build_table(iter(self.daily_data)))

    def build_table(self, itr_daily_data):
        '''
        A Recursive function that takes an iterator of the daily stock data
        as an argument. It builds a row of the table cell by cell from the
        strings in each iteratorion of the iterator. By calling itself it moves
        on to do the next row of the table until it is done
        '''
        table = self.table_row_divider
        try:
            row = itr_daily_data.next()
            for value in row:
                table += "|%s" % value
                for i in range((self.longest_string + 2) - len(value)):
                    table += " "
            table += "|\n"
            table += self.build_table(itr_daily_data)
        except StopIteration:
            pass
        finally:
            return table

    def plot_graph(self):
        '''
        plots a matplotlib graph from the stocks data. Dates on the x axis and
        Closing Prices on the y axis. Then adds it to the graph_win in the
        display frame as a tk widget()
        '''
        x_axis = [
			dt.datetime.strptime(self.daily_data[day][0], '%Y-%m-%d')
            for day in range(1, len(self.daily_data) - 1)
		]
        y_axis = [
			self.daily_data[cls_adj][-1]
            for cls_adj in range(1, len(self.daily_data) - 1)
		]
        fig = plt.figure()
        ax = fig.add_subplot("111")
        ax.plot(
			x_axis,
            y_axis,
            marker='h',
            linestyle='-.',
            color='r',
            label='Daily Adjusted Closing Prices'
		)
        labels = ax.get_xticklabels()
        for label in labels:
            label.set_rotation(15)
        plt.xlabel('Dates')
        plt.ylabel('Close Adj')
        plt.legend()
        plt.tight_layout()  # adjusts the graph to fit in the space its limited to
        self.data_plot = FigureCanvasTkAgg(fig, master=self.display)
        self.data_plot.show()
        self.graph_win = self.data_plot.get_tk_widget()

    def render_file_contents(self):
        '''
        Called from a button, it passes the raw_data win to the
        self.change_view() function. In turn rendering it in the display
        '''
        self.change_view(self.data_win)

    def render_table(self):
        '''
        Called from a button, it passes the table win to the self.change_view()
        function. In turn rendering it in the display
        '''
        self.change_view(self.table_win)

    def render_graph(self):
        '''
        Called from a button, it passes the graph win to the self.change_view()
        function. In turn rendering it in the display
        '''
        self.change_view(self.graph_win)

    def change_view(self, new_view):
        '''
        Takes new_view, the desired widget to be displayed, removes the
        currently displayed widget from view and displays new view in its place
        '''
        self.current_view.forget()
        new_view.pack(side=BOTTOM, fill=BOTH, expand=1)
        self.current_view = new_view
        self.display_scroller.config(command=new_view.yview)
        new_view.config(yscrollcommand=self.display_scroller.set)

    def quit_app(self):
        '''
        called from the quit button, it prompts the user to ensur they actually
        want to quit the application
        '''
        if askokcancel("Quit", "Do you wish to quit?"):
            self.master.destroy()


def main():
    '''
    initialises the root Tk() window and instaniates the csv_stocks app.
    '''
    root = Tk()
    root.geometry("670x530")
    root.title("StocksApp")
    app = csv_stocks_app(root)
    root.mainloop()

if __name__ == '__main__':
    main()
