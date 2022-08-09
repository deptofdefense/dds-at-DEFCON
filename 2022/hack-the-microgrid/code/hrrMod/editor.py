import numpy as np # needed for array shape
import netCDF4 # needed to read and edit netCDF4 files
import shutil # needed to make a copy of the file
import glob # needed to search current directory
import sys # needed to exit


class Editor:

    def __init__(self, ncFile):
        """
        Init method

        Args:
            ncFile (str): the netCDF4 file to edit
        """

        self.dset = netCDF4.Dataset(ncFile, 'r+')

        #print(str(self.dset))

    def editStatusField(self, key, selection, value):
        """
        Function to edit the status field within an HRRR file

        Args:
            key (str): the field key to edit
            selection (str / int): the data point to edit
            value (float): the new value to use
        """

        if str(selection).isdigit(): # edit a specific value
            self.dset[str(key)][int(selection)] = float(value)
        else: # edit all of them
            self.dset[str(key)][:] = float(value)


    def editWeatherField(self, key, val, time='a', x='a', y='a'):
        """
        Edits the HRRR weather field given by the key variable.  
        Allows the user to change a specific x-y coordinate and time or 
        all possible values when the user places an 'a' in the field

        Args:
            key (str): the key for the HRRR field to edit
            val (float): The new value of the field
            time (str / int, optional): The forecast hour to edit, or use 'a' to edit all of them. Defaults to 'a'.
            x (str / int, optional): the row to edit, or 'a' for all of them. Defaults to 'a'.
            y (str / int, optional): the column to edit, or 'a' for all of them. Defaults to 'a'.
        """

        if str(time).isdigit(): # targeting a specific time
            if str(x).isdigit(): # targeting a specific x
                if str(y).isdigit(): # targeting a specific y
                    #print(str(self.dset[str(key)][int(time), int(x), int(y)]))
                    self.dset[str(key)][int(time), int(x), int(y)] = float(val)
                else: # target all y
                    #print(str(self.dset[str(key)][int(time), int(x), :]))
                    self.dset[str(key)][int(time), int(x), :] = float(val)
            else: # target all x
                if str(y).isdigit(): # targeting a specific y
                    #print(str(self.dset[str(key)][int(time), :, int(y)]))
                    self.dset[str(key)][int(time), :, int(y)] = float(val)
                else: # target all y
                    #print(str(self.dset[str(key)][int(time), :, :]))
                    self.dset[str(key)][int(time), :, :] = float(val)
        else: # target all time
            if str(x).isdigit(): # targeting a specific x
                if str(y).isdigit(): # targeting a specific y
                    #print(str(self.dset[str(key)][:, int(x), int(y)]))
                    self.dset[str(key)][:, int(x), int(y)] = float(val)
                else: # target all y
                    #print(str(self.dset[str(key)][:, int(x), :]))
                    self.dset[str(key)][:, int(x), :] = float(val)
            else: # target all x
                if str(y).isdigit(): # targeting a specific y
                    #print(str(self.dset[str(key)][:, :, int(y)]))
                    self.dset[str(key)][:, :, int(y)] = float(val)
                else: # target all y
                    #print(str(self.dset[str(key)][:, :, :]))
                    self.dset[str(key)][:, :, :] = float(val)

    def listField(self, key, loc):
        """
        Returns a list of values for the given key

        Args:
            key (str): The key representing the HRRR field to look at
            loc (int / str): 'a' for all of them, or a int for a specific value in the array

        Returns:
            str : The values in the key as a string, using new line delimiters
        """
        
        tempString = ''

        try:
            if loc == 'a':
                for x in self.dset[str(key)]:
                    tempString = tempString + str(x) + '\n'
            else:
                tempString = tempString + str(self.dset[str(key)][int(loc)]) + '\n'
        except:
            tempString = "Error, Key or position not found"
        
        return tempString

    def editInteractive(self):
        """
        Interactive function that prompts the user for fields and values to edit.  
        This acts as an entry point for the other functions when the user is local.  
        """

        print("\nList of editable variables:")
        var = list(self.dset.variables.keys())
        for i in range(len(var)):
            print(f"{i} : {str(var[i])}")
        
        try:

            choice = input("Enter the field number to edit: ")

            print(f"\n\n{str(var[int(choice)])}")

            if len(np.shape(self.dset[str(var[int(choice)])])) == 3: # editing a conventional weather field

                while True:

                    print("\n"+str(self.listField(str(var[int(choice)]), 'a')))

                    time = input(f"Enter a time from 0 to {str(len(self.dset[str(var[int(choice)])]) - 1)} to edit, 'a' to do all, or anything else to go back: ")
                    
                    if (str(time).isdigit() and int(time) <= (len(self.dset[str(var[int(choice)])]) - 1)) or str(time).lower() == 'a':
                        print(str(self.listField(str(var[int(choice)]), time)))
                    else:
                        break # nonvaid entry, exit loop

                    row = len(self.dset[str(var[int(choice)])][0]) - 1
                    col = len(self.dset[str(var[int(choice)])][0][0]) - 1

                    xVal = input(f"Enter the row number from 0 to {str(row)} to edit or 'a' for all: ")
                    
                    if (str(xVal).isdigit() and int(xVal) <= row) or str(xVal).lower() == 'a':
                        yVal = input(f"Enter the column from 0 to {str(col)} to edit or 'a' for all: ")

                        if (str(yVal).isdigit() and int(yVal) <= col) or str(yVal).lower() == 'a':
                            value = input('Enter the new value of the field: ')
                            self.editWeatherField(str(var[int(choice)]), value, time, xVal, yVal)
                        else:
                            break # nonvaid entry, exit loop
                    else:
                        break # nonvaid entry, exit loop

                    
            
            else: # editing one of the one dimensional fields

                while True:
                    print("\n"+str(self.listField(str(var[int(choice)]), 'a')))

                    selction = input(f"Enter the selection from 0 to {str(len(self.dset[str(var[int(choice)])]) - 1)} to edit, 'a' to do all, or anything else to go back: ")
                    
                    if (str(selction).isdigit() and int(selction) <= (len(self.dset[str(var[int(choice)])]) - 1)) or str(selction).lower() == 'a':
                        value = input('Enter the new value of the field: ')
                        self.editStatusField(str(var[int(choice)]), selction, value)
                    else:
                        break # nonvaid entry, exit loop


        except IndexError:
            print("Error, index not found")
        except ValueError:
            print("Error, incorrect value entered")

if __name__ == "__main__":
    files = glob.glob('./*.nc')

    if len(files) < 1:
        print("No netCDF4 files found in current directory")
        print("Please make sure that all netCDF files are using '.nc' as a file extension")
        sys.exit(1)
    else:
        print("List of '.nc' files: ")
        for i in range(len(files)):

            temp = str(files[i]).split('\\')
            files[i] = temp[len(temp) - 1]

            print(f'File {str(i)} : {str(files[i])}')

    fileChoice = input('Enter the number of the file to use, or anything to exit: ')

    if str(fileChoice).isdigit():
        if int(fileChoice) < len(files):
            print(f'Using {str(files[int(fileChoice)])}')
            
            tempFile = str(files[int(fileChoice)]).split('.')[0]
            tempFile = tempFile + '-edit.nc'

            shutil.copyfile(str(files[int(fileChoice)]), tempFile)
            print(f"Creating {str(tempFile)} to contain edits")

            editor = Editor(tempFile)

            while True:
                try:
                    print("Edit fields, or press CTRL+C to exit: ")
                    editor.editInteractive()
                except KeyboardInterrupt:
                    print("\nExiting")
                    editor.dset.close()
                    sys.exit(0)

    else:
        print('Not an int, exiting')
        sys.exit()
