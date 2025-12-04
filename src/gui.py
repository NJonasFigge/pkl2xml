from __future__ import annotations

# noinspection PyPep8Naming
import PySimpleGUI as sg


class _:  # global vars
    current_location: tuple[int, int] = NotImplemented
    welcome_window: sg.Window = NotImplemented
    wait_window_news: None | tuple[str, int, int] = None
    is_cancel_clicked: bool = False
    is_exit_clicked: bool = False


def init():
    sg.theme('DarkBlue14')


def welcome_and_input():
    if _.welcome_window is NotImplemented:
        layout = [
            [sg.Text('Welcome to PKL2XML-GUI!')],
            [sg.Text('Enter a path below. This can be a direct filepath ("C:/.../filename.pkl") or even a directory '
                     'path, in which case all contained .pkl files will be converted.')],
            [sg.Text('Your input:'), sg.InputText()],
            [sg.Button('Convert'), sg.Button('Exit')],
        ]
        location = (None, None) if _.current_location is NotImplemented else _.current_location  # This might be first window
        _.welcome_window = sg.Window('PKL2XML-GUI', layout, location=location, finalize=True)
    else:
        _.welcome_window.move(*_.current_location)
        _.welcome_window.un_hide()
    event, values = _.welcome_window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        _.is_exit_clicked = True
        res = None
        _.welcome_window.close()
    else:
        res = values[0]
        _.welcome_window.hide()
        _.current_location = _.welcome_window.CurrentLocation()
    return res


def start_waiting():
    layout = [
        [sg.Text('Please wait...')],
        [sg.Text('Starting conversion...', key='NEWS')],
        [sg.Button('Cancel')],
    ]
    window = sg.Window('PKL2XML-GUI', layout, location=_.current_location, finalize=True)
    while _.wait_window_news is not None:
        filename, number, of_total = _.wait_window_news
        window['NEWS'].update(f'"{filename}" is being converted ({number} / {of_total})')
        _.current_location = window.CurrentLocation()
        event, values = window.read(timeout=1)
        if event == sg.WIN_CLOSED:
            _.is_exit_clicked = True
            break
        if event == 'Cancel':
            _.is_cancel_clicked = True
            break
    window.close()


def update_wait_news(filename: str, number: int, of_total: int): _.wait_window_news = filename, number, of_total
def end_waiting(): _.wait_window_news = None


def success_and_askmore(num_converted: int):
    layout = [
        [sg.Text('Success!')],
        [sg.Text(f'Files converted: {num_converted}.')],
        [sg.Button('Convert more'), sg.Button('Exit')],
    ]
    window = sg.Window('PKL2XML-GUI', layout, location=_.current_location, finalize=True)
    event, values = window.read()
    res = True
    if event in (sg.WIN_CLOSED, 'Exit'):
        _.is_exit_clicked = True
        res = False
    _.current_location = window.CurrentLocation()
    window.close()
    return res


def error(msg: str):
    layout = [
        [sg.Text('An error occurred:')],
        [sg.Text(msg)],
        [sg.Button('Ok')],
    ]
    window = sg.Window('PKL2XML-GUI', layout, location=_.current_location, finalize=True)
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        _.is_exit_clicked = True
    _.current_location = window.CurrentLocation()
    window.close()


def overwrite_warning_and_askskip(filename: str):
    layout = [
        [sg.Text(f'An XML file already exists for "{filename}". How do you want to proceed?')],
        [sg.Button('Overwrite'), sg.Button('Skip')],
    ]
    window = sg.Window('PKL2XML-GUI', layout, location=_.current_location, finalize=True)
    event, values = window.read()
    is_skip = True
    if event == sg.WIN_CLOSED:
        _.is_exit_clicked = True
    elif event == 'Overwrite':
        is_skip = False
    _.current_location = window.CurrentLocation()
    window.close()
    return is_skip


def is_cancel_computation(): return _.is_cancel_clicked or _.is_exit_clicked
def is_exit(): return _.is_exit_clicked
