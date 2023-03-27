from fpdf import FPDF

class PDF1(FPDF):
    """Clase que crea el reporte de revaluación de cupo """
    def header(self):
        """Crea el encabezado de todas las hojas del pdf"""
        # Logo
        self.image('Imagenes/gasco.png', 10, 8, 25)
        # Fuente
        self.set_font('helvetica', 'B', 20)
        # Padding o relleno
        self.cell(80)
        # Título
        self.cell(30, 10, 'Reporte reevaluación de cupo', border=False, ln=1, align='C')
        # Line break
        self.ln(5)
    def chapter_title(self,  ch_title):
        """Crea un título"""
        # set font
        self.set_font('helvetica', '', 12)
        # background color
        self.set_fill_color(200, 220, 255)
        # Chapter title
        self.cell(0, 5, ch_title, ln=1, fill=1)
    def chapter_title_2(self,  ch_title):
        """Crea un subtítulo"""
        # set font
        self.set_font('helvetica', 'B', 15)
        # Chapter title
        self.cell(0,  5, ch_title, ln=1, align = 'C')
        # line break
        self.ln()

class PDF2(FPDF):
    """Clase que crea el reporte de cliente nuevo"""
    def header(self):
        """Crea el encabezado de todas las hojas del pdf"""
        # Logo
        self.image('Imagenes/gasco.png', 10, 8, 25)
        # font
        self.set_font('helvetica', 'B', 20)
        # Padding
        self.cell(80)
        # Title
        self.cell(30, 10, 'Reporte cliente nuevo', border=False, ln=1, align='C')
        # Line break
        self.ln(5)
    def chapter_title(self,  ch_title):
        """Crea un título"""
        # set font
        self.set_font('helvetica', '', 12)
        # background color
        self.set_fill_color(200, 220, 255)
        # Chapter title
        self.cell(0, 5, ch_title, ln=1, fill=1)
    def chapter_title_2(self,  ch_title):
        """Crea un subtítulo"""
        # set font
        self.set_font('helvetica', 'B', 15)
        # Chapter title
        self.cell(0,  5, ch_title, ln=1, align = 'C')
        # line break
        self.ln()
