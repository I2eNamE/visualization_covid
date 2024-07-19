# Importing the required libraries
import os
from supabase import create_client, Client
from matplotlib.figure import Figure
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter.ttk import Combobox

# Read the environment variables
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
# Create a new Supabase client
supabase: Client = create_client(url, key)

# set graph font
mpl.font_manager.fontManager.addfont('Sarabun-Regular.ttf')
mpl.rc('font', family='Sarabun')
mpl.rcParams ['font.family'] = ('Sarabun')

# Define the Dropdown class
class Dropdown(tk.Frame):
    def __init__(self, master, **options):
        # Create the frame
        super().__init__(master)
        # Set the default options
        for option in ['text', 'unit', 'values', 'font', 'width']:
            setattr(self, option, options.get(option, None))

        # Create the label and combobox
        tk.Label(self, text=self.text, font=self.font).pack(side=tk.LEFT)
        self.dropdown = Combobox(self, width=self.width, values=self.values, font=self.font, state="readonly")
        self.dropdown.pack(side=tk.LEFT, padx=5)
        self.dropdown.current(0)
        tk.Label(self, text=self.unit, font=self.font).pack(side=tk.LEFT)
    
    # Define the get methods
    def get(self):
        return self.dropdown.get()
    
    # Define the set methods
    def set(self, value):
        self.dropdown.set(value)

    # Define the current method
    def current(self, index):
        self.dropdown.current(index)

    def bind(self, event, function):
        self.dropdown.bind(event, function)

