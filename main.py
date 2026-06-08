import asyncio
import logging
import sys
import argparse
from pathlib import Path

from automation_server_client import AutomationServer, Workqueue, WorkItemError, Credential, WorkItemStatus
from kmd_nexus_client.manager import NexusClientManager
from odk_tools.tracking import Tracker
from odk_tools.reporting import report
from proces.excel_service import ExcelService
from proces.nexus_service import NexusService
from proces.models import Medarbejder, Opgavetype

nexus: NexusClientManager
tracker: Tracker

procesnavn = "Flyt medarbejder i Nexus"

async def populate_queue(workqueue: Workqueue, excel_sti:str):
    logger = logging.getLogger(__name__)

    excel_service = ExcelService(excel_sti)
    
    medarbejdere: list[Medarbejder] = excel_service.afkode_excel()
    
    for medarbejder in medarbejdere:
        workqueue.add_item(medarbejder.model_dump(), medarbejder.initialer)
    
    Path(excel_sti).parent.joinpath("Indlæst.txt").write_text("", encoding="utf-8")


async def process_workqueue(workqueue: Workqueue):
    logger = logging.getLogger(__name__)
    nexus_service = NexusService(nexus)
    
    for item in workqueue:
        with item:
            medarbejder: Medarbejder = Medarbejder.model_validate(item.data) # Item data deserialized from json as dict
            try:
                bruger = nexus.brugere.hent_bruger(medarbejder.initialer)
                if bruger is None:
                    raise WorkItemError(f"Kunne ikke hente bruger i Nexus")
                
                manuel_besked = ""
                
                match medarbejder.opgavetype:
                    case Opgavetype.TILFOEJELSE:
                        manuel_besked = nexus_service.tilføj_organisation_til_medarbejder(medarbejder.organisation, bruger)                           
                    case Opgavetype.FJERNELSE:
                        manuel_besked = nexus_service.fjern_organisation_fra_medarbejder(medarbejder.organisation, bruger)
                    case Opgavetype.TILFOEJELSE_ROLLE:
                        manuel_besked = nexus_service.tilføj_rolle_til_medarbejder(medarbejder.rolle, bruger)
                    case Opgavetype.FJERNELSE_ROLLE:
                        manuel_besked = nexus_service.fjern_rolle_fra_medarbejder(medarbejder.rolle, bruger)
                        
                if manuel_besked != "":
                    report(
                    "flyt_medarbejder_i_nexus",
                    "Fejl",
                    {
                        "Initialer": medarbejder.initialer,
                        "Fejl": manuel_besked
                    }
                    )
                    tracker.track_partial_task(procesnavn)
                else:
                    tracker.track_task(procesnavn)
                    
            except WorkItemError as e:
                # A WorkItemError represents a soft error that indicates the item should be passed to manual processing or a business logic fault                
                report(
                    "flyt_medarbejder_i_nexus",
                    "Fejl",
                    {
                        "Initialer": medarbejder.initialer,
                        "Fejl": e
                    }
                )
                logger.error(f"Error processing item: {medarbejder.initialer}. Error: {e}")
                item.fail(str(e))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    ats = AutomationServer.from_environment()
    workqueue = ats.workqueue()
    parser = argparse.ArgumentParser(description=procesnavn)
    
    parser.add_argument(
        "--queue",
        action="store_true"
    )
    
    parser.add_argument(
        "--excel-file",
        type=Path,
        default=Path("Excel.xlsx"),
    )
    
    args = parser.parse_args()

    # Initialize external systems for automation here..
    nexus_credential = Credential.get_credential("KMD Nexus - produktion")
    tracking_credential = Credential.get_credential("Odense SQL Server")
    
    nexus = NexusClientManager(
        nexus_credential.data["instance"],
        nexus_credential.username or "",
        nexus_credential.password or "",
    )
    
    tracker = Tracker(
        username=tracking_credential.username or "",
        password=tracking_credential.password or ""
    )

    # Queue management
    if args.queue:
        workqueue.clear_workqueue(WorkItemStatus.NEW)
        asyncio.run(populate_queue(workqueue, args.excel_file))
        exit(0)

    # Process workqueue
    asyncio.run(process_workqueue(workqueue))
