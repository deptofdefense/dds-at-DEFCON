from tkinter import *
from tkinter import HORIZONTAL
from microgridController import MicrogridController


app = Tk()
app.title("DDS - Microgrid Hacking")
app.geometry('700x400')

default_submit_button_text = "OK"

"""
Global Variables
"""
cloud_coverage_actual = DoubleVar(value=0.5)
cloud_coverage_inject = DoubleVar(value=0.5)

wind_speed_actual = IntVar(value=5)
wind_speed_inject = IntVar(value=5)

wind_direction_actual = IntVar(value=180)
wind_direction_inject = IntVar(value=180)

temp_high_actual = IntVar(value=80)
temp_high_inject = IntVar(value=80)

temp_low_actual = IntVar(value=50)
temp_low_inject = IntVar(value=50)

submit_button_text = StringVar(app, default_submit_button_text)

microgridController = MicrogridController("COM13", "COM18")



def submit_button_pressed():
    #print("Callback called")
    data = dict()
    data["cloud_coverage_actual"] = cloud_coverage_actual.get()
    data["cloud_coverage_inject"] = cloud_coverage_inject.get()
    data["wind_speed_actual"] = wind_speed_actual.get()
    data["wind_speed_inject"] = wind_speed_inject.get()
    data["wind_direction_actual"] = wind_direction_actual.get()
    data["wind_direction_inject"] = wind_direction_inject.get()
    data["temp_low_actual"] = temp_low_actual.get()
    data["temp_low_inject"] = temp_low_inject.get()
    data["temp_high_actual"] = temp_high_actual.get()
    data["temp_high_inject"] = temp_high_inject.get()
    print(data)

    microgridController.updateGrid(data)

    # Change the button back to default to indicate changes have been applied
    submit_button_text.set(default_submit_button_text)

def change_detected(*args):
    """
    Function exists to change the submit button text upon change of other widgets
    """
    submit_button_text.set("Submit Changes")


"""
Actual Conditions Column
"""

actual_canvas = Canvas()

actual_label = Label(actual_canvas, text="Actual Conditions", font=("Arial Bold", 20))
actual_label.grid(row=0, column=0, columnspan=2)

cloud_coverage_actual_label = Label(actual_canvas, text="Cloud coverage")
cloud_coverage_actual_label.grid(row=1, column=0)
cloud_coverage_actual_entry = Scale(actual_canvas, from_=0, to=1, length=200, sliderlength=30, orient=HORIZONTAL, variable=cloud_coverage_actual, resolution=.05)
cloud_coverage_actual_entry.bind("<ButtonRelease-1>", change_detected)
cloud_coverage_actual_entry.grid(row=1, column=1)

wind_speed_actual_label = Label(actual_canvas, text="Wind Speed")
wind_speed_actual_label.grid(row=2, column=0)
wind_speed_actual_entry = Scale(actual_canvas, from_=0, to=200, length=200, sliderlength=30, orient=HORIZONTAL, variable=wind_speed_actual)
wind_speed_actual_entry.bind("<ButtonRelease-1>", change_detected)
wind_speed_actual_entry.grid(row=2, column=1)

wind_direction_actual_label = Label(actual_canvas, text="Wind Direction")
wind_direction_actual_label.grid(row=3, column=0)
wind_direction_actual_entry = Scale(actual_canvas, from_=0, to=359, length=200, sliderlength=30, orient=HORIZONTAL, variable=wind_direction_actual)
wind_direction_actual_entry.bind("<ButtonRelease-1>", change_detected)
wind_direction_actual_entry.grid(row=3, column=1)

temp_low_actual_label = Label(actual_canvas, text="Temp. Low")
temp_low_actual_label.grid(row=4, column=0)
temp_low_actual_entry = Scale(actual_canvas, from_=-20, to=140, length=200, sliderlength=30, orient=HORIZONTAL, variable=temp_low_actual)
temp_low_actual_entry.bind("<ButtonRelease-1>", change_detected)
temp_low_actual_entry.grid(row=4,column=1)

temp_high_actual_label = Label(actual_canvas, text="Temp. High")
temp_high_actual_label.grid(row=5, column=0)
temp_high_actual_entry = Scale(actual_canvas, from_=-20, to=140, length=200, sliderlength=30, orient=HORIZONTAL, variable=temp_high_actual)
temp_high_actual_entry.bind("<ButtonRelease-1>", change_detected)
temp_high_actual_entry.grid(row=5,column=1)

actual_canvas.grid(row=0, column=0, padx=20, pady=20)

"""
Inject Conditions
"""
inject_canvas = Canvas()

inject_label = Label(inject_canvas, text="Inject Conditions", font=("Arial Bold", 20))
inject_label.grid(row=0, column=0, columnspan=2)

cloud_coverage_inject_label = Label(inject_canvas, text="Cloud coverage")
cloud_coverage_inject_label.grid(row=1, column=0)
cloud_coverage_inject_entry = Scale(inject_canvas, from_=0, to=1, length=200, sliderlength=30, orient=HORIZONTAL, variable=cloud_coverage_inject, resolution=.05)
cloud_coverage_inject_entry.bind("<ButtonRelease-1>", change_detected)
cloud_coverage_inject_entry.grid(row=1, column=1)

wind_speed_inject_label = Label(inject_canvas, text="Wind Speed")
wind_speed_inject_label.grid(row=2, column=0)
wind_speed_inject_entry = Scale(inject_canvas, from_=0, to=200, length=200, sliderlength=30, orient=HORIZONTAL, variable=wind_speed_inject)
wind_speed_inject_entry.bind("<ButtonRelease-1>", change_detected)
wind_speed_inject_entry.grid(row=2, column=1)

wind_direction_inject_label = Label(inject_canvas, text="Wind Direction")
wind_direction_inject_label.grid(row=3, column=0)
wind_direction_inject_entry = Scale(inject_canvas, from_=0, to=359, length=200, sliderlength=30, orient=HORIZONTAL, variable=wind_direction_inject)
wind_direction_inject_entry.bind("<ButtonRelease-1>", change_detected)
wind_direction_inject_entry.grid(row=3, column=1)

temp_low_inject_label = Label(inject_canvas, text="Temp. Low")
temp_low_inject_label.grid(row=4, column=0)
temp_low_inject_entry = Scale(inject_canvas, from_=-20, to=140, length=200, sliderlength=30, orient=HORIZONTAL, variable=temp_low_inject)
temp_low_actual_entry.bind("<ButtonRelease-1>", change_detected)
temp_low_inject_entry.grid(row=4,column=1)

temp_high_inject_label = Label(inject_canvas, text="Temp. High")
temp_high_inject_label.grid(row=5, column=0)
temp_high_inject_entry = Scale(inject_canvas, from_=-20, to=140, length=200, sliderlength=30, orient=HORIZONTAL, variable=temp_high_inject)
temp_high_inject_entry.bind("<ButtonRelease-1>", change_detected)
temp_high_inject_entry.grid(row=5,column=1)

inject_canvas.grid(row=0, column=2)



"""
Submit Button 
"""

submit_button = Button(app, textvariable=submit_button_text, width=10, command=submit_button_pressed)
submit_button.grid(row=2, column=0, columnspan=3, padx=30, pady=30)




app.mainloop()