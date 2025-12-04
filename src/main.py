
import pickle
import gui
from threading import Thread
from pathlib import Path
from xml_building import build_xml


# - A global variable, in which the filenames with failed conversions will be collected (initialized when used)
ERROR_FILENAMES: list[str] = NotImplemented


def __convert_pkl(p: Path):
    """Actual conversion method, using the """
    ### Load content from pickle file (UnpicklingError might occur because of different endline characters)
    try:
        content = pickle.load(open(p, 'rb'))
    except pickle.UnpicklingError:
        # - (This snippet was taken from the internet, solving the error that is caught here)
        with open(p, 'rb') as f:
            lines = [line.rstrip('\r\n'.encode()) for line in f.readlines()]
            content = pickle.loads('\n'.encode().join(lines))
    ### Build XML from loaded content
    xml_doc = build_xml(content)
    ### Write XML to the output file
    with open(p.parent / p.name.replace('.pkl', '.xml'), 'w') as f:
        f.write(xml_doc.toprettyxml(indent='  '))


def __convert_all(pkl_path_list: list[Path]):
    """Goes through given pkl path list and calls __convert_pkl() on them, while updating the gui, collecting
    erroring files and checking if user cancelled computation"""
    # - Go through list of pickle paths
    for i, p in enumerate(pkl_path_list):
        # - Cancel if user clicked "Cancel"
        if gui.is_cancel_computation(): break
        # - Update GUI
        gui.update_wait_news(p.name, i, len(pkl_path_list))
        # - Execute actual conversion, collect erroring file names in global list
        # noinspection PyBroadException
        try: __convert_pkl(p)
        except Exception: ERROR_FILENAMES.append(p.name)
    # - Finally stop waiting dialog
    gui.end_waiting()


if __name__ == '__main__':
    gui.init()
    while True:
        ### Acquire pkl paths to convert
        # - Get input
        inp = gui.welcome_and_input()
        # - Handle click on "Exit"
        if gui.is_exit(): break
        # - Convert path string to pathlib.Path instance
        path = Path(inp)
        # - Check if path exists
        if not path.exists():
            gui.error('The given path does not exist.')
            continue
        # - Queue up found pkl file paths (if direct file path was given, only that)
        pkl_paths_queue = [path] if path.is_file() else list(path.rglob('*.pkl'))
        # - Handle absence of pkl files
        if len(pkl_paths_queue) == 0:
            gui.error('No pkl files could be found in the given directory.')
            continue
        # - Go through queued paths and add them to the "real" conversion list
        pkl_paths = []
        for pkl_path in pkl_paths_queue:
            # - If an .xml file already exists, ask if it should be skipped. If so, do not add it to the list
            xml_path = pkl_path.parent / (pkl_path.name.split('.')[0] + '.xml')
            if not xml_path.exists() or not gui.overwrite_warning_and_askskip(pkl_path.name):
                pkl_paths.append(pkl_path)
        # - Handle absence of pkl files after filtering out the ones to skip
        if len(pkl_paths) == 0:
            gui.error('No pkl files left to convert.')
            continue
        ### Convert all found pkl files
        # - Initialize a list containing filenames of pkls that raised an error
        ERROR_FILENAMES = []
        # - Start conversion in a separate thread
        computation_thread = Thread(target=__convert_all, args=[pkl_paths])
        computation_thread.start()
        # - Wait on the thread to finish (and show details updated by conversion function)
        gui.start_waiting()
        computation_thread.join()
        # - Handle errors that might have occurred
        if len(ERROR_FILENAMES) > 0:
            gui.error(f'Something went wrong during conversion of the following pkl file(s):\n'
                      + ', '.join(ERROR_FILENAMES) + '\nTo find out more, please contact the developer, Jonas Figge.')
            continue
        ### Manage user needs
        # - If the computation was cancelled or user clicks "Convert more" on success screen, start over
        if gui.is_cancel_computation() or gui.success_and_askmore(len(pkl_paths)):
            continue
        # - Every "start over" scenario was managed using continue, so if we arrive here, the program should stop
        break