# Define the Page class
class Page:
    def __init__(self):
        # Create the root window
        self.root = tk.Tk()
        # Set the window size, title, background color, and font
        self.root.geometry("1024x768+240+25")
        self.root.title("Data Visualizer")
        self.root.configure(bg="#FFF")
        self.root.option_add("*Font", "Arial 20")
        self.root.option_add("*Background", "#FFF")
        self.root.attributes('-fullscreen',True)
        self.root.bind("<F11>", lambda event: self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen")))
        self.root.bind("<Escape>", lambda event: self.root.quit())

        # Create a variable to store the current page
        self.current = tk.StringVar(self.root, "covid")

        # Create the header, optional, and body frames
        self.header = tk.Frame(self.root)
        self.header.pack(padx=50, pady=10)

        self.optional = tk.Frame(self.root)
        self.optional.pack(padx=50, pady=10)

        self.body = tk.Frame(self.root, bg="#EBA9A9")
        self.body.pack(fill=tk.BOTH, padx=15, pady=15, ipadx=15, ipady=15)

        # Create the title lable
        self.title = tk.Label(self.header, text="Data Visualizer", font=("Arial", 36))
        self.title.pack(padx=5,pady=10)

        # Create the topic radio buttons
        self.covid_btn = tk.Radiobutton(self.header, text="Covid", bg="#D9D9D9", selectcolor="#003049", width=10, borderwidth=0,
                            indicator=0, command=self.covid, value="covid", variable=self.current)
        self.covid_btn.pack(side=tk.LEFT, padx=20)

        self.fault_btn = tk.Radiobutton(self.header, text="Fault", bg="#D9D9D9", selectcolor="#003049", width=10, borderwidth=0,
                            indicator=0, command=self.fault, value="fault", variable=self.current)
        self.fault_btn.pack(side=tk.LEFT, padx=20)

        self.farm_btn = tk.Radiobutton(self.header, text="Farm", bg="#D9D9D9", selectcolor="#003049", width=10, borderwidth=0,
                            indicator=0, command=self.farm, value="farm", variable=self.current)
        self.farm_btn.pack(side=tk.LEFT, padx=20)
    # ani = animation.FuncAnimation(f, animate, interval=1000)

    # Create the clear function
    def _clear(self):
        # Clear the body and optional frames
        for widget in self.body.winfo_children():
            widget.destroy()

        for widget in self.optional.winfo_children():
            widget.destroy()
        
        # Change the color of the selected button
        if self.current.get() == "covid":
            self.covid_btn.configure(fg="#FFF")
            self.fault_btn.configure(fg="#000")
            self.farm_btn.configure(fg="#000")
        elif self.current.get() == "fault":
            self.covid_btn.configure(fg="#000")
            self.fault_btn.configure(fg="#FFF")
            self.farm_btn.configure(fg="#000")
        elif self.current.get() == "farm":
            self.covid_btn.configure(fg="#000")
            self.fault_btn.configure(fg="#000")
            self.farm_btn.configure(fg="#FFF")

    def update():
        return

    # Create the covid function
    def covid(self):
        # Clear the body and optional frames
        self._clear()
        # Create the age dropdown
        age_set = ["เลือกช่วงอายุ", "น้อยกว่า 18", "19-30", "31-40", "41-50", "51-60", "61-70", "71-80", "81-90", "91-100", "มากกว่า 101"]
        age_option = Dropdown(self.optional, text="อายุ", unit="ปี", values=age_set, font=("Arial", 20), width=9)
        age_option.pack(side=tk.LEFT, padx=20)

        # Create the province dropdown
        province_set = ["เลือกจังหวัด"] + list(dict.fromkeys([data['province_of_onset'] for data in supabase.from_("covid").select("province_of_onset").execute().data if data['province_of_onset'] is not None]))
        province_option = Dropdown(self.optional, text="จังหวัด", values=province_set, font=("Arial", 20), width=10)
        province_option.pack(side=tk.LEFT, padx=20)


        def update_graph1(selected_province, selected_age_range, plot1, graph1):
            min_age, max_age = convert_age_to_query_condition(selected_age_range)
            
            if selected_province == "เลือกจังหวัด":
                query = supabase.from_("covid").select("risk")
            else:
                query = supabase.from_("covid").select("risk").eq("province_of_onset", selected_province)
                
            if min_age is not None and max_age is not None:
                query = query.gte("age", min_age).lte("age", max_age)
            
            data = query.execute().data
            # Count the occurrences of each risk
            risk_counts = {}
            for item in data:
                risk = item['risk']
                if risk in risk_counts:
                    risk_counts[risk] += 1
                else:
                    risk_counts[risk] = 1
                    
            # Calculate total count and percentages
            total_count = sum(risk_counts.values())
            risk_percentages = {risk: (count / total_count * 100) for risk, count in risk_counts.items()}
            
            # Filter out risks below 0.5%
            filtered_risks = {risk: percentage for risk, percentage in risk_percentages.items() if percentage >= 0.5}
            
            # Prepare data for pie chart
            labels = filtered_risks.keys()
            sizes = filtered_risks.values()
            
            plot1.clear()
            plot1.title.set_text("COVID-19 Risk Analysis (%) in " + selected_province)
            
            # Check if there are any categories to display
            if sizes:
                plot1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            else:
                plot1.text(0.5, 0.5, 'No data available or all categories are below 0.5%', horizontalalignment='center', verticalalignment='center')
            plot1.axis('equal')
            graph1.draw()

        def update_graph2(selected_province, plot2, graph2):
            # Define age ranges to query and count
            age_ranges = [
                "น้อยกว่า 18",
                "19-30",
                "31-40",
                "41-50",
                "51-60",
                "61-70",
                "71-80",
                "81-90",
                "91-100",
                "มากกว่า 101"
            ]

            # Prepare lists to hold the labels and counts for each age range
            labels = age_ranges 
            counts = []

            for age_range in age_ranges:
                min_age, max_age = convert_age_to_query_condition(age_range)

                # Adjust query based on selected province
                if selected_province != "เลือกจังหวัด":
                    query = supabase.from_("covid").select("id", count="exact")
                    if min_age is not None and max_age is not None:
                        query = query.gte("age", min_age).lte("age", max_age)
                    query = query.eq("province_of_onset", selected_province)
                else:
                    query = supabase.from_("covid").select("id", count="exact")
                    if min_age is not None and max_age is not None:
                        query = query.gte("age", min_age).lte("age", max_age)

                # Execute the query and get the count
                result = query.execute()
                count = len(result.data)  # Assuming result.data is a list of records

                counts.append(count)

            plot2.clear()
            plot2.title.set_text("Total Number of People by Age Range in " + selected_province)

            # Plot a bar chart
            bar_positions = range(len(labels))  # Positional index for each bar
            plot2.bar(bar_positions, counts, tick_label=labels)

            # Customize the plot
            plot2.set_xticklabels(labels, rotation=45, ha="right")
            plot2.set_ylabel("Total Number of People")
            graph2.draw()
            
        def convert_age_to_query_condition(selected_age_range):
            if '-' in selected_age_range:
                min_age, max_age = selected_age_range.split('-')
                return int(min_age), int(max_age)
            elif(selected_age_range == 'น้อยกว่า 18'):
                return int(0), int(17)
            elif(selected_age_range == 'มากกว่า 101'):
                return int(101), int(1000)
            return None, None

        def on_dropdown_change(event):
            selected_province = province_option.get()
            selected_age_range = age_option.get()
            update_graph1(selected_province, selected_age_range, plot1, graph1)
            update_graph2(selected_province, plot2, graph2)

            
        province_option.bind("<<ComboboxSelected>>", on_dropdown_change)
        age_option.bind("<<ComboboxSelected>>", on_dropdown_change)
        #------- กราฟวงกลมแสดงสาเหตุการติดโควิด -------

        fig1 = Figure(figsize = (6, 8), dpi = 80)
        plot1 = fig1.add_subplot(1, 1, 1)
        plot1.title.set_text("กราฟDDDD")
        # Creating the Tkinter canvas containing the Matplotlib figure 
        graph1 = FigureCanvasTkAgg(fig1, master=self.body)
        # placing the canvas on the Tkinter window 
        graph1.get_tk_widget().pack(side=tk.LEFT, padx=15, pady=20)
        update_graph1("เลือกจังหวัด", "เลือกช่วงอายุ", plot1, graph1)

        #------- กราฟแท่งเปรียบเทียบอายุ -------
        # Create graph
        y = [i**2 for i in range(101)]
        fig2 = Figure(figsize = (6, 8), dpi = 80)
        plot2 = fig2.add_subplot(1,1,1)
        plot2.plot(y) # <- พอร์ตกราฟตรงนี้
        plot2.title.set_text("กราฟตัวอย่าง")
        # Creating the Tkinter canvas containing the Matplotlib figure 
        graph2 = FigureCanvasTkAgg(fig2, master=self.body)
        graph2.draw()
        # placing the canvas on the Tkinter window 
        graph2.get_tk_widget().pack(side=tk.LEFT, padx=15, pady=20)
        update_graph2("เลือกจังหวัด", plot2, graph2)

        #------- กราฟแท่งแสดงจำนวนคนที่ติดแต่ละจังหวัด -------
        # List of squares
        data = supabase.from_("covid_provic").select("*").execute().data

        # Aggregate cases by province
        province_cases = {}
        for item in data:
            province = item["province_of_isolation"]
            cases = item["cases"]
            if province in province_cases:
                province_cases[province] += cases
            else:
                province_cases[province] = cases

        # Sort provinces by cases and select the top 10
        top_provinces = sorted(province_cases.items(), key=lambda x: x[1], reverse=True)[:10]

        # Separate the top 10 for labels and their case counts
        province_names = [item[0] for item in top_provinces]
        cases_counts = [item[1] for item in top_provinces]

        # Sum the cases for all other provinces not in the top 10
        others_cases = sum(province_cases[province] for province in province_cases if province not in province_names)

        # Add the "Others" category to your data
        province_names.append("Others")
        cases_counts.append(others_cases)

        # Plotting the graph
        fig4 = Figure(figsize=(6, 8), dpi=80)
        plot4 = fig4.add_subplot(1, 1, 1)
        bar_positions = range(len(province_names))
        bar = plot4.bar(bar_positions, cases_counts)

        # Setting the title and labels for the axes
        plot4.title.set_text("COVID-19 Cases by Province")
        plot4.set_ylabel("Number of Cases")
        plot4.set_xticks(bar_positions)
        plot4.set_xticklabels(province_names, rotation=45, ha="right", fontsize=8)

        # Drawing the graph
        graph4 = FigureCanvasTkAgg(fig4, master=self.body)
        graph4.draw()
        graph4.get_tk_widget().pack(side=tk.LEFT, padx=15, pady=20)
        
    # Create the fault function
    def fault(self):
        # Clear the body and optional frames
        self._clear()
        
        def update_graph2(selected_province, plot2, graph2):
            plot2.clear()
            # List of squares 
            if selected_province == "เลือกจังหวัด":
                y = [data["recurrence"] for data in supabase.from_("recurrence_province").select("*").execute().data]
                province_name = [data["f_zone_t"] for data in supabase.from_("recurrence_province").select("*").execute().data]
                plot2.title.set_text("กราฟแท่งแสดง Recurrence ในแต่ละจังหวัด")
            else:
                y = [data["recurrence"] for data in supabase.from_("fault").select("recurrence").eq("f_zone_t",selected_province).order('recurrence',desc=True).limit(15).execute().data]
                province_name = [data["f_name_t"] for data in supabase.from_("fault").select("f_name_t").eq("f_zone_t",selected_province).order('recurrence',desc=True).limit(15).execute().data]
                plot2.title.set_text("กราฟแท่งแสดง Recurrence ในจังหวัด"+selected_province)
            # Update data in the existing graph
            bar = plot2.bar(range(len(y)), y)
            for bar, val in zip(bar, y):
                plot2.text(bar.get_x() + bar.get_width() / 2, val,"{:.0f}K".format(val/1000) , ha='center', va='bottom', fontsize=8)
            plot2.set_xticks(range(len(y)))
            plot2.set_xticklabels(province_name, rotation=45, ha='right', fontsize=10)

            # Redraw the graph canvas
            graph2.draw()

        def update_graph3(selected_province, plot3, graph3):
            plot3.clear()
            # List of squares 
            if selected_province == "เลือกจังหวัด":
                type_fault = sorted([data['type'] for data in supabase.from_("fault").select("type").execute().data])
                type_name = list(dict.fromkeys(type_fault))
                type_amount = [type_fault.count(name) for name in type_name ]
                plot3.title.set_text("กราฟวงกลมแสดงประเภทของรอยเลื่อน(%)")
            else:
                type_fault = sorted([data['type'] for data in supabase.from_("fault").select("type").eq("f_zone_t", selected_province).execute().data])
                type_name = list(dict.fromkeys(type_fault))
                type_amount = [type_fault.count(name) for name in type_name ]
                plot3.title.set_text("กราฟวงกลมแสดงประเภทของรอยเลื่อน(%) ในจังหวัด" + selected_province)
                
            plot3.pie(type_amount, labels=type_name, startangle=90, autopct='%1.1f%%')
            # Redraw the graph canvas
            graph3.draw()

        # Create the province dropdown
        province_set = ["เลือกจังหวัด"] + list(dict.fromkeys([data['f_zone_t'] for data in supabase.from_("fault").select("f_zone_t").execute().data]))
        province_option = Dropdown(self.optional, text="จังหวัด", values=province_set, font=("Arial", 20), width=10)
        province_option.pack(side=tk.LEFT, padx=20)
        
        # List of value 
        y = [data["slip_rate"] for data in supabase.from_("slip_rate_province").select("*").execute().data]# <- อ่านค่าจากฐานข้อมูลตรงนี้
        province_name = [data["f_zone_t"] for data in supabase.from_("slip_rate_province").select("*").execute().data]
        #------- กราฟแท่งแสดง Slip_Rate ของแต่ละสถานที่ ในจังหวัด  -------
        # Create graph
        fig1 = Figure(figsize = (6, 8), dpi = 80)
        plot1 = fig1.add_subplot(1,1,1)
        bar = plot1.bar(range(len(y)), y) # <- พอร์ตกราฟตรงนี้
        plot1.title.set_text("กราฟแท่งแสดง Slip_Rate ในแต่ละจังหวัด")
        # Creating the Tkinter canvas containing the Matplotlib figure 
        graph1 = FigureCanvasTkAgg(fig1, master=self.body)
        graph1.draw()
        # placing the canvas on the Tkinter window 
        graph1.get_tk_widget().pack(side=tk.LEFT, padx=15, pady=20)
        for bar, val in zip(bar, y):
            plot1.text(bar.get_x() + bar.get_width() / 2, val,"{:.2f}".format(val) , ha='center', va='bottom', fontsize=8)
        plot1.set_xticks(range(len(y)))
        plot1.set_xticklabels(province_name, rotation=45, ha='right', fontsize=10)
        
        def on_dropdown_change(event):  # เพิ่มพารามิเตอร์ event ที่รับมา
            selected_province = province_option.get()
            # update_graph1(selected_province, plot1, graph1)
            update_graph2(selected_province, plot2, graph2)
            update_graph3(selected_province, plot3, graph3)
            
        province_option.bind("<<ComboboxSelected>>", on_dropdown_change)

        #------- กราฟแท่งแสดง Recurrence ของแต่ละ สถานที่ ในจังหวัด  -------
        # Create graph
        fig2 = Figure(figsize = (6, 8), dpi = 80)
        plot2 = fig2.add_subplot(1,1,1)
        plot2.title.set_text("กราฟแท่งแสดง Recurrence ในแต่ละจังหวัด")
        # Creating the Tkinter canvas containing the Matplotlib figure 
        graph2 = FigureCanvasTkAgg(fig2, master=self.body)
        # placing the canvas on the Tkinter window 
        graph2.get_tk_widget().pack(side=tk.LEFT, padx=15, pady=20)
        update_graph2("เลือกจังหวัด", plot2, graph2)

        # ------- กราฟวงกลมแสดงประเภทของรอยเลื่อน(%) -------
        # Create the pie chart
        fig3 = Figure(figsize = (6, 8), dpi = 80)
        plot3 = fig3.add_subplot(1, 1, 1)
        # plot3.pie(type_amount, labels=type_name, startangle=90, autopct='%1.1f%%')
        plot3.title.set_text("กราฟวงกลมแสดงประเภทของรอยเลื่อน(%)")
        # Creating the Tkinter canvas containing the Matplotlib figure 
        graph3 = FigureCanvasTkAgg(fig3, master=self.body)
        # placing the canvas on the Tkinter window 
        graph3.get_tk_widget().pack(side=tk.LEFT, padx=15, pady=20)
        update_graph3("เลือกจังหวัด", plot3, graph3)
       

    # Create the farm function
    def farm(self):
        def update_graph1(year, plot, graph):
            # List of squares
            if year == "เลือกปี":
                occupation = sorted([data['occupation_name'] for data in supabase.from_("farm").select("occupation_name, register_date").execute().data])
                occupation_name = list(dict.fromkeys(occupation))
                occupation_amount = [occupation.count(name) for name in occupation_name]
            else:
                occupation = sorted([data['occupation_name'] for data in supabase.from_("farm").select("occupation_name, register_date").execute().data if int(data['register_date'].split('/')[2]) <= int(year)])
                occupation_name = list(dict.fromkeys(occupation))
                occupation_amount = [occupation.count(name) for name in occupation_name]
                
            plot.clear()
            plot1.pie(occupation_amount, labels=occupation_name, startangle=90, autopct='%1.1f%%')
            plot1.title.set_text("กราฟวงกลมแสดงอาชีพที่ประกอบ")
            # Redraw the graph canvas
            graph.draw()


        def select_year(event):
            year = year_option.get()
            update_graph1(year, plot1, graph1)

        # Clear the body and optional frames
        self._clear()
        # Create the year dropdown
        year_set = ["เลือกปี"] + sorted(list(set([int(data['register_date'].split('/')[2]) for data in supabase.from_("farm").select("register_date").execute().data])))
        year_option = Dropdown(self.optional, text="ปี", values=year_set, font=("Arial", 20), width=10)
        year_option.pack(side=tk.LEFT, padx=20)
        year_option.bind("<<ComboboxSelected>>", select_year)

        #------- กราฟวงกลมแสดงอาชีพที่ประกอบ  -------
        # Create the pie chart
        fig1 = Figure(figsize = (7, 8), dpi = 100)
        plot1 = fig1.add_subplot(1, 1, 1)
        # Creating the Tkinter canvas containing the Matplotlib figure 
        graph1 = FigureCanvasTkAgg(fig1, master=self.body)
        graph1.draw()
        # placing the canvas on the Tkinter window 
        graph1.get_tk_widget().pack(side=tk.LEFT, padx=15, pady=20)
        update_graph1("เลือกปี", plot1, graph1)

        #------- กราฟเส้นนับจำนวนวันที่จดองค์กร แสดงเป็นปี -------
        # อ่านค่าจากฐาน   
        data_list = supabase.from_("farm").select("register_date").execute().data 
        year_list = []
        for entry in data_list:
            register_date = entry['register_date']
            if register_date:
                year = int(register_date.split('/')[-1])
                year_list.append(year)
        
        # นับจำนวนปี
        year_counts = {} 

        for year in year_list:
            if year in year_counts:
                year_counts[year] += 1
            else:
                year_counts[year] = 1

        sorted_years = sorted(year_counts.keys())

        # รวมค่าจากปีก่อนๆ
        cumulative_counts = {}
        cumulative_sum = 0
        for year in sorted_years:
            cumulative_sum += year_counts[year]
            cumulative_counts[year] = cumulative_sum

        x_values = list(cumulative_counts.keys())
        y_values = list(cumulative_counts.values())

        fig2 = Figure(figsize = (8, 8), dpi = 100)
        plot2 = fig2.add_subplot(1,1,1)
        plot2.plot(x_values, y_values, marker='o') # <- พอร์ตกราฟตรงนี้
        plot2.title.set_text("จำนวนองค์กรที่จดทะเบียน")
        plot2.set_xticks(x_values)
        plot2.set_xticklabels(x_values, rotation=45, ha='right')
        # Creating the Tkinter canvas containing the Matplotlib figure
        graph2 = FigureCanvasTkAgg(fig2, master=self.body)
        graph2.draw()
        # placing the canvas on the Tkinter window 
        graph2.get_tk_widget().pack(side=tk.LEFT, padx=15, pady=20)

# Create a new page and run the main loop
if __name__ == "__main__":
    page = Page()
    page.covid()
    page.root.mainloop()


# code แสดงการ query ใน Supabase เพราะการเชื่อม API กับ Python มันมีข้อจำกัดในการ Query ตาราง เราเลยทำการสร้างตารางเพิ่มใน Supabase เพื่อทำให้ดึงข้อมูลมาใช้ได้ง่าย

# create table recurrence_province as
# SELECT  "f_zone_t", AVG("recurrence") as recurrence FROM fault GROUP BY  "f_zone_t" ORDER BY  AVG("recurrence") desc
# create table slip_rate_province as
# SELECT  "f_zone_t", AVG("slip_rate") as slip_rate FROM fault GROUP BY  "f_zone_t" ORDER BY  AVG("slip_rate") desc