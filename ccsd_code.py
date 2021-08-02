import numpy as np
import pandas as pd
from matplotlib import dates
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from IPython.display import display
import tkinter as tk
import math
import statsmodels
import psycopg2
import os

# query = ''
#
# connect = psycopg2.connect('dbname=test user=postgres password=postgres')
# cur = connect.cursor()
# cur.execute(query)
# tup = cur.fetchall()
# column_names = [desc[0] for desc in cur.description]
#
# data = pd.DataFrame(tup, columns = column_names)

greenfield_acc_data = pd.read_csv('/Users/tylerkim/Desktop/SquarePanda/Greenfield/Greenfield_data_accuracy_games.csv',
                              thousands=',')
greenfield_data = pd.read_csv('/Users/tylerkim/Desktop/SquarePanda/Greenfield/Greenfield Final - Greenfield_data_complete.csv',
                              thousands=',')


### MAKE SURE THAT SCHOOL NAMES MATCHES THE REGION MAP
region_data = pd.read_csv("/Users/tylerkim/Desktop/SquarePanda/CCSD/CCSD REAL Program_ParticipatingSchools_070221 School Participation List (1).xlsx - All Schools By Region.csv")
region_1 = []
region_2 = []
region_3 = []
for row in region_data.iterrows():
    region = row[1][1]
    school= row[1][0]
    if region == 1:
        region_1.append(school)
    if region == 2:
        region_2.append(school)
    if region == 3:
        region_3.append(school)

def df_with_filter(data, filter_by, value):
    '''
    :param data: pandas dataframe of school data
    :param filter_by: str, the condition to filter on (ex. area, whole game, core skill)
    :param value: str, the desired value of filter_by (ex. filter_by = Area, value = Phonological Awareness)
    :return: a new pd df where filter_by = value›
    '''
    # only returns obs where data[filter_by] == value is true
    if filter_by == "Dates":
        start_date = value[0]
        end_date = value[1]
        mask = ((pd.to_datetime(data['Session Date']) >= pd.to_datetime(start_date)) & (pd.to_datetime(data['Session Date']) <= pd.to_datetime(end_date)))
        return data[mask]
    bool = data[filter_by] == value
    return data[bool]

def regionize(data, region):
    ### MAKE SURE THAT SCHOOL NAMES ARE SAME AS ON REGION MAP
    if region == 1:
        return data[data['School'].isin(region_1)]
    elif region == 2:
        return data[data['School'].isin(region_2)]
    elif region == 3:
        return data[data['School'].isin(region_3)]


def clean_data(data):
    data = data.convert_dtypes()
    bool = data['Duration (Mins)'] >= .05
    data = data[bool]
    bool2 = data['Duration (Mins)'] <= 15
    data = data[bool2]
    return data

def get_path():
    file_name = os.path.splitext(os.path.basename(os.path.realpath(__file__)))[0]

    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Results")

    if not os.path.exists(full_path):
        os.mkdir(full_path)

        if not os.path.exists(os.path.join(full_path, file_name)):
            os.mkdir(os.path.join(full_path, file_name))

    file_location = os.path.join(full_path, file_name, 'data.csv')
    return file_location


def convert_to_week(data):
    # as index=False to keep the Session.Date column
    data2 = data.groupby('Session Date', as_index=False).sum()
    # #Convert to datetime with dashes from datetime with slashes
    data2['Session Date'] = pd.to_datetime(data2['Session Date'], infer_datetime_format=True)
    # convert datetimes to week numbers (unsure how it works for multi-years)
    data2['Session Date'] = data2['Session Date'].dt.isocalendar().week
    return data

