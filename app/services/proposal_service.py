from app.db.database import SessionLocal
from app.models.models import CommercialProposal

def save_proposal(client_inn: str, file_path: str) -> int:
    db = SessionLocal()
    proposal = CommercialProposal(client_inn=client_inn, file_path=file_path)
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    db.close()
    return proposal.id