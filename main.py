import requests
from tkinter import *
from tkinter import ttk
from tkinter.font import Font
from tkinter import messagebox

# counter in seconds
COUNTER = 60
# number of sentences to get from metaphorpsum.com
SENTENCES = 5


class MainWindow:
    def __init__(self, r: Tk, t: str, t_status: str):
        self.root = r
        self.text = t
        self.text_status = t_status
        self.counting = False  # to avoid triggering the countdown multiple times
        self.countdown_var = StringVar(value="")  # to store and display the timer
        self.speed_var = StringVar(value="")  # to display the number of correct words typed
        self.mistakes_var = StringVar(value="")  # to display the number of mistakes
        self.root.minsize(width=1024, height=768)

        mainframe = ttk.Frame(self.root, width=1024, height=768)
        mainframe.configure(borderwidth=10, relief="raised")
        mainframe.grid_propagate(False)
        mainframe.grid(column=1, row=1)

        style = ttk.Style()
        font = Font(font=("Segoe UI", 9, "normal italic"))
        style.configure("Status.TLabel", foreground="green", font=font)
        
        # display source of the text: default or random
        text_status_label = ttk.Label(mainframe, width=20, text=self.text_status, style="Status.TLabel")
        text_status_label.grid(column=2, row=0)
        
        # information labels on left side of the original text
        font = Font(font=("Segoe UI", 12, NORMAL))
        style.configure("Info.TLabel", font=font)
        info_label_1 = ttk.Label(mainframe, text=f"You have to type the text in the gray box.\n"
                                               f"These are {SENTENCES} sentences pulled from\nmetaphorpsum.com",
                                 wraplength=180, style="Info.TLabel")
        info_label_1.grid(column=0, row=1, rowspan=2)
        info_label_2 = ttk.Label(mainframe, text=f"You have {COUNTER} seconds to complete the test.",
                                 wraplength=180, style="Info.TLabel")
        info_label_2.grid(column=0, row=3, rowspan=2)

        # original text
        font = Font(font=("Arial", 18, NORMAL))
        text_text = Text(mainframe, width=43, height=10, wrap=WORD, font=font, background="#cecbcb", padx=10, pady=10)
        text_text.insert(index=INSERT, chars=self.text)
        text_text.configure(state=DISABLED)
        text_text.grid(column=1, row=1, rowspan=4)

        # empty labels on the right side of the original text to allow proper grid alignment
        font = Font(font=("Segoe UI", 14, NORMAL))
        style.configure("Countdown_label.TLabel", foreground="green", font=font)
        font = Font(font=("Segoe UI", 40, NORMAL))
        style.configure("Countdown.TLabel", foreground="green", font=font)
        placeholder_label_2 = ttk.Label(mainframe, style="Countdown_label.TLabel", text=" ")
        placeholder_label_2.grid(column=2, row=1)
        placeholder_label_3 = ttk.Label(mainframe, style="Countdown.TLabel", text=" ")
        placeholder_label_3.grid(column=2, row=2)

        # label to display the timer
        countdown_text_label = ttk.Label(mainframe, style="Countdown_label.TLabel", text="Timer")
        countdown_text_label.grid(column=2, row=3)
        countdown_label = ttk.Label(mainframe, style="Countdown.TLabel", textvariable=self.countdown_var)
        countdown_label.grid(column=2, row=4)

        # canvas to horizontally separate the text boxes and force the width of the frame
        canvas = Canvas(mainframe, width=1024 - 10 - 20, height=5, background="#83b0f7")
        canvas.grid(column=0, columnspan=3, row=5)

        # information labels on left side of the typed text
        info_label_3 = ttk.Label(mainframe, text=f"Click the whitebox and start typing!",
                                 wraplength=180, style="Info.TLabel")
        info_label_3.grid(column=0, row=6, rowspan=2)
        info_label_4 = ttk.Label(mainframe, text=f"Score is calculated comparing original words "
                                                 f"to typed words at the same index",
                                 wraplength=180, style="Info.TLabel")
        info_label_4.grid(column=0, row=8, rowspan=2)

        # Text widget for user to type the text
        font = Font(font=("Arial", 18, NORMAL))
        self.testing_text = Text(mainframe, width=43, height=10, wrap=WORD, font=font, background="white",
                                 padx=10, pady=10)
        self.testing_text.grid(column=1, row=6, rowspan=4)
        self.testing_text.bind("<FocusIn>", self.start_count)
        self.testing_text.bind("<space>", self.update_results)
        self.testing_text.bind("<Return>", self.ignore_cr)
        # configure tag to highlight the mistakes; tags will be added in the final execution of update_results
        self.testing_text.tag_configure("highlight", foreground="red")

        # information labels on right side of the typed text
        font = Font(font=("Segoe UI", 14, NORMAL))
        style.configure("Results_labels.TLabel", foreground="red", font=font)
        speed_text_label = ttk.Label(mainframe, style="Results_labels.TLabel", text="Correct words")
        speed_text_label.grid(column=2, row=6)
        mistakes_text_label = ttk.Label(mainframe, style="Results_labels.TLabel", text="Mistakes")
        mistakes_text_label.grid(column=2, row=8)

        # labels to display number of correct words and mistakes 
        font = Font(font=("Segoe UI", 40, NORMAL))
        style.configure("Results.TLabel", foreground="red", font=font)
        speed_label = ttk.Label(mainframe, style="Results.TLabel", textvariable=self.speed_var)
        speed_label.grid(column=2, row=7)
        mistakes_label = ttk.Label(mainframe, style="Results.TLabel", textvariable=self.mistakes_var)
        mistakes_label.grid(column=2, row=9)

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

    # countdown timer called recursively every second 
    def countdown(self, timer: int):
        self.countdown_var.set(value=f"{timer}")
        if timer > 0:
            self.root.after(1000, self.countdown, timer-1)
        else:
            self.finish()

    # bind to FocusIn event (only once as self.counting becomes True)
    def start_count(self, event):
        if not self.counting:
            self.speed_var.set(value="0")
            self.mistakes_var.set(value="0")
            self.countdown(COUNTER)
            self.counting = True

    # count the correct words and mistake; update corresponding vars; bind to <space> event; extra call at the end
    def update_results(self, event):
        # creating arrays of words from the original and the typed text
        typed_text = self.testing_text.get("1.0", "end -1 chars")  # skip the newline at the end
        typed_text_array = typed_text.split(" ")
        # remove the blank element that might be generated by a space at the end
        if typed_text_array[-1] == "":
            typed_text_array.pop()
        # find the next space in the original text in order to retrieve full words in the array
        next_space = self.text.find(" ", len(typed_text) - 1)
        original_text_array = self.text[0:next_space].split(" ")
        good = 0
        bad = 0
        # print for testing purposes
        print(typed_text_array)
        print(original_text_array)
        print("================")
        # compare the arrays element by element
        for i in range(len(typed_text_array)):
            if i < len(original_text_array) and typed_text_array[i] == original_text_array[i]:
                good += 1
            else:
                bad += 1
                if self.countdown_var.get() == "0":
                    # add tags just at the finish, not during typing
                    # search the mistake from a calculated index
                    col_index = 0
                    # calculate a search index to avoid matching the mistake to early in the original text
                    for w in typed_text_array[0:i-1]:
                        col_index += len(w)
                        col_index += 1
                    search_index = f"1.{col_index}"
                    mistake_start = self.testing_text.search(f"{typed_text_array[i]}", search_index)
                    mistake_end = f"{mistake_start.split('.')[0]}." \
                                  f"{int(mistake_start.split('.')[1]) + len(typed_text_array[i])}"
                    # tag the mistake
                    self.testing_text.tag_add("highlight", mistake_start, mistake_end)
                    # print for testing purposes
                    print(mistake_start, mistake_end)
        self.speed_var.set(value=f"{good}")
        self.mistakes_var.set(value=f"{bad}")

    # ignore Return key and insert space instead
    def ignore_cr(self, event):
        self.testing_text.insert(index=INSERT, chars=" ")
        return "break"

    # refresh results and disable the Text widget
    def finish(self):
        self.update_results("")
        self.testing_text.configure(state=DISABLED)
        messagebox.showinfo(title="Finish", message="Time's up!")

    def quit(self):
        self.root.destroy()


test_text = "Framed in a different way, kinglike curves show us how cockroaches can be pushes. " \
            "If this was somewhat unclear, they were lost without the shelly glue that composed their gander. " \
            "A cent can hardly be considered a whoreson ikebana without also being a drug. They were lost without " \
            "the nervine bass that composed their machine. The zeitgeist contends that the airmail is a margaret."
text_status = "Using default text"

try:
    response = requests.get(f"http://metaphorpsum.com/sentences/{SENTENCES}")
    response.raise_for_status()
    test_text = response.text
except requests.exceptions.RequestException as e:
    print(f"Error getting random text\n**********\n{e}\n**********")
else:
    text_status = "Using random text"
finally:
    print(test_text)
    root = Tk()
    root.title("Typing Speed Test")
    MainWindow(root, test_text, text_status)
    root.mainloop()
