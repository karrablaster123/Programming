import time
import logging
import win32com.client as win32

from sys import stdout
from itertools import chain
from psutil import process_iter
from pathlib import Path, WindowsPath
from tkinter import Tk, filedialog


class ASPEN:
    """
    A class to interface with the ASPEN simulation software.

    This class provides methods to connect to ASPEN, manipulate simulation parameters,
    run simulations, and handle logging and error management.

    Attributes:
        _log_folder_name : str
            The name of the log folder.
        _visibility : bool
            The visibility state of the ASPEN application.
        _run_id : int
            The ID of the current run, incremented with each run.
        _aspen_is_running : bool
            Flag indicating whether ASPEN is currently running.
        _connected_to_aspen : bool
            Flag indicating whether the class is connected to ASPEN.
        err_flag : bool
            Flag indicating whether an error has occurred.
        __logger : logging.Logger
            The logger instance for logging messages.
        __log_path : pathlib.Path
            The path to the log folder.
        aspen : win32com.client.CDispatch
            The ASPEN application instance.
        aspen_path : pathlib.Path
            The path to the ASPEN file.

    Methods:
        __enter__():
            Allows for the use of the with keyword to safely utilize instances of this class.
        __exit__(exc_type, exc_value, traceback):
            Handles both normal and abnormal exits during execution.
        set_node_value(address, value):
            Sets the value of a node in the Aspen simulation using a string address.
        get_node_value(address):
            Gets the value of an address in the simulation.
        find_node(address):
            Finds a node in the tree based on the given address.
        _get_logging():
            Sets up logging for the current run.
        error(err_string):
            Logs an error message and sets the error flag.
        port_names():
            Prints a list of commonly used port names and their descriptions.
        block_list():
            Retrieves a list of block names from the Aspen tree structure.
        stream_list():
            Retrieves a list of stream names from the Aspen tree structure.
        stream_reconnect(disconnect_from, connect_to, stream_name, port_name):
            Reconnects a stream from one block to another.
        stream_disconnect(block_name, stream_name, port_name):
            Disconnects a stream from a specified block and port.
        stream_connect(block_name, stream_name, port_name):
            Connects a stream to a specified block and port.
        _fetch_block(block_name):
            Fetches a block from the Aspen tree structure based on the given block name.
        _fetch_stream(stream_name):
            Fetches a stream from the Aspen tree structure based on the given stream name.
        _fetch_reaction(reaction_name):
            Fetches a reaction from the Aspen tree structure based on the given reaction name.
        get_reaction_input(reaction_name):
            Retrieves the input elements of a specified reaction.
        get_stream_input(stream_name):
            Retrieves the input elements of a specified stream.
        get_stream_output(stream_name):
            Retrieves the output elements of a specified stream.
        get_block_input(block_name):
            Retrieves the input elements of a specified block.
        toggle_visibility():
            Toggles the visibility of the Aspen application.
        get_block_output(block_name):
            Retrieves the output elements of a specified block.
        get_calculator_block():
            Retrieves the calculator block from the Aspen tree structure.
        save_aspen_file():
            Saves the current Aspen file, with a warning about overwriting the current file.
        get_block_design_spec(block_name):
            Retrieves the design specifications of a specified block.
        get_flowsheet_design_spec():
            Retrieves the design specifications of the flowsheet.
        get_aspen_path_from_user():
            Prompts the user to select an Aspen simulation file and logs the selected file path.
        reconnect_to_aspen(aspen_path=None):
            Reconnects to the ASPEN application using the specified path.
        connect_to_aspen(aspen_path=None):
            Connects to the ASPEN application using the specified path.
        get_block_run_status_message(block_name):
            Retrieves the run status message of a specified block.
        run_aspen(autosave=True):
            Runs the ASPEN simulation and optionally saves the results.
        _kill_aspen():
            Terminates the ASPEN application.
    """
    
    def __init__(self, log_folder: str=None):
        """
        Initialize an instance of the class and sets up the logger.

        Args:
            log_folder (str, optional): The path to the folder where log files will be stored.
                If not provided, defaults to 'ASPEN Simulation Run Log'.
        """
        # Set log folder name. Handle default case. 
        if log_folder is None: log_folder = 'ASPEN Simulation Run Log'
        self._log_folder_name = log_folder
        
        # Default visibility is False
        self._visibility = False
        
        # run_id is 1 and incremented each time ASPEN is run.
        self._run_id = 1
        self._aspen_is_running = False
        self._connected_to_aspen = False
        self.err_flag = False
        
        # Setup the logger.
        self._get_logging()

    def __enter__(self):
        """
        Allows for the use of the with keyword to safely utilise instances of this class.

        Returns:
            ASPEN: An instance of the ASPEN class.
        """
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        The other side necessary for the utilisation of the with keyword. Handles both normal and abnormal exits during execution.

        Args:
            exc_type (_type_): Type of exception. None when code executes normally.
            exc_value (_type_): Value of exception. None when code executes normally.
            traceback (_type_): Traceback of exception. None when code executes normally.
        """
        # If ASPEN is running, stop the engine before quitting
        if self._aspen_is_running:
            self.aspen.Engine.Stop()
            self.error("Something went wrong! Stopping ASPEN...")
            time.sleep(5)
        
        # Kill the ASPEN instance.
        self._kill_aspen()
        
        # If exit due to an exception, log the exception.
        if exc_type is not None:
            self.error(f"Exception: {exc_type} {exc_value} {traceback}")
        
        # Clear the logger.  
        try:
            self.__logger.handlers.clear()
        except AttributeError:
            pass
        
        # Shutdown logging.
        logging.shutdown()
    
    def set_node_value(self, address: str, value: float):
        """
        Sets the value of a node in the Aspen simulation when using a string address. 
        
        This is one way to set a value.

        Args:
            address (str): Variable Explorer - Path to Node.
            value (float): The value you want to set.
        """
        node = self.find_node(address)
        if node is None:
            self.error(f"Unable to set the value for this address: {address}")
            return None
        node.Value = value
        return 0
    
    def get_node_value(self, address: str):
        """
        Get the value of an address in the simulation.

        Args:
            address (str): The string address.

        Returns:
            float/None: returns a value if successful or None if unsuccessful.
        """
        node = self.find_node(address)
        if node is None:
            self.error(f"Unable to get the value for this address: {address}")
            return None
        return node.Value
    
    def find_node(self, address: str):
        """
        Finds a node in the tree based on the given address.

        Args:
            address (str): The address of the node to find.

        Returns:
            Node: The node if found, otherwise None.
        """
        try:
            return self.aspen.Tree.FindNode(address)
        except AttributeError:
            self.error(f"Could not find that address: {address}")
            return None
    
    def _get_logging(self):
        """
        Sets up logging for the current run, ensuring no directory collisions and creating necessary directories and loggers.

        Returns:
            int: 0 if the logger already has handlers, otherwise None.
        """
        try:
            if self.__logger.hasHandlers():
                return 0
        except AttributeError:
            pass
        
        # Generate a directory for this run.
        folder_number = 0
        self.__log_path = Path.cwd() / 'Run_Logs' / (f"{self._log_folder_name}")
        
        # Prevent Directory collisions.
        while self.__log_path.exists():
            folder_number += 1
            self.__log_path = Path.cwd() / 'Run_Logs' / (f"{self._log_folder_name} " + str(folder_number))
        
        # Create output directory
        for path in chain(reversed(self.__log_path.parents), [self.__log_path]):
            if not path.exists():
                path.mkdir()
        
        # Create a new logger for this file.
        self.__logger = logging.getLogger(__name__)
        self.__logger.propagate = False
        
        # Set formatter and handlers. 
        format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console = logging.StreamHandler(stdout)
        file = logging.FileHandler(filename=self.__log_path/'Simulation Log File.log')
        
        # Setup Logger.
        self.__logger.setLevel(logging.INFO)
        console.setFormatter(format)
        file.setFormatter(format)
        self.__logger.addHandler(console)
        self.__logger.addHandler(file)
        self.log = self.__logger.info
        self.log(f'Logging started. Log folder path: {str(self.__log_path)}')
    
    def error(self, err_string):
        """
        Logs an error message and sets the error flag.

        Args:
            err_string (str): The error message to log.

        Returns:
            None
        """
        # Set the error flag to True.
        self.err_flag = True
        
        # Log the error message using the logger.
        self.__logger.error(err_string)
    
    @staticmethod
    def port_names():
        """
        Prints a list of commonly used port names and their descriptions.

        Returns:
            None
        """
        # Print a message indicating that the list is not exhaustive.
        print("This is not an exhaustive list of ports. Just the most commonly used.")
        
        # Print the list of port names and their descriptions.
        print(str([
            "'F(IN)' - Feed (Most Blocks)",
            "'P(OUT)' - Product (Most Blocks)",
            "'V(OUT)' - Vapour (Flash Separators)",
            "'L(OUT)' - Liquid (Flash Separators)",
            "'D(OUT)' - Distillate (Distillation Columns)",
            "'B(OUT)' - Bottoms (Distillation Columns)",
            "'H(IN)' - Hot Liquid In (Heat Exchanger)",
            "'C(IN)' - Coolant In (Heat Exchanger)",
            "'H(OUT)' - Hot Liquid Out (Heat Exchanger)",
            "'C(OUT)' - Coolant Out (Heat Exchanger)",
            "'C(IN)' - Thermal Fluid (R-PLUG)",
            "'C(OUT)' - Thermal Fluid Out (R-PLUG)",
            "'VD(OUT)' - Vapour Distillate (Absorber/RECT)",
            "'LD(OUT)' - Liquid Distillate (Absorber/RECT)"
        ]))
    
    @property
    def block_list(self):
        """
        Retrieves a list of block names from the Aspen tree structure.

        Returns:
            list: A list of block names if successful, otherwise None.
        """
        try:
            # Generate a list of block names from the Aspen tree structure.
            return [item.Name for item in self.aspen.Tree.Elements("Data").Elements("Blocks").Elements]
        except AttributeError:
            # Log an error message if an AttributeError occurs.
            self.error("Unable to output list of blocks. Attribute Error.")
            return None
    
    @property
    def stream_list(self):
        """
        Retrieves a list of stream names from the Aspen tree structure.

        Returns:
            list: A list of stream names if successful, otherwise None.
        """
        try:
            # Generate a list of stream names from the Aspen tree structure.
            return [item.Name for item in self.aspen.Tree.Elements("Data").Elements("Streams").Elements]
        except AttributeError:
            # Log an error message if an AttributeError occurs.
            self.error("Unable to output list of streams. Attribute Error.")
            return None
    
    def stream_reconnect(self, disconnect_from, connect_to, stream_name, port_name):
        """
        Reconnects a stream from one block to another.

        Args:
            disconnect_from (str): The block to disconnect the stream from.
            connect_to (str): The block to connect the stream to.
            stream_name (str): The name of the stream to reconnect.
            port_name (str): The port name used for the connection.

        Returns:
            int: The result of the disconnection and reconnection operations.
        """
        # Disconnect the stream from the specified block.
        result = self.stream_disconnect(disconnect_from, stream_name, port_name)
        
        # Connect the stream to the new block.
        result += self.stream_connect(connect_to, stream_name, port_name)
        
        # Log the reconnection operation.
        self.log(f"Reconnected {stream_name} from {disconnect_from} to {connect_to}")
        
        # Return the result of the operations.
        return result
    
    def stream_disconnect(self, block_name, stream_name, port_name):
        """
        Disconnects a stream from a specified block and port.

        Args:
            block_name (str): The name of the block to disconnect the stream from.
            stream_name (str): The name of the stream to disconnect.
            port_name (str): The name of the port to disconnect the stream from.

        Returns:
            int: 0 if the disconnection is successful, -1 if an error occurs.
        """
        # Fetch the block object using the block name.
        block = self._fetch_block(block_name)
        
        # Log the attempt to disconnect the stream.
        self.log(f"Trying to connect {stream_name} to {block_name}")
        
        try:
            # Attempt to remove the stream from the specified port.
            block.Elements("Ports").Elements(port_name).Elements.Remove(stream_name)
        except:
            # Log an error message if the disconnection fails.
            self.error(f"Unable to disconnect {stream_name} and {block_name}")
            
            # Provide additional logging information for troubleshooting.
            self.log("Check PORTNAME, BLOCKNAME, and STREAMNAME.")
            self.log("Check variable explorer to be sure the port name is associated with your block.")
            
            # Return -1 to indicate failure.
            return -1
        
        # Log a success message if the disconnection is successful.
        self.log(f"Success!")
        
        # Return 0 to indicate success.
        return 0
    
    def stream_connect(self, block_name, stream_name, port_name):
        """
        Connects a stream to a specified block and port.

        Args:
            block_name (str): The name of the block to connect the stream to.
            stream_name (str): The name of the stream to connect.
            port_name (str): The name of the port to connect the stream to.

        Returns:
            int: 0 if the connection is successful, -1 if an error occurs.
        """
        # Fetch the block object using the block name.
        block = self._fetch_block(block_name)
        
        # Log the attempt to connect the stream.
        self.log(f"Trying to connect {stream_name} to {block_name}")
        
        try:
            # Attempt to add the stream to the specified port.
            block.Elements("Ports").Elements(port_name).Elements.Add(stream_name)
        except:
            # Log an error message if the connection fails.
            self.error(f"Unable to connect {stream_name} and {block_name}")
            
            # Provide additional logging information for troubleshooting.
            self.log("Check PORTNAME, BLOCKNAME, and STREAMNAME.")
            self.log("Check variable explorer to be sure the port name is associated with your block.")
            
            # Return -1 to indicate failure.
            return -1
        
        # Log a success message if the connection is successful.
        self.log(f"Success!")
        
        # Return 0 to indicate success.
        return 0
        
    def _fetch_block(self, block_name):
        """
        Fetches a block from the Aspen tree structure based on the given block name.

        Args:
            block_name (str): The name of the block to fetch.

        Returns:
            Block: The block if found, otherwise None.
        """
        try:
            # Attempt to retrieve the block from the Aspen tree structure.
            return self.aspen.Tree.Elements("Data").Elements("Blocks").Elements(block_name)
        except AttributeError:
            # Log an error message if the block does not exist.
            self.log(f"This block {block_name} doesn't exist!")
            return None
    
    def _fetch_stream(self, stream_name):
        """
        Fetches a stream from the Aspen tree structure based on the given stream name.

        Args:
            stream_name (str): The name of the stream to fetch.

        Returns:
            Stream: The stream if found, otherwise None.
        """
        try:
            # Attempt to retrieve the stream from the Aspen tree structure.
            return self.aspen.Tree.Elements("Data").Elements("Streams").Elements(stream_name)
        except AttributeError:
            # Log an error message if the stream does not exist.
            self.log(f"This stream {stream_name} doesn't exist!")
            return None

    
    def _fetch_reaction(self, reaction_name):
        """
        Fetches a reaction from the Aspen tree structure based on the given reaction name.

        Args:
            reaction_name (str): The name of the reaction to fetch.

        Returns:
            Reaction: The reaction if found, otherwise None.
        """
        try:
            # Attempt to retrieve the reaction from the Aspen tree structure.
            return self.aspen.Tree.Elements("Data").Elements("Reactions").Elements("Reactions").Elements(reaction_name)
        except AttributeError:
            # Log an error message if the reaction does not exist.
            self.log(f"This reaction {reaction_name} doesn't exist!")
            return None

    def get_reaction_input(self, reaction_name):
        """
        Retrieves the input elements of a specified reaction.

        Args:
            reaction_name (str): The name of the reaction.

        Returns:
            Elements: The input elements of the reaction if found, otherwise None.
        """
        # Fetch the reaction using the reaction name.
        reaction = self._fetch_reaction(reaction_name)
        if reaction is not None:
            # Return the input elements of the reaction.
            return reaction.Elements("Input")
        return None

    def get_stream_input(self, stream_name):
        """
        Retrieves the input elements of a specified stream.

        Args:
            stream_name (str): The name of the stream.

        Returns:
            Elements: The input elements of the stream if found, otherwise None.
        """
        # Fetch the stream using the stream name.
        stream = self._fetch_stream(stream_name)
        if stream is not None:
            # Return the input elements of the stream.
            return stream.Elements("Input")
        return None

    def get_stream_output(self, stream_name):
        """
        Retrieves the output elements of a specified stream.

        Args:
            stream_name (str): The name of the stream.

        Returns:
            Elements: The output elements of the stream if found, otherwise None.
        """
        # Fetch the stream using the stream name.
        stream = self._fetch_stream(stream_name)
        if stream is not None:
            # Return the output elements of the stream.
            return stream.Elements("Output")
        return None

    def get_block_input(self, block_name):
        """
        Retrieves the input elements of a specified block.

        Args:
            block_name (str): The name of the block.

        Returns:
            Elements: The input elements of the block if found, otherwise None.
        """
        # Fetch the block using the block name.
        block = self._fetch_block(block_name)
        if block is not None:
            # Return the input elements of the block.
            return block.Elements("Input")
        return None

    def toggle_visibility(self):
        """
        Toggles the visibility of the Aspen application.

        Returns:
            None
        """
        # Toggle the visibility state of the Aspen application.
        self.aspen.Visible = self._visibility = not self._visibility

    def get_block_output(self, block_name):
        """
        Retrieves the output elements of a specified block.

        Args:
            block_name (str): The name of the block.

        Returns:
            Elements: The output elements of the block if found, otherwise None.
        """
        # Fetch the block using the block name.
        block = self._fetch_block(block_name)
        if block is not None:
            # Return the output elements of the block.
            return block.Elements("Output")
        return None

    def get_calculator_block(self):
        """
        Retrieves the calculator block from the Aspen tree structure.

        Returns:
            Block: The calculator block if found, otherwise None.
        """
        try:
            # Attempt to retrieve the calculator block from the Aspen tree structure.
            return self.aspen.Tree.Elements("Data").Elements("Flowsheeting Options").Elements("Calculator")
        except AttributeError:
            # Log an error message if the calculator block does not exist.
            self.log("Unable to get Calculator Block")
            return None

    def save_aspen_file(self):
        """
        Saves the current Aspen file, with a warning about overwriting the current file.

        Returns:
            None
        """
        # Log a warning message about overwriting the current file.
        self.log("This will overwrite the current file. Use this carefully!")
        # Wait for 10 seconds before saving the file.
        time.sleep(10)
        # Save the current Aspen file.
        self.aspen.Save()

    def get_block_design_spec(self, block_name):
        """
        Retrieves the design specifications of a specified block.

        Args:
            block_name (str): The name of the block.

        Returns:
            Elements: The design specifications of the block if found, otherwise None.
        """
        # Fetch the block using the block name.
        block = self._fetch_block(block_name)
        if block is not None:
            try:
                # Attempt to retrieve the design specifications of the block.
                return block.Elements("Subobjects").Elements("Design Specs")
            except AttributeError:
                # Log an error message if the block does not have design specifications.
                self.log(f"{block_name} might not have design specs. This operation didn't work.")
                return None

    def get_flowsheet_design_spec(self):
        """
        Retrieves the design specifications of the flowsheet.

        Returns:
            Elements: The design specifications of the flowsheet if found, otherwise None.
        """
        try:
            # Attempt to retrieve the design specifications of the flowsheet.
            return self.aspen.Tree.Elements("Data").Elements("Flowsheeting Options").Elements("Design-Spec")
        except AttributeError:
            # Log an error message if the design specifications do not exist.
            self.log("Unable to get Design Specs")
            return None

    def get_aspen_path_from_user(self):
        """
        Prompts the user to select an Aspen simulation file and logs the selected file path.

        Returns:
            None
        """
        # Create a Tkinter root window.
        root = Tk()
        try:
            # Get file path from user.
            self.aspen_path = filedialog.askopenfilename(
                initialdir=Path.cwd(),
                title="Select simulation file",
                filetypes=(("ASPEN Plus Backup File", "*.bkp"), ("ASPEN Plus Simulation File", "*.apw"))
            )
            # Log the selected file path.
            self.log(f"File selected: {str(Path(self.aspen_path))}")
        finally:
            # Ensure the window is destroyed and prevent crashes even if the user cancels input.
            root.destroy()
    
    def reconnect_to_aspen(self, aspen_path: str | WindowsPath=None):
        """
        Reconnects to the ASPEN application using the specified path.

        Args:
            aspen_path (str | WindowsPath, optional): The path to the ASPEN file. Defaults to None.

        Returns:
            None
        """
        # Check if connected to ASPEN.
        if not self._connected_to_aspen:
            self.log("Not connected to ASPEN. Cannot reconnect.")
            return
        
        # Kill the current ASPEN instance.
        self._kill_aspen()
        
        # Connect to ASPEN using the specified path.
        self.connect_to_aspen(aspen_path)
        
        # Log the reconnection.
        self.log("Reconnected to ASPEN.")

    def connect_to_aspen(self, aspen_path: str | WindowsPath=None):
        """
        Connects to the ASPEN application using the specified path.

        Args:
            aspen_path (str | WindowsPath, optional): The path to the ASPEN file. Defaults to None.

        Returns:
            None
        """
        # Check if a path is provided.
        if aspen_path is not None:
            # Convert string path to Path object if necessary.
            if isinstance(aspen_path, str):
                aspen_path = Path(aspen_path)
            # Check if the path exists.
            if not aspen_path.exists():
                self.error("Input aspen path does not exist. Please check.")
                raise ValueError(f"ASPEN path invalid: {aspen_path}")
            self.aspen_path = aspen_path
        else:
            # Prompt the user to select a path.
            self.get_aspen_path_from_user()
        
        # Log the dispatching of the ASPEN instance.
        self.log("Dispatching ASPEN instance.")
        start_time = time.time()
        
        # Dispatch the ASPEN instance.
        self.aspen = win32.gencache.EnsureDispatch('Apwn.Document')
        self.log(f"ASPEN instance dispatched. Time taken: {time.time() - start_time} seconds")
        
        start_time = time.time()
        self.log("Connecting to the ASPEN file.")
        
        # Connect to the ASPEN file.
        self.aspen.InitFromArchive2(Path(self.aspen_path))
        self.log(f"Connected. Time taken: {time.time() - start_time} seconds")
        
        # Set the connection flag.
        self._connected_to_aspen = True

    def get_block_run_status_message(self, block_name):
        """
        Retrieves the run status message of a specified block.

        Args:
            block_name (str): The name of the block.

        Returns:
            dict: A dictionary containing the status and message of the block.
        """
        # Fetch the block using the block name.
        block = self._fetch_block(block_name)
        if block is not None:
            # Return the status and message of the block.
            return {
                "status": block.Elements("Output").Elements("BLKSTAT").Value,
                "message": block.Elements("Output").Elements("BLKMSG").Value
            }

    def run_aspen(self, autosave: bool=True):
        """
        Runs the ASPEN simulation and optionally saves the results.

        Args:
            autosave (bool, optional): Whether to autosave the results. Defaults to True.

        Returns:
            None
        """
        try:
            # Set the running flag.
            self._aspen_is_running = True
            start_time = time.time()
            
            # Log the start of the ASPEN run.
            self.log("Running ASPEN")
            
            # Run the ASPEN simulation.
            self.aspen.Engine.Run2()
            self.log("ASPEN Run. Time taken: " + str(time.time() - start_time) + " seconds.")
            
            # Clear the running flag.
            self._aspen_is_running = False
        finally:
            if autosave:
                # Save the ASPEN file and export the report.
                self.aspen.SaveAs(str(self.__log_path / f"ASPEN Simulation {self._run_id}.bkp"), False)
                self.aspen.Export(2, str(self.__log_path / f"ASPEN Simulation Report {self._run_id}"))
                self._run_id += 1

    def _kill_aspen(self):
        """
        Terminates the ASPEN application.

        Returns:
            None
        """
        if self.aspen is not None:
            # Quit the ASPEN application.
            self.aspen.Quit()
            try:
                self.log("Quit ASPEN using WIN32")
            except AttributeError:
                pass
            time.sleep(5)
        else:
            # Kill ASPEN processes if the application is not running.
            for p in process_iter():
                if p.name() in ["AspenPlus.exe", "APropMain.exe", "AspenProperties.exe"]:
                    try:
                        self.log("ASPEN was running. Killing process via Windows")
                    except AttributeError:
                        pass
                    p.kill()
                    time.sleep(5)

    # def set_aspen_path(self, path: str):
    #     if Path(path).exists():
    #         self.__aspen_path = path
    #     else:
    #         self.error(f"Path {path} does not exist.")

    # def get_aspen_path_from_user(self, save: bool=False):
    #     root = Tk()
    #     #root.withdraw()
    #     try:
    #         # Get file path from user
    #         self.__aspen_path =  filedialog.askopenfilename(initialdir = Path.cwd(),title = "Select simulation file",filetypes = (("ASPEN Backup File","*.bkp"),))
    #         self.log(f"File selected: {str(Path(self.__aspen_path))}")
    #     finally:
    #         # This ensures the window is destroyed and prevents crashes even if the users cancels input. 
    #         root.destroy()
    #         if save: self._write_aspen_path_to_file()
    
    # def get_aspen_path_from_file(self):
    #     try:
    #         with open(Path.cwd() / "path_param.json", "r") as json_file:
    #             self.__aspen_path = json.load(json_file)["aspen_path"]
    #     except:
    #         raise RuntimeError("Unable to Read ASPEN Path.")
    
    # def _write_aspen_path_to_file(self):
    #     with open(Path.cwd() / "path_param.json", "w") as json_file:
    #         json.dump({"aspen_path": str(self.__aspen_path)}, json_file, indent=4)
    #     self.log("File path written to path_param.json. You can use this on the next startup by setting use_file_path to True.")