def report_duration(raw_data, grouping=None, applied_fx='sum', segment=None, filter_by=None, value=None, time_series=False,
                    visualize=True, table=False, pathname=None, week = False, region = None, save_plt = False):
    """
    :param data: pd df of usage data
    :param grouping: optional str, the name of the column to use for categorical variable (the groups on the x axis)
    :param applied_fx: str, default = 'sum', name of numpy function to be used to aggregate data (e.g. mean, sum)
    :param segment: optional, str, column name to be used to further segment visualized data (used in hue)
    :param filter_by: optional, str, filter condition to be used with df_with_filter()
    :param value: optional, str, value to be used with df_with_filter
    :param time_series: optional, bool, indicates whether the visualization should be done as a scatter/line plot or as a barplot
    :param visualize: bool, whether or not you want a visualization to appear. default = True
    :param table: bool, whether or not you want a table of data to appear. default - False
    :return:
    """
    data = clean_data(raw_data)
    if filter_by and value:
        data = df_with_filter(data, filter_by, value)
    if region:
        data = regionize(data, region)
    if visualize:
        sns.set()
        if time_series:
            if week:
                data = convert_to_week(data)
            sns.lmplot(data=data.astype(float), x='Session Date', y='Duration (Mins)', hue=segment, robust=True)
            plt.xticks(rotation=90)
            if week:
                plt.xlabel('Session Week')
            else:
                plt.xlabel('Session Date')
            plt.xticks(fontsize=8)
            if filter_by and value:
                plt.title(f'Plot of duration over time for {filter_by}:{value}')
            else:
                plt.title(f'Plot of duration over time')
        else:
            plt.xticks(rotation=90)
            if week:
                data = convert_to_week(data)
                plt.xticks(rotation=90)
            sns.barplot(data=data, x=grouping, y='Duration (Mins)', hue= segment, ci=None,
                        estimator=getattr(np, applied_fx))
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=1, fontsize=8)
            plt.xticks(fontsize=8)
            # title formatting based on the type of visualization
            if filter_by and value and segment:
                plt.title(
                    f'{applied_fx.title()} of duration data for {value} \nby {grouping.replace(".", " ")}, broken down by {segment.replace(".", " ")}')
            elif filter_by and value:
                plt.title(f'{applied_fx.title()} of duration data for {value} \nby {grouping.replace(".", " ")}')
            elif segment:
                plt.title(
                    f'{applied_fx.title()} of duration data by {grouping.replace(".", " ")}, broken down by {segment.replace(".", " ")}')
            else:
                plt.title(f'{applied_fx.title()} of duration data by {grouping.replace(".", " ")}')
        if save_plt:
            plt.savefig(get_path())
        else:
            plt.show()
    if table:
        pass

def report_acc(raw_data, grouping=None, applied_fx='sum', segment=None, filter_by=None, value=None, time_series=False,
                    visualize=True, table=False, week = False, region = None, save_plt = False):
    """
    :param data: pd df of usage data
    :param grouping: optional str, the name of the column to use for categorical variable (the groups on the x axis)
    :param applied_fx: str, default = 'sum', name of numpy function to be used to aggregate data (e.g. mean, sum)
    :param segment: optional, str, column name to be used to further segment visualized data (used in hue)
    :param filter_by: optional, str, filter condition to be used with df_with_filter()
    :param value: optional, str, value to be used with df_with_filter
    :param time_series: optional, bool, indicates whether the visualization should be done as a scatter/line plot or as a barplot
    :param visualize: bool, whether or not you want a visualization to appear. default = True
    :param table: bool, whether or not you want a table of data to appear. default - False
    :return:
    """
    data = clean_data(raw_data)
    if filter_by and value:
        data = df_with_filter(data, filter_by, value)
    if region:
        data = regionize(data, region)
    if visualize:
        sns.set()
        if time_series:
            if week:
                data = convert_to_week(data)
            sns.lmplot(data=data.astype(float), x='Session Date', y='Game Score', hue=segment, robust=True)
            plt.xticks(rotation=90)
            if week:
                plt.xlabel('Session Week')
            else:
                plt.xlabel('Session Date')
            plt.xticks(fontsize=8)
            if filter_by and value:
                plt.title(f'Plot of duration over time for {filter_by}:{value}')
            else:
                plt.title(f'Plot of duration over time')
        else:
            plt.xticks(rotation=90)
            if week:
                data = convert_to_week(data)
                plt.xticks(rotation=90)
            sns.barplot(data=data, x=grouping, y='Game Score', hue= segment, ci=None, estimator=getattr(np, applied_fx))
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=1, fontsize=8)
            plt.xticks(fontsize=8)
            # title formatting based on the type of visualization
            if filter_by and value and segment:
                plt.title(
                    f'{applied_fx.title()} of duration data for {value} \nby {grouping.replace(".", " ")}, broken down by {segment.replace(".", " ")}')
            elif filter_by and value:
                plt.title(f'{applied_fx.title()} of duration data for {value} \nby {grouping.replace(".", " ")}')
            elif segment:
                plt.title(
                    f'{applied_fx.title()} of duration data by {grouping.replace(".", " ")}, broken down by {segment.replace(".", " ")}')
            else:
                plt.title(f'{applied_fx.title()} of duration data by {grouping.replace(".", " ")}')
        if save_plt:
            plt.savefig(get_path())
        plt.show()
    if table:
        if segment:
            tab_data = data[['Duration (Mins)', f'{grouping}', f'{segment}']]
        else:
            tab_data = data[['Duration (Mins)', f'{grouping}']]
        grouped = tab_data.groupby([grouping, segment])
        agg = grouped.aggregate(applied_fx)
        print(agg)
        if segment:
            agg.to_csv(f'/Users/tylerkim/Desktop/SquarePanda/{grouping}_{segment}_table_data.csv')
        else:
            agg.to_csv(f'/Users/tylerkim/Desktop/SquarePanda/{grouping}_table_data.csv')


def launch_gui():
    window = tk.Tk()
    window.title('Visualization selector')

    grouping_frame = tk.Frame()
    view_frame = tk.Frame()
    range_frame = tk.Frame()
    start_date_frame = tk.Frame()
    end_date_frame = tk.Frame()


    grouping = tk.StringVar(window)
    grouping.set('Classroom')

    view_var = tk.StringVar(window)
    view_var.set('Accuracy')

    range_var = tk.StringVar(window)
    range_var.set('False')


    specific_label = tk.Label(master=grouping_frame, text="How would you like to group the results?")
    specific_label.pack()
    view_label = tk.Label(master=view_frame, text="Would you like to see accuracy or duration?")
    view_label.pack()
    range_label = tk.Label(master = range_frame, text = 'Would you like to select a date range?')
    range_label.pack()
    start_label = tk.Label(master=start_date_frame, text = 'Start date (format as yyyy-mm-dd)')
    start_label.pack()
    end_label = tk.Label(master = end_date_frame, text = 'End Date (format as yyyy-mm-dd)')
    end_label.pack()

    choice = tk.OptionMenu(
        grouping_frame, grouping, 'Classroom', 'Region'
    )
    choice.pack()

    view = tk.OptionMenu(
        view_frame, view_var, 'Accuracy', 'Duration'
    )
    view.pack()

    range = tk.OptionMenu(
        range_frame, range_var, 'True', 'False'
    )
    range.pack()

    start_date_var = tk.Entry(start_date_frame)
    start_date_var.pack()

    end_date_var = tk.Entry(end_date_frame)
    end_date_var.pack()

    def close_window():
        window.quit()

    def getInput():
        a = view_var.get()
        b = grouping.get()
        c = range_var.get()
        d = start_date_var.get()
        e = end_date_var.get()
        global response
        response = [a, b, c, d, e]

    button = tk.Button(window, text = 'Enter',command=getInput, height = 2, width = 10, highlightbackground = '#0000ff')
    # getInput()
    view_frame.pack()
    grouping_frame.pack()
    range_frame.pack()
    start_date_frame.pack()
    end_date_frame.pack()
    button.pack()
    # getInput()

    window.mainloop()
    return response

if __name__ == '__main__':
    choice = launch_gui()
    view = choice[0]
    grouping = choice[1]
    print(choice)
    if choice[3]:
        start_date = choice[4][0]
        end_date = choice[4][1]

    if view == 'Accuracy':
        if choice[1] == 'Region':
            report_acc(greenfield_acc_data, grouping = 'Session Date', week = True)
        #   report_acc(greenfield_acc_data, grouping = 'Session Date', week = True, segment = 'Region)
        elif choice[1] == 'Classroom':
            pass
            # report_acc(greenfield_acc_data, grouping='Session Date', week=True, region = 1)
            # report_acc(data, grouping='Session Date', week=True, segment='Classroom Name', region = 2)
            # report_acc(data, grouping='Session Date', week=True, segment='Classroom Name', region = 3)
    elif choice[0] == 'Duration':
        if choice[1] == 'Region':
            #   report_duration(data, grouping = 'Session Date', week = True, segment='Region')
            report_duration(greenfield_data, grouping='Session Date', week=True)
        elif choice[1] =='Classroom':
            pass
            # report_duration(data, grouping='Session Date', week = True, segment = 'Classroom Name', region = 1)
            # report_duration(data, grouping='Session Date', week=True, segment='Classroom Name', region = 2)
            # report_duration(data, grouping='Session Date', week=True, segment='Classroom Name', region = 3)

