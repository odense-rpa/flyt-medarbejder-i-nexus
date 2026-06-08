from kmd_nexus_client.manager import NexusClientManager
from automation_server_client import WorkItemError
class NexusService:
    def __init__(
        self,
        nexus: NexusClientManager
        ):
        self.nexus = nexus
    
    def tilføj_organisation_til_medarbejder(self, organisationsnavn:str, bruger:dict) -> str:
        
        organisation = self.nexus.organisationer.hent_organisation_ved_navn(organisationsnavn)
        if organisation is None:
            raise WorkItemError("Kunne ikke finde organisation")
        
        if not self.nexus.organisationer.tilføj_organisation_til_medarbejder(bruger, organisation):
            return f"Ikke muligt at tilføje organisation til buger: {organisationsnavn}"
        else:
            return ""

    def fjern_organisation_fra_medarbejder(self, organisationsnavn:str, bruger:dict) -> str:
        
        organisation = self.nexus.organisationer.hent_organisation_ved_navn(organisationsnavn)
        if organisation is None:
            raise WorkItemError("Kunne ikke finde organisation")
        
        if not self.nexus.organisationer.fjern_organisation_fra_medarbejder(bruger, organisation):
            return f"Ikke muligt at fjerne organisation fra bruger: {organisationsnavn}"
        else:
            return ""
    
    def tilføj_rolle_til_medarbejder(self, rollenavn:str, bruger:dict) -> str:
        
        if not self.nexus.brugere.tilføj_rolle_til_bruger(bruger, rollenavn):
            return f"Ikke muligt at tilføje rolle til bruger: {rollenavn}"
        else:
            return ""
    
    def fjern_rolle_fra_medarbejder(self, rollenavn:str, bruger:dict) -> str:
        
        if not self.nexus.brugere.fjern_rolle_fra_bruger(bruger, rollenavn):
            return f"Ikke muligt at fjerne rolle fra bruger: {rollenavn}"
        else:
            return ""