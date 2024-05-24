
try :
    import pywinstyles
    import logger_manager
    import spacy
    import numpy as np
    import pandas as pd
    import customtkinter
except Exception as e:
    import os
    os.system("pip install -r requirements.txt")

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("dark-blue")

nlp = spacy.load('en_core_web_sm')


def method_test():
    print("Method Called")


blacklist = ['library', 'audio', 'books', 'audiobook', 'read', 'tobuy', 'ebook', 'ya', 'ownedbooks', 'default',
             'readin', 'kindle', 'bookclub', 'series', 'booksiown', 'owned', 'currentlyreading', 'favourites',
             'favorites', 'ebooks', 'childrens', 'toread', 'audiobooks']


def button_callback():
    print("button pressed")


def main():
    manager = logger_manager.LoggerManager()
    logger = manager.get_logger()

    RAW_DATA = pd.read_csv("../datasets/books_updated.csv")

    columns = ['original_title', 'tag_name']
    df = RAW_DATA[columns].copy()
    test = RAW_DATA['tag_name'].copy()
    test.replace("", np.nan, inplace=True)
    print(test.head())
    test.dropna(inplace=True)

    unique_tags = [val.strip() for sublist in test.dropna().str.split(",").tolist() for val in sublist]
    print(unique_tags[0:10])
    tags_summary = pd.DataFrame(unique_tags, columns=['tag_name']).value_counts().reset_index().rename(
        columns={0: 'count'})
    print(tags_summary[0:5])

    print("end")

    app = customtkinter.CTk()
    app.title("Books Updated")
    app.geometry("800x600")

    button = customtkinter.CTkButton(app, text="my button", command=button_callback)
    button.grid(row=0, column=0, padx=20, pady=20)

    app.mainloop()


class App(customtkinter.CTk):
    WIDTH = 1024
    HEIGHT = 768
    DEFAULT_GRAY = ("gray50", "gray30")

    def __init__(self, isTest: bool = False):
        super().__init__()
        self.__build_ui()
        # self.__drawMenuFrame()

    def __build_ui(self):

        self.title("Test")
        # pywinstyles.change_header_color(self, color="#202123")
        # pywinstyles.change_border_color(self, color="#515473")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.update()
        self.minsize(App.WIDTH, App.HEIGHT)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        # self.protocol("WM_DELETE_WINDOW", self.on_closing())

        self.frame = customtkinter.CTkFrame(master=self)
        self.frame.pack(expand=True, fill="both", padx=5, pady=5)

        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(2, weight=1)

    def on_closing(self):
        self.destroy()

    def __drawMenuFrame(self):
        self.menu_frame = customtkinter.CTkFrame(self, corner_radius=0, width=240, height=768)
        self.menu_frame.pack(expand=True, fill="y", pady=5)
        self.menu_frame.columnconfigure(0, weight=1)
        self.menu_frame.rowconfigure(1, weight=1)
        self.menu_frame.grid_rowconfigure(4, weight=1)
        pywinstyles.set_opacity(self.menu_frame.winfo_id(), value=0.1)
        self.menu_title = customtkinter.CTkLabel(self.menu_frame, text="The Golden Bough", compound="center",
                                                 font=customtkinter.CTkFont(size=15, weight="bold"))
        pywinstyles.set_opacity(self.menu_title.winfo_id(), value = 1.0)
        self.menu_title.grid(row=0, column=0, padx=20, pady=20)

        self.sidebar_button_1 = customtkinter.CTkButton(self.menu_frame, command=self.on_button_clicked)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=(20, 10))
        # pywinstyles.set_opacity(self.menu_frame.winfo_id(), color="white")

        self.appearence_mode_label = customtkinter.CTkLabel(self.menu_frame, text="Appearence Mode", anchor="w")
        self.appearence_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))

        self.appearence_mode_optionmenu = customtkinter.CTkOptionMenu(self.menu_frame,
                                                                      values=["Test", "Test2", "Test3"],
                                                                      command=self.change_appearence_mode)
        self.appearence_mode_optionmenu.grid(row=6, column=0, padx=20, pady=(10, 10))



    def change_appearence_mode(self, mode: str):
        if mode == "Test":
            customtkinter.set_appearance_mode("Dark")
        elif mode == "Test2":
            customtkinter.set_appearance_mode("Light")
        else:
            customtkinter.set_appearance_mode("System")

    def on_button_clicked(self):
        print("test")
        print(pywinstyles.get_accent_color())

    def draw_scrollable_frame(self):
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self.frame)
        self.scrollable_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=(0,10), sticky="nsew")



if __name__ == '__main__':
    TEST = True
    app = App(TEST)
    app.mainloop()
