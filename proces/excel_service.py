import openpyxl
from pathlib import Path
from proces.models import Medarbejder, Opgavetype


class ExcelService:
    def __init__(self, excel_sti: str | Path):
        self.excel_sti = excel_sti

    def afkode_excel(self) -> list[Medarbejder]:
        wb = openpyxl.load_workbook(self.excel_sti, data_only=True)
        medarbejdere: list[Medarbejder] = []

        for opgavetype in Opgavetype:
            if opgavetype.value not in wb.sheetnames:
                continue

            ws = wb[opgavetype.value]
            headers = [cell.value for cell in ws[1]]

            medarbejder_col = headers.index("Medarbejdere")

            if opgavetype in (Opgavetype.TILFOEJELSE, Opgavetype.FJERNELSE):
                kontekst_col = headers.index("Organisation")
                kontekst_felt = "organisation"
            else:
                kontekst_col = headers.index("Rolle")
                kontekst_felt = "rolle"

            current_kontekst: str | None = None

            for row in ws.iter_rows(min_row=2, values_only=True):
                kontekst_value = row[kontekst_col]
                initialer_value = row[medarbejder_col]

                if kontekst_value:
                    current_kontekst = str(kontekst_value).strip()

                if not initialer_value:
                    continue

                for initialer in str(initialer_value).splitlines():
                    initialer = initialer.strip()
                    if not initialer:
                        continue

                    m = Medarbejder(
                        initialer=initialer,
                        opgavetype=opgavetype,
                        **{kontekst_felt: current_kontekst},
                    )
                    medarbejdere.append(m)

        return medarbejdere
        