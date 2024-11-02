from aspen import ASPEN
from multiprocessing import Pool
from pathlib import Path

class AspenExample(ASPEN):
    """
    A class to represent an example of using ASPEN.

    Attributes
    ----------
    log_folder : str
        The folder where logs will be stored.

    Methods
    -------
    set_coldshot_ratio(ratio):
        Sets the coldshot ratio in the ASPEN model.
    production_rate:
        Retrieves the production rate from the ASPEN model.
    """
    def __init__(self, log_folder: str):
        """
        Constructs all the necessary attributes for the AspenExample object.

        Parameters
        ----------
            log_folder : str
                The folder where logs will be stored.
        """
        super().__init__(log_folder=log_folder)  # Initialize the parent ASPEN class with the log folder
        self.connect_to_aspen()  # Connect to the ASPEN software
    
    def set_coldshot_ratio(self, ratio):
        """
        Sets the coldshot ratio in the ASPEN model.

        Parameters
        ----------
        ratio : float
            The coldshot ratio to be set.
        
        Raises
        ------
        RuntimeError
            If unable to set the coldshot ratio.
        """
        try:
            # Set the coldshot ratio in the ASPEN model
            self.get_block_input("CLDSPLT").Elements("FRAC").Elements("CLDSHT-1").Value = ratio
        except AttributeError:
            # Raise an error if unable to set the coldshot ratio
            raise RuntimeError("Unable to set coldshot ratio")
        self.log(f"Coldshot ratio set to {ratio}")  # Log the coldshot ratio
    
    @property
    def production_rate(self):
        """
        Retrieves the production rate from the ASPEN model.

        Returns
        -------
        float
            The production rate.
        
        Raises
        ------
        RuntimeError
            If unable to get the production rate.
        """
        try:
            # Retrieve the production rate from the ASPEN model
            return self.get_calculator_block() \
                .Elements("OUTVAR") \
                .Elements("Output") \
                .Elements("WRITE_VAL") \
                .Elements.Item(0,0).Value
        except AttributeError:
            # Raise an error if unable to get the production rate
            raise RuntimeError("Unable to get production rate")

class AspenMultiProcessingExample(ASPEN):
    """
    A class to represent an example of using ASPEN with multiprocessing.

    Attributes
    ----------
    aspen_path : str
        The path to the ASPEN file.
    log_folder : str
        The folder where logs will be stored.

    Methods
    -------
    set_coldshot_ratio(ratio):
        Sets the coldshot ratio in the ASPEN model.
    production_rate:
        Retrieves the production rate from the ASPEN model.
    """
    def __init__(self, aspen_path, log_folder):
        """
        Constructs all the necessary attributes for the AspenMultiProcessingExample object.

        Parameters
        ----------
            aspen_path : str
                The path to the ASPEN file.
            log_folder : str
                The folder where logs will be stored.
        """
        super().__init__(log_folder)  # Initialize the parent ASPEN class with the log folder
        self.connect_to_aspen(aspen_path)  # Connect to the ASPEN software with the given path
    
    def set_coldshot_ratio(self, ratio):
        """
        Sets the coldshot ratio in the ASPEN model.

        Parameters
        ----------
        ratio : float
            The coldshot ratio to be set.
        
        Raises
        ------
        RuntimeError
            If unable to set the coldshot ratio.
        """
        try:
            # Set the coldshot ratio in the ASPEN model
            self.get_block_input("CLDSPLT").Elements("FRAC").Elements("CLDSHT-1").Value = ratio
        except AttributeError:
            # Raise an error if unable to set the coldshot ratio
            raise RuntimeError("Unable to set coldshot ratio")
        self.log(f"Coldshot ratio set to {ratio}")  # Log the coldshot ratio
    
    @property
    def production_rate(self):
        """
        Retrieves the production rate from the ASPEN model.

        Returns
        -------
        float
            The production rate.
        
        Raises
        ------
        RuntimeError
            If unable to get the production rate.
        """
        try:
            # Retrieve the production rate from the ASPEN model
            return self.get_calculator_block() \
                .Elements("OUTVAR") \
                .Elements("Output") \
                .Elements("WRITE_VAL") \
                .Elements.Item(0,0).Value
        except AttributeError:
            # Raise an error if unable to get the production rate
            raise RuntimeError("Unable to get production rate")

def multiprocessing_example(coldshot_ratio):
    """
    Example function to demonstrate multiprocessing with ASPEN.

    Parameters
    ----------
    coldshot_ratio : float
        The coldshot ratio to be set.

    Returns
    -------
    float
        The production rate or 0 if an error occurs.
    """
    # Define the path to the ASPEN file
    aspen_path = r"C:\Users\SWAMINATHU\OneDrive - NOVA Chemicals Corporation\My Stuff" \
                 r"\Jodell Project\Experimentation\LDPE Simulation\LDPE Simulation2-Mixing,GE,Tadj,PH2ADJ.bkp"
    try:
        # Create an instance of AspenMultiProcessingExample and set the coldshot ratio
        with AspenMultiProcessingExample(aspen_path, f"Coldshot Simulation {coldshot_ratio}") as aspen:
            aspen.set_coldshot_ratio(coldshot_ratio)
            aspen.run_aspen()  # Run the ASPEN simulation
            return aspen.production_rate  # Return the production rate
    except RuntimeError:
        return 0  # Return 0 if an error occurs

if __name__ == "__main__":
    # Basic Run Example
    with AspenExample(None) as aspen:
        aspen.set_coldshot_ratio(0.5)  # Set the coldshot ratio to 0.5
        aspen.run_aspen()  # Run the ASPEN simulation
        print(aspen.production_rate)  # Print the production rate

    # Multiprocessing example
    with Pool(4) as p:
        # Run the multiprocessing example with different coldshot ratios
        print(p.map(multiprocessing_example, [0.2, 0.4, 0.6, 0.8]))