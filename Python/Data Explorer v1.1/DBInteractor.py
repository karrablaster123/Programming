
from tkinter import filedialog, Tk
from pathlib import Path
import pandas as pd
import ipywidgets as widgets
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from itertools import product
from tkinter.messagebox import showinfo
import traceback
from scipy import interpolate


class DataBaseInteractor():

    def __init__(self, old_run=None):
        self._numerical_option = ["<Numerical Columns below (may not work)>"]
        self.save_dict = None
        self.widgets = []
        self.applied_advanced_filters = []
        self.output = widgets.Output()
        self._display_output()
        self.palette = sns.color_palette("tab10", desat=1)
        if old_run is None:
            self.root = Tk()
            self._display([widgets.HTML(
                value="<p>Your file should have only one worksheet, "
                "a top row of variable names, "
                "and the rest of the rows must be data rows. Ensure "
                "there isn't any text in your numeric columns, "
                "empty cells are fine.</p>")])
            try:
                self.file_name = filedialog.askopenfilename(
                    initialdir=Path.cwd(),
                    title="Select database source",
                    filetypes=(("Excel Workbook File", "*.xlsx"),
                               ("Excel File", "*.xls")))
                self._display([widgets.HTML(
                    value=f"File selected: {str(Path(self.file_name))}")])
            except Exception as e:
                self.err_msg(f"Error: {e}")
            finally:
                self.root.destroy()

            if self.file_name == '':
                raise RuntimeError("Error selecting file")

            self.go_button = self._create_button("Go")
            self.go_button.on_click(self._on_go_button_clicked)
            self._display([self.go_button])
        else:
            pass

    def _format_list_to_string(self, list_to_format):
        """Given a list of strings, format it into a single string
        with a comma and space separating each item."""

        return ", ".join(list_to_format)

    def _on_go_button_clicked(self, b):
        
        self._clear_display()
        self._display([widgets.HTML(
            value="<h4>Reading Data</h4>")])
        self.data = pd.read_excel(self.file_name, engine='calamine')
        self._display([widgets.HTML(
            value="<h4>Column Names and Dimensions</h4>")])
        self._display([widgets.HTML(
            value=f"<h5>{self._format_list_to_string(self.data.columns)}</h5>"
        )])
        self._display([widgets.HTML(
            value=f"<h5>Rows: {self.data.shape[0]}\
                <br>Columns: {self.data.shape[1]}</h5>")])
        self._display([widgets.HTML(
            value="<h4>Check if they make sense.</h4>")])
        self.go_button = self._create_button("Continue")
        self.go_button.on_click(self._on_continue_button_clicked)
        self._display([self.go_button])
        px_per_item = 400 / 5
        self.height_of_box = px_per_item * len(self.data.columns) / 8
        if self.height_of_box < 150:
            self.height_of_box = 150
        self._generate_handle_nan()

    def _on_continue_button_clicked(self, b):
        if len(self.numeric_columns) == 0:
            self._generate_filters()
            self.main_menu()
        else:
            self.nan_menu()

    def _generate_handle_nan(self):
        self.numeric_columns = set()
        self.categorical_columns = set()
        self.handle_numeric_nans = ["Replace with zeroes",
                                    "Drop rows",
                                    "Replace with minimum value",
                                    "Keep as NaN"]
        self.handle_categorical_nans = ["Replace with \'No Data\'",
                                        "Drop rows"]
        num_nan_cols = self.data.isnull().any().sum()
        length_of_grid = int(np.ceil(num_nan_cols / 4))
        if length_of_grid == 0:
            return
        self.nan_grid = widgets.GridspecLayout(length_of_grid, 4)
        self.nan_grid_indices = product(range(int(length_of_grid)), range(4))
        self.nan_widgets = {}
        for column, (x, y) in zip(self.data.columns[self.data.isnull().any()],
                                  self.nan_grid_indices):
            if self.data[column].dtype.kind in 'biufc':
                self.numeric_columns.update((column, ))
                self.nan_widgets[column] = self.\
                    _create_dropdown(column, self.handle_numeric_nans)
                self.nan_grid[x, y] = self.nan_widgets[column]
            elif any([isinstance(val, str) for val in self.data[column]]):
                self.categorical_columns.update((column, ))
                self.nan_widgets[column] = self.\
                    _create_dropdown(column, self.handle_categorical_nans)
                self.nan_grid[x, y] = self.nan_widgets[column]

    def nan_menu(self):
        self._clear_display()
        self._display([widgets.HTML(
            value="<h4>How do I handle NaN or null values?</h4>")])
        self._display([self.nan_grid])
        self._display([self._go_back_button(self.apply_nan, "Continue")])

    def apply_nan(self, b):
        self._clear_display()
        self._display([widgets.HTML(value="<h4>Applying NaN Handling</h4>")])
        for column in self.numeric_columns:
            if self.nan_widgets[column].value == "Replace with zeroes":
                self.data[column].fillna(0, inplace=True)
            elif self.nan_widgets[column].value == "Drop rows":
                self.data.dropna(subset=[column], inplace=True)
            elif (self.nan_widgets[column].value ==
                  "Replace with minimum value"):
                self.data[column].fillna(self.data[column].min(), inplace=True)
        for column in self.categorical_columns:
            if self.nan_widgets[column].value == "Replace with \'No Data\'":
                self.data[column].fillna("No Data", inplace=True)
            elif self.nan_widgets[column].value == "Drop rows":
                self.data.dropna(subset=[column], inplace=True)
        self._generate_filters()
        self.main_menu()

    def _filter_data(self, b):
        self._clear_display()
        self._display(self.filter_widgets_all)

    def _generate_filters(self):
        self.active_data = self.data.copy()
        length_of_grid = int(np.ceil(len(self.data.columns) / 3))
        self.filter_grid = widgets.GridspecLayout(length_of_grid, 3)
        self.filter_grid_indices = product(range(int(length_of_grid)),
                                           range(3))
        self.filters = {}
        self.filter_widgets = {}
        self.filter_widgets_all = []
        for column in self.data.columns:
            if self.data[column].dtype.kind in 'biufc':
                self.numeric_columns.update((column, ))
                if self.data[column].min() == self.data[column].max():
                    continue
                self.filters[column] = (self.data[column].min(),
                                        self.data[column].max())
                self.filter_widgets[column] = self._create_slider(column)

            elif any([isinstance(val, str) for val in self.data[column]]):
                self.categorical_columns.update((column, ))
                self.filters[column] = list(self.data[column].unique())
                self.filter_widgets[column] = self._create_multi_select(
                    column,
                    ["Select All"] + list(self.data[column].unique()), 'auto')

        for i, (x, y) in enumerate(self.filter_grid_indices):
            if i < len(self.filters):
                self.filter_grid[x, y] = list(self.filter_widgets.values())[i]
        title = widgets.VBox([widgets.HTML(value="<h3>Filter Data</h3>")],
                             layout=widgets.Layout(width='100%',
                                                   display='flex',
                                                   align_items='center'))
        warning = widgets.VBox([widgets.HTML(
            value="<p>The sliders do not reflect any applied\
                advanced filters.</p>")],
            layout=widgets.Layout(width='100%', display='flex',
                                  align_items='center'))
        self._clear_filters_button = self._create_button("Clear Filters",
                                                         style='danger')
        self._clear_filters_button.on_click(self._clear_filters)
        self._apply_filters_button = self._create_button("Apply Filters",
                                                         style='success')
        self._apply_filters_button.on_click(self._apply_filters)
        self.filter_widgets_all.extend([
            self._apply_filters_button,
            title,
            warning,
            self.filter_grid,
            self._clear_filters_button
        ])
        self._ui_generate()

    def _clear_filters(self, b):
        self._generate_filters()
        self._filter_data(None)

    def _apply_filters(self, b):
        if b != "Advanced Filtering Caller":
            self._clear_display()
        filtered_data = self.data.copy()
        for column, widget in self.filter_widgets.items():
            if column in self.numeric_columns:
                min_value, max_value = widget.value
                filtered_data = filtered_data[
                    (filtered_data[column] >= min_value) &
                    (filtered_data[column] <= max_value)]
            elif column in self.categorical_columns:
                selected_values = widget.value
                if len(selected_values) == 0:
                    continue
                if "Select All" in selected_values:
                    continue
                filtered_data = filtered_data[
                    filtered_data[column].isin(list(selected_values))]
        self.active_data = filtered_data
        if len(self.applied_advanced_filters) > 0:
            for query in self.applied_advanced_filters:
                self.active_data = self.active_data.query(query)
        if b != "Advanced Filtering Caller":
            self.main_menu()

    def _ui_generate(self):
        self.twoD_multi_y_options = ["Subplots",
                                     "Single overlaid plot w/ up to 4 y-axes",
                                     "Single overlaid plot w/ single y-axis"]
        self._generate_main_menu()
        self._generate_corr_plot()
        self._generate_oneD_plot()
        self._generate_twoD_plot()
        self._generate_twoD_scatter_plot()
        self._generate_twoD_line_plot()
        self._generate_twoD_regression_plot()
        self._generate_twoD_categorical_plot()
        self._generate_threeD_plot()
        self._generate_advanced_filtering()
        self._generate_twoD_histogram()
        self._generate_twoD_scatter_colorbar()
        self._generate_table()

    def _generate_advanced_filtering(self):
        self.advanced_filter_widgets_all = []
        self.advanced_filter_widgets_all.append(
            self._go_back_button(self.main_menu))
        self.advanced_filter_widgets_all.append(widgets.VBox([widgets.HTML(
            value="<h3>Advanced Filtering</h3>")],
            layout=widgets.Layout(width='100%', display='flex',
                                  align_items='center')))
        self.advanced_filter_widgets_all.append(widgets.HTML(
            value="<p>This place allows you to input a query to "
            "filter the dataframe manually. The text in the text box below "
            "will be fed to the query function of a dataframe. "
            "See this for more info: "
            "<a target=\"_blank\" href= \"https://datagy.io/pandas-query/\">"
            "Pandas Query</a></p>"))
        self.advanced_filter_textbox = widgets.Textarea(
            placeholder='Enter your query here',
            description='Query:',
            disabled=False)
        self.advanced_filter_widgets_all.append(self.advanced_filter_textbox)

        self.advanced_filter_widgets_all.append(widgets.HTML(
            value="<p>Note that the queries are applied "
            "on top of existing filters.</p>"))
        self.advanced_filter_button = self._create_button("Apply Query",
                                                          style='success')
        self.advanced_clear_filters = self._create_button(
            "Clear all advanced filters", style='danger')
        self.undo_last_filter = self._create_button("Undo Last Filter",
                                                    style='warning')
        self.advanced_filter_button_Hbox = widgets.HBox(
            [self.advanced_filter_button,
             self.undo_last_filter])
        self.undo_last_filter.on_click(self._undo_last_advanced_filter)
        self.advanced_clear_filters.on_click(self._advanced_clear_filter)
        self.advanced_filter_button.on_click(self._apply_advanced_filter)
        self.advanced_filter_history = widgets.HTML(
            value="<h4>Applied Filters</h4>")
        self.advanced_filter_widgets_all.append(
            self.advanced_filter_button_Hbox)
        self.advanced_filter_widgets_all.append(self.advanced_clear_filters)
        self.advanced_filter_widgets_all.append(self.advanced_filter_history)

    def _apply_advanced_filter(self, b):
        try:
            self.active_data = self.active_data.query(
                self.advanced_filter_textbox.value)
            self.applied_advanced_filters.append(
                self.advanced_filter_textbox.value)
            self._update_advanced_filtering_history()
            self._display([widgets.HTML(value="<h4>Query Applied</h4>")])
        except Exception as e:
            self.err_msg(f"Error: {e}")

    def _undo_last_advanced_filter(self, b):
        if len(self.applied_advanced_filters) > 0:
            self.applied_advanced_filters.pop()
            self._apply_filters("Advanced Filtering Caller")
            self._update_advanced_filtering_history()

    def _update_advanced_filtering_history(self):
        self.advanced_filter_history.value = "<h4>Applied Filters</h4>"
        self.advanced_filter_history.value += "<ol>"
        for filter_string in self.applied_advanced_filters:
            self.advanced_filter_history.value += f"<li>{filter_string}</li>"
        self.advanced_filter_history.value += "</ol>"

    def _advanced_clear_filter(self, b):
        self.applied_advanced_filters = []
        self._apply_filters("Advanced Filtering Caller")
        self._update_advanced_filtering_history()

    def _advanced_filtering(self, b):
        self._clear_display()
        self._display(self.advanced_filter_widgets_all)

    def _generate_main_menu(self):
        self.main_menu_widgets_all = []
        self.main_menu_widgets_all.append(widgets.VBox([widgets.HTML(
            value="<h3>Main Menu</h3>")],
            layout=widgets.Layout(width='100%', display='flex',
                                  align_items='center')))
        self.main_menu_grid = widgets.GridspecLayout(3, 2)
        self.filter_button = self._create_button("Filter Data",
                                                 style='success')
        self.filter_button.on_click(self._filter_data)

        self.oneD_plot_button = self._create_button("1D Plot", style='success')
        self.oneD_plot_button.on_click(self._oneD_plot)

        self.twoD_plot_button = self._create_button("2D Plot", style='success')
        self.twoD_plot_button.on_click(self._twoD_plot)

        self.threeD_plot_button = self._create_button("3D Plot",
                                                      style='success')
        self.threeD_plot_button.on_click(self._threeD_plot)

        self.corr_plot_button = self._create_button("Correlation Matrix Plot",
                                                    style='success')
        self.corr_plot_button.on_click(self._corr_plot)

        self.gen_table_button = self._create_button("Show Table",
                                                    style='success')
        self.gen_table_button.on_click(self._table)

        self.main_menu_grid[0, 0] = self.filter_button
        self.main_menu_grid[0, 1] = self.oneD_plot_button
        self.main_menu_grid[1, 0] = self.twoD_plot_button
        self.main_menu_grid[1, 1] = self.threeD_plot_button
        self.main_menu_grid[2, 0] = self.corr_plot_button
        self.main_menu_grid[2, 1] = self.gen_table_button

        self.statistics_button = self._create_button("Show Table Statistics",
                                                     style='success')
        self.statistics_button.on_click(self._show_statistics)

        self.advanced_filter_button = self._create_button("Advanced Filtering",
                                                          style='warning')
        self.advanced_filter_button.on_click(self._advanced_filtering)

        self.main_menu_widgets_all.append(self.main_menu_grid)
        self.main_menu_widgets_all.append(widgets.VBox(
            [self.statistics_button],
            layout=widgets.Layout(width='100%', display='flex',
                                  align_items='center')))
        self.main_menu_widgets_all.append(widgets.VBox(
            [self.advanced_filter_button],
            layout=widgets.Layout(width='100%', display='flex',
                                  align_items='center')))

    def main_menu(self, b=None):
        self._clear_display()
        self._display(self.main_menu_widgets_all)

    def _show_statistics(self, b):
        self._clear_display()
        self._display([self._go_back_button(self.main_menu)])
        self._display(
            [
                widgets.VBox(
                    [
                        widgets.HTML(
                            value="<h3>Table Statistics "
                            "(Includes Applied Filters)</h3>")],
                    layout=widgets.Layout(
                        width='100%',
                        display='flex',
                        align_items='center'))])
        self._display(
            [
                widgets.VBox(
                    [
                        widgets.HTML(
                            value=f"<h3>Rows: {self.active_data.shape[0]}, "
                            f"Columns: {self.active_data.shape[1]}</h3>")],
                    layout=widgets.Layout(
                        width='100%',
                        display='flex',
                        align_items='center'))])
        self._display(
            [widgets.HTML(value=self.active_data
                          .describe(include='all')
                          .to_html())])

    def _table(self, b):
        self._clear_display()
        self._gen_table()
        self._display(self.table_widgets)

    def _gen_table(self):
        table = f"<table style=\"{self.table_style}\">"
        table += self._return_HTML_header_row(self.active_data.columns)
        for i, (_, row) in enumerate(self.active_data.iterrows()):
            if i % 2 == 0:
                even = True
            else:
                even = False
            table += self._return_HTML_row(row, even)
        table += "</table>"
        self.table.value = table

    def _generate_table(self):
        self.table_widgets = []
        self.table_style = "border: 1px solid black;border-collapse: collapse"
        self.table_color = ["background-color: rgba(200, 120, 120, 0.2)",
                            "background-color: rgba(60, 60, 60, 0.2)"]
        self.table = widgets.HTML(value="Empty")
        self.table_widgets.append(self._go_back_button(self.main_menu))
        self.table_widgets.append(
            widgets.VBox(
                [
                    widgets.HTML(
                        value="<h3>Table</h3>")],
                layout=widgets.Layout(
                    width='100%',
                    display='flex',
                    align_items='center')))
        export_button = self._create_button("Export Table as XLSX")
        export_button.on_click(self._export_table)
        self.table_widgets.append(export_button)
        self.table_widgets.append(self.table)

    def _return_HTML_cell(self, data):
        for i, item in enumerate(data):
            if i % 2 == 0:
                yield f"<td style=\"{self.table_style}\">{item}</td>"
            else:
                yield f"""<td style=\"{self.table_style};\
                    {self.table_color[1]}\">{item}</td>"""

    def _return_HTML_row(self, data, even):
        if even:
            row_str = "<tr>"
        else:
            row_str = f"<tr style=\"{self.table_color[0]}\">"
        for item in self._return_HTML_cell(data):
            row_str += item
        return row_str + "</tr>"

    def _return_HTML_header_cell(self, data):
        for i, item in enumerate(data):
            if i % 2 == 0:
                yield f"<th style=\"{self.table_style}\">{item}</th>"
            else:
                yield f"""<th style=\"{self.table_style};\
                    {self.table_color[1]}\">{item}</th>"""

    def _return_HTML_header_row(self, data):
        row_str = "<tr>"
        for item in self._return_HTML_header_cell(data):
            row_str += item
        return row_str + "</tr>"

    def _generate_threeD_plot(self):
        self.threeD_plot_widgets = []
        self.threeD_plot_widgets.append(self._go_back_button(self.main_menu))
        self.threeD_plot_widgets.append(
            widgets.VBox(
                [
                    widgets.HTML(
                        value="<h3>3D Plotting</h3>")],
                layout=widgets.Layout(
                    width='100%',
                    display='flex',
                    align_items='center')))
        self.threeD_grid_1 = widgets.GridspecLayout(1, 3)
        self.threeD_grid_2 = widgets.GridspecLayout(1, 3)
        self.select_plot = self._create_dropdown(
            "Type of Plot",
            [
                "Scatter Plot",
                "Surface plot with interpolation",
                "Surface Plot without interpolation",
                "Wireframe Plot with interpolation",
                "Contour Plot with interpolation",
                "Contour Plot without interpolation",
                "Contourf Plot with interpolation",
                "Contourf Plot without interpolation"])
        self.select_var_x = self._create_dropdown(
            "X Variable", self.num_list_ordered)
        self.select_var_y = self._create_dropdown(
            "Y Variable", self.num_list_ordered)
        self.select_var_z = self._create_dropdown(
            "Z Variable", self.num_list_ordered)
        self.threeD_grid_1[0, 0] = self.select_var_x
        self.threeD_grid_1[0, 1] = self.select_var_y
        self.threeD_grid_1[0, 2] = self.select_var_z
        self.interpolation_method = self._create_dropdown(
            "Interpolation Method", ["linear", "cubic", "nearest"])
        self.threeD_log_X = self._create_checkbox("Log X Axis", value=False)
        self.threeD_log_Y = self._create_checkbox("Log Y Axis", value=False)
        self.threeD_log_Z = self._create_checkbox("Log Z Axis", value=False)
        self.threeD_grid_2[0, 0] = self.threeD_log_X
        self.threeD_grid_2[0, 1] = self.threeD_log_Y
        self.threeD_grid_2[0, 2] = self.threeD_log_Z
        self.plot_button = self._create_button("Plot")
        self.plot_button.on_click(self._threeD_plotter)
        self.threeD_plot_widgets.extend([self.select_plot,
                                         self.interpolation_method,
                                         self.threeD_grid_1,
                                         self.threeD_grid_2,
                                         self.plot_button])

    def _threeD_plot(self, b):
        self._clear_display()
        self._display(self.threeD_plot_widgets)

    def _threeD_plotter(self, b):
        self.currfig = plt.figure()
        plt.get_current_fig_manager().window.showMaximized()
        plt.gcf().set_layout_engine("tight")
        self.plotting_data = self.active_data.copy()
        x = self.select_var_x.value
        y = self.select_var_y.value
        z = self.select_var_z.value

        if self.select_plot.value == "Scatter Plot":
            ax = self.currfig.add_subplot(111, projection='3d')
            ax.scatter(
                self.active_data[x],
                self.active_data[y],
                self.active_data[z])
            ax.set_xlabel(x)
            ax.set_ylabel(y)
            ax.set_zlabel(z)
        elif self.select_plot.value == "Surface plot with interpolation":
            ax = self.currfig.add_subplot(111, projection='3d')
            self.plotting_data = self.plotting_data.sort_values(by=[x, y])
            xypoints = self.plotting_data[[x, y]].values
            zpoints = self.plotting_data[z].values
            grid_x, grid_y = np.meshgrid(
                np.linspace(
                    self.plotting_data[x].min(),
                    self.plotting_data[x].max(),
                    1000),
                np.linspace(
                    self.plotting_data[y].min(),
                    self.plotting_data[y].max(),
                    1000))
            grid_z = interpolate.griddata(
                xypoints, zpoints, (grid_x, grid_y),
                method=self.interpolation_method.value)
            ax.plot_surface(grid_x, grid_y, grid_z, cmap='viridis')
            ax.set_xlabel(x)
            ax.set_ylabel(y)
            ax.set_zlabel(z)
            ax.set_title(f"{z} as surface of {x} and {y}")
        elif self.select_plot.value == "Surface Plot without interpolation":
            ax = self.currfig.add_subplot(111, projection='3d')
            self.plotting_data = self.plotting_data.sort_values(by=[x, y])
            ax.plot_trisurf(
                self.plotting_data[x],
                self.plotting_data[y],
                self.plotting_data[z],
                cmap='viridis')
            ax.set_xlabel(x)
            ax.set_ylabel(y)
            ax.set_zlabel(z)
            ax.set_title(f"{z} as surface of {x} and {y}")
        elif self.select_plot.value == "Wireframe Plot with interpolation":
            ax = self.currfig.add_subplot(111, projection='3d')
            self.plotting_data = self.plotting_data.sort_values(by=[x, y])
            xypoints = self.plotting_data[[x, y]].values
            zpoints = self.plotting_data[z].values
            grid_x, grid_y = np.meshgrid(
                np.linspace(
                    self.plotting_data[x].min(),
                    self.plotting_data[x].max(),
                    1000),
                np.linspace(
                    self.plotting_data[y].min(),
                    self.plotting_data[y].max(),
                    1000))
            grid_z = interpolate.griddata(
                xypoints, zpoints, (grid_x, grid_y),
                method=self.interpolation_method.value)
            ax.plot_wireframe(grid_x, grid_y, grid_z)
            ax.set_xlabel(x)
            ax.set_ylabel(y)
            ax.set_zlabel(z)
            ax.set_title(f"{z} as wireframe of {x} and {y}")
        elif self.select_plot.value == "Contour Plot without interpolation":
            ax = self.currfig.add_subplot(111)
            self.plotting_data = self.plotting_data.sort_values(by=[x, y])
            c = ax.tricontour(
                self.plotting_data[x],
                self.plotting_data[y],
                self.plotting_data[z])
            ax.clabel(c, inline=True)
            ax.set_xlabel(x)
            ax.set_ylabel(y)
            ax.set_title(f"{z} as contours of {x} and {y}")
        elif self.select_plot.value == "Contourf Plot without interpolation":
            ax = self.currfig.add_subplot(111)
            self.plotting_data = self.plotting_data.sort_values(by=[x, y])
            c = ax.tricontourf(
                self.plotting_data[x],
                self.plotting_data[y],
                self.plotting_data[z])
            cbar = self.currfig.colorbar(c)
            ax.set_xlabel(x)
            ax.set_ylabel(y)
            cbar.set_label(f"{z}", rotation=270)
            ax.set_title(f"{z} as contours of {x} and {y}")
        elif self.select_plot.value == "Contour Plot with interpolation":
            self.plotting_data = self.plotting_data.sort_values(by=[x, y])
            ax = self.currfig.add_subplot(111)
            xypoints = self.plotting_data[[x, y]].values
            zpoints = self.plotting_data[z].values
            grid_x, grid_y = np.meshgrid(
                np.linspace(
                    self.plotting_data[x].min(),
                    self.plotting_data[x].max(),
                    1000),
                np.linspace(
                    self.plotting_data[y].min(),
                    self.plotting_data[y].max(),
                    1000))
            grid_z = interpolate.griddata(
                xypoints, zpoints, (grid_x, grid_y),
                method=self.interpolation_method.value)
            c = ax.contour(grid_x, grid_y, grid_z)
            ax.clabel(c, inline=True)
            ax.set_xlabel(x)
            ax.set_ylabel(y)
            ax.set_title(f"{z} as contours of {x} and {y}")
        elif self.select_plot.value == "Contourf Plot with interpolation":
            self.plotting_data = self.plotting_data.sort_values(by=[x, y])
            ax = self.currfig.add_subplot(111)
            xypoints = self.plotting_data[[x, y]].values
            zpoints = self.plotting_data[z].values
            grid_x, grid_y = np.meshgrid(
                np.linspace(
                    self.plotting_data[x].min(),
                    self.plotting_data[x].max(),
                    1000),
                np.linspace(
                    self.plotting_data[y].min(),
                    self.plotting_data[y].max(),
                    1000))
            grid_z = interpolate.griddata(
                xypoints, zpoints, (grid_x, grid_y),
                method=self.interpolation_method.value)
            c = ax.contourf(grid_x, grid_y, grid_z)
            cbar = self.currfig.colorbar(c)
            ax.set_xlabel(x)
            ax.set_ylabel(y)
            cbar.set_label(f"{z}", rotation=270)
            ax.set_title(f"{z} as contours of {x} and {y}")

    def _generate_oneD_plot(self):
        self.oneD_plot_widgets = []
        self.oneD_plot_widgets.append(self._go_back_button(self.main_menu))
        self.oneD_plot_widgets.append(
            widgets.VBox(
                [
                    widgets.HTML(
                        value="<h3>1D Plot</h3>")],
                layout=widgets.Layout(
                    width='100%',
                    display='flex',
                    align_items='center')))
        self.select_plot_oneD = self._create_dropdown(
            "Type of Plot", [
                "Histogram",
                "Kernel Density Estimate",
                "Empirical Cumulative Distribution"])
        self.select_var = self._create_dropdown(
            "Select Variable", self.data.columns.tolist())
        self.oneD_hue_var = self._create_dropdown(
            "Select Hue (Optional)",
            ["None"] +
            self.cat_list_ordered +
            self._numerical_option +
            self.num_list_ordered)
        self.oneD_col_var = self._create_dropdown(
            "Select Columns (Optional)",
            ["None"] +
            self.cat_list_ordered +
            self._numerical_option +
            self.num_list_ordered)
        self.oneD_row_var = self._create_dropdown(
            "Select Rows (Optional)",
            ["None"] +
            self.cat_list_ordered +
            self._numerical_option +
            self.num_list_ordered)
        self.oneD_categorical_box = widgets.HBox([
            self.oneD_hue_var,
            self.oneD_col_var,
            self.oneD_row_var
        ])
        self.oneD_log_X = self._create_checkbox("Log X Axis", value=False)
        self.oneD_log_Y = self._create_checkbox("Log Y Axis", value=False)
        self.plot_button = self._create_button("Plot")
        self.plot_button.on_click(self._oneD_plotter)
        self.oneD_plot_widgets.extend(
            [
                self.select_plot_oneD,
                self.select_var,
                self.oneD_categorical_box,
                self.oneD_log_X,
                self.oneD_log_Y,
                self.plot_button])

    def _oneD_plot(self, b):
        self._clear_display()
        self._display(self.oneD_plot_widgets)

    def _oneD_plotter(self, b):
        hue = None
        col = None
        row = None
        element = "bars"
        if self.oneD_hue_var.value not in [
                "None", "<Numerical Columns below (may not work)>"]:
            hue = self.oneD_hue_var.value
            element = "step"

        if self.oneD_col_var.value not in [
                "None", "<Numerical Columns below (may not work)>"]:
            col = self.oneD_col_var.value

        if self.oneD_row_var.value not in [
                "None", "<Numerical Columns below (may not work)>"]:
            row = self.oneD_row_var.value

        self.plotting_data = self.active_data.copy()

        if hue in self.num_list_ordered:
            self.plotting_data[hue] = self.plotting_data[hue].astype(
                'category')
        try:
            if self.select_plot_oneD.value == "Histogram":
                self.currfig = sns.displot(
                    self.plotting_data,
                    x=self.select_var.value,
                    hue=hue,
                    element=element,
                    kind="hist",
                    log_scale=(
                        self.oneD_log_X.value,
                        self.oneD_log_Y.value),
                    row=row, col=col, palette=self.palette)
            elif self.select_plot_oneD.value == "Kernel Density Estimate":
                self.currfig = sns.displot(
                    self.plotting_data,
                    x=self.select_var.value,
                    hue=hue,
                    kind="kde",
                    log_scale=(
                        self.oneD_log_X.value,
                        self.oneD_log_Y.value),
                    row=row, col=col, palette=self.palette)
            elif (self.select_plot_oneD.value ==
                  "Empirical Cumulative Distribution"):
                self.currfig = sns.displot(
                    self.plotting_data,
                    x=self.select_var.value,
                    hue=hue,
                    kind="ecdf",
                    log_scale=(
                        self.oneD_log_X.value,
                        self.oneD_log_Y.value),
                    row=row, col=col, palette=self.palette)
        except Exception as e:
            self.err_msg(
                "Check your selected variables. "
                "Also ensure you don't use Log X/Y-axis "
                "if there are 0 values in your column")
            self.err_msg(e)
        plt.get_current_fig_manager().window.showMaximized()
        plt.gcf().set_layout_engine("tight")

    def _get_valid_path(self, name, filetype):
        num = 0
        path = Path.cwd() / f"{name}{filetype}"
        while path.exists():
            num += 1
            path = Path.cwd() / f"{name}_{num}{filetype}"
        return path

    def _export_table(self, b):
        path = self._get_valid_path("Table", ".xlsx")
        self.active_data.to_excel(path)
        showinfo(
            "Table Exported",
            f"Plot has been successfully exported as\n{path}")

    def _generate_twoD_plot(self):
        self.twoD_plot_widgets = []
        self.twoD_plot_widgets.append(self._go_back_button(self.main_menu))
        self.twoD_plot_widgets.append(
            widgets.VBox(
                [
                    widgets.HTML(
                        value="<h3>2D Plotting</h3>")],
                layout=widgets.Layout(
                    width='100%',
                    display='flex',
                    align_items='center')))
        self.twoD_plot_dropdown = self._create_dropdown(
            "Type of Plot", [
                "Scatter Plots", "Line Plots",
                "Regression Plots", "Categorical Plots",
                "2D Histograms", "Scatter Plot with Colorbar"])
        self.twoD_plot_widgets.extend(
            [self.twoD_plot_dropdown, self._create_button("Select Plot Type")])
        self.twoD_plot_widgets[-1].on_click(self._twoD_plotter)

    def _twoD_plot(self, b):
        self._clear_display()
        self._display(self.twoD_plot_widgets)

    def _twoD_plotter(self, b):
        if self.twoD_plot_dropdown.value == "Scatter Plots":
            self._twoD_scatter_plot()
        elif self.twoD_plot_dropdown.value == "Line Plots":
            self._twoD_line_plot()
        elif self.twoD_plot_dropdown.value == "Regression Plots":
            self._twoD_regression_plot()
        elif self.twoD_plot_dropdown.value == "Categorical Plots":
            self._twoD_categorical_plot()
        elif self.twoD_plot_dropdown.value == "2D Histograms":
            self._twoD_histogram()
        elif self.twoD_plot_dropdown.value == "Scatter Plot with Colorbar":
            self._twoD_scatter_colorbar()

    def _generate_twoD_scatter_colorbar(self):
        self.twoD_scatter_colorbar_widgets = []
        self.twoD_scatter_colorbar_widgets.append(
            self._go_back_button(self._twoD_plot))
        self.twoD_scatter_colorbar_widgets.append(
            widgets.VBox(
                [
                    widgets.HTML(
                        value="<h3>2D Scatter Plot with Colorbar</h3>")],
                layout=widgets.Layout(
                    width='100%',
                    display='flex',
                    align_items='center')))
        self.twoD_scatter_colorbar_x = self._create_dropdown(
            "X Variable", self.data.columns.tolist())
        self.twoD_scatter_colorbar_y = self._create_dropdown(
            "Y Variable", self.data.columns.tolist())
        self.twoD_scatter_colorbar_c = self._create_dropdown(
            "Color Variable", self.data.columns.tolist())
        self.twoD_scatter_colorbar_grid = widgets.GridspecLayout(1, 2)
        self.twoD_scatter_colorbar_grid[0, 0] = self.twoD_scatter_colorbar_x
        self.twoD_scatter_colorbar_grid[0, 1] = self.twoD_scatter_colorbar_y
        self.twoD_scatter_colorbar_widgets.extend(
            [self.twoD_scatter_colorbar_grid,
             self.twoD_scatter_colorbar_c])
        self.twoD_scatter_colorbar_plot_button = self._create_button("Plot")
        self.twoD_scatter_colorbar_plot_button.on_click(
            self._twoD_scatter_colorbar_plotter)
        self.twoD_scatter_colorbar_widgets.append(
            self.twoD_scatter_colorbar_plot_button)

    def _twoD_scatter_colorbar(self):
        self._clear_display()
        self._display(self.twoD_scatter_colorbar_widgets)

    def _twoD_scatter_colorbar_plotter(self, b):
        self.currfig = plt.figure()
        try:
            scatter = plt.scatter(
                self.active_data[self.twoD_scatter_colorbar_x.value],
                self.active_data[self.twoD_scatter_colorbar_y.value],
                c=self.active_data[self.twoD_scatter_colorbar_c.value])
            plt.colorbar(scatter, label=self.twoD_scatter_colorbar_c.value)
            plt.xlabel(self.twoD_scatter_colorbar_x.value)
            plt.ylabel(self.twoD_scatter_colorbar_y.value)
            plt.title(
                f"{self.twoD_scatter_colorbar_y.value} vs "
                f"{self.twoD_scatter_colorbar_x.value} vs "
                f"{self.twoD_scatter_colorbar_c.value}")
        except Exception as e:
            self.err_msg("Unable to plot. Check selected variables.")
            self.err_msg(f"Error: {e}")
            self.err_msg(traceback.format_exc())
        plt.get_current_fig_manager().window.showMaximized()
        plt.gcf().set_layout_engine("tight")

    def _generate_twoD_histogram(self):
        self.twoD_histogram_widgets = []
        self.twoD_histogram_widgets.append(
            self._go_back_button(self._twoD_plot))
        self.twoD_histogram_widgets.append(
            widgets.VBox(
                [
                    widgets.HTML(
                        value="<h3>2D Histogram</h3>")],
                layout=widgets.Layout(
                    width='100%',
                    display='flex',
                    align_items='center')))
        self.twoD_histogram_x = self._create_dropdown(
            "X Variable", self.data.columns.tolist())
        self.twoD_histogram_y = self._create_dropdown(
            "Y Variable", self.data.columns.tolist())
        self.twoD_histogram_type = self._create_dropdown(
            "Type of Plot", ["Square", "Hexagonal"])
        self.twoD_histogram_grid = widgets.GridspecLayout(1, 2)
        self.twoD_histogram_grid[0, 0] = self.twoD_histogram_x
        self.twoD_histogram_grid[0, 1] = self.twoD_histogram_y
        self.twoD_histogram_log_X = self._create_checkbox(
            "Log X Axis", value=False)
        self.twoD_histogram_log_Y = self._create_checkbox(
            "Log Y Axis", value=False)
        self.twoD_histogram_widgets.extend(
            [self.twoD_histogram_type,
             self.twoD_histogram_grid,
             self.twoD_histogram_log_X,
             self.twoD_histogram_log_Y])
        self.twoD_histogram_plot_button = self._create_button("Plot")
        self.twoD_histogram_plot_button.on_click(self._twoD_histogram_plotter)
        self.twoD_histogram_widgets.append(self.twoD_histogram_plot_button)

    def _twoD_histogram(self):
        self._clear_display()
        self._display(self.twoD_histogram_widgets)

    def _twoD_histogram_plotter(self, b):
        self.currfig = plt.figure()
        try:
            if self.twoD_histogram_type.value == "Square":
                hst = plt.hist2d(
                    self.active_data[self.twoD_histogram_x.value],
                    self.active_data[self.twoD_histogram_y.value],
                    cmap='Blues')
                self.currfig.colorbar(hst[3], ax=plt.gca(), label='count')
            elif self.twoD_histogram_type.value == "Hexagonal":
                hb = plt.hexbin(
                    self.active_data[self.twoD_histogram_x.value],
                    self.active_data[self.twoD_histogram_y.value],
                    gridsize=(int(self.active_data.shape[0] / 20)
                              if self.active_data.shape[0] > 100 else 10),
                    cmap='inferno')
                self.currfig.colorbar(hb, ax=plt.gca(), label='count')
            plt.ylabel(self.twoD_histogram_y.value)
            plt.xlabel(self.twoD_histogram_x.value)
            if self.twoD_histogram_log_X.value:
                plt.gca().set_xscale('log')
            if self.twoD_histogram_log_Y.value:
                plt.gca().set_yscale('log')
            plt.title(
                f"Histogram of {self.twoD_histogram_x.value} and "
                f"{self.twoD_histogram_y.value}")
        except Exception as e:
            self.err_msg(
                "Check your selected variables. "
                "Also ensure you don't use Log X/Y-axis "
                "if there are 0 values in your column")
            self.err_msg(e)
        plt.get_current_fig_manager().window.showMaximized()

    def _generate_twoD_scatter_plot(self):
        self.twoD_scatter_plot_widgets = []
        self.twoD_scatter_plot_widgets.append(
            self._go_back_button(self._twoD_plot))
        self.twoD_scatter_plot_widgets.append(
            widgets.VBox(
                [
                    widgets.HTML(
                        value="<h3>Scatter Plot</h3>")],
                layout=widgets.Layout(
                    width='100%',
                    display='flex',
                    align_items='center')))
        self.twoD_scatter_plot_x = self._create_dropdown(
            "X Variable", self.data.columns.tolist())
        self.twoD_scatter_plot_y = self._create_multi_select(
            "Y Variable", self.data.columns.tolist(),
            height=f'{self.height_of_box}px')
        self.twoD_scatter_grid_1 = widgets.GridspecLayout(1, 2)
        self.twoD_scatter_grid_1[0, 0] = self.twoD_scatter_plot_x
        self.twoD_scatter_grid_1[0, 1] = self.twoD_scatter_plot_y
        self.twoD_scatter_plot_multi_y = self._create_dropdown(
            "How do I handle multiple Y-variables?", self.twoD_multi_y_options)
        self.twoD_scatter_plot_hue = self._create_dropdown(
            "Hue (Optional)",
            ["None"] +
            self.cat_list_ordered +
            self._numerical_option +
            self.num_list_ordered)
        self.twoD_scatter_plot_style = self._create_dropdown(
            "Style (Optional)",
            ["None"] +
            self.cat_list_ordered +
            self._numerical_option +
            self.num_list_ordered
        )
        self.twoD_scatter_plot_col = self._create_dropdown(
            "Column (Optional) (Only works with one Y var)",
            ["None"] +
            self.cat_list_ordered +
            self._numerical_option +
            self.num_list_ordered)
        self.twoD_scatter_plot_row = self._create_dropdown(
            "Row (Optional) (Only works with one Y var)",
            ["None"] + self.cat_list_ordered +
            self._numerical_option + self.num_list_ordered)
        self.twoD_scatter_log_X = self._create_checkbox(
            "Log X Axis", value=False)
        self.twoD_scatter_log_Y = self._create_checkbox(
            "Log Y Axis", value=False)
        self.twoD_scatter_plot_categorical_box = widgets.GridspecLayout(2, 1)
        self.twoD_scatter_plot_categorical_box[0, 0] = widgets.HBox([
            self.twoD_scatter_plot_hue,
            self.twoD_scatter_plot_style
        ])
        self.twoD_scatter_plot_categorical_box[1, 0] = widgets.HBox([
            self.twoD_scatter_plot_col,
            self.twoD_scatter_plot_row
        ])

        self.twoD_scatter_plot_widgets.extend(
            [self.twoD_scatter_grid_1,
             self.twoD_scatter_plot_categorical_box,
             self.twoD_scatter_plot_multi_y,
             self.twoD_scatter_log_X,
             self.twoD_scatter_log_Y]
        )
        self.twoD_scatter_plot_widgets.append(self._create_button("Plot"))
        self.twoD_scatter_plot_widgets[-1].on_click(self._twoD_scatter_plotter)

    def _twoD_scatter_plot(self, b=None):
        self._clear_display()
        self._display(self.twoD_scatter_plot_widgets)

    def _twoD_scatter_plotter(self, b):

        hue = None
        col = None
        row = None
        style = None
        if self.twoD_scatter_plot_hue.value not in [
                "None", "<Numerical Columns below (may not work)>"]:
            hue = self.twoD_scatter_plot_hue.value

        if self.twoD_scatter_plot_col.value not in [
                "None", "<Numerical Columns below (may not work)>"]:
            col = self.twoD_scatter_plot_col.value
        if self.twoD_scatter_plot_row.value not in [
                "None", "<Numerical Columns below (may not work)>"]:
            row = self.twoD_scatter_plot_row.value
        if self.twoD_scatter_plot_style.value not in [
                "None", "<Numerical Columns below (may not work)>"]:
            style = self.twoD_scatter_plot_style.value

        if len(self.twoD_scatter_plot_y.value) < 1:
            self.err_msg("Please select at least one Y-variable")
        elif len(self.twoD_scatter_plot_y.value) == 1:
            try:
                self.currfig = sns.relplot(
                    self.active_data,
                    x=self.twoD_scatter_plot_x.value,
                    y=self.twoD_scatter_plot_y.value[0],
                    hue=hue,
                    col=col, style=style, row=row, palette=self.palette)
                plt.get_current_fig_manager().window.showMaximized()
                plt.gcf().set_layout_engine("tight")
                if self.twoD_scatter_log_X.value:
                    self.currfig.set(xscale="log")
                if self.twoD_scatter_log_Y.value:
                    self.currfig.set(yscale="log")
                if col is None and row is None:
                    plt.title(
                        f"Scatter Plot of {self.twoD_scatter_plot_x.value} "
                        f"vs {self.twoD_scatter_plot_y.value[0]}")

            except Exception as e:
                self.err_msg("Unable to plot. Check selected variables.")
                self.err_msg(f"Error: {e}")
                self.err_msg(traceback.format_exc())
        else:
            if self.twoD_scatter_plot_multi_y.value == "Subplots":
                try:
                    self.currfig, axes = plt.subplots(
                        int(np.ceil(len(self.twoD_scatter_plot_y.value) / 2)),
                        2)
                    axes = axes.flatten()
                    for y, ax in zip(self.twoD_scatter_plot_y.value, axes):
                        plt.sca(ax)
                        sns.scatterplot(
                            self.active_data,
                            x=self.twoD_scatter_plot_x.value,
                            y=y,
                            hue=hue, style=style, palette=self.palette)
                        if self.twoD_scatter_log_Y.value:
                            plt.gca().set_yscale('log')
                        if self.twoD_scatter_log_X.value:
                            plt.gca().set_xscale('log')
                        plt.title(
                            f"Scatter Plot of {self.twoD_scatter_plot_x.value}"
                            f" vs {y}")

                except Exception as e:
                    self.err_msg("Unable to plot. Check selected variables.")
                    self.err_msg(f"Error: {e}")
                    self.err_msg(traceback.format_exc())
            elif (self.twoD_scatter_plot_multi_y.value ==
                  "Single overlaid plot w/ single y-axis"):
                try:
                    self.currfig = plt.figure()
                    plt.get_current_fig_manager().window.showMaximized()
                    plt.gcf().set_layout_engine("tight")
                    for y in self.twoD_scatter_plot_y.value:
                        sns.scatterplot(
                            self.active_data,
                            x=self.twoD_scatter_plot_x.value,
                            y=y,
                            style=style)
                    if self.twoD_scatter_log_Y.value:
                        plt.gca().set_yscale('log')
                    if self.twoD_scatter_log_X.value:
                        plt.gca().set_xscale('log')
                    plt.title(
                        f"Scatter Plot of {self.twoD_scatter_plot_x.value} "
                        f"vs {', '.join(self.twoD_scatter_plot_y.value)}")
                    plt.legend(self.twoD_scatter_plot_y.value)

                except Exception as e:
                    self.err_msg("Unable to plot. Check selected variables.")
                    self.err_msg(f"Error: {e}")
                    self.err_msg(traceback.format_exc())
            elif (self.twoD_scatter_plot_multi_y.value ==
                  "Single overlaid plot w/ up to 4 y-axes"):
                try:
                    if len(self.twoD_scatter_plot_y.value) > 4:
                        self.err_msg(
                            "Can only handle up to 4 y-variables "
                            "with this option")
                        raise ValueError("Can only handle up to 4 y-variables "
                                         "with this option")
                    self.currfig, ax = plt.subplots()
                    if len(self.twoD_scatter_plot_y.value) > 2:
                        self.currfig.subplots_adjust(right=0.8)
                    plt.get_current_fig_manager().window.showMaximized()
                    loc_array = [0, 0, 1.1, 1.2]
                    colors = ["black", "red", "green", "magenta"]
                    axes = [ax]
                    for i in range(len(self.twoD_scatter_plot_y.value) - 1):
                        twin = ax.twinx()
                        axes.append(twin)
                    for i, (y, ax) in enumerate(
                            zip(self.twoD_scatter_plot_y.value, axes)):
                        plt.sca(ax)
                        if loc_array[i] != 0:
                            ax.spines\
                                .right.set_position(('axes',
                                                     loc_array[i]))
                        sns.scatterplot(
                            self.active_data,
                            x=self.twoD_scatter_plot_x.value,
                            y=y,
                            color=colors[i], style=style)
                        if self.twoD_scatter_log_Y.value:
                            plt.gca().set_yscale('log')
                        if self.twoD_scatter_log_X.value:
                            plt.gca().set_xscale('log')
                        ax.set(ylabel=y)
                        ax.tick_params(axis='y', colors=colors[i])
                        ax.yaxis.label.set_color(colors[i])
                    plt.title(
                        f"Scatter Plot of "
                        f"{', '.join(self.twoD_scatter_plot_y.value)} "
                        f"vs {self.twoD_scatter_plot_x.value}")
                except Exception as e:
                    self.err_msg("Unable to plot. Check selected variables.")
                    self.err_msg(f"Error: {e}")
                    self.err_msg(traceback.format_exc())

    def _twoD_line_plot(self, b=None):
        self._clear_display()
        self._display(self.twoD_line_plot_widgets)

    def _generate_twoD_line_plot(self):
        self.twoD_line_plot_widgets = []
        self.twoD_line_plot_widgets.append(
            self._go_back_button(self._twoD_plot))
        self.twoD_line_plot_widgets.append(
            widgets.VBox(
                [
                    widgets.HTML(
                        value="<h3>Line Plot</h3>")],
                layout=widgets.Layout(
                    width='100%',
                    display='flex',
                    align_items='center')))
        self.twoD_line_plot_x = self._create_dropdown(
            "X Variable", self.data.columns.tolist())
        self.twoD_line_plot_y = self._create_multi_select(
            "Y Variable", self.data.columns.tolist(),
            height=f'{self.height_of_box}px')
        self.twoD_line_grid_1 = widgets.GridspecLayout(1, 2)
        self.twoD_line_grid_1[0, 0] = self.twoD_line_plot_x
        self.twoD_line_grid_1[0, 1] = self.twoD_line_plot_y
        self.twoD_line_plot_hue = self._create_dropdown(
            "Hue (Optional)",
            ["None"] +
            self.cat_list_ordered +
            self._numerical_option +
            self.num_list_ordered)
        self.twoD_line_plot_style = self._create_dropdown(
            "Style (Optional)",
            ["None"] +
            self.cat_list_ordered +
            self._numerical_option +
            self.num_list_ordered)
        self.twoD_line_plot_col = self._create_dropdown(
            "Columns (Optional) (Only works with one Y var)",
            ["None"] +
            self.cat_list_ordered +
            self._numerical_option +
            self.num_list_ordered)
        self.twoD_line_plot_row = self._create_dropdown(
            "Row (Optional) (Only works with one Y var)",
            ["None"] + self.cat_list_ordered +
            self._numerical_option + self.num_list_ordered)
        self.twoD_line_plot_multi_y = self._create_dropdown(
            "How do I handle multiple Y-variables?", self.twoD_multi_y_options)
        self.twoD_line_log_X = self._create_checkbox("Log X Axis", value=False)
        self.twoD_line_log_Y = self._create_checkbox("Log Y Axis", value=False)
        self.twod_line_plot_categorical_box = widgets.GridspecLayout(2, 1)
        self.twod_line_plot_categorical_box[0, 0] = widgets.HBox([
            self.twoD_line_plot_hue,
            self.twoD_line_plot_style
        ])
        self.twod_line_plot_categorical_box[1, 0] = widgets.HBox([
            self.twoD_line_plot_col,
            self.twoD_line_plot_row
        ])
        self.twoD_line_plot_widgets.extend(
            [self.twoD_line_grid_1,
             self.twod_line_plot_categorical_box,
             self.twoD_line_plot_multi_y,
             self.twoD_line_log_X,
             self.twoD_line_log_Y]
        )
        self.twoD_line_plot_widgets.append(self._create_button("Plot"))
        self.twoD_line_plot_widgets[-1].on_click(self._twoD_line_plotter)

    def _twoD_line_plotter(self, b):

        hue = None
        col = None
        row = None
        style = None
        if self.twoD_line_plot_hue.value not in [
                "None", "<Numerical Columns below (may not work)>"]:
            hue = self.twoD_line_plot_hue.value

        if self.twoD_line_plot_col.value not in [
                "None", "<Numerical Columns below (may not work)>"]:
            col = self.twoD_line_plot_col.value
        if self.twoD_line_plot_row.value not in [
                "None", "<Numerical Columns below (may not work)>"]:
            row = self.twoD_line_plot_row.value
        if self.twoD_line_plot_style.value not in [
                "None", "<Numerical Columns below (may not work)>"]:
            style = self.twoD_line_plot_style.value
        if len(self.twoD_line_plot_y.value) < 1:
            self.err_msg("Please select at least one Y-variable")
        elif len(self.twoD_line_plot_y.value) == 1:
            try:
                self.currfig = sns.relplot(
                    self.active_data,
                    x=self.twoD_line_plot_x.value,
                    y=self.twoD_line_plot_y.value[0],
                    kind="line",
                    hue=hue,
                    col=col, row=row, style=style, palette=self.palette)
                plt.get_current_fig_manager().window.showMaximized()
                plt.gcf().set_layout_engine("tight")
                if self.twoD_line_log_X.value:
                    self.currfig.set(xscale="log")
                if self.twoD_line_log_Y.value:
                    self.currfig.set(yscale="log")

            except Exception as e:
                self.err_msg("Unable to plot. Check selected variables.")
                self.err_msg(f"Error: {e}")
        else:
            if self.twoD_line_plot_multi_y.value == "Subplots":
                try:
                    self.currfig, axes = plt.subplots(
                        int(np.ceil(len(self.twoD_line_plot_y.value) / 2)), 2)
                    axes = axes.flatten()
                    for y, ax in zip(self.twoD_line_plot_y.value, axes):
                        plt.sca(ax)
                        sns.lineplot(
                            self.active_data,
                            x=self.twoD_line_plot_x.value,
                            y=y,
                            hue=hue, style=style, palette=self.palette)
                        if self.twoD_line_log_Y.value:
                            plt.gca().set_yscale('log')
                        if self.twoD_line_log_X.value:
                            plt.gca().set_xscale('log')
                        plt.title(
                            f"Line Plot of {self.twoD_line_plot_x.value} "
                            f"vs {y}")

                except Exception as e:
                    self.err_msg("Unable to plot. Check selected variables.")
                    self.err_msg(f"Error: {e}")
                    self.err_msg(traceback.format_exc())
            elif (self.twoD_line_plot_multi_y.value ==
                  "Single overlaid plot w/ single y-axis"):
                try:
                    self.currfig = plt.figure()
                    plt.get_current_fig_manager().window.showMaximized()
                    plt.gcf().set_layout_engine("tight")
                    for y in self.twoD_line_plot_y.value:
                        sns.lineplot(
                            self.active_data,
                            x=self.twoD_line_plot_x.value,
                            y=y,
                            style=style)
                    if self.twoD_line_log_Y.value:
                        plt.gca().set_yscale('log')
                    if self.twoD_line_log_X.value:
                        plt.gca().set_xscale('log')
                    plt.title(
                        f"Line Plot of "
                        f"{', '.join(self.twoD_line_plot_y.value)} "
                        f"vs {self.twoD_line_plot_x.value}")
                    plt.legend(self.twoD_line_plot_y.value)

                except Exception as e:
                    self.err_msg("Unable to plot. Check selected variables.")
                    self.err_msg(f"Error: {e}")
                    self.err_msg(traceback.format_exc())
            elif (self.twoD_line_plot_multi_y.value ==
                  "Single overlaid plot w/ up to 4 y-axes"):
                try:
                    if len(self.twoD_line_plot_y.value) > 4:
                        self.err_msg(
                            "Can only handle up to 4 y-variables "
                            "with this option")
                        raise ValueError("Can only handle up to 4 y-variables "
                                         "with this option")
                    self.currfig, ax = plt.subplots()
                    if len(self.twoD_line_plot_y.value) > 2:
                        self.currfig.subplots_adjust(right=0.8)
                    plt.get_current_fig_manager().window.showMaximized()
                    loc_array = [0, 0, 1.1, 1.2]
                    colors = ["black", "red", "green", "magenta"]
                    axes = [ax]
                    for i in range(len(self.twoD_line_plot_y.value) - 1):
                        twin = ax.twinx()
                        axes.append(twin)
                    for i, (y, ax) in enumerate(
                            zip(self.twoD_line_plot_y.value, axes)):
                        plt.sca(ax)
                        if loc_array[i] != 0:
                            ax.spines\
                                .right.set_position(('axes',
                                                     loc_array[i]))
                        sns.lineplot(
                            self.active_data,
                            x=self.twoD_line_plot_x.value,
                            y=y,
                            color=colors[i], style=style)
                        if self.twoD_line_log_Y.value:
                            plt.gca().set_yscale('log')
                        if self.twoD_line_log_X.value:
                            plt.gca().set_xscale('log')
                        ax.set(ylabel=y)
                        ax.tick_params(axis='y', colors=colors[i])
                        ax.yaxis.label.set_color(colors[i])
                    plt.title(
                        f"Line Plot of "
                        f"{', '.join(self.twoD_line_plot_y.value)} "
                        f"vs {self.twoD_line_plot_x.value}")
                except Exception as e:
                    self.err_msg("Unable to plot. Check selected variables.")
                    self.err_msg(f"Error: {e}")
                    self.err_msg(traceback.format_exc())

    def _generate_twoD_regression_plot(self):
        self.twoD_regression_plot_widgets = []
        self.twoD_regression_plot_widgets.append(
            self._go_back_button(self._twoD_plot))
        self.twoD_regression_plot_widgets.append(
            widgets.VBox(
                [
                    widgets.HTML(
                        value="<h3>Regression Plot</h3>")],
                layout=widgets.Layout(
                    width='100%',
                    display='flex',
                    align_items='center')))
        self.twoD_regression_plot_x = self._create_dropdown(
            "X Variable", self.num_list_ordered)
        self.twoD_regression_plot_y = self._create_dropdown(
            "Y Variable", self.num_list_ordered)
        self.twoD_regression_plot_options = self._create_dropdown(
            "Order of regression?", [1, 2, 3, 4, 5])
        self.twoD_regression_plot_grid = widgets.GridspecLayout(2, 2)
        self.twoD_regression_plot_grid[0, 0] = self.twoD_regression_plot_x
        self.twoD_regression_plot_grid[0, 1] = self.twoD_regression_plot_y
        self.twoD_regression_plot_grid[1,
                                       0] = self.twoD_regression_plot_options
        self.twoD_regression_plot_widgets.extend(
            [self.twoD_regression_plot_grid])
        self.twoD_regression_plot_widgets.append(self._create_button("Plot"))
        self.twoD_regression_plot_widgets[-1].on_click(
            self._twoD_regression_plotter)

    def _twoD_regression_plot(self, b=None):
        self._clear_display()
        self._display(self.twoD_regression_plot_widgets)

    def _twoD_regression_plotter(self, b):
        try:
            model = np.polyfit(
                self.active_data[self.twoD_regression_plot_x.value],
                self.active_data[self.twoD_regression_plot_y.value],
                self.twoD_regression_plot_options.value)
            self.currfig = plt.figure()
            plt.get_current_fig_manager().window.showMaximized()
            plt.gcf().set_layout_engine("tight")
            plt.scatter(self.active_data[self.twoD_regression_plot_x.value],
                        self.active_data[self.twoD_regression_plot_y.value])
            x = np.linspace(
                self.active_data[self.twoD_regression_plot_x.value].min(),
                self.active_data[self.twoD_regression_plot_x.value].max(), 100)
            y = np.polyval(model, x)
            y_hat = np.polyval(
                model, self.active_data[self.twoD_regression_plot_x.value])
            ssr = np.sum(
                (y_hat -
                 self.active_data[self.twoD_regression_plot_y.value])
                ** 2)
            sst = np.sum(
                (self.active_data[self.twoD_regression_plot_y.value] -
                 self.active_data[self.twoD_regression_plot_y.value].mean())
                ** 2)
            plt.plot(x, y)
            plt.title(
                f"Regression Plot of {self.twoD_regression_plot_x.value} "
                f"vs {self.twoD_regression_plot_y.value} "
                f"of order {self.twoD_regression_plot_options.value}")
            model = [
                f"{np.format_float_scientific(i, precision=4)}*x^{j}"
                for j, i in enumerate(model[::-1])]
            plt.legend(
                ["Data Points", f"Regression Model: {' + '.join(model)}"],
                loc="best")
            plt.xlabel(self.twoD_regression_plot_x.value)
            plt.ylabel(self.twoD_regression_plot_y.value)
            self._display([widgets.HTML(
                value=f"<p>Regression Model: {' + '.join(model)} "
                ", R squared: "
                f"{np.format_float_positional((1-ssr/sst), precision=3) } "
                "</p>")])
        except Exception as e:
            self.err_msg("Unable to plot. Check selected variables.")
            self.err_msg(f"Error: {e}")

    def _twoD_categorical_plot(self, b=None):
        self._clear_display()
        self._display(self.twoD_categorical_plot_widgets)

    def _generate_twoD_categorical_plot(self):
        self.twoD_categorical_plot_widgets = []
        self.twoD_categorical_plot_widgets.append(
            self._go_back_button(self._twoD_plot))
        self.twoD_categorical_plot_widgets.append(
            widgets.VBox(
                [
                    widgets.HTML(
                        value="<h3>Categorical</h3>")],
                layout=widgets.Layout(
                    width='100%',
                    display='flex',
                    align_items='center')))
        self.twoD_categorical_plot_x = self._create_dropdown(
            "X Variable", self.num_list_ordered)
        self.twoD_categorical_plot_y = self._create_dropdown(
            "Y Variable",
            ["None"] +
            self.cat_list_ordered +
            self._numerical_option +
            self.num_list_ordered)
        self.twoD_categorical_plot_hue = self._create_dropdown(
            "Hue (Optional)",
            ["None"] +
            self.cat_list_ordered +
            self._numerical_option +
            self.num_list_ordered)
        self.twoD_cateogrical_plot_type = self._create_dropdown(
            "Type of plot", [
                "Strip", "Swarm", "Box", "Violin",
                "Boxen", "Point", "Bar", "Count"])
        self.twoD_categorical_plot_grid = widgets.GridspecLayout(2, 2)
        self.twoD_categorical_plot_grid[0, 0] = self.twoD_categorical_plot_x
        self.twoD_categorical_plot_grid[0, 1] = self.twoD_categorical_plot_y
        self.twoD_categorical_plot_grid[1, 0] = self.twoD_categorical_plot_hue
        self.twoD_categorical_plot_grid[1, 1] = self.twoD_cateogrical_plot_type
        self.twoD_categorical_plot_col = self._create_dropdown(
            "Columns (Optional)",
            ["None"] +
            self.cat_list_ordered +
            self._numerical_option +
            self.num_list_ordered)
        self.twoD_categorical_plot_row = self._create_dropdown(
            "Rows (Optional)",
            ["None"] +
            self.cat_list_ordered +
            self._numerical_option +
            self.num_list_ordered)
        self.twoD_categorical_plot_rowcolbox = widgets.HBox(
            [self.twoD_categorical_plot_col, self.twoD_categorical_plot_row])
        self.twoD_categorical_plot_log_X = self._create_checkbox(
            "Log X Axis", value=False)
        self.twoD_categorical_plot_log_Y = self._create_checkbox(
            "Log Y Axis", value=False)
        self.twoD_categorical_plot_widgets.extend(
            [
                self.twoD_categorical_plot_grid,
                self.twoD_categorical_plot_rowcolbox,
                self.twoD_categorical_plot_log_X,
                self.twoD_categorical_plot_log_Y])
        self.twoD_categorical_plot_widgets.append(self._create_button("Plot"))
        self.twoD_categorical_plot_widgets[-1].on_click(
            self._twoD_categorical_plotter)

    def _twoD_categorical_plotter(self, b):
        y = None
        hue = None
        row = None
        col = None
        if self.twoD_categorical_plot_row.value not in [
                "None", "<Numerical Columns below (may not work)>"]:
            row = self.twoD_categorical_plot_row.value
        if self.twoD_categorical_plot_col.value not in [
                "None", "<Numerical Columns below (may not work)>"]:
            col = self.twoD_categorical_plot_col.value
        if self.twoD_categorical_plot_hue.value not in [
                "None", "<Numerical Columns below (may not work)>"]:
            hue = self.twoD_categorical_plot_hue.value
        if self.twoD_categorical_plot_y.value not in [
                "<Numerical Columns below (may not work)>", "None"]:
            y = self.twoD_categorical_plot_y.value

        self.plotting_data = self.active_data.copy()

        if y in self.num_list_ordered:
            self.plotting_data[y] = self.plotting_data[y].astype('category')
        if hue in self.num_list_ordered:
            self.plotting_data[hue] = self.plotting_data[hue].astype(
                'category')
        try:
            self.currfig = sns.catplot(
                self.plotting_data,
                x=self.twoD_categorical_plot_x.value,
                y=y,
                hue=hue,
                kind=self.twoD_cateogrical_plot_type.value.lower(),
                row=row,
                col=col, palette=self.palette)
            plt.get_current_fig_manager().window.showMaximized()
            plt.gcf().set_layout_engine("tight")
            if self.twoD_categorical_plot_log_X.value:
                self.currfig.set(xscale="log")
            if self.twoD_categorical_plot_log_Y.value:
                self.currfig.set(yscale="log")

        except Exception as e:
            self.err_msg("Unable to plot. Check selected variables.")
            self.err_msg(f"Error: {e}")
            self.err_msg(traceback.format_exc())

    def _generate_corr_plot(self):
        self.corr_plot_widgets = []
        self.corr_plot_widgets.append(self._go_back_button(self.main_menu))
        self.corr_plot_widgets.append(
            widgets.VBox(
                [
                    widgets.HTML(
                        value="<h3>Correlation Plot</h3>")],
                layout=widgets.Layout(
                    width='100%',
                    display='justify_content',
                    align_items='center')))
        self.multi_select = self._create_multi_select(
            "Variables", self.data.columns.tolist(),
            height=f'{self.height_of_box}px')
        self.corr_plot_widgets.append(self.multi_select)
        self.corr_plot_widgets.append(
            self._create_button(
                "Plot", style='success'))
        self.corr_plot_widgets[-1].on_click(self._corr_plotter)

    def _corr_plot(self, b):
        self._clear_display()
        self._display(self.corr_plot_widgets)

    def _corr_plotter(self, b):
        if len(self.multi_select.value) < 2:
            self._display(
                [widgets.HTML("<p>Please select at least two variables</p>")])
        else:
            try:
                self.currfig = plt.figure()
                sns.heatmap(self.active_data[list(
                    self.multi_select.value)].corr())
                plt.get_current_fig_manager().window.showMaximized()
                plt.gcf().set_layout_engine("tight")

                plt.show()
            except BaseException:
                self._display([widgets.HTML(
                    "<p>Unable to plot chosen variables.\n"
                    "Please ensure you only chose numerical variables.</p>")])

    def _create_checkbox(self, description, value=False):
        return widgets.Checkbox(
            description=description,
            value=value,
            disabled=False,
            indent=False)

    def _main_menu_button(self):
        self.main_menu_button = self._create_button("Main Menu", style='info')
        self.main_menu_button.on_click(self.main_menu)
        self._display([self.main_menu_button])

    def _go_back_button(self, func, description="Go Back"):
        self.back_button = self._create_button(description, style='info')
        self.back_button.on_click(func)
        return self.back_button

    def _display(self, widgets_in):
        for widget in widgets_in:
            if widget not in self.widgets:
                self.widgets.append(widget)
            else:
                if isinstance(widget, widgets.GridspecLayout):
                    widget.layout.display = 'grid'
                elif isinstance(widget, widgets.VBox):
                    widget.layout.display = 'flex'
                    widget.layout.width = 'auto'
                    widget.layout.align_items = 'center'
                elif isinstance(widget, widgets.Button):
                    widget.layout.display = 'flex'
                    widget.layout.width = 'auto'
                    widget.layout.height = 'auto'
                elif isinstance(widget, widgets.SelectMultiple):
                    widget.layout.display = 'flex'
                    widget.layout.width = '400px'
                    widget.layout.height = f'{self.height_of_box}px'
                elif isinstance(widget, widgets.Dropdown):
                    widget.layout.display = 'flex'
                    widget.layout.width = '400px'
                else:
                    widget.layout.display = 'flex'
                    widget.layout.width = 'auto'
                    widget.layout.height = 'auto'
                continue
            self.output.append_display_data(widget)

    def _display_output(self):
        display(self.output)  # type: ignore

    def _clear_display(self):
        for widget in self.widgets:
            widget.layout.display = 'none'

    def _create_slider(self, column_name):
        return widgets.FloatRangeSlider(
            description=column_name,
            value=(
                self.data[column_name].min(),
                self.data[column_name].max()),
            min=self.data[column_name].min(),
            max=self.data[column_name].max(),
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            layout=widgets.Layout(
                width='500px'),
            style={
                'description_width': 'initial'})

    def _create_dropdown(self, description, options):
        return widgets.Dropdown(description=description,
                                options=options,
                                value=options[0],
                                disabled=False,
                                layout=widgets.Layout(width='400px'),
                                style={'description_width': 'initial'})

    def _create_button(self, description, disabled=False, style=''):
        return widgets.Button(
            description=description,
            disabled=disabled,
            button_style=style,
            layout=widgets.Layout(
                height='auto',
                width='auto'))

    def _create_check_box(self, description, value=False):
        return widgets.Checkbox(
            description=description,
            value=value,
            disabled=False,
            indent=False)

    def _create_multi_select(self, description, options, height='200px'):
        return widgets.SelectMultiple(
            description=description,
            options=options,
            disabled=False,
            layout=widgets.Layout(
                width='400px',
                height=height))

    def err_msg(self, msg):
        self._display([widgets.HTML(value=f"<p style='color:red'>{msg}</p>")])

    @property
    def num_list_ordered(self):
        rtlist = []
        for column in self.data.columns:
            if column in self.numeric_columns:
                rtlist.append(column)
        return rtlist

    @property
    def cat_list_ordered(self):
        rtlist = []
        for column in self.data.columns:
            if column in self.categorical_columns:
                rtlist.append(column)
        return rtlist
