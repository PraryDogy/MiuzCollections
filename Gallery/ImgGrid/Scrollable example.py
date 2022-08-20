import tkinter
import cfg

class Scrollable:
    def Scrollable(self, imgFrame):
        '''
        Returns tkinter scrollable frame. 
        Pack inside this frame any content.
        '''
        
        container = tkinter.Frame(imgFrame)

        canvas = tkinter.Canvas(
            container, bg=cfg.BGCOLOR, highlightbackground=cfg.BGCOLOR)

        scrollbar = tkinter.Scrollbar(
            container, width=12, orient='vertical', command=canvas.yview)

        self.scrollable = tkinter.Frame(canvas)

        self.scrollable.bind(
            "<Configure>", 
            lambda e: canvas.config(scrollregion=canvas.bbox("all"))
            )

        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta), "units"),
            # lambda e: canvas.yview_scroll(-1*(e.delta/120), "units")
            )

        canvas.create_window((0,0), window=self.scrollable, anchor='nw')
        canvas.config(yscrollcommand=scrollbar.set)

        container.pack(fill='both', expand=True)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        return self.scrollable
