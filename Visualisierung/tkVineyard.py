from threading import Event
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import tkinter as tk
import time
import getValues as cosmos

class Animate:

    def __init__(self, root, plot=None, fps=25):
        self.root = root
        self.wait_time = int(1000 / fps)
        self.plot = plot
        self.done = Event()
        #self.pause = Event()

    def animate(self):
        if not self.done.is_set():
            self.plot()
            self.root.after(self.wait_time, self.animate)
      
    def cancel(self):
        self.done.set()

class Main(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()
        self._root().protocol('WM_DELETE_WINDOW', self.endit)
        self.animate = Animate(self._root(), self.plot)

    def create_widgets(self):
        "erzeuge alle Widgets"
        # create figure
        self.fig, self.ax1 = plt.subplots(figsize=(13,5))
        self.ax2 = self.ax1.twinx()
        # frames
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X)
        label_frame = tk.Frame(self)
        label_frame.pack(fill=tk.X)
        visualising_frame = tk.Frame(self)
        visualising_frame.pack(fill=tk.X)
        # Menu-Buttons
        initialize = tk.Button(btn_frame, text="initialize",font=12 ,command=self.db_init)
        initialize.pack(side=tk.LEFT)
        close = tk.Button(btn_frame, text="close",font=12 ,command=self.endit)
        close.pack(side=tk.LEFT)
        # labels in column=0
        label_endpoint=tk.Label(label_frame, text="endpoint: ",font=12)
        label_endpoint.grid(row=0, column=0)
        label_key=tk.Label(label_frame, text="key: ",font=12)
        label_key.grid(row=1, column=0)
        label_database=tk.Label(label_frame, text="database: ",font=12)
        label_database.grid(row=2, column=0)
        label_container=tk.Label(label_frame, text="container: ",font=12)
        label_container.grid(row=3, column=0)
        # entries in column=1
        self.entry_endpoint = tk.Entry(label_frame, bg="white",font=12)
        self.entry_endpoint.grid(row=0, column=1, sticky=tk.EW)
        self.entry_key = tk.Entry(label_frame, bg="white",font=12)
        self.entry_key.grid(row=1, column=1, sticky=tk.EW)
        self.entry_database = tk.Entry(label_frame, bg="white",font=12)
        self.entry_database.grid(row=2, column=1, sticky=tk.EW)
        self.entry_container = tk.Entry(label_frame, bg="white",font=12)
        self.entry_container.grid(row=3, column=1, sticky=tk.EW)
        # set weights
        label_frame.columnconfigure(1, weight=1)
        # visualization
        self.label_output = tk.Label(visualising_frame, text="Geben Sie Ihre Datenquelle an.", font=12, bg="white")
        self.label_output.pack()
        self.canvas_data = FigureCanvasTkAgg(self.fig, master=visualising_frame)
        self.canvas_data.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(self.canvas_data, self)
        toolbar.update()
        self.canvas_data._tkcanvas.pack(fill=tk.BOTH, expand=True)
        # self.canvas.show()
        

    def db_init(self):
        self.endpoint = self.entry_endpoint.get() 
        self.key = self.entry_key.get()
        self.database_name = self.entry_database.get()
        self.container_name=self.entry_container.get()
        if self.endpoint == "":
            # our Cosmos DB
            self.endpoint = 'https://cectesthttpexsample.documents.azure.com:443'
            self.key = '1jEbFBUhKhPFi1eck3FNczVuxGsbX3x7BD6WtLAZF0M1KjdDS8UlvayvkXji907Fk54ekOFGDgLgCFBmWBbgWQ=='
            self.database_name='my-database' 
            self.container_name= 'my-container'
            self.entry_endpoint.insert(0, self.endpoint)
            self.entry_key.insert(0, self.key)
            self.entry_database.insert(0, self.database_name)
            self.entry_container.insert(0, self.container_name)
        self.client, self.database, self.container = cosmos.initialize(self.endpoint, self.key, self.database_name, self.container_name)
        self.label_output["text"]="Initialisierung fertig"
        self._root().update()
        self.animate.animate()
    
    def plot(self):
        # self.label_output["text"]= "hole Daten"
        values, title = cosmos.getValues_from_container(self.container, num=100, sensor_name='sensor1')
        
        humid_limit = 70
        temp_s = values["temperature"]
        humid_s = values["humidity"]
        time_s = values["timestamp"]
        dry_s = [humid_limit for x in range (len(time_s))]
        self.ax1.clear()
        self.ax2.clear()
        self.ax1.plot(time_s, temp_s, label="temperature", color="orange")
        self.ax2.plot(time_s, humid_s, label="humidity", color="blue")
        self.ax2.plot(time_s, dry_s, linestyle="dotted", label="limit", color="red")

        self.fig.autofmt_xdate() # setzt Uhrzeit auf x-achse schräg
        self.ax1.set_ylim(20,35)
        self.ax2.set_ylim(0,110)
        self.ax1.set_xlabel("Zeit")
        self.ax1.set_ylabel("temperatur")
        self.ax2.set_ylabel("humidity")
        mytitle = "\n" + title+"\n"
        self.ax1.set_title(mytitle)
        self.fig.legend(loc='lower right')

        text = "Daten geholt " + time.strftime("%d %b %Y %H:%M:%S")
        # check wether its to dry
        dry = [lambda i:i>humid_limit, humid_s]
        if len(dry)>5:
            text = text + "zu tocken => starten der Bewässerung"
        self.label_output["text"]= text

        self.canvas_data.draw()
        self._root().update()

    def endit(self):
        "Beende die Anwendung sauber"
        print("Anwendung beendet")
        self._root().quit()
        self._root().destroy()

def main():
    "main"
    root = tk.Tk()
    root.title("Cosmos DB - get Data")
    root.minsize(600,200)
    _main = Main(root)
    root.mainloop()

if __name__ == '__main__':
    main()